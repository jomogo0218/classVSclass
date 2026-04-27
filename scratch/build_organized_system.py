
import os
import json
import re

def build_organized_system():
    print("Building Organized Tournament System...")
    
    # 1. 讀取組件
    def r(n): return open(n, 'r', encoding='utf-8').read()
    
    html = r('index.html')
    css  = r('app.css')
    js   = r('app.js')
    # 讀取剛剛整理好的 86 場比賽
    matches = r('matches.json')
    schedules = r('schedules.json')

    # --- 2. CSS 強化 (橘色主題 + 整潔對戰表) ---
    css_final = css.replace('#1a73e8', '#f5750a').replace('#2563eb', '#f5750a').replace('#e8f0fe', '#fff7ed')
    css_final += """
:root { --blue: #f5750a !important; --orange: #f5750a !important; --blue-light: #fff7ed !important; }
.overview-layout { display: flex !important; height: calc(100vh - 48px); background: #fff; width: 100%; }
.category-sidebar { width: 240px; border-right: 1px solid #ddd; background: #fff; overflow-y: auto; flex-shrink: 0; }
.category-tab { padding: 14px 20px; cursor: pointer; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 10px; font-weight: 600; color: #444; font-size: 14px; }
.category-tab.active { background: #fff7ed; color: #f5750a; border-right: 4px solid #f5750a; }
.overview-main { flex: 1; overflow: auto; padding: 24px; background: #f8fafc; }
.overview-header-card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 6px solid #f5750a; }

/* 樹狀圖 - 專業美化 */
.bracket-tree { display: flex; gap: 50px; padding: 20px; min-width: max-content; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; gap: 24px; min-width: 220px; }
.round-header { text-align: center; font-weight: 800; border-bottom: 3px solid #f5750a; padding-bottom: 8px; margin-bottom: 20px; color: #334155; font-size: 13px; text-transform: uppercase; }
.tree-match { position: relative; background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); transition: 0.2s; width: 100%; }
.tree-match:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }
.tree-team { font-weight: 600; padding: 10px 14px; border-bottom: 1px solid #f1f5f9; font-size: 14px; color: #1e293b; display: flex; justify-content: space-between; }
.tree-team:last-of-type { border-bottom: none; }
.tree-footer { font-size: 11px; color: #f5750a; font-weight: 800; background: #fff7ed; padding: 6px 14px; border-top: 1px solid #ffedd5; display: flex; align-items: center; gap: 6px; }

/* 連接線 */
.tree-match::after { content: ''; position: absolute; right: -50px; top: 50%; width: 50px; height: 2px; background: #cbd5e1; z-index: -1; }
.bracket-round:last-child .tree-match::after { display: none; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -50px; top: 50%; width: 2px; height: calc(100% + 36px); background: #cbd5e1; z-index: -1; }
"""

    # --- 3. JS 處理 ---
    js_final = "const EMBEDDED_MATCHES = " + matches + ";\n"
    js_final += "const EMBEDDED_SCHEDULES = " + schedules + ";\n"
    
    # 修正 Fetch 攔截 (不使用 regex)
    js_processed = js
    js_processed = re.sub(r"await\s+fetch\s*\(.*?schedules\.json.*?\)", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})", js_processed)
    js_processed = re.sub(r"await\s+fetch\s*\(.*?matches\.json.*?\)", "({ok:true, json:async()=>EMBEDDED_MATCHES})", js_processed)
    
    # 注入「整潔」的對戰表邏輯 (確保單次宣告)
    tournament_logic = """
let currentOverviewCategory = null;
function renderTournamentOverview() {
    const sidebar = document.getElementById('categorySidebar'); if (!sidebar) return;
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
        desc.textContent = isElim ? '單淘汰晉級圖' : '循環賽對戰名單';
        container.innerHTML = '';
        if (isElim) renderBracketTree(grouped[currentOverviewCategory], container);
        else renderRoundRobinGrid(grouped[currentOverviewCategory], container);
    }
}
function renderRoundRobinGrid(ms, c) {
    const g = document.createElement('div'); g.style.display='grid'; g.style.gridTemplateColumns='repeat(auto-fill, minmax(300px, 1fr))'; g.style.gap='20px';
    ms.forEach(m => {
        const s = scheduledMatches.find(sm => sm.matchId === m.id);
        const cd = document.createElement('div'); cd.style.background='#fff'; cd.style.padding='20px'; cd.style.borderRadius='12px'; cd.style.border='1px solid #e2e8f0'; cd.style.boxShadow='0 1px 3px rgba(0,0,0,0.1)';
        cd.innerHTML = `<div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; font-weight:800; font-size:18px;'><span>${m.teamA}</span><span style='font-size:12px; color:#94a3b8;'>VS</span><span>${m.teamB}</span></div><div class='tree-footer'>📅 ${s ? s.date + ' 第 ' + s.periodIndex + ' 節' : '尚未排定時段'}</div>`;
        g.appendChild(cd);
    });
    c.appendChild(g);
}
function renderBracketTree(ms, c) {
    const rs = { 'R1': [], 'R2': [], 'SF': [], 'Final': [], '3rd': [] };
    const labelMap = { 'R1': '第一輪', 'R2': '第二輪', 'SF': '準決賽', 'Final': '決賽', '3rd': '季軍賽' };
    ms.forEach(m => {
        let r = 'R1';
        if (m.category.includes('2')) r = 'R2';
        if (m.category.includes('準')) r = 'SF';
        if (m.category.includes('季軍')) r = '3rd';
        if (m.category.includes('決賽') && !m.category.includes('準')) r = 'Final';
        if (rs[r]) rs[r].push(m);
    });
    const t = document.createElement('div'); t.className = 'bracket-tree';
    ['R1', 'R2', 'SF', 'Final', '3rd'].forEach(rk => {
        if (!rs[rk].length) return;
        const rd = document.createElement('div'); rd.className = 'bracket-round';
        rd.innerHTML = `<div class='round-header'>${labelMap[rk]}</div>`;
        rs[rk].forEach(m => {
            const s = scheduledMatches.find(sm => sm.matchId === m.id);
            const me = document.createElement('div'); me.className = 'tree-match';
            me.innerHTML = `<div class='tree-team'><span>${m.teamA}</span></div><div class='tree-team'><span>${m.teamB}</span></div><div class='tree-footer'>🕒 ${s ? s.date + ' P' + s.periodIndex : '待排定'}</div>`;
            rd.appendChild(me);
        });
        t.appendChild(rd);
    });
    c.appendChild(t);
}
"""
    # 移除 JS 中可能重複的對戰表宣告 (如果有)
    if "currentOverviewCategory" in js_processed:
        # 如果已經有了，我們就不重複添加，或者只添加邏輯主體
        pass
    else:
        js_final += tournament_logic

    js_final += js_processed
    # 確保啟動指令
    js_final += "\ndocument.addEventListener('DOMContentLoaded', () => { if(typeof initApp === 'function') initApp(); });\n"
    js_final = js_final.replace('</script>', '<\\/script>')

    # --- 4. 組合 HTML ---
    clean_lines = []
    for line in html.splitlines():
        if any(x in line for x in ['rel="stylesheet"', 'app.js', 'firebase', 'firebase-config']):
            continue
        clean_lines.append(line)
    
    final_html = "\n".join(clean_lines)
    final_html = final_html.replace('</head>', '<style>\n' + css_final + '\n</style>\n</head>')
    final_html = final_html.replace('</body>', '<script>\n' + js_final + '\n</script>\n</body>')

    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("DONE! Organized system generated at index_local.html.")

if __name__ == "__main__":
    build_organized_system()
