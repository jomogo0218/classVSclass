import json
import os

app_js_path = 'd:/classVSclass/app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the old tournament functions at the end
start_marker = "// NEW: Tournament Overview Rendering"
if start_marker in content:
    content = content[:content.find(start_marker)]

# 2. Add the new overhauled logic
new_logic = """
// NEW: Tournament Overview Overhaul (Sidebar + Tree)
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
        div.innerHTML = `<span style='font-size:16px;'>${getSportIcon(cat).split('</span>')[0]}</span></span> <span>${cat}</span>`;
        div.onclick = () => switchOverviewCategory(cat);
        sidebar.appendChild(div);
    });

    if (!currentOverviewCategory && categories.length > 0) {
        switchOverviewCategory(categories[0]);
    } else if (currentOverviewCategory) {
        renderSelectedCategory(grouped[currentOverviewCategory]);
    }
}

function switchOverviewCategory(cat) {
    currentOverviewCategory = cat;
    renderTournamentOverview();
}

function renderSelectedCategory(matches) {
    const container = document.getElementById('tournamentContainer');
    const title = document.getElementById('selectedCategoryTitle');
    const desc = document.getElementById('selectedCategoryDesc');
    if (!container) return;
    
    const cat = currentOverviewCategory;
    title.textContent = cat;
    const isElimination = cat.includes('羽球');
    desc.textContent = isElimination ? '單淘汰晉級圖' : '循環賽對戰名單';
    
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
                <span style='font-size:16px; font-weight:700;'>${m.teamA}</span>
                <span style='font-size:12px; color:var(--text-3); font-weight:700;'>VS</span>
                <span style='font-size:16px; font-weight:700;'>${m.teamB}</span>
            </div>
            <div style='font-size:13px; font-weight:500; color: ${scheduled ? 'var(--blue)' : 'var(--text-3)'};'>
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
    const order = ['R1', 'R2', 'SF', 'Final'];
    
    const tree = document.createElement('div');
    tree.className = 'bracket-tree';
    
    order.forEach(rKey => {
        if (!roundsMap[rKey]) return;
        
        const roundDiv = document.createElement('div');
        roundDiv.className = 'bracket-round';
        roundDiv.innerHTML = `<div class='round-header'>${roundLabels[rKey]}</div>`;
        
        roundsMap[rKey].forEach(m => {
            const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
            const matchEl = document.createElement('div');
            matchEl.className = `tree-match ${scheduled ? 'scheduled' : ''}`;
            if (scheduled) matchEl.style.borderLeft = '4px solid var(--orange)';
            
            matchEl.innerHTML = `
                <div class='tree-team top'>${m.teamA}</div>
                <div class='tree-team bottom'>${m.teamB}</div>
                ${scheduled ? `<div class='tree-info'>📅 ${scheduled.date} P${scheduled.periodIndex}</div>` : ''}
            `;
            roundDiv.appendChild(matchEl);
        });
        tree.appendChild(roundDiv);
    });
    
    container.appendChild(tree);
}
"""

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content + new_logic)
