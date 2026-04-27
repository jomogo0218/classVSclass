import os
import re

# paths
html_path = 'd:/classVSclass/index.html'
css_path  = 'd:/classVSclass/app.css'
js_path   = 'd:/classVSclass/app.js'

# --- 1. Update CSS ---
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Orange Theme Override
css = re.sub(r'--blue:\s*#[a-zA-Z0-9]+;', '--blue: #f5750a;', css)
css = re.sub(r'--blue-light:\s*#[a-zA-Z0-9]+;', '--blue-light: #fff7ed;', css)
css = re.sub(r'--orange:\s*#[a-zA-Z0-9]+;', '--orange: #f5750a;', css)
css = re.sub(r'--orange-light:\s*#[a-zA-Z0-9]+;', '--orange-light: #fff7ed;', css)

# New Layout Styles
css += """
/* ═══════════════ 對戰表 (參考網站風格) ═══════════════ */
.overview-layout { display: flex; height: calc(100vh - var(--topbar-h)); width: 100%; background: var(--white); }
.category-sidebar { width: 240px; border-right: 1px solid var(--border); background: var(--white); overflow-y: auto; flex-shrink: 0; }
.category-tab { padding: 16px 20px; cursor: pointer; border-bottom: 1px solid var(--border-light); display: flex; align-items: center; gap: 12px; font-weight: 600; color: var(--text-2); transition: 0.2s; }
.category-tab:hover { background: var(--orange-light); color: var(--orange); }
.category-tab.active { background: var(--orange-light); color: var(--orange); border-right: 4px solid var(--orange); }
.overview-main { flex: 1; overflow: auto; padding: 30px; background: var(--bg); }
.overview-header-card { background: var(--white); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 6px solid var(--orange); }
.bracket-tree { display: flex; gap: 60px; padding: 20px 0; min-width: max-content; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; min-width: 220px; gap: 40px; }
.round-header { text-align: center; font-size: 12px; font-weight: 800; color: var(--text-3); text-transform: uppercase; margin-bottom: 20px; border-bottom: 3px solid var(--orange); padding-bottom: 8px; width: 100%; }
.tree-match { position: relative; background: var(--white); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06); width: 100%; z-index: 1; }
.tree-team { padding: 10px 14px; font-weight: 600; font-size: 14px; color: var(--text-1); border-bottom: 1px solid var(--border-light); }
.tree-team.bottom { border-bottom: none; }
.tree-footer { padding: 6px 14px; font-size: 11px; background: var(--orange-light); color: var(--orange); font-weight: 700; border-top: 1px solid #fee2e2; }
.tree-match::after { content: ''; position: absolute; right: -60px; top: 50%; width: 60px; height: 2px; background: #cbd5e1; z-index: -1; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -60px; top: 50%; width: 2px; height: calc(100% + 42px); background: #cbd5e1; z-index: -1; }
"""

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# --- 2. Update HTML ---
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add Tab Button
html = html.replace(
    '<button class="tab-btn" data-tab="scheduling"><i class="fas fa-calendar-check"></i> 賽程規畫</button>',
    '<button class="tab-btn" data-tab="scheduling"><i class="fas fa-calendar-check"></i> 賽程規畫</button>\n    <button class="tab-btn" data-tab="overview"><i class="fas fa-sitemap"></i> 對戰表</button>'
)

# Add Tab Content
tab_overview_html = """
<!-- ===== 對戰總覽 Tab ===== -->
<div class="tab-content" id="tab-overview">
    <div class="app-layout overview-layout">
        <aside class="category-sidebar" id="categorySidebar"></aside>
        <main class="overview-main">
            <div id="overviewHeader" class="overview-header-card">
                <h1 id="selectedCategoryTitle">🏆 請選擇項目</h1>
                <p id="selectedCategoryDesc">點擊左側項目查看對戰表</p>
            </div>
            <div id="tournamentContainer"></div>
        </main>
    </div>
</div>
"""
html = html.replace('<div class="sidebar-overlay"', tab_overview_html + '\n<div class="sidebar-overlay"')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# --- 3. Update JS ---
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Update tab switcher
js = js.replace(
    "if (tabId === 'scheduling') renderSchedulingView();",
    "if (tabId === 'scheduling') renderSchedulingView();\n            if (tabId === 'overview') renderTournamentOverview();"
)

# Append new logic
new_js_logic = """
// NEW: Tournament Overview
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
        div.innerHTML = `<span>${getSportIcon(cat)}</span> <span>${cat}</span>`;
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
    grid.className = 'rr-grid';
    grid.style.display = 'grid';
    grid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))';
    grid.style.gap = '15px';
    matches.forEach(m => {
        const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
        const card = document.createElement('div');
        card.className = `rr-card ${scheduled ? 'scheduled' : ''}`;
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
            matchEl.innerHTML = `<div class='tree-team top'>${m.teamA}</div><div class='tree-team bottom'>${m.teamB}</div><div class='tree-footer'>${scheduled ? scheduled.date + ' P' + scheduled.periodIndex : '待定'}</div>`;
            roundDiv.appendChild(matchEl);
        });
        tree.appendChild(roundDiv);
    });
    container.appendChild(tree);
}
"""
with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js + new_js_logic)

# --- 4. Robust Builder ---
with open('mega_build.py', 'w', encoding='utf-8') as f:
    f.write("""
import os
import re

def build():
    print("Building...")
    read = lambda n: open(n, 'r', encoding='utf-8').read()
    html, css, js = read('index.html'), read('app.css'), read('app.js')
    matches, schedules = read('matches.json'), read('schedules.json')
    
    html = html.replace('<link rel="stylesheet" href="app.css">', f"<style>\\n{css}\\n</style>")
    
    js_data = f"const EMBEDDED_MATCHES = {matches};\\nconst EMBEDDED_SCHEDULES = {schedules};\\n"
    js = js.replace("await fetch('schedules.json')", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})")
    js = js.replace("await fetch('matches.json?v=' + Date.now())", "({ok:true, json:async()=>EMBEDDED_MATCHES})")
    
    script_block = f"<script>\\n{js_data}\\n{js}\\n</script>"
    
    # Clean old scripts and inject new
    html_lines = []
    for line in html.splitlines():
        if any(x in line for x in ['app.js', 'firebase', 'firebase-config']): continue
        html_lines.append(line)
    
    final = "\\n".join(html_lines).replace('</body>', f"{script_block}\\n</body>")
    
    with open('index_local.html', 'w', encoding='utf-8') as f: f.write(final)
    print("Done!")

if __name__ == "__main__": build()
""")
