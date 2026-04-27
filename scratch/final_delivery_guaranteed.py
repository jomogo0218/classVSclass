import os
import json
import re

def final_delivery():
    print("Final Delivery Start...")
    
    # 1. 讀取原始資料
    def read_f(name):
        with open(name, 'r', encoding='utf-8') as f: return f.read()

    try:
        html = read_f('index.html')
        css = read_f('app.css')
        js = read_f('app.js')
        matches_json = read_f('matches.json')
        schedules_json = read_f('schedules.json')
    except Exception as e:
        print(f"Error reading files: {e}")
        return

    # 2. 處理 CSS (強制橘色主題與樹狀圖樣式)
    # 替換變數
    css = css.replace('#1a73e8', '#f5750a') # Blue -> Orange
    css = css.replace('#e8f0fe', '#fff7ed') # Blue Light -> Orange Light
    css = css.replace('#1557b0', '#e66a09') # Blue Hover -> Dark Orange
    css = css.replace('#2563eb', '#f5750a') # Indigo -> Orange
    
    # 增加樹狀圖與側欄樣式 (確保在裡面)
    tournament_css = """
/* ══ 對戰表佈局 ══ */
.overview-layout { display: flex; height: calc(100vh - 48px); background: #fff; }
.category-sidebar { width: 240px; border-right: 1px solid #e0e0e0; background: #fff; overflow-y: auto; flex-shrink: 0; }
.category-tab { padding: 16px 20px; cursor: pointer; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 12px; font-weight: 600; color: #444; transition: 0.2s; }
.category-tab:hover { background: #fff7ed; color: #f5750a; }
.category-tab.active { background: #fff7ed; color: #f5750a; border-right: 4px solid #f5750a; }
.overview-main { flex: 1; overflow: auto; padding: 30px; background: #f4f6f8; }
.overview-header-card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 6px solid #f5750a; }
.bracket-tree { display: flex; gap: 60px; padding: 20px 0; min-width: max-content; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; min-width: 220px; gap: 40px; }
.round-header { text-align: center; font-size: 12px; font-weight: 800; color: #777; text-transform: uppercase; margin-bottom: 20px; border-bottom: 3px solid #f5750a; padding-bottom: 8px; width: 100%; }
.tree-match { position: relative; background: #fff; border: 1px solid #e0e0e0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06); width: 100%; z-index: 1; }
.tree-team { padding: 10px 14px; font-weight: 600; font-size: 14px; color: #1a1a1a; border-bottom: 1px solid #f0f0f0; }
.tree-footer { padding: 6px 14px; font-size: 11px; background: #fff7ed; color: #f5750a; font-weight: 700; border-top: 1px solid #fee2e2; }
.tree-match::after { content: ''; position: absolute; right: -60px; top: 50%; width: 60px; height: 2px; background: #cbd5e1; z-index: -1; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -60px; top: 50%; width: 2px; height: calc(100% + 42px); background: #cbd5e1; z-index: -1; }
"""
    css += tournament_css

    # 3. 處理 JS (修正 Fetch 攔截)
    js_data = f"const EMBEDDED_MATCHES = {matches_json};\nconst EMBEDDED_SCHEDULES = {schedules_json};\n"
    # 使用 regex 全域替換 fetch 調用，不論參數格式
    js = re.sub(r"await\s+fetch\s*\(['\"].*?schedules\.json.*?['\"]\+?.*?\)", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})", js)
    js = re.sub(r"await\s+fetch\s*\(['\"].*?matches\.json.*?['\"]\+?.*?\)", "({ok:true, json:async()=>EMBEDDED_MATCHES})", js)
    
    # 確保 tab 切換邏輯在
    if "overview" not in js:
        js = js.replace("if (tabId === 'scheduling') renderSchedulingView();", 
                       "if (tabId === 'scheduling') renderSchedulingView();\\n            if (tabId === 'overview') renderTournamentOverview();")

    # 注入對戰表邏輯 (如果不在裡面)
    tournament_js = """
let currentOverviewCategory = null;
function renderTournamentOverview() {
    const sidebar = document.getElementById('categorySidebar');
    if (!sidebar) return;
    sidebar.innerHTML = '';
    const grouped = {};
    matchesData.forEach(m => {
        if (!grouped[m.category]) grouped[m.category] = [];
        grouped[m.category].push(m);
    });
    const categories = Object.keys(grouped).sort();
    categories.forEach(cat => {
        const div = document.createElement('div');
        div.className = `category-tab ${currentOverviewCategory === cat ? 'active' : ''}`;
        div.innerHTML = `<span>🏆</span> <span>${cat}</span>`;
        div.onclick = () => { currentOverviewCategory = cat; renderTournamentOverview(); };
        sidebar.appendChild(div);
    });
    if (!currentOverviewCategory && categories.length > 0) currentOverviewCategory = categories[0];
    if (currentOverviewCategory) renderSelectedCategory(grouped[currentOverviewCategory]);
}

function renderSelectedCategory(matches) {
    const container = document.getElementById('tournamentContainer');
    const title = document.getElementById('selectedCategoryTitle');
    const desc = document.getElementById('selectedCategoryDesc');
    if (!container) return;
    const cat = currentOverviewCategory;
    title.innerHTML = `🏆 ${cat}`;
    const isElimination = cat.includes('羽球');
    desc.textContent = isElimination ? '單淘汰晉級圖' : '循環賽對戰表';
    container.innerHTML = '';
    if (isElimination) renderBracketTree(matches, container);
    else renderRoundRobinGrid(matches, container);
}

function renderRoundRobinGrid(matches, container) {
    const grid = document.createElement('div');
    grid.style.display = 'grid'; grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))'; grid.style.gap = '15px';
    matches.forEach(m => {
        const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
        const card = document.createElement('div');
        card.style.background = '#fff'; card.style.padding = '20px'; card.style.borderRadius = '12px'; card.style.border = '1px solid #eee';
        card.innerHTML = `<div style='display:flex; justify-content:space-between; margin-bottom:12px; font-weight:800; font-size:18px;'><span>${m.teamA}</span><span style='color:#ccc;'>VS</span><span>${m.teamB}</span></div><div class='tree-footer'>${scheduled ? scheduled.date + ' 第 ' + scheduled.periodIndex + ' 節' : '尚未排定'}</div>`;
        grid.appendChild(card);
    });
    container.appendChild(grid);
}

function renderBracketTree(matches, container) {
    const roundsMap = {};
    matches.forEach(m => {
        let r = 'R1';
        if (m.category.includes('第 2 輪')) r = 'R2';
        if (m.category.includes('準決賽')) r = 'SF';
        if (m.category.includes('決賽') && !m.category.includes('準')) r = 'Final';
        if (!roundsMap[r]) roundsMap[r] = [];
        roundsMap[r].push(m);
    });
    const order = ['R1', 'R2', 'SF', 'Final'].filter(r => roundsMap[r]);
    const tree = document.createElement('div');
    tree.className = 'bracket-tree';
    order.forEach(rKey => {
        const roundDiv = document.createElement('div');
        roundDiv.className = 'bracket-round';
        roundDiv.innerHTML = `<div class='round-header'>${rKey}</div>`;
        roundsMap[rKey].forEach(m => {
            const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
            const matchEl = document.createElement('div');
            matchEl.className = 'tree-match';
            matchEl.innerHTML = `<div class='tree-team'>${m.teamA}</div><div class='tree-team'>${m.teamB}</div><div class='tree-footer'>${scheduled ? scheduled.date + ' P' + scheduled.periodIndex : '待定'}</div>`;
            roundDiv.appendChild(matchEl);
        });
        tree.appendChild(roundDiv);
    });
    container.appendChild(tree);
}
"""
    if "renderBracketTree" not in js:
        js += tournament_js

    # 4. 組合 HTML
    # 移除原本的 CSS 與 JS 標籤
    html = re.sub(r'<link.*?href=["\'].*?app\.css.*?["\'].*?>', f"<style>\\n{css}\\n</style>", html)
    
    # 清理舊的 script
    html_lines = []
    for line in html.splitlines():
        if any(x in line for x in ['app.js', 'firebase', 'firebase-config.js']): continue
        html_lines.append(line)
    
    script_block = f"<script>\\n{js_data}\\n{js}\\n</script>"
    final_html = "\\n".join(html_lines).replace('</body>', f"{script_block}\\n</body>")

    # 5. 輸出
    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("DONE! index_local.html is ready.")

if __name__ == "__main__":
    final_delivery()
