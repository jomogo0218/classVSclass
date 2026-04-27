import os
import re

# paths
html_path = 'd:/classVSclass/index.html'
css_path  = 'd:/classVSclass/app.css'
js_path   = 'd:/classVSclass/app.js'

# 1. Update CSS - Force Orange Theme
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace variables in :root
css = re.sub(r'--blue:\s*#[a-zA-Z0-9]+;', '--blue: #f5750a;', css)
css = re.sub(r'--blue-light:\s*#[a-zA-Z0-9]+;', '--blue-light: #fff7ed;', css)
css = re.sub(r'--orange:\s*#[a-zA-Z0-9]+;', '--orange: #f5750a;', css)
css = re.sub(r'--orange-light:\s*#[a-zA-Z0-9]+;', '--orange-light: #fff7ed;', css)

# Add Bracket Tree styles if missing
if '.bracket-tree' not in css:
    css += """
/* ═══════════════ 對戰總覽分頁 (參考網站風格) ═══════════════ */
.overview-layout { display: flex; height: calc(100vh - var(--topbar-h)); width: 100%; background: var(--white); }
.category-sidebar { width: 240px; border-right: 1px solid var(--border); background: var(--white); overflow-y: auto; flex-shrink: 0; padding-top: 10px; }
.category-tab { padding: 16px 20px; cursor: pointer; border-bottom: 1px solid var(--border-light); display: flex; align-items: center; gap: 12px; font-weight: 600; transition: all 0.2s; color: var(--text-2); font-size: 14px; }
.category-tab:hover { background: var(--orange-light); color: var(--orange); }
.category-tab.active { background: var(--orange-light); color: var(--orange); border-right: 4px solid var(--orange); }
.overview-main { flex: 1; overflow: auto; padding: 30px; background: var(--bg); }
.overview-header-card { background: var(--white); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 6px solid var(--orange); }
.bracket-tree { display: flex; gap: 50px; padding: 20px 0; min-width: max-content; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; min-width: 220px; gap: 40px; }
.round-header { text-align: center; font-size: 12px; font-weight: 800; color: var(--text-3); text-transform: uppercase; margin-bottom: 20px; border-bottom: 3px solid var(--orange); padding-bottom: 8px; letter-spacing: 1px; width: 100%; }
.tree-match { position: relative; background: var(--white); border: 1px solid var(--border); border-radius: 10px; padding: 0; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06); width: 100%; z-index: 1; }
.tree-team { padding: 10px 14px; font-weight: 600; font-size: 14px; color: var(--text-1); display: flex; justify-content: space-between; align-items: center; }
.tree-team.top { background: #fafafa; border-bottom: 1px solid var(--border-light); }
.tree-footer { padding: 6px 14px; font-size: 11px; background: var(--orange-light); color: var(--orange); font-weight: 700; border-top: 1px solid #fee2e2; display: flex; align-items: center; gap: 4px; }
.tree-match::after { content: ''; position: absolute; right: -50px; top: 50%; width: 50px; height: 2px; background: var(--border); z-index: -1; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -50px; top: 50%; width: 2px; height: calc(100% + 40px); background: var(--border); z-index: -1; }
"""

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Update JS - Ensure Bracket connectors are drawn correctly
with open(js_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Fix the renderBracketTree logic to handle rounds better
bracket_fix = """
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
            
            matchEl.innerHTML = `
                <div class='tree-team top'>
                    <span>${m.teamA}</span>
                </div>
                <div class='tree-team bottom'>
                    <span>${m.teamB}</span>
                </div>
                <div class='tree-footer'>
                    ${scheduled ? '<i class=\\'fas fa-clock\\'></i> ' + scheduled.date + ' P' + scheduled.periodIndex : '<i class=\\'fas fa-hourglass-start\\'></i> 待定'}
                </div>
            `;
            roundDiv.appendChild(matchEl);
        });
        tree.appendChild(roundDiv);
    });
    container.appendChild(tree);
}
"""

if "function renderBracketTree" in js:
    # Replace the existing function
    js = re.sub(r'function renderBracketTree[\s\S]*?\}\s*\}', bracket_fix + '\n}', js)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js)
