
import os

def final_stitch():
    print("Final Stitching Process Start...")
    
    # 1. 讀取所有組件
    def read_file(name):
        with open(name, 'r', encoding='utf-8') as f:
            return f.read()

    try:
        html = read_file('index.html')
        css = read_file('app.css')
        js = read_file('app.js')
        matches = read_file('matches.json')
        schedules = read_file('schedules.json')
    except Exception as e:
        print("Read Error:", e)
        return

    # --- 2. 準備 CSS (橘色主題強制覆蓋) ---
    css_orange = css.replace('#1a73e8', '#f5750a').replace('#2563eb', '#f5750a').replace('#e8f0fe', '#fff7ed')
    # 補強對戰表樣式
    css_orange += """
:root { --blue: #f5750a !important; --orange: #f5750a !important; --blue-light: #fff7ed !important; }
.overview-layout { display: flex !important; height: calc(100vh - 48px); background: #fff; width: 100%; }
.category-sidebar { width: 240px; border-right: 1px solid #ddd; background: #fff; overflow-y: auto; flex-shrink: 0; }
.category-tab { padding: 16px; cursor: pointer; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 10px; font-weight: 600; color: #444; }
.category-tab.active { background: #fff7ed; color: #f5750a; border-right: 4px solid #f5750a; }
.overview-main { flex: 1; overflow: auto; padding: 30px; background: #f4f6f8; }
.bracket-tree { display: flex; gap: 40px; padding: 20px; min-width: max-content; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; gap: 30px; min-width: 200px; }
.round-header { text-align: center; font-weight: 800; border-bottom: 2px solid #f5750a; padding-bottom: 5px; margin-bottom: 15px; color: #777; }
.tree-match { position: relative; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.tree-team { font-weight: 600; padding: 4px 0; border-bottom: 1px solid #eee; font-size: 14px; }
.tree-footer { font-size: 11px; color: #f5750a; margin-top: 5px; font-weight: 700; }
.tree-match::after { content: ''; position: absolute; right: -40px; top: 50%; width: 40px; height: 2px; background: #ccc; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -40px; top: 50%; width: 2px; height: calc(100% + 42px); background: #ccc; }
"""

    # --- 3. 準備 JS (數據嵌入 + 核心邏輯補完) ---
    js_final = "const EMBEDDED_MATCHES = " + matches + ";\\n"
    js_final += "const EMBEDDED_SCHEDULES = " + schedules + ";\\n"
    
    # 補回遺失的 localStorage 讀取函數
    core_logic = """
function loadScheduledMatches() {
    const saved = localStorage.getItem('scheduledMatches');
    if (saved) { scheduledMatches = JSON.parse(saved); }
    else { scheduledMatches = []; }
}
function saveScheduledMatches() { localStorage.setItem('scheduledMatches', JSON.stringify(scheduledMatches)); }
function loadSubjectSettings() {
    const saved = localStorage.getItem('subjectSettings');
    if (saved) {
        const s = JSON.parse(saved);
        document.querySelectorAll('.subject-checkbox').forEach(cb => { if(s[cb.dataset.id] !== undefined) cb.checked = s[cb.dataset.id]; });
    }
}
function saveSubjectSettings() {
    const s = {}; document.querySelectorAll('.subject-checkbox').forEach(cb => { s[cb.dataset.id] = cb.checked; });
    localStorage.setItem('subjectSettings', JSON.stringify(s));
}
"""
    js_final += core_logic + "\\n" + js
    
    # 攔截 Fetch (強力替換)
    import re
    js_final = re.sub(r"await\s+fetch\s*\(.*?schedules\.json.*?\)", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})", js_final)
    js_final = re.sub(r"await\s+fetch\s*\(.*?matches\.json.*?\)", "({ok:true, json:async()=>EMBEDDED_MATCHES})", js_final)
    
    # 注入對戰表渲染 (如果缺少)
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
        const t = document.getElementById('selectedCategoryTitle'); const container = document.getElementById('tournamentContainer');
        if(t) t.innerHTML = `🏆 ${currentOverviewCategory}`;
        if(container) {
            container.innerHTML = '';
            if(currentOverviewCategory.includes('羽球')) renderBracketTree(g[currentOverviewCategory], container);
            else renderRoundRobinGrid(g[currentOverviewCategory], container);
        }
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

    # 確保啟動指令
    js_final += "\\ndocument.addEventListener('DOMContentLoaded', () => { initApp(); });\\n"
    # 安全轉義
    js_final = js_final.replace('</script>', '<\\\\/script>')

    # --- 4. 組合 HTML ---
    # 分離原始 HTML 行，過濾掉舊標籤
    clean_html_lines = []
    for line in html.splitlines():
        if any(x in line for x in ['rel="stylesheet"', 'app.js', 'firebase', 'firebase-config.js']):
            continue
        clean_html_lines.append(line)
    
    # 縫合
    final_html = "\\n".join(clean_html_lines)
    # 注入樣式在 </head> 前
    final_html = final_html.replace('</head>', '<style>\\n' + css_orange + '\\n</style>\\n</head>')
    # 注入腳本在 </body> 前
    final_html = final_html.replace('</body>', '<script>\\n' + js_final + '\\n</script>\\n</body>')

    # 5. 輸出
    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("DONE! Absolute Final index_local.html generated.")

if __name__ == "__main__":
    final_stitch()
