import os
import re

# 1. Update index.html
html_path = 'd:/classVSclass/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Tab Button
if 'data-tab="overview"' not in content:
    content = content.replace(
        '<button class="tab-btn" data-tab="scheduling"><i class="fas fa-calendar-check"></i> 賽程規畫</button>',
        '<button class="tab-btn" data-tab="scheduling"><i class="fas fa-calendar-check"></i> 賽程規畫</button>\n    <button class="tab-btn" data-tab="overview"><i class="fas fa-sitemap"></i> 對戰總覽</button>'
    )

# Add Tab Content
new_tab_overview = """
<!-- ===== 對戰總覽 Tab ===== -->
<div class="tab-content" id="tab-overview">
    <div class="app-layout overview-layout">
        <aside class="category-sidebar" id="categorySidebar">
            <!-- 項目清單會由 JS 動態生成 -->
        </aside>
        
        <main class="overview-main">
            <div id="overviewHeader" style="margin-bottom: 24px;">
                <h1 id="selectedCategoryTitle" style="font-size: 24px; font-weight: 700; color: var(--text-1); margin-bottom: 4px;">請選擇賽事項目</h1>
                <p id="selectedCategoryDesc" style="color: var(--text-3); font-size: 14px;">點擊左側清單切換項目</p>
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
if 'id="tab-overview"' not in content:
    content = content.replace('<div class="sidebar-overlay"', new_tab_overview + '\n<div class="sidebar-overlay"')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Update app.css
css_path = 'd:/classVSclass/app.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

new_css = """
/* ═══════════════ 對戰總覽分頁 (高級樹狀圖 + 側邊欄) ═══════════════ */
.overview-layout { display: flex; height: 100%; gap: 0; background: var(--white); }
.category-sidebar { 
    width: 220px; border-right: 1px solid var(--border); 
    background: #fdfdfd; overflow-y: auto; flex-shrink: 0;
}
.category-tab { 
    padding: 14px 18px; cursor: pointer; border-bottom: 1px solid var(--border-light);
    display: flex; align-items: center; gap: 10px; font-weight: 500; transition: all 0.2s;
    color: var(--text-2);
}
.category-tab:hover { background: var(--bg); color: var(--blue); }
.category-tab.active { 
    background: var(--blue-light); color: var(--blue); font-weight: 700; 
    border-right: 4px solid var(--blue); 
}

.overview-main { flex: 1; overflow: auto; padding: 32px; background: var(--bg); position: relative; }

.rr-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
.rr-card {
    background: var(--white); border-radius: 12px; border: 1px solid var(--border);
    padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); transition: all 0.2s;
}
.rr-card:hover { transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,0.08); }
.rr-card.scheduled { border-top: 5px solid var(--blue); }

/* 樹狀圖 Bracket Tree */
.bracket-tree { display: flex; gap: 60px; padding: 20px 0; min-width: max-content; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; min-width: 200px; gap: 30px; }
.round-header {
    text-align: center; font-size: 11px; font-weight: 800; color: var(--text-3);
    text-transform: uppercase; margin-bottom: 15px; border-bottom: 2px solid var(--border); 
    padding-bottom: 6px; letter-spacing: 1px;
}

.tree-match {
    position: relative; background: var(--white); border: 1px solid var(--border);
    border-radius: 8px; padding: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    width: 100%; z-index: 1;
}
.tree-team { 
    padding: 6px 8px; font-weight: 600; font-size: 14px; border-radius: 4px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; 
}
.tree-team.top { border-bottom: 1px solid var(--border-light); }
.tree-info { font-size: 11px; color: var(--orange); margin-top: 6px; font-weight: 600; display: flex; align-items: center; gap: 4px; }

/* 樹狀連接線系統 */
.tree-match::after {
    content: ''; position: absolute; right: -60px; top: 50%;
    width: 60px; height: 2px; background: var(--border); z-index: -1;
}
.bracket-round:last-child .tree-match::after { display: none; }

/* 垂直連線 */
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before {
    content: ''; position: absolute; right: -60px; top: 50%;
    width: 2px; height: calc(100% + 30px); background: var(--border); z-index: -1;
}
"""
if '對戰總覽分頁' not in css:
    with open(css_path, 'a', encoding='utf-8') as f:
        f.write(new_css)

# 3. Update app.js
app_js_path = 'd:/classVSclass/app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Update tab switcher
js = js.replace(
    "if (tabId === 'scheduling') renderSchedulingView();",
    "if (tabId === 'scheduling') renderSchedulingView();\n            if (tabId === 'overview') renderTournamentOverview();"
)

# Append logic
new_js_logic = """
// NEW: Tournament Overview (Sidebar + Tree)
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
    title.textContent = cat;
    const isElimination = cat.includes('羽球');
    desc.textContent = isElimination ? '🏆 單淘汰晉級圖 (樹狀結構)' : '📊 循環賽對戰組合 (網格結構)';
    
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
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                <span style='font-size:18px; font-weight:700;'>${m.teamA}</span>
                <span style='font-size:12px; color:var(--text-3); font-weight:900;'>VS</span>
                <span style='font-size:18px; font-weight:700;'>${m.teamB}</span>
            </div>
            <div style='font-size:14px; font-weight:500; color: ${scheduled ? 'var(--blue)' : 'var(--text-3)'};'>
                ${scheduled ? '<i class=\\'far fa-calendar-alt\\'></i> ' + scheduled.date + ' 第 ' + scheduled.periodIndex + ' 節' : '⌛ 尚未排定時段'}
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
            matchEl.className = `tree-match ${scheduled ? 'scheduled' : ''}`;
            if (scheduled) matchEl.style.borderLeft = '5px solid var(--orange)';
            
            matchEl.innerHTML = `
                <div class='tree-team top'>${m.teamA}</div>
                <div class='tree-team bottom'>${m.teamB}</div>
                ${scheduled ? `<div class='tree-info'><i class='far fa-clock'></i> ${scheduled.date} P${scheduled.periodIndex}</div>` : ''}
            `;
            roundDiv.appendChild(matchEl);
        });
        tree.appendChild(roundDiv);
    });
    container.appendChild(tree);
}
"""
if 'renderTournamentOverview' not in js:
    with open(app_js_path, 'a', encoding='utf-8') as f:
        f.write(new_js_logic)
