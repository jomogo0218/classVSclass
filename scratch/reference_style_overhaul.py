import os
import re

# paths
html_path = 'd:/classVSclass/index.html'
css_path  = 'd:/classVSclass/app.css'
app_js_path = 'd:/classVSclass/app.js'

# 1. Update index.html for Sidebar Layout in Overview Tab
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add the Tab Button (if not already there)
if 'data-tab="overview"' not in html:
    html = html.replace(
        '<button class="tab-btn" data-tab="scheduling"><i class="fas fa-calendar-check"></i> 賽程規畫</button>',
        '<button class="tab-btn" data-tab="scheduling"><i class="fas fa-calendar-check"></i> 賽程規畫</button>\n    <button class="tab-btn" data-tab="overview"><i class="fas fa-sitemap"></i> 對戰表</button>'
    )

# Replace the tab-overview content with the sidebar structure
tab_overview_html = """
<!-- ===== 對戰總覽 Tab ===== -->
<div class="tab-content" id="tab-overview">
    <div class="app-layout overview-layout">
        <aside class="category-sidebar" id="categorySidebar">
            <!-- 由 JS 動態生成項目清單 -->
        </aside>
        
        <main class="overview-main">
            <div id="overviewHeader" class="overview-header-card">
                <h1 id="selectedCategoryTitle">🏆 請選擇賽事項目</h1>
                <p id="selectedCategoryDesc">點擊左側清單切換對戰表</p>
            </div>

            <div id="tournamentContainer" class="tournament-container">
                <div class="empty-state">
                    <div class="empty-icon">🏆</div>
                    <p>請從左側選擇賽事項目</p>
                </div>
            </div>
        </main>
    </div>
</div>
"""

if 'id="tab-overview"' in html:
    # Replace existing one
    html = re.sub(r'<!-- ===== 對戰總覽 Tab ===== -->[\s\S]*?<!-- 側欄遮罩', tab_overview_html + '\n\n<!-- 側欄遮罩', html)
else:
    # Insert new one
    html = html.replace('<div class="sidebar-overlay"', tab_overview_html + '\n<div class="sidebar-overlay"')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

# 2. Update app.js (Ensure tab switcher and logic are present)
with open(app_js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Add tab switcher logic
if "if (tabId === 'overview') renderTournamentOverview();" not in js:
    js = js.replace(
        "if (tabId === 'scheduling') renderSchedulingView();",
        "if (tabId === 'scheduling') renderSchedulingView();\n            if (tabId === 'overview') renderTournamentOverview();"
    )

# Cleanup old tournament logic and append new one
if "// NEW: Tournament Overview" in js:
    js = js[:js.find("// NEW: Tournament Overview")]

new_js_logic = """
// NEW: Tournament Overview (Reference Site Style)
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
        div.onclick = () => {
            currentOverviewCategory = cat;
            renderTournamentOverview();
        };
        sidebar.appendChild(div);
    });

    if (!currentOverviewCategory && categories.length > 0) {
        currentOverviewCategory = categories[0];
    }
    
    if (currentOverviewCategory) {
        renderSelectedCategory(grouped[currentOverviewCategory]);
    }
}

function renderSelectedCategory(matches) {
    const container = document.getElementById('tournamentContainer');
    const title = document.getElementById('selectedCategoryTitle');
    const desc = document.getElementById('selectedCategoryDesc');
    if (!container) return;
    
    const cat = currentOverviewCategory;
    title.innerHTML = `🏆 ${cat}`;
    const isElimination = cat.includes('羽球');
    desc.textContent = isElimination ? '單淘汰晉級圖 (Tree Bracket)' : '循環賽對戰表 (Round Robin)';
    
    container.innerHTML = '';
    if (isElimination) {
        renderBracketTree(matches, container);
    } else {
        renderRoundRobinGrid(matches, container);
    }
}

function renderRoundRobinGrid(matches, container) {
    const grid = document.createElement('div');
    grid.className = 'rr-grid';
    matches.forEach(m => {
        const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
        const card = document.createElement('div');
        card.className = `rr-card ${scheduled ? 'scheduled' : ''}`;
        card.innerHTML = `
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;'>
                <span style='font-size:20px; font-weight:800; color:var(--text-1);'>${m.teamA}</span>
                <span style='font-size:12px; color:var(--text-3); font-weight:900;'>VS</span>
                <span style='font-size:20px; font-weight:800; color:var(--text-1);'>${m.teamB}</span>
            </div>
            <div class='tree-footer'>
                <i class='far fa-calendar-check'></i> 
                ${scheduled ? scheduled.date + ' 第 ' + scheduled.periodIndex + ' 節' : '尚未排定時段'}
            </div>
        `;
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

    const roundLabels = { 'R1': '第一輪', 'R2': '第二輪', 'SF': '準決賽', 'Final': '決賽' };
    const order = ['R1', 'R2', 'SF', 'Final'].filter(r => roundsMap[r]);
    
    const tree = document.createElement('div');
    tree.className = 'bracket-tree';
    
    order.forEach(rKey => {
        const roundDiv = document.createElement('div');
        roundDiv.className = 'bracket-round';
        roundDiv.innerHTML = `<div class='round-header'>${roundLabels[rKey]}</div>`;
        
        roundsMap[rKey].forEach(m => {
            const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
            const matchEl = document.createElement('div');
            matchEl.className = 'tree-match';
            if (scheduled) matchEl.style.borderColor = 'var(--orange)';
            
            matchEl.innerHTML = `
                <div class='tree-team top'>
                    <span>${m.teamA}</span>
                </div>
                <div class='tree-team bottom'>
                    <span>${m.teamB}</span>
                </div>
                <div class='tree-footer'>
                    ${scheduled ? '<i class=\\'far fa-clock\\'></i> ' + scheduled.date + ' P' + scheduled.periodIndex : '<i class=\\'far fa-hourglass\\'></i> 待定'}
                </div>
            `;
            roundDiv.appendChild(matchEl);
        });
        tree.appendChild(roundDiv);
    });
    container.appendChild(tree);
}
"""
with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(js + new_js_logic)
