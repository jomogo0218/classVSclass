/* ============================================================
   排課配課系統 — app.js
   功能：多班選擇、LocalStorage 科目記憶、週切換、衝突標記
   ============================================================ */

'use strict';

// ===== 常數 =====
const PERIOD_NAMES = ['早自習','第1節','第2節','第3節','第4節','第5節','第6節','第7節','課業輔導','精進學習'];
const PERIOD_TIMES = ['07:40-08:00','08:05-08:50','09:00-09:45','10:00-10:45','11:00-11:45','13:00-13:45','14:00-14:45','15:00-15:45','15:55-16:40','16:45-17:30'];
const DAYS         = ['Mon','Tue','Wed','Thu','Fri'];
const DAY_NAMES    = ['週一','週二','週三','週四','週五'];
const COLORS       = 6; // number of color cycles

const SKILL_KEYWORDS = ['體育','音樂','美術','視覺藝術','表演藝術','童軍','家政','生活科技',
    '資訊科技','機器人','社團','班週會','輔導','健康教育','軍訓','生命教育','藝術','創客','Maker','自習','空堂',
    // 彈性/探究/多元課程
    '彈性','多元','選修','探究','實作','科技','環境','生命科學','地球科學',
    '生涯','週會','本土語','閱讀','識字','晨讀','科學',
    // 精進學習
    '精進','精進學習'];

const CONFLICTS = [
    { start:'2026-03-25', end:'2026-03-26', label:'全校第一次段考',           type:'exam'    },
    { start:'2026-04-15', end:'2026-04-17', label:'高二畢旅/高一公訓/國二隔宿', type:'event'   },
    { start:'2026-04-21', end:'2026-04-22', label:'國三模擬考',               type:'exam'    },
    { start:'2026-04-23', end:'2026-04-24', label:'高三畢業考',               type:'exam'    },
    { start:'2026-05-01', end:'2026-05-01', label:'勞動節（全校放假）',        type:'holiday' },
    { start:'2026-05-05', end:'2026-05-06', label:'國三第二次段考',            type:'exam'    },
    { start:'2026-05-08', end:'2026-05-08', label:'母親節合唱比賽',            type:'event'   },
    { start:'2026-05-14', end:'2026-05-15', label:'全校第二次段考',            type:'exam'    },
    { start:'2026-05-16', end:'2026-05-17', label:'國中教育會考',              type:'exam'    },
    { start:'2026-05-22', end:'2026-05-22', label:'國三生涯發展講座',          type:'event'   },
    { start:'2026-06-05', end:'2026-06-05', label:'畢業典禮',                 type:'event'   },
    { start:'2026-06-19', end:'2026-06-19', label:'端午節（放假）',            type:'holiday' },
    { start:'2026-06-26', end:'2026-06-30', label:'全校期末考',               type:'exam'    },
];

const STORAGE_KEY_SUBJECTS = 'classVSclass_allowed_subjects_v3';

// ===== 狀態 =====
let scheduleData    = null;
let selectedClasses = [];       // array of class names
let allowedSubjects = new Set();
let currentMonday   = getMonday(new Date());

// ===== 賽程相關狀態 =====
let matchesData       = []; // all matches from JSON
let scheduledMatches  = []; // [{ matchId, date, periodIndex }]
let selectedMatchId   = null;
let matchSearchTerm   = '';

