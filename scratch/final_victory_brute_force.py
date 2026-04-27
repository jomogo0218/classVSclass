
import os
import re

def final_victory_brute_force():
    print("Brute Force Victory Build Start...")
    
    # 1. 讀取組件
    def r(n): return open(n, 'r', encoding='utf-8').read()
    
    html_raw = r('index.html')
    css_raw  = r('app.css')
    js_raw   = r('app.js')
    matches_json = r('matches.json')
    schedules_json = r('schedules.json')

    # --- 2. 處理 CSS (橘色主題) ---
    css_final = css_raw.replace('#1a73e8', '#f5750a').replace('#2563eb', '#f5750a').replace('#e8f0fe', '#fff7ed')
    css_final += """
/* 強制樣式覆蓋 */
:root { --blue: #f5750a !important; --blue-light: #fff7ed !important; --orange: #f5750a !important; }
.main-tabs .tab-btn.active { color: #f5750a !important; border-bottom-color: #f5750a !important; }
.overview-layout { display: flex !important; height: calc(100vh - 48px) !important; background: #fff !important; width: 100%; }
.category-sidebar { width: 240px; border-right: 1px solid #ddd; background: #fff; overflow-y: auto; flex-shrink: 0; }
.category-tab { padding: 16px 20px; cursor: pointer; border-bottom: 1px solid #f0f0f0; display: flex; align-items: center; gap: 12px; font-weight: 600; color: #444; }
.category-tab.active { background: #fff7ed; color: #f5750a; border-right: 4px solid #f5750a; }
.overview-main { flex: 1; overflow: auto; padding: 30px; background: #f4f6f8; }
.bracket-tree { display: flex; gap: 40px; padding: 20px; min-width: max-content; }
.tree-match { position: relative; background: #fff; border: 1px solid #ddd; border-radius: 10px; padding: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.tree-team { font-weight: 600; padding: 4px 0; border-bottom: 1px solid #eee; font-size: 14px; }
.tree-footer { font-size: 11px; color: #f5750a; margin-top: 5px; font-weight: 700; background: #fff7ed; padding: 4px; border-radius: 4px; }
.tree-match::after { content: ''; position: absolute; right: -40px; top: 50%; width: 40px; height: 2px; background: #cbd5e1; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -40px; top: 50%; width: 2px; height: calc(100% + 42px); background: #cbd5e1; }
"""

    # --- 3. 處理 JS ---
    js_data = "const EMBEDDED_MATCHES = " + matches_json + ";\\n"
    js_data += "const EMBEDDED_SCHEDULES = " + schedules_json + ";\\n"
    
    # 使用強力 regex 攔截 fetch
    js_final = js_raw
    js_final = re.sub(r"await\s+fetch\s*\(\s*['\"].*?schedules\.json.*?['\"]\s*\+?\s*.*?\)", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})", js_final)
    js_final = re.sub(r"await\s+fetch\s*\(\s*['\"].*?matches\.json.*?['\"]\s*\+?\s*.*?\)", "({ok:true, json:async()=>EMBEDDED_MATCHES})", js_final)
    
    # 注入對戰表邏輯 (如果缺少)
    if "renderTournamentOverview" not in js_final:
        js_final += """
let currentOverviewCategory = null;
function renderTournamentOverview() {
    const s = document.getElementById('categorySidebar'); if(!s) return; s.innerHTML = '';
    const g = {}; matchesData.forEach(m => { if(!g[m.category]) g[m.category]=[]; g[m.category].push(m); });
    const cs = Object.keys(g).sort();
    cs.forEach(c => {
        const d = document.createElement('div'); d.className = `category-tab ${currentOverviewCategory===c?'active':''}`;
        d.innerHTML = `<span>🏆</span> <span>${c}</span>`;
        d.onclick = () => { currentOverviewCategory = c; renderTournamentOverview(); };
        s.appendChild(d);
    });
    if(!currentOverviewCategory && cs.length > 0) currentOverviewCategory = cs[0];
    if(currentOverviewCategory) {
        const t = document.getElementById('selectedCategoryTitle'); const ds = document.getElementById('selectedCategoryDesc');
        if(t) t.innerHTML = `🏆 ${currentOverviewCategory}`;
        const container = document.getElementById('tournamentContainer'); if(!container) return; container.innerHTML = '';
        if(currentOverviewCategory.includes('羽球')) renderBracketTree(g[currentOverviewCategory], container);
        else renderRoundRobinGrid(g[currentOverviewCategory], container);
    }
}
function renderRoundRobinGrid(ms, c) {
    const g = document.createElement('div'); g.style.display='grid'; g.style.gridTemplateColumns='repeat(auto-fill, minmax(280px, 1fr))'; g.style.gap='15px';
    ms.forEach(m => {
        const s = scheduledMatches.find(sm => sm.matchId === m.id);
        const cd = document.createElement('div'); cd.style.background='#fff'; cd.style.padding='15px'; cd.style.borderRadius='10px'; cd.style.border='1px solid #ddd';
        cd.innerHTML = `<div style='display:flex; justify-content:space-between; font-weight:700;'><span>${m.teamA}</span><span>VS</span><span>${m.teamB}</span></div><div class='tree-footer'>${s ? s.date + ' P' + s.periodIndex : '待排定'}</div>`;
        g.appendChild(cd);
    });
    c.appendChild(g);
}
function renderBracketTree(ms, c) {
    const rs = { 'R1':[], 'R2':[], 'SF':[], 'Final':[] };
    ms.forEach(m => { let r='R1'; if(m.category.includes('2')) r='R2'; if(m.category.includes('準')) r='SF'; if(m.category.includes('決賽') && !m.category.includes('準')) r='Final'; if(rs[r]) rs[r].push(m); });
    const t = document.createElement('div'); t.className = 'bracket-tree';
    ['R1', 'R2', 'SF', 'Final'].forEach(rk => {
        if(!rs[rk].length) return;
        const rd = document.createElement('div'); rd.className = 'bracket-round'; rd.innerHTML = `<div class='round-header'>${rk}</div>`;
        rs[rk].forEach(m => {
            const s = scheduledMatches.find(sm => sm.matchId === m.id);
            const me = document.createElement('div'); me.className = 'tree-match';
            me.innerHTML = `<div class='tree-team'>${m.teamA}</div><div class='tree-team'>${m.teamB}</div><div class='tree-footer'>${s ? s.date + ' P' + s.periodIndex : '待定'}</div>`;
            rd.appendChild(me);
        });
        t.appendChild(rd);
    });
    c.appendChild(t);
}
"""

    # 補強啟動指令
    js_final += "\\ndocument.addEventListener('DOMContentLoaded', () => { try { if (typeof initApp === 'function') initApp(); } catch(e) { console.error('Init Error:', e); } });\\n"
    # 安全轉義
    js_final = js_final.replace('</script>', '<\\\\/script>')

    # --- 4. 組合 HTML ---
    # 移除 CSS 與 JS 標籤
    html_lines = []
    for line in html_raw.splitlines():
        if any(x in line for x in ['rel="stylesheet"', 'app.js', 'firebase', 'firebase-config.js']):
            continue
        html_lines.append(line)
    
    final_content = "\\n".join(html_lines)
    # 注入 Style 與 Script
    final_content = final_content.replace('</head>', '<style>\\n' + css_final + '\\n</style>\\n</head>')
    
    script_block = '<script>\\n' + js_data + js_final + '\\n</script>'
    final_content = final_content.replace('</body>', script_block + '\\n</body>')

    # 5. 輸出
    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print("DONE! index_local.html is robust and ready.")

if __name__ == "__main__":
    final_victory_brute_force()
