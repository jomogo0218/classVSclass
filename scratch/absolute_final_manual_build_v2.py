
import os

def final_manual_build():
    print("Starting Absolute Final Manual Build (V2)...")
    
    # 1. 讀取原始檔案
    def r(n): return open(n, 'r', encoding='utf-8').read()
    
    html_raw = r('index.html')
    css_raw  = r('app.css')
    js_raw   = r('app.js')
    matches  = r('matches.json')
    schedules = r('schedules.json')

    # --- 2. 準備樣式 ---
    css_final = css_raw.replace('#1a73e8', '#f5750a').replace('#2563eb', '#f5750a').replace('#e8f0fe', '#fff7ed')
    css_final += """
/* 強制橘色主題與樹狀圖 */
:root { --blue: #f5750a !important; --blue-light: #fff7ed !important; --orange: #f5750a !important; }
.main-tabs .tab-btn.active { color: #f5750a !important; border-bottom-color: #f5750a !important; }
.overview-layout { display: flex !important; height: calc(100vh - 48px) !important; background: #fff !important; }
.category-sidebar { width: 240px; border-right: 1px solid #ddd; background: #fff; overflow-y: auto; }
.category-tab { padding: 16px; cursor: pointer; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 10px; font-weight: 600; }
.category-tab.active { background: #fff7ed; color: #f5750a; border-right: 4px solid #f5750a; }
.overview-main { flex: 1; overflow: auto; padding: 30px; background: #f4f6f8; }
.bracket-tree { display: flex; gap: 40px; padding: 20px; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; gap: 30px; min-width: 200px; }
.round-header { text-align: center; font-weight: 800; border-bottom: 2px solid #f5750a; padding-bottom: 5px; margin-bottom: 15px; }
.tree-match { position: relative; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.tree-team { font-weight: 600; padding: 4px 0; border-bottom: 1px solid #eee; }
.tree-footer { font-size: 11px; color: #f5750a; margin-top: 5px; font-weight: 700; }
.tree-match::after { content: ''; position: absolute; right: -40px; top: 50%; width: 40px; height: 2px; background: #ccc; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -40px; top: 50%; width: 2px; height: calc(100% + 30px); background: #ccc; }
"""

    # --- 3. 準備邏輯 ---
    js_header = f"const EMBEDDED_MATCHES = {matches};\\nconst EMBEDDED_SCHEDULES = {schedules};\\n"
    js_final = js_raw.replace("await fetch('schedules.json')", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})")
    js_final = js_final.replace('await fetch("schedules.json")', "({ok:true, json:async()=>EMBEDDED_SCHEDULES})")
    js_final = js_final.replace("await fetch('matches.json?v=' + Date.now())", "({ok:true, json:async()=>EMBEDDED_MATCHES})")
    
    # 補強對戰表函數
    if "renderTournamentOverview" not in js_final:
        js_final += """
let currentOverviewCategory = null;
function renderTournamentOverview() {
    const sidebar = document.getElementById('categorySidebar');
    if (!sidebar) return;
    sidebar.innerHTML = '';
    const grouped = {};
    matchesData.forEach(m => { if (!grouped[m.category]) grouped[m.category] = []; grouped[m.category].push(m); });
    const cats = Object.keys(grouped).sort();
    cats.forEach(c => {
        const d = document.createElement('div');
        d.className = `category-tab ${currentOverviewCategory === c ? 'active' : ''}`;
        d.innerHTML = `<span>🏆</span> <span>${c}</span>`;
        d.onclick = () => { currentOverviewCategory = c; renderTournamentOverview(); };
        sidebar.appendChild(d);
    });
    if (!currentOverviewCategory && cats.length > 0) currentOverviewCategory = cats[0];
    if (currentOverviewCategory) {
        const container = document.getElementById('tournamentContainer');
        const title = document.getElementById('selectedCategoryTitle');
        const desc = document.getElementById('selectedCategoryDesc');
        title.innerHTML = `🏆 ${currentOverviewCategory}`;
        const isElim = currentOverviewCategory.includes('羽球');
        desc.textContent = isElim ? '單淘汰晉級圖' : '循環賽對戰表';
        container.innerHTML = '';
        if (isElim) renderBracketTree(grouped[currentOverviewCategory], container);
        else renderRoundRobinGrid(grouped[currentOverviewCategory], container);
    }
}
function renderRoundRobinGrid(matches, container) {
    const grid = document.createElement('div');
    grid.style.display = 'grid'; grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))'; grid.style.gap = '15px';
    matches.forEach(m => {
        const s = scheduledMatches.find(sm => sm.matchId === m.id);
        const c = document.createElement('div');
        c.style.background = '#fff'; c.style.padding = '15px'; c.style.borderRadius = '10px'; c.style.border = '1px solid #ddd';
        c.innerHTML = `<div style='display:flex; justify-content:space-between; font-weight:700;'><span>${m.teamA}</span><span>VS</span><span>${m.teamB}</span></div><div class='tree-footer'>${s ? s.date + ' P' + s.periodIndex : '待排定'}</div>`;
        grid.appendChild(c);
    });
    container.appendChild(grid);
}
function renderBracketTree(matches, container) {
    const rounds = { 'R1': [], 'R2': [], 'SF': [], 'Final': [] };
    matches.forEach(m => {
        let r = 'R1'; if (m.category.includes('第 2 輪')) r = 'R2'; if (m.category.includes('準決賽')) r = 'SF'; if (m.category.includes('決賽') && !m.category.includes('準')) r = 'Final';
        if (rounds[r]) rounds[r].push(m);
    });
    const tree = document.createElement('div'); tree.className = 'bracket-tree';
    ['R1', 'R2', 'SF', 'Final'].forEach(rk => {
        if (!rounds[rk] || !rounds[rk].length) return;
        const rd = document.createElement('div'); rd.className = 'bracket-round';
        rd.innerHTML = `<div class='round-header'>${rk}</div>`;
        rounds[rk].forEach(m => {
            const s = scheduledMatches.find(sm => sm.matchId === m.id);
            const me = document.createElement('div'); me.className = 'tree-match';
            me.innerHTML = `<div class='tree-team'>${m.teamA}</div><div class='tree-team'>${m.teamB}</div><div class='tree-footer'>${s ? s.date + ' P' + s.periodIndex : '待定'}</div>`;
            rd.appendChild(me);
        });
        tree.appendChild(rd);
    });
    container.appendChild(tree);
}
"""

    # --- 4. 組合最終 HTML (完全零 Regex) ---
    html_lines = []
    for line in html_raw.splitlines():
        if 'rel="stylesheet"' in line and 'app.css' in line:
            html_lines.append(f'<style>\\n{css_final}\\n</style>')
        elif 'app.js' in line or 'firebase' in line:
            continue
        else:
            html_lines.append(line)
    
    final_html = "\\n".join(html_lines)
    js_block = f'<script>\\n{js_header}\\n{js_final}\\n</script>'
    
    if '</body>' in final_html:
        final_html = final_html.replace('</body>', f'{js_block}\\n</body>')
    else:
        final_html += f"\\n{js_block}"

    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("DONE! index_local.html is generated safely.")

if __name__ == "__main__":
    final_manual_build()
