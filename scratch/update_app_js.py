import json
import os

app_js_path = 'd:/classVSclass/app.js'
with open(app_js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update setupTabSwitcher
content = content.replace(
    "if (tabId === 'scheduling') renderSchedulingView();",
    "if (tabId === 'scheduling') renderSchedulingView();\n            if (tabId === 'overview') renderTournamentOverview();"
)

new_code = """
// NEW: Tournament Overview Rendering
function renderTournamentOverview() {
    const container = document.getElementById('tournamentContainer');
    const categoryFilterSelect = document.getElementById('overviewCategoryFilter');
    const categoryFilter = categoryFilterSelect ? categoryFilterSelect.value : 'all';
    if (!container) return;
    container.innerHTML = '';

    const grouped = {};
    matchesData.forEach(m => {
        if (!grouped[m.category]) grouped[m.category] = [];
        grouped[m.category].push(m);
    });

    if (categoryFilterSelect && categoryFilterSelect.options.length <= 1) {
        Object.keys(grouped).sort().forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat;
            opt.textContent = cat;
            categoryFilterSelect.appendChild(opt);
        });
    }

    const categories = categoryFilter === 'all' ? Object.keys(grouped).sort() : [categoryFilter];

    categories.forEach(cat => {
        const section = document.createElement('section');
        section.className = 'tournament-section panel';
        section.style.marginBottom = '24px';
        
        const isElimination = cat.includes('羽球');
        const typeLabel = isElimination ? '單淘汰賽' : '循環賽';
        const typeClass = isElimination ? 'type-elimination' : 'type-roundrobin';

        section.innerHTML = `
            <div class='panel-header' style='justify-content: flex-start; gap: 12px; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 16px;'>
                <span class='panel-icon'>${getSportIcon(cat)}</span>
                <h2 class='panel-title'>${cat}</h2>
                <span class='tournament-type-badge ${typeClass}' style='margin-left: auto; background: ${isElimination ? '#fef3c7' : '#dcfce7'}; color: ${isElimination ? '#92400e' : '#166534'}; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;'>${typeLabel}</span>
            </div>
            <div class='tournament-content' id='tournament-content-${cat.replace(/\\s+/g, '-')}'></div>
        `;
        container.appendChild(section);

        const content = section.querySelector('.tournament-content');
        if (isElimination) {
            renderEliminationBracket(grouped[cat], content);
        } else {
            renderRoundRobinTable(grouped[cat], content);
        }
    });
}

function renderRoundRobinTable(matches, container) {
    const table = document.createElement('div');
    table.style.display = 'grid';
    table.style.gridTemplateColumns = 'repeat(auto-fill, minmax(250px, 1fr))';
    table.style.gap = '12px';
    
    matches.forEach(m => {
        const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
        const card = document.createElement('div');
        card.style.padding = '12px';
        card.style.borderRadius = '8px';
        card.style.border = '1px solid var(--border)';
        card.style.background = scheduled ? 'var(--blue-light)' : 'var(--bg-2)';
        
        card.innerHTML = `
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
                <span style='font-weight:700;'>${m.teamA}</span>
                <span style='font-size:12px; color:var(--text-3);'>VS</span>
                <span style='font-weight:700;'>${m.teamB}</span>
            </div>
            <div style='font-size:12px; color: ${scheduled ? 'var(--blue)' : 'var(--text-3)'};'>
                ${scheduled ? '📅 ' + scheduled.date + ' 第 ' + scheduled.periodIndex + ' 節' : '⌛ 待排定'}
            </div>
        `;
        table.appendChild(card);
    });
    container.appendChild(table);
}

function renderEliminationBracket(matches, container) {
    const rounds = {};
    matches.forEach(m => {
        let round = '第一輪';
        if (m.category.includes('第 2 輪')) round = '第二輪';
        if (m.category.includes('準決賽')) round = '準決賽';
        if (m.category.includes('決賽') && !m.category.includes('準')) round = '決賽';
        if (!rounds[round]) rounds[round] = [];
        rounds[round].push(m);
    });

    const roundOrder = ['第一輪', '第二輪', '準決賽', '決賽'];
    const sortedRounds = Object.keys(rounds).sort((a, b) => roundOrder.indexOf(a) - roundOrder.indexOf(b));

    const bracketWrapper = document.createElement('div');
    bracketWrapper.style.display = 'flex';
    bracketWrapper.style.gap = '20px';
    bracketWrapper.style.overflowX = 'auto';
    
    sortedRounds.forEach(r => {
        const roundCol = document.createElement('div');
        roundCol.style.minWidth = '200px';
        roundCol.style.flex = '1';
        roundCol.innerHTML = "<h4 style='font-size:13px; color:var(--text-3); margin-bottom:12px; text-align:center; border-bottom:2px solid var(--border); padding-bottom:4px;'>" + r + "</h4>";
        
        rounds[r].forEach(m => {
            const scheduled = scheduledMatches.find(sm => sm.matchId === m.id);
            const matchBox = document.createElement('div');
            matchBox.style.marginBottom = '12px';
            matchBox.style.padding = '8px';
            matchBox.style.borderRadius = '6px';
            matchBox.style.border = '1px solid var(--border)';
            matchBox.style.background = scheduled ? 'var(--orange-light)' : 'var(--bg-1)';
            
            matchBox.innerHTML = "<div style='font-size:13px; font-weight:500; border-bottom:1px solid var(--border); padding-bottom:2px; margin-bottom:2px;'>" + m.teamA + "</div>" +
                                "<div style='font-size:13px; font-weight:500;'>" + m.teamB + "</div>" +
                                (scheduled ? "<div style='font-size:10px; color:var(--orange); margin-top:4px;'>📅 " + scheduled.date + " P" + scheduled.periodIndex + "</div>" : "");
            roundCol.appendChild(matchBox);
        });
        bracketWrapper.appendChild(roundCol);
    });
    container.appendChild(bracketWrapper);
}
"""
with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(content + new_code)
