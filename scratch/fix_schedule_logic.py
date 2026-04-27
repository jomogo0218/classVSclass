"""
fix_schedule_logic.py  (v2 - all strings as raw or ascii-safe)
"""

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

print('Original length:', len(content))
fixes = 0

# ---- Fix 1: STORAGE_KEY_CLASSES constant ----
if 'STORAGE_KEY_CLASSES' not in content:
    old = "const STORAGE_KEY_SUBJECTS = 'classVSclass_allowed_subjects_v3';"
    new = old + "\nconst STORAGE_KEY_CLASSES = 'classVSclass_selected_classes_v2';"
    content = content.replace(old, new)
    fixes += 1
    print('Fix 1: Added STORAGE_KEY_CLASSES')
else:
    print('Fix 1: STORAGE_KEY_CLASSES already exists')

# ---- Fix 2: currentOverviewCategory state ----
if 'currentOverviewCategory' not in content:
    old = "let showOnlyDupes     = false; // "
    # find it
    idx = content.find(old)
    if idx >= 0:
        end = content.find('\n', idx)
        line = content[idx:end]
        content = content.replace(line, line + '\nlet currentOverviewCategory = null;')
        fixes += 1
        print('Fix 2: Added currentOverviewCategory')
    else:
        print('Fix 2: WARNING - could not find showOnlyDupes line')
else:
    print('Fix 2: currentOverviewCategory already exists')

# ---- Fix 3: init() - add loadClassSelection after buildClassPicker ----
if 'loadClassSelection' not in content or 'loadClassSelection()' not in content.split('function loadClassSelection')[0]:
    # Check if it's called in init
    init_idx = content.find('async function init()')
    init_end = content.find('\nasync function ', init_idx + 10)
    if init_end < 0:
        init_end = content.find('\nfunction ', init_idx + 10)
    init_body = content[init_idx:init_end]
    
    if 'loadClassSelection' not in init_body:
        old = '        buildClassPicker();\n        buildSubjectList();'
        new = '        loadClassSelection();\n        buildClassPicker();\n        updateClassUI();\n        buildSubjectList();'
        if old in content:
            content = content.replace(old, new)
            fixes += 1
            print('Fix 3: Added loadClassSelection() to init()')
        else:
            print('Fix 3: WARNING - could not find init section')
    else:
        print('Fix 3: loadClassSelection already in init()')
else:
    print('Fix 3: loadClassSelection already exists')

# ---- Fix 4: toggleClass - add saveClassSelection ----
old4 = 'function toggleClass(cls) {\n    const idx = selectedClasses.indexOf(cls);\n    if (idx === -1) selectedClasses.push(cls);\n    else            selectedClasses.splice(idx, 1);\n    updateClassUI();\n    renderTable();\n}'
new4 = 'function toggleClass(cls) {\n    const idx = selectedClasses.indexOf(cls);\n    if (idx === -1) selectedClasses.push(cls);\n    else            selectedClasses.splice(idx, 1);\n    updateClassUI();\n    saveClassSelection();\n    renderTable();\n}'
if old4 in content:
    content = content.replace(old4, new4)
    fixes += 1
    print('Fix 4: Fixed toggleClass() to save selection')
elif 'saveClassSelection' in content and 'function toggleClass' in content:
    print('Fix 4: toggleClass already saves selection')
else:
    print('Fix 4: WARNING - toggleClass not found in expected form')

# ---- Fix 5: clearClasses - add saveClassSelection ----
old5 = 'function clearClasses() {\n    selectedClasses = [];\n    updateClassUI();\n    renderTable();\n}'
new5 = 'function clearClasses() {\n    selectedClasses = [];\n    updateClassUI();\n    saveClassSelection();\n    renderTable();\n}'
if old5 in content:
    content = content.replace(old5, new5)
    fixes += 1
    print('Fix 5: Fixed clearClasses() to save selection')
elif 'saveClassSelection' in content:
    print('Fix 5: clearClasses probably already fixed')
else:
    print('Fix 5: WARNING - clearClasses not found')

# ---- Fix 6: Add loadClassSelection and saveClassSelection functions ----
if 'function loadClassSelection' not in content:
    old6 = 'function saveSubjectSettings() {\n    localStorage.setItem(STORAGE_KEY_SUBJECTS, JSON.stringify([...allowedSubjects]));\n}'
    new6 = old6 + """

function saveClassSelection() {
    localStorage.setItem(STORAGE_KEY_CLASSES, JSON.stringify(selectedClasses));
}

function loadClassSelection() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY_CLASSES);
        if (saved) selectedClasses = JSON.parse(saved);
    } catch(e) { selectedClasses = []; }
}"""
    if old6 in content:
        content = content.replace(old6, new6)
        fixes += 1
        print('Fix 6: Added saveClassSelection() and loadClassSelection()')
    else:
        # Append at end before DOMContentLoaded
        insert_point = content.rfind('document.addEventListener')
        if insert_point > 0:
            insert = """
function saveClassSelection() {
    localStorage.setItem(STORAGE_KEY_CLASSES, JSON.stringify(selectedClasses));
}

function loadClassSelection() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY_CLASSES);
        if (saved) selectedClasses = JSON.parse(saved);
    } catch(e) { selectedClasses = []; }
}

"""
            content = content[:insert_point] + insert + content[insert_point:]
            fixes += 1
            print('Fix 6: Inserted saveClassSelection/loadClassSelection before DOMContentLoaded')
        else:
            print('Fix 6: WARNING - could not insert class selection functions')