// Helper to get Icon
function getSportIcon(cat) {
    if (cat.includes('籃球') || cat.includes('籃')) return '<span style="font-size:1.1rem; vertical-align:middle; margin-right:4px;">🏀</span>';
    if (cat.includes('排球') || cat.includes('排')) return '<span style="font-size:1.1rem; vertical-align:middle; margin-right:4px;">🏐</span>';
    if (cat.includes('羽球') || cat.includes('羽')) {
        // Unmistakable Custom Shuttlecock Silhouette
        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style="width:1.2rem;height:1.2rem;fill:currentColor;vertical-align:-0.125em;margin-right:4px;">
            <path d="M 144 300 L 64 128 L 128 32 L 192 192 L 256 32 L 320 192 L 384 32 L 448 128 L 368 300 Z" />
            <path d="M 150 320 L 362 320 L 354 360 L 158 360 Z" />
            <path d="M 160 380 L 352 380 A 96 96 0 0 1 160 380 Z" />
        </svg>`;
    }
    return '🏆';
}

// NEW: Initialize Firestore Listener
function initFirestoreListener() {
    if (!window.db) return;
    console.log("Initializing Firestore Listener...");
    db.collection('scheduledMatches').onSnapshot(querySnapshot => {
        const matches = [];
        querySnapshot.forEach(doc => {
            matches.push({ matchId: parseInt(doc.id), ...doc.data() });
        });
        scheduledMatches = matches;
        console.log("Firestore updated, matches count:", matches.length);
        
        // Re-render if we are in the middle of viewing
        if (document.querySelector('.tab-btn[data-tab="scheduling"]').classList.contains('active')) {
            renderSchedulingView();
        } else {
            renderTable();
        }
    }, err => {
        console.warn("Firestore error (likely missing config):", err);
    });
}

// ===== 初始化 =====
async function init() {
    try {
        const res = await fetch('schedules.json');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        scheduleData = await res.json();

        loadSubjectSettings();
        buildClassPicker();
        buildSubjectList();
        setupWeekControls();
        setupMobileSidebar();
        setupTabSwitcher(); 
        
        await loadMatches(); 
        
        // Try to load from Firestore, otherwise fallback to LocalStorage
        if (window.db) {
            initFirestoreListener();
            // Optional: Migration from LocalStorage if Firestore is empty
            db.collection('scheduledMatches').limit(1).get().then(snap => {
                if (snap.empty) {
                    const localData = localStorage.getItem('classVSclass_scheduled_matches');
                    if (localData) {
                        try {
                            const parsed = JSON.parse(localData);
                            console.log("Migrating LocalStorage data to Firestore...");
                            parsed.forEach(m => saveScheduledMatchToFirestore(m));
                        } catch(e) {}
                    }
                }
            });
        } else {
            loadScheduledMatches(); 
        }
        
        renderTable();
        renderSchedulingView(); 
    } catch (e) {
        document.getElementById('errorModal').style.display = 'flex';
        document.getElementById('errorMsg').textContent = e.stack || e.message;
    }
}

// ===== 日期工具 =====
function getMonday(d) {
    const date = new Date(d);
    date.setHours(0,0,0,0);
    const day  = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(date.setDate(diff));
}

function isoDate(d) {
    return d.toISOString().split('T')[0];
}

function shortDate(d) {
    return `${d.getMonth()+1}/${d.getDate()}`;
}

function getWeekDates() {
    return DAYS.map((_, i) => {
        const d = new Date(currentMonday);
        d.setDate(d.getDate() + i);
        return d;
    });
}

function conflictsForDate(dStr) {
    return CONFLICTS.filter(c => dStr >= c.start && dStr <= c.end);
}

// ===== 週控制 =====
function setupWeekControls() {
    document.getElementById('btnPrevWeek').onclick = () => { 
        currentMonday.setDate(currentMonday.getDate()-7); 
        renderTable(); 
        renderSchedulingView(); 
    };
    document.getElementById('btnNextWeek').onclick = () => { 
        currentMonday.setDate(currentMonday.getDate()+7); 
        renderTable(); 
        renderSchedulingView(); 
    };
    document.getElementById('btnToday').onclick = () => { 
        currentMonday = getMonday(new Date()); 
        renderTable(); 
        renderSchedulingView(); 
    };
}

function updateWeekDisplay() {
    const dates   = getWeekDates();
    const mon     = dates[0], fri = dates[4];
    const today   = getMonday(new Date());
    const isToday = isoDate(mon) === isoDate(today);

    document.getElementById('weekLabel').textContent = isToday ? '本週' : '';
    document.getElementById('weekRange').textContent =
        `${mon.getFullYear()}/${String(mon.getMonth()+1).padStart(2,'0')}/${String(mon.getDate()).padStart(2,'0')} – ${String(fri.getMonth()+1).padStart(2,'0')}/${String(fri.getDate()).padStart(2,'0')}`;

    // Conflict banner
    const banner    = document.getElementById('conflictBanner');
    const weekStr   = dates.map(isoDate);
    const weekConf  = [];
    CONFLICTS.forEach(c => {
        if (weekStr.some(ds => ds >= c.start && ds <= c.end)) weekConf.push(c.label);
    });
    if (weekConf.length) {
        banner.style.display = 'flex';
        banner.textContent   = '⚠️ 本週：' + weekConf.join(' · ');
    } else {
        banner.style.display = 'none';
    }
}

// ===== 班級選擇 =====
function buildClassPicker() {
    const picker = document.getElementById('classPicker');
    picker.innerHTML = '';

    // 明確定義年級分組順序
    const GRADE_ORDER = ['國一','國二','國三','高一','高二','高三','其他'];

    const groups = {};
    GRADE_ORDER.forEach(g => groups[g] = []);

    scheduleData.classes.forEach(cls => {
        let matched = false;
        for (const grade of GRADE_ORDER.slice(0, -1)) {
            if (cls.startsWith(grade)) {
                groups[grade].push(cls);
                matched = true;
                break;
            }
        }
        if (!matched) groups['其他'].push(cls);
    });

    GRADE_ORDER.forEach(grade => {
        const classes = groups[grade];
        if (classes.length === 0) return;

        const groupEl = document.createElement('div');
        groupEl.className = 'grade-group';
        groupEl.innerHTML = `<div class="grade-label">${grade}</div>`;

        const btnsEl = document.createElement('div');
        btnsEl.className = 'grade-buttons';

        classes.sort().forEach(cls => {
            const btn = document.createElement('button');
            btn.className   = 'class-btn';
            // 顯示文字：取出年級後的部分（班號或班名）
            const suffix = cls.slice(grade.length).trim();
            btn.textContent = suffix || cls;
            btn.title       = cls;   // hover 顯示完整名稱
            btn.dataset.cls = cls;
            btn.onclick     = () => toggleClass(cls);
            btnsEl.appendChild(btn);
        });

        groupEl.appendChild(btnsEl);
        picker.appendChild(groupEl);
    });

    document.getElementById('btnClearClasses').onclick = clearClasses;
}

function toggleClass(cls) {
    const idx = selectedClasses.indexOf(cls);
    if (idx === -1) selectedClasses.push(cls);
    else            selectedClasses.splice(idx, 1);
    updateClassUI();
    renderTable();
}

function clearClasses() {
    selectedClasses = [];
    updateClassUI();
    renderTable();
}

function updateClassUI() {
    // Update buttons
    document.querySelectorAll('.class-btn').forEach(btn => {
        btn.classList.toggle('active', selectedClasses.includes(btn.dataset.cls));
    });

    // Update chips
    const chips = document.getElementById('selectedChips');
    chips.innerHTML = '';
    if (selectedClasses.length === 0) {
        chips.innerHTML = '<span class="no-selection-hint">請點選下方班級（可多選）</span>';
        return;
    }
    selectedClasses.forEach(cls => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.innerHTML = `${cls}<button class="chip-remove" data-cls="${cls}">×</button>`;
        chip.querySelector('.chip-remove').onclick = () => { toggleClass(cls); };
        chips.appendChild(chip);
    });
}

// ===== 科目設定 =====
function loadSubjectSettings() {
    const saved = localStorage.getItem(STORAGE_KEY_SUBJECTS);
    if (saved) {
        try { allowedSubjects = new Set(JSON.parse(saved)); return; } catch(e) {}
    }
    // 預設：勾選技能科目
    extractAllSubjects().forEach((norm, display) => {
        if (SKILL_KEYWORDS.some(kw => norm.includes(kw.normalize('NFKC')))) {
            allowedSubjects.add(norm);
        }
    });
    saveSubjectSettings();
}

function saveSubjectSettings() {
    localStorage.setItem(STORAGE_KEY_SUBJECTS, JSON.stringify([...allowedSubjects]));
}

function extractAllSubjects() {
    const map = new Map(); // norm -> display
    Object.values(scheduleData.schedules).forEach(sched => {
        DAYS.forEach(day => {
            (sched[day] || []).forEach(raw => {
                if (!raw || raw.trim() === '' || raw === '---') return;
                const [subj] = raw.split('|');
                const norm   = (subj || '').normalize('NFKC').replace(/\s/g,'');
                const disp   = (subj || '').normalize('NFKC').trim().replace(/\s+/g,' ');
                if (norm && !map.has(norm)) map.set(norm, disp);
            });
        });
    });
    return map;
}

function buildSubjectList(searchTerm = '') {
    const list = document.getElementById('subjectList');
    list.innerHTML = '';
    const lower = searchTerm.toLowerCase();

    const map     = extractAllSubjects();
    const entries = [...map.entries()].sort((a,b) => a[1].localeCompare(b[1], 'zh-TW'));

    let count = 0;
    entries.forEach(([norm, disp]) => {
        if (lower && !disp.toLowerCase().includes(lower)) return;
        count++;
        const label = document.createElement('label');
        label.className = 'subject-item';
        const checked = allowedSubjects.has(norm);
        label.innerHTML = `
            <input type="checkbox" value="${norm}" ${checked ? 'checked' : ''}>
            <span class="subject-check"></span>
            <span class="subject-name" title="${disp}">${disp}</span>`;
        label.querySelector('input').onchange = e => {
            if (e.target.checked) allowedSubjects.add(norm);
            else                  allowedSubjects.delete(norm);
            saveSubjectSettings();
            renderTable();
        };
        list.appendChild(label);
    });

    if (count === 0) list.innerHTML = '<div style="color:var(--text-3);font-size:0.75rem;padding:0.5rem;grid-column:span 2">找不到符合科目</div>';

    // Select / Deselect All (filtered)
    document.getElementById('btnSelectAll').onclick = () => {
        entries.forEach(([norm, disp]) => {
            if (!lower || disp.toLowerCase().includes(lower)) allowedSubjects.add(norm);
        });
        saveSubjectSettings(); buildSubjectList(searchTerm); renderTable();
    };
    document.getElementById('btnDeselectAll').onclick = () => {
        entries.forEach(([norm, disp]) => {
            if (!lower || disp.toLowerCase().includes(lower)) allowedSubjects.delete(norm);
        });
        saveSubjectSettings(); buildSubjectList(searchTerm); renderTable();
    };
}

function setupSubjectSearch() {
    document.getElementById('subjectSearch').oninput = e => buildSubjectList(e.target.value);
}

// ===== 手機側邊欄 =====
function setupMobileSidebar() {
    const toggle  = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function open()  { sidebar.classList.add('open'); overlay.classList.add('open'); }
    function close() { sidebar.classList.remove('open'); overlay.classList.remove('open'); }

    toggle.onclick  = open;
    overlay.onclick = close;
}

// ===== 主渲染 =====
function renderTable() {
    updateWeekDisplay();
    updateStats();

    const emptyState  = document.getElementById('emptyState');
    const tableScroll = document.getElementById('tableScroll');

    if (selectedClasses.length === 0) {
        emptyState.style.display  = '';
        tableScroll.style.display = 'none';
        return;
    }
    emptyState.style.display  = 'none';
    tableScroll.style.display = '';

    buildTableHead();
    buildTableBody();
}

function buildTableHead() {
    const thead = document.getElementById('tableHead');
    thead.innerHTML = '';
    const tr = document.createElement('tr');

    // Period col
    const th0 = document.createElement('th');
    th0.className   = 'period-col';
    th0.textContent = '節次';
    tr.appendChild(th0);

    const dates = getWeekDates();
    dates.forEach((date, i) => {
        const dStr  = isoDate(date);
        const confs = conflictsForDate(dStr);
        const th    = document.createElement('th');
        if (confs.length) th.classList.add('has-conflict');
        th.innerHTML = `${DAY_NAMES[i]}<span class="date-sub">${shortDate(date)}${confs.length ? ' ⚠' : ''}</span>`;
        tr.appendChild(th);
    });

    thead.appendChild(tr);
}

function buildTableBody() {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

    let peCount = 0, skillCount = 0;

    for (let p = 0; p < PERIOD_NAMES.length; p++) {
        const tr = document.createElement('tr');

        // Period cell
        const tdP = document.createElement('td');
        tdP.className = 'period-cell';
        tdP.innerHTML = `<span class="p-name">${PERIOD_NAMES[p]}</span><span class="p-time">${PERIOD_TIMES[p]}</span>`;
        tr.appendChild(tdP);

        DAYS.forEach((day, di) => {
            const td   = document.createElement('td');
            const inner = document.createElement('div');
            inner.className = 'cell-inner';

            // Collect slot info for each selected class
            const slots = selectedClasses.map((cls, cidx) => {
                const raw      = (scheduleData.schedules[cls]?.[day]?.[p] || '').trim();
                const [subj, teacher] = raw.split('|');
                const subjClean = (subj || '').normalize('NFKC').trim().replace(/\s+/g,' ');
                const norm      = subjClean.normalize('NFKC').replace(/\s/g,'');
                const isEmpty   = !subjClean || subjClean === '---';
                const isSkill   = isEmpty || allowedSubjects.has(norm);
                return { cls, cidx, subjClean, teacher: (teacher||'').trim(), norm, isEmpty, isSkill };
            });

            // Determine cell status
            const allSkill  = slots.every(s => s.isSkill);
            const someSkill = slots.some(s => s.isSkill);
            const allPE     = slots.every(s => s.subjClean.replace(/\s/g,'').includes('體育'));
            const hasAny    = slots.some(s => !s.isEmpty);

            if (allPE && hasAny) {
                td.className = 'cell-pe'; peCount++;
            } else if (allSkill && hasAny && selectedClasses.length >= 2) {
                td.className = 'cell-skill'; skillCount++;
            } else if (someSkill && !allSkill && hasAny) {
                td.className = 'cell-partial';
            } else if (!allSkill && hasAny) {
                td.className = 'cell-blocked';
            }

            // Render each class row
            slots.forEach(({ cls, cidx, subjClean, teacher, isSkill, isEmpty }) => {
                if (selectedClasses.length === 1 || !isEmpty) {
                    const row   = document.createElement('div');
                    row.className = `class-slot slot-color-${cidx % COLORS} ${!isSkill ? 'slot-core' : ''}`;

                    const tag   = document.createElement('span');
                    tag.className   = `slot-class-tag tag-color-${cidx % COLORS}`;
                    tag.textContent = cls.replace(/[^\d\u4e00-\u9fa5]/g,'').slice(-3); // short label

                    const sub   = document.createElement('span');
                    sub.className   = 'slot-subject';
                    sub.textContent = isEmpty ? '—' : subjClean;

                    const tea   = document.createElement('span');
                    tea.className   = 'slot-teacher';
                    tea.textContent = teacher;

                    row.appendChild(tag);
                    row.appendChild(sub);
                    if (teacher) row.appendChild(tea);
                    inner.appendChild(row);
                }
            });

            // Badge
            if (hasAny && selectedClasses.length >= 2) {
                if (allPE) {
                    const b = document.createElement('div');
                    b.className = 'match-badge badge-pe';
                    b.textContent = '🏃 全班體育';
                    inner.appendChild(b);
                } else if (allSkill) {
                    const b = document.createElement('div');
                    b.className = 'match-badge badge-skill';
                    b.textContent = '✅ 全班可排';
                    inner.appendChild(b);
                }
            }

            // SHOW SCHEDULED MATCH IF ANY
            const dateStr = isoDate(getWeekDates()[di]);
            const existingMatch = scheduledMatches.find(sm => sm.date === dateStr && sm.periodIndex === p);
            if (existingMatch) {
                td.style.backgroundColor = 'var(--cell-scheduled)';
                const matchInfo = matchesData.find(m => m.id === existingMatch.matchId);
                const b = document.createElement('div');
                b.className = 'match-badge';
                b.style.background = 'var(--accent)';
                b.style.color = '#000';
                b.style.marginTop = '4px';
                b.style.fontSize = '0.65rem';
                b.innerHTML = matchInfo 
                    ? `${getSportIcon(matchInfo.category)} 賽程：${matchInfo.teamA} vs ${matchInfo.teamB}`
                    : `🏆 已結束賽事 (ID: ${existingMatch.matchId})`;
                inner.appendChild(b);
            }

            td.appendChild(inner);
            tr.appendChild(td);
        });

        tbody.appendChild(tr);
    }

    // Update skill count (excludes PE)
    document.getElementById('statPE').innerHTML    = `體育時段 <strong>${peCount}</strong> 個`;
    document.getElementById('statMatch').innerHTML = `推薦時段 <strong>${skillCount}</strong> 個`;
}

function updateStats() {
    document.getElementById('statSelected').innerHTML = `已選 <strong>${selectedClasses.length}</strong> 班`;
}

// ===== 頁籤控制 =====
function setupTabSwitcher() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.onclick = () => {
            const tabId = btn.dataset.tab;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
            
            if (tabId === 'scheduling') renderSchedulingView();
            else renderTable();
        };
    });
}

// ===== 賽程排定邏輯 =====
function getSportType(category) {
    if (category.includes('籃')) return '籃球';
    if (category.includes('排')) return '排球';
    if (category.includes('羽')) return '羽球';
    return '其他';
}

function getGender(category) {
    if (category.includes('男')) return '男';
    if (category.includes('女')) return '女';
    return '通用';
}

function getMatchClasses(match) {
    if (!match) return [];
    const classes = [];
    [match.teamA, match.teamB].forEach(teamStr => {
        if (!teamStr) return;
        // Normalize: Full-width to half-width and remove spaces
        const norm = (s) => s.normalize('NFKC').replace(/\s/g, '');
        const teamMatch = norm(teamStr);
        
        // 1. Exact match ignoring spaces
        let found = scheduleData.classes.find(c => norm(c) === teamMatch);
        
        // 2. Contains match
        if (!found) found = scheduleData.classes.find(c => norm(c).includes(teamMatch));
        
        // 3. Fallback: regex for "Grade Class" format
        if (!found) {
            const m = teamStr.match(/(高[一二三][\u4e00-\u9fa5]+|國[一二三]\d?)/);
            if (m) found = m[1];
        }
        
        if (found) classes.push(found);
    });
    const unique = [...new Set(classes)];
    if (unique.length === 0) {
        // Ultimate fallback to prevent selection failure
        console.warn("Could not detect classes for match:", match.teamA, match.teamB);
    }
    return unique;
}

function getSportLimit(sport) {
    if (sport === '籃球') return 2;
    if (sport === '排球') return 2;
    if (sport === '羽球') return 1;
    return 1;
}

async function loadMatches() {
    /* 暫時停用 Firestore 載入，以確保抓到最新的 matches.json 補班資料
    if (window.db) {
        try {
            const snap = await db.collection('matches').get();
            if (!snap.empty) {
                const matches = [];
                snap.forEach(doc => {
                    matches.push({ id: parseInt(doc.id), ...doc.data() });
                });
                matchesData = matches.sort((a,b) => a.id - b.id);
                console.log("Loaded matches from Firestore:", matchesData.length);
                return;
            }
        } catch (e) {
            console.warn("Firestore matches load failed, using local JSON:", e);
        }
    }
    */

    const res = await fetch('matches.json?v=' + Date.now());
    matchesData = await res.json();
    console.log("Loaded matches from static JSON (Cache-busted):", matchesData.length);

    // Auto-migrate if Firestore is empty
    if (window.db && matchesData.length > 0) {
        db.collection('matches').limit(1).get().then(snap => {
            if (snap.empty) {
                console.log("Migrating matchesData to Firestore...");
                matchesData.forEach(m => {
                    const { id, ...data } = m;
                    db.collection('matches').doc(id.toString()).set(data);
                });
            }
        });
    }
}

function saveScheduledMatches() {
    localStorage.setItem('classVSclass_scheduled_matches', JSON.stringify(scheduledMatches));
    
    // Also update Firestore if available
    if (window.db) {
        // Warning: This simplistic approach might be slow for many matches, but fine for current scale.
        // For better performance, we should do individual doc updates (see call sites).
    }
}

function saveScheduledMatchToFirestore(match) {
    if (!window.db) return;
    const { matchId, date, periodIndex } = match;
    db.collection('scheduledMatches').doc(matchId.toString()).set({
        date,
        periodIndex
    }).catch(err => console.error("Error saving match:", err));
}

function removeScheduledMatchFromFirestore(matchId) {
    if (!window.db) return;
    db.collection('scheduledMatches').doc(matchId.toString()).delete()
        .catch(err => console.error("Error removing match:", err));
}

function renderSchedulingView() {
    renderMatchList();
    renderSchedulingTable();
    renderScheduledGrid();
}

function renderMatchList() {
    const list = document.getElementById('pendingMatchList');
    list.innerHTML = '';
    
    // Normalize helper: convert full-width numbers to half-width and remove spaces
    const normalize = (str) => {
        return str.normalize('NFKC').replace(/\s/g, '').toLowerCase();
    };

    const searchNorm = normalize(matchSearchTerm);

    const filtered = matchesData.filter(m => {
        if (m.status === '✅ 已結束' || m.status.includes('已結束')) return false;
        
        const content = normalize(m.category + m.teamA + m.teamB);
        return content.includes(searchNorm);
    });

    // Add a counter header for debugging
    const countHeader = document.createElement('div');
    countHeader.style = 'padding: 4px 8px; font-size: 0.7rem; color: var(--text-3); font-weight: 700; border-bottom: 1px solid var(--border); margin-bottom: 4px;';
    countHeader.textContent = `📊 載入賽事：${matchesData.length} 場 (符合：${filtered.length})`;
    list.appendChild(countHeader);

    // Sort: Pending first, then by ID
    const sorted = [...filtered].sort((a, b) => {
        const isAScheduled = scheduledMatches.some(sm => sm.matchId === a.id);
        const isBScheduled = scheduledMatches.some(sm => sm.matchId === b.id);
        if (isAScheduled && !isBScheduled) return 1;
        if (!isAScheduled && isBScheduled) return -1;
        return a.id - b.id;
    });

    sorted.forEach(match => {
        const scheduledInfo = scheduledMatches.find(sm => sm.matchId === match.id);
        const isScheduled = !!scheduledInfo;
        
        const el = document.createElement('div');
        el.className = `match-item ${selectedMatchId === match.id ? 'active' : ''} ${isScheduled ? 'scheduled' : ''}`;
        el.innerHTML = `
            <div class="match-cat-row">
                <span class="match-cat">${getSportIcon(match.category)} ${match.category} ${isScheduled ? '✅' : ''}</span>
                ${isScheduled ? `<span class="match-date-badge">${scheduledInfo.date.split('-').slice(1).join('/')} ${PERIOD_NAMES[scheduledInfo.periodIndex]}</span>` : ''}
            </div>
            <div class="match-teams">
                <span class="match-team">${match.teamA}</span>
                <span class="match-vs">VS</span>
                <span class="match-team">${match.teamB}</span>
            </div>
        `;
        el.onclick = () => {
            try {
                selectedMatchId = match.id;
                
                // AUTO NAVIGATION: If scheduled, jump to that week
                if (isScheduled) {
                    const matchDate = new Date(scheduledInfo.date);
                    currentMonday = getMonday(matchDate);
                    renderTable(); 
                }
                
                renderSchedulingView();
            } catch (err) {
                console.error("Selection error:", err);
                selectedMatchId = match.id; // Still set it even if nav fails
                renderSchedulingView();
            }
        };
        list.appendChild(el);
    });

    document.getElementById('matchSearch').oninput = (e) => {
        matchSearchTerm = e.target.value;
        renderMatchList();
    };
}

function renderSchedulingTable() {
    const tableHead = document.getElementById('schedulingTableHead');
    const tableBody = document.getElementById('schedulingTableBody');
    const empty     = document.getElementById('schedulingEmpty');
    const scroll    = document.getElementById('schedulingTableScroll');
    const title     = document.getElementById('currentSchedulingMatch');
    const tips      = document.getElementById('schedulingTips');

    if (selectedMatchId === null) {
        empty.style.display = 'flex';
        scroll.style.display = 'none';
        title.textContent = '請先從左側選擇賽事';
        tips.style.display = 'none';
        return;
    }

    const match = matchesData.find(m => m.id === selectedMatchId);
    title.textContent = `對照：${match.teamA} vs ${match.teamB}`;
    tips.style.display = 'block';
    empty.style.display = 'none';
    scroll.style.display = 'block';

    // Get classes for comparison using the unifying function
    const classes = getMatchClasses(match);

    // Build Head
    tableHead.innerHTML = '';
    const trH = document.createElement('tr');
    trH.innerHTML = `<th class="period-col">節次</th>`;
    const dates = getWeekDates();
    dates.forEach((d, i) => {
        const dStr = isoDate(d);
        const confs = conflictsForDate(dStr);
        trH.innerHTML += `<th class="${confs.length ? 'has-conflict' : ''}">${DAY_NAMES[i]}<span class="date-sub">${shortDate(d)}${confs.length ? ' ⚠' : ''}</span></th>`;
    });
    tableHead.appendChild(trH);

    // Build Body
    tableBody.innerHTML = '';
    for (let p = 0; p < PERIOD_NAMES.length; p++) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td class="period-cell"><span class="p-name">${PERIOD_NAMES[p]}</span><span class="p-time">${PERIOD_TIMES[p]}</span></td>`;

        DAYS.forEach((day, di) => {
            const td = document.createElement('td');
            const inner = document.createElement('div');
            inner.className = 'cell-inner';
            const dateStr = isoDate(dates[di]);

            const match = matchesData.find(m => m.id === selectedMatchId);
            const thisSport  = getSportType(match.category);
            const thisGender = getGender(match.category);
            const thisClasses = getMatchClasses(match);
            const limit      = getSportLimit(thisSport);

            // 1. Check Sport Limit (All matches of same sport in slot)
            const sportOccupants = scheduledMatches.filter(sm => {
                if (sm.date !== dateStr || sm.periodIndex !== p) return false;
                const m = matchesData.find(md => md.id === sm.matchId);
                return m && getSportType(m.category) === thisSport;
            });
            
            // 2. Check Class Conflict (Identify if involved classes are in same-gender matches)
            let classConflictReason = null;
            const scheduledInSlot = scheduledMatches.filter(sm => sm.date === dateStr && sm.periodIndex === p && sm.matchId !== selectedMatchId);
            
            for (const sm of scheduledInSlot) {
                const m = matchesData.find(md => md.id === sm.matchId);
                if (!m) continue; // Skip if match data is missing (finished/removed)
                const mClasses = getMatchClasses(m);
                const mGender  = getGender(m.category);
                
                // Compare classes
                for (const cls of thisClasses) {
                    if (mClasses.includes(cls)) {
                        // Class matched! Check gender.
                        if (mGender === thisGender || mGender === '通用' || thisGender === '通用') {
                            classConflictReason = `${cls} 已有${mGender}子賽事`;
                            break;
                        }
                    }
                }
                if (classConflictReason) break;
            }

            const isSelf = scheduledMatches.some(sm => sm.matchId === selectedMatchId && sm.date === dateStr && sm.periodIndex === p);
            const isFull = sportOccupants.length >= limit && !isSelf;
            const isBlocked = (isFull || classConflictReason) && !isSelf;

            const slots = classes.map((cls, cidx) => {
                const raw = (scheduleData.schedules[cls]?.[day]?.[p] || '').trim();
                const [subj] = raw.split('|');
                const norm = (subj || '').normalize('NFKC').replace(/\s/g,'');
                const isSkill = !subj || subj === '---' || allowedSubjects.has(norm);
                const isPE = (subj || '').includes('體育');
                return { cls, subj, isSkill, isPE };
            });

            const allSkill = (slots.length > 0) && slots.every(s => s.isSkill);
            const allPE    = (slots.length > 0) && slots.every(s => s.isPE);

            if (classConflictReason) {
                td.className = 'cell-blocked';
                const msg = document.createElement('div');
                msg.className = 'match-badge';
                msg.style.background = 'var(--green)'; // User requested Bright Green for important warnings
                msg.style.color = '#000';
                msg.style.fontWeight = '900';
                msg.style.boxShadow = '0 0 15px var(--green)';
                msg.innerHTML = `🚫 班級：${classConflictReason}`;
                inner.appendChild(msg);
                
                // Show the conflicting match
                const conflictingSM = scheduledInSlot.find(sm => {
                    const m = matchesData.find(md => md.id === sm.matchId);
                    return m && getMatchClasses(m).some(cls => thisClasses.includes(cls));
                });
                if (conflictingSM) {
                    const m = matchesData.find(md => md.id === conflictingSM.matchId);
                    if (m) {
                        const info = document.createElement('div');
                        info.style.fontSize = '0.7rem';
                        info.style.color = 'var(--text-3)';
                        info.style.marginTop = '4px';
                        info.textContent = `衝突：${m.teamA} vs ${m.teamB}`;
                        inner.appendChild(info);
                    }
                }
            } else if (isFull) {
                td.className = 'cell-blocked';
                const msg = document.createElement('div');
                msg.className = 'match-badge';
                msg.style.background = 'var(--green)';
                msg.style.color = '#000';
                msg.style.fontWeight = '900';
                msg.style.boxShadow = '0 0 15px var(--green)';
                msg.innerHTML = `⚠️ ${thisSport}場滿`;
                inner.appendChild(msg);
                
                // Show occupants clearly
                sportOccupants.forEach(sm => {
                    const m = matchesData.find(md => md.id === sm.matchId);
                    const info = document.createElement('div');
                    info.style.fontSize = '0.7rem';
                    info.style.color = 'var(--accent)';
                    info.style.fontWeight = '600';
                    info.textContent = `• ${m.teamA} vs ${m.teamB}`;
                    inner.appendChild(info);
                });
            } else if (isSelf) {
                td.className = 'cell-skill scheduling-cell';
                td.style.backgroundColor = 'var(--cell-scheduled)';
                td.style.boxShadow = 'inset 0 0 0 4px var(--green)';
                td.style.color = '#000'; // Dark text on bright green bg
                const selfMsg = document.createElement('div');
                selfMsg.className = 'match-badge';
                selfMsg.style.background = 'var(--green)';
                selfMsg.style.color = '#000';
                selfMsg.textContent = '📍 已排定在此';
                inner.appendChild(selfMsg);
            } else if (allPE) {
                td.className = 'cell-pe scheduling-cell';
            } else if (allSkill) {
                td.className = 'cell-skill scheduling-cell';
            } else {
                td.className = 'cell-blocked';
            }

            // Click to Schedule (Admin Override mode: Allow everything but warn)
            td.onclick = () => {
                const hasWarning = isBlocked || (!allSkill && !allPE);
                const warningMsg = isBlocked ? (classConflictReason || '時段已滿') : '該時段有正式學科課程';

                if (isSelf) {
                    if (confirm('確定取消此時段的排程？')) {
                        const targetId = selectedMatchId;
                        scheduledMatches = scheduledMatches.filter(sm => sm.matchId !== targetId);
                        saveScheduledMatches();
                        removeScheduledMatchFromFirestore(targetId);
                        renderSchedulingView();
                    }
                    return;
                }

                if (hasWarning) {
                    if (!confirm(`⚠️ 注意：${warningMsg}，確定要強制排入嗎？`)) return;
                } else {
                    if (!confirm(`確定排入此時段？`)) return;
                }
                
                const newMatch = {
                    matchId: selectedMatchId,
                    date: dateStr,
                    periodIndex: p
                };
                
                // Clear any existing schedule for this specific match first
                scheduledMatches = scheduledMatches.filter(sm => sm.matchId !== selectedMatchId);
                scheduledMatches.push(newMatch);
                saveScheduledMatches();
                saveScheduledMatchToFirestore(newMatch);
                renderSchedulingView();
                renderTable();
            };
            td.style.cursor = 'pointer';

            // Show classes in cell
            slots.forEach((s, i) => {
                const row = document.createElement('div');
                row.className = `class-slot slot-color-${i} ${!s.isSkill ? 'slot-core' : ''}`;
                row.innerHTML = `<span class="slot-class-tag tag-color-${i}">${s.cls.slice(-3)}</span><span class="slot-subject">${s.subj || '—'}</span>`;
                inner.appendChild(row);
            });

            td.appendChild(inner);
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    }
}

function renderScheduledGrid() {
    const grid = document.getElementById('scheduledGrid');
    grid.innerHTML = '';
    const dates = getWeekDates();

    dates.forEach((date, di) => {
        const dStr = isoDate(date);
        const dayBox = document.createElement('div');
        dayBox.className = 'scheduled-day';
        dayBox.innerHTML = `<h4>${DAY_NAMES[di]} ${shortDate(date)}</h4>`;

        const dayMatches = scheduledMatches.filter(sm => sm.date === dStr)
            .sort((a, b) => a.periodIndex - b.periodIndex);

        if (dayMatches.length === 0) {
            dayBox.innerHTML += '<div style="font-size:0.7rem;color:var(--text-3)">暫無賽程</div>';
        }

        dayMatches.forEach((sm, idx) => {
            const match = matchesData.find(m => m.id === sm.matchId);
            if (!match) return;

            // CROSS-CHECK FOR CONFLICTS WITHIN THE GRID
            let hasConflict = false;
            const thisGender = getGender(match.category);
            const thisClasses = getMatchClasses(match);
            
            dayMatches.forEach((otherSm, otherIdx) => {
                if (idx === otherIdx) return;
                if (sm.periodIndex !== otherSm.periodIndex) return; // only same period
                
                const otherM = matchesData.find(m => m.id === otherSm.matchId);
                const otherGender = getGender(otherM.category);
                const otherClasses = getMatchClasses(otherM);
                
                for(const cls of thisClasses) {
                    if (otherClasses.includes(cls)) {
                        if (thisGender === otherGender || thisGender === '通用' || otherGender === '通用') {
                            hasConflict = true;
                        }
                    }
                }
            });

            const div = document.createElement('div');
            div.className = 'scheduled-match cell-scheduled';
            if (hasConflict) {
                div.style.borderLeft = '3px solid #ff4d4d';
                div.style.background = 'rgba(255, 77, 77, 0.15)';
            } else {
                div.style.background = 'var(--cell-scheduled)';
            }
            
            div.innerHTML = `
                <span class="match-time-tag">${PERIOD_NAMES[sm.periodIndex]} ${hasConflict ? ' <span style="color:#ff4d4d">⚠️ 班級衝突</span>' : ''}</span>
                <div class="match-team-names">${getSportIcon(match.category)} ${match.teamA} VS ${match.teamB}</div>
                <button class="match-remove-btn" title="取消排程">✕</button>
            `;
            div.querySelector('.match-remove-btn').onclick = (e) => {
                e.stopPropagation();
                if (confirm('確定移除此賽程？')) {
                    const targetId = sm.matchId;
                    scheduledMatches = scheduledMatches.filter(item => item !== sm);
                    saveScheduledMatches();
                    removeScheduledMatchFromFirestore(targetId);
                    renderSchedulingView();
                    renderTable();
                }
            };
            dayBox.appendChild(div);
        });

        grid.appendChild(dayBox);
    });
}

// ===== 啟動 =====
document.addEventListener('DOMContentLoaded', () => {
    init().then(() => {
        setupSubjectSearch();
    });
});

// ===== 匯出功能 =====
function exportSchedule() {
    window.print();
}

function exportScheduleData() {
    if (scheduledMatches.length === 0) {
        alert('目前沒有排定的賽程資料可匯出！');
        return;
    }
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(scheduledMatches, null, 2));
    const dlAnchorElem = document.createElement('a');
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", `class_schedule_${isoDate(new Date())}.json`);
    document.body.appendChild(dlAnchorElem); // required for Firefox
    dlAnchorElem.click();
    dlAnchorElem.remove();
}

function importScheduleData(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            if (Array.isArray(data)) {
                scheduledMatches = data;
                saveScheduledMatches(); // Save to localStorage
                // Bulk sync to Firestore if available
                if (window.db) {
                    data.forEach(m => saveScheduledMatchToFirestore(m));
                }
                renderSchedulingView();
                renderTable();
                alert(`成功匯入 ${data.length} 筆賽程資料！`);
            } else {
                alert('錯誤：檔案內容不是有效的賽程陣列！');
            }
        } catch (err) {
            alert('檔案解析失敗，請確認檔案格式正確。');
        }
        event.target.value = ''; // Reset input so same file can be loaded again if needed
    };
    reader.readAsText(file);
}