else:
    print('Fix 6: loadClassSelection already exists')

# ---- Fix 7: Add loadScheduledMatches if missing ----
if 'function loadScheduledMatches' not in content:
    old7 = 'function saveScheduledMatches()'
    insert7 = """function loadScheduledMatches() {
    const saved = localStorage.getItem('classVSclass_scheduled_matches');
    if (saved) {
        try { scheduledMatches = JSON.parse(saved); } catch(e) { scheduledMatches = []; }
    } else if (typeof EMBEDDED_SCHEDULED_DATA !== 'undefined') {
        scheduledMatches = EMBEDDED_SCHEDULED_DATA;
    } else {
        scheduledMatches = [];
    }
}

"""
    if old7 in content:
        content = content.replace(old7, insert7 + old7)
        fixes += 1
        print('Fix 7: Added loadScheduledMatches()')
    else:
        print('Fix 7: WARNING - saveScheduledMatches not found')
else:
    print('Fix 7: loadScheduledMatches already exists')

# ---- Fix 8: Add renderTournamentOverview and related functions ----
if 'function renderTournamentOverview' not in content:
    tournament = r"""

// ===== Tournament Overview =====
function selectOverviewCategory(cat) {
    currentOverviewCategory = cat;
    const titleEl = document.getElementById('selectedCategoryTitle');
    const descEl = document.getElementById('selectedCategoryDesc');
    if (titleEl) titleEl.textContent = cat;
    if (descEl) descEl.textContent = cat;
    renderTournamentOverview();
}

function renderTournamentOverview() {
    const sidebar = document.getElementById('categorySidebar');
    const container = document.getElementById('tournamentContainer');
    if (!sidebar || !container) return;

    const categories = Array.from(new Set(matchesData.map(m => {
        return m.category.replace(/\u7b2c \d \u8f2a|\u6e96\u6c7a\u8cfd|\u6c7a\u8cfd|\u5b63\u8ecd\u8cfd/g, '').trim();
    }))).sort();

    sidebar.innerHTML = categories.map(cat =>
        `<div class="sidebar-item ${currentOverviewCategory === cat ? 'active' : ''}" onclick="selectOverviewCategory('${cat.replace(/'/g, "\\'")}')">${getSportIcon(cat)} ${cat}</div>`
    ).join('');

    if (!currentOverviewCategory && categories.length > 0) {
        currentOverviewCategory = categories[0];
        selectOverviewCategory(currentOverviewCategory);
        return;
    }

    if (currentOverviewCategory) {
        const catMatches = matchesData.filter(m => m.category.includes(currentOverviewCategory));
        const isRR = catMatches.some(m => m.category.includes('\u9810\u8cfd') || m.category.includes('\u5faa\u74b0'));
        container.innerHTML = '';
        if (isRR) renderRoundRobinGrid(catMatches, container);
        else renderBracketTree(catMatches, container);
    }
}

function renderRoundRobinGrid(matches, container) {
    const teams = Array.from(new Set(matches.flatMap(m => [m.teamA, m.teamB]))).sort();
    const stats = {};
    teams.forEach(t => { stats[t] = { pts:0, w:0, d:0, l:0, pf:0, pa:0, played:0 }; });
    const matrix = {};
    matches.forEach(m => {
        if (!matrix[m.teamA]) matrix[m.teamA] = {};
        if (!matrix[m.teamB]) matrix[m.teamB] = {};
        if (m.status === "\u2705 \u5df2\u7d50\u675f" && m.score) {
            matrix[m.teamA][m.teamB] = m.score;
            matrix[m.teamB][m.teamA] = m.score.split(':').reverse().join(':');
            const sa = m.scoreA||0, sb = m.scoreB||0;
            stats[m.teamA].played++; stats[m.teamB].played++;
            stats[m.teamA].pf += sa; stats[m.teamA].pa += sb;
            stats[m.teamB].pf += sb; stats[m.teamB].pa += sa;
            if (m.winner === m.teamA) { stats[m.teamA].w++; stats[m.teamA].pts+=3; stats[m.teamB].l++; }
            else if (m.winner === m.teamB) { stats[m.teamB].w++; stats[m.teamB].pts+=3; stats[m.teamA].l++; }
            else { stats[m.teamA].d++; stats[m.teamB].d++; stats[m.teamA].pts++; stats[m.teamB].pts++; }
        }
    });
    const sorted = Object.entries(stats).sort((a,b) => b[1].pts - a[1].pts);
    container.innerHTML =
        `<div class="rr-dashboard">
        <div class="rr-leaderboard">
        ${sorted.map(([t,s],i) => `
            <div class="rr-rank-card ${i===0?'rank-top':''}">
                <div class="rr-rank-num">${i+1}</div>
                <div class="rr-rank-name">${t}</div>
                <div class="rr-rank-stats">W${s.w} D${s.d} L${s.l} | ${s.pf}:${s.pa}</div>
                <div class="rr-rank-pts">${s.pts} PTS</div>
            </div>`).join('')}
        </div>
        <table class="rr-matrix-table">
            <thead><tr><th></th>${teams.map(t=>`<th>${t}</th>`).join('')}</tr></thead>
            <tbody>
            ${teams.map(row => `
                <tr><td class="rr-matrix-label">${row}</td>
                ${teams.map(col => {
                    if (row === col) return '<td class="rr-void">/</td>';
                    const m = matches.find(x => (x.teamA===row&&x.teamB===col)||(x.teamB===row&&x.teamA===col));
                    const score = matrix[row] && matrix[row][col];
                    const sch = m ? scheduledMatches.find(sm => String(sm.matchId)===String(m.id)) : null;
                    return `<td class="${score?'rr-has-score':''}" onclick="openEditScoreModal('${m?m.id:''}')" style="cursor:pointer;position:relative;">
                        ${score||'-'}
                        ${sch ? `<i class="fas fa-print" style="position:absolute;bottom:2px;right:2px;font-size:8px;color:#999;" onclick="event.stopPropagation();printMatchSlipById('${m.id}')"></i>` : ''}
                    </td>`;
                }).join('')}</tr>`
            ).join('')}
            </tbody>
        </table></div>`;
}

function renderBracketTree(matches, container) {
    const roundsMap = {};
    matches.forEach(m => {
        let r = '\u7b2c\u4e00\u8f2a';
        if (m.category.includes('\u7b2c 2 \u8f2a')) r = '\u7b2c\u4e8c\u8f2a';
        if (m.category.includes('\u6e96\u6c7a\u8cfd')) r = '\u6e96\u6c7a\u8cfd';
        if (m.category.includes('\u6c7a\u8cfd') && !m.category.includes('\u6e96')) r = '\u6c7a\u8cfd';
        if (m.category.includes('\u5b63\u8ecd')) r = '\u5b63\u8ecd\u8cfd';
        if (!roundsMap[r]) roundsMap[r] = [];
        roundsMap[r].push(m);
    });
    const order = ['\u7b2c\u4e00\u8f2a','\u7b2c\u4e8c\u8f2a','\u6e96\u6c7a\u8cfd','\u6c7a\u8cfd','\u5b63\u8ecd\u8cfd'].filter(r => roundsMap[r]);
    const tree = document.createElement('div');
    tree.className = 'bracket-tree';
    order.forEach(rKey => {
        const roundDiv = document.createElement('div');
        roundDiv.className = 'bracket-round';
        roundDiv.innerHTML = `<div class='round-header'>${rKey}</div>`;
        roundsMap[rKey].forEach(m => {
            const sch = scheduledMatches.find(sm => String(sm.matchId)===String(m.id));
            const el = document.createElement('div');
            el.className = 'tree-match';
            el.onclick = () => openEditScoreModal(m.id);
            el.innerHTML = `
                <div class='tree-team top ${m.winner===m.teamA?"winner":""}'><span>${m.teamA}</span><span style="opacity:0.6">${m.status==="\u2705 \u5df2\u7d50\u675f"?(m.scoreA||0):''}</span></div>
                <div class='tree-team bottom ${m.winner===m.teamB?"winner":""}'><span>${m.teamB}</span><span style="opacity:0.6">${m.status==="\u2705 \u5df2\u7d50\u675f"?(m.scoreB||0):''}</span></div>
                <div class='tree-footer'>
                    <span>#${m.id.split('_').pop()}</span>
                    <div style="display:flex;align-items:center;gap:5px;">
                        ${sch ? `<i class="fas fa-print" style="color:var(--blue);cursor:pointer;" onclick="event.stopPropagation();printMatchSlipById('${m.id}')"></i>` : ''}
                        <span class='${sch?"footer-scheduled":""}'>${sch ? '\u{1F4C5} ' + sch.date.split('-').slice(1).join('/') + ' P' + sch.periodIndex : '\u23f3 \u5f85\u6392\u5b9a'}</span>
                    </div>
                </div>`;
            roundDiv.appendChild(el);
        });
        tree.appendChild(roundDiv);
    });
    container.appendChild(tree);
}
"""
    content = content.rstrip() + '\n' + tournament
    fixes += 1
    print('Fix 8: Added renderTournamentOverview and related functions')
else:
    print('Fix 8: renderTournamentOverview already exists')

# Write
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print()
print(f'Total fixes applied: {fixes}')
print(f'Final file: {len(content)} chars')

import re
funcs = re.findall(r'^(?:async )?function (\w+)', content, re.MULTILINE)
key_check = ['loadClassSelection', 'saveClassSelection', 'loadScheduledMatches',
             'renderTournamentOverview', 'renderRoundRobinGrid', 'renderBracketTree',
             'selectOverviewCategory']
print('Key functions:')
for f in key_check:
    print(f'  [{"OK" if f in funcs else "MISSING"}] {f}')
