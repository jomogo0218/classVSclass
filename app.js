/* ============================================================

   排課配課系統 — app.js

   功能：多班選擇、LocalStorage 科目記憶、週切換、衝突標記

   ============================================================ */



'use strict';



// ===== 常數 =====

const PERIOD_NAMES = ['早自習','第1節','第2節','第3節','第4節','第5節','第6節','第7節','課業輔導','精進學習'];

const DAY_NAMES    = ['週一','週二','週三','週四','週五'];

const DAYS         = ['Mon','Tue','Wed','Thu','Fri'];

const COLORS       = 10; // 固定為 10 班配色

const PERIOD_TIMES = ['07:40-08:00','08:05-08:50','09:00-09:45','10:00-10:45','11:00-11:45','13:00-13:45','14:00-14:45','15:00-15:45','15:55-16:40','16:45-17:30'];



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
const STORAGE_KEY_CLASSES = 'classVSclass_selected_classes_v2';



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

let showOnlyDupes     = false; // 重複檢查模式
let currentOverviewCategory = null;



// Helper to get Icon

function getSportIcon(cat) {

    const isMale   = cat.includes('男');

    const isFemale = cat.includes('女');

    const genderTag = isMale

        ? `<span style="font-size:0.75rem;color:#1a73e8;font-weight:900;vertical-align:middle;">♂</span>`

        : isFemale

        ? `<span style="font-size:0.75rem;color:#d93025;font-weight:900;vertical-align:middle;">♀</span>`

        : '';



    if (cat.includes('籃球') || cat.includes('籃')) {

        return `<span style="font-size:1.1rem;vertical-align:middle;margin-right:2px;">🏀</span>${genderTag} `;

    }

    if (cat.includes('排球') || cat.includes('排')) {

        return `<span style="font-size:1.1rem;vertical-align:middle;margin-right:2px;">🏐</span>${genderTag} `;

    }

    if (cat.includes('羽球') || cat.includes('羽')) {

        return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" style="width:1.1rem;height:1.1rem;fill:currentColor;vertical-align:-0.125em;margin-right:2px;">

            <path d="M 144 300 L 64 128 L 128 32 L 192 192 L 256 32 L 320 192 L 384 32 L 448 128 L 368 300 Z" />

            <path d="M 150 320 L 362 320 L 354 360 L 158 360 Z" />

            <path d="M 160 380 L 352 380 A 96 96 0 0 1 160 380 Z" />

        </svg>${genderTag} `;

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



        // 即時清除幽靈排程：matchId 找不到對應賽事的一律刪除

        const validIds = new Set(matchesData.map(m => m.id));

        const ghosts = matches.filter(sm => !validIds.has(sm.matchId));

        if (ghosts.length > 0) {

            console.warn(`⚠️ Firestore 含 ${ghosts.length} 筆幽靈排程，清除中...`, ghosts.map(g => g.matchId));

            ghosts.forEach(sm => {

                db.collection('scheduledMatches').doc(sm.matchId.toString()).delete();

            });

        }



        scheduledMatches = matches.filter(sm => validIds.has(sm.matchId));

        console.log("Firestore updated, valid matches:", scheduledMatches.length);



        // 同步更新兩個 Tab

        renderTable();

        renderSchedulingView();

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

        console.log("1. schedules.json 載入成功");



        loadSubjectSettings();
        loadClassSelection();

        buildClassPicker();
        updateClassUI();

        buildSubjectList();

        setupWeekControls();

        setupMobileSidebar();

        setupTabSwitcher(); 

        console.log("2. 基本介面組件初始化完成");

        

        await loadMatches(); 

        console.log("3. matches.json 載入完成，目前賽事數:", matchesData.length);

        

        // Try to load from Firestore, otherwise fallback to LocalStorage

        if (window.db) {

            console.log("4. 偵測到 Firestore，啟動監聽器");

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

                        } catch(e) { console.error("Migration error:", e); }

                    }

                }

            }).catch(err => console.error("Firestore get failed:", err));

        } else {

            console.log("4. 無 Firestore，使用 LocalStorage");

            loadScheduledMatches(); 

        }

        

        renderTable();

        renderSchedulingView();



        // 自動清理幽靈排程（統一用字串比對，避免數字/字串型別不一致）

        const validIds = new Set(matchesData.map(m => String(m.id)));

        const ghostMatches = scheduledMatches.filter(sm => !validIds.has(String(sm.matchId)));

        if (ghostMatches.length > 0) {

            console.warn(`⚠️ 發現 ${ghostMatches.length} 筆幽靈排程，自動清除中...`, ghostMatches);

            scheduledMatches = scheduledMatches.filter(sm => validIds.has(String(sm.matchId)));

            saveScheduledMatches();

            if (window.db) {

                ghostMatches.forEach(sm => removeScheduledMatchFromFirestore(sm.matchId));

            }

            renderTable();

            renderSchedulingView();

        }





    } catch (e) {

        document.getElementById('errorModal').style.display = 'flex';

        document.getElementById('errorMsg').textContent = e.stack || e.message;

    }

}



// ===== 日期工具 =====

function getMonday(d) {

    const date = new Date(d);

    date.setHours(0, 0, 0, 0); // Force to local midnight

    const day = date.getDay();

    const diff = date.getDate() - day + (day === 0 ? -6 : 1);

    const monday = new Date(date);

    monday.setDate(diff);

    monday.setHours(0, 0, 0, 0);

    return monday;

}



function isoDate(d) {

    const y = d.getFullYear();

    const m = String(d.getMonth() + 1).padStart(2, '0');

    const b = String(d.getDate()).padStart(2, '0');

    return `${y}-${m}-${b}`;

}



// NEW: Robust local date parser to avoid timezone offsets

function parseISO(s) {

    const [y, m, d] = s.split('-').map(Number);

    return new Date(y, m - 1, d);

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

    const weekRangeText = `${mon.getFullYear()}/${String(mon.getMonth()+1).padStart(2,'0')}/${String(mon.getDate()).padStart(2,'0')} – ${String(fri.getMonth()+1).padStart(2,'0')}/${String(fri.getDate()).padStart(2,'0')}`;

    document.getElementById('weekRange').textContent = weekRangeText;



    // 同步更新賽程規劃頁面的週次顯示

    const el2 = document.getElementById('weekRange2');

    const lb2 = document.getElementById('weekLabel2');

    if (el2) el2.textContent = weekRangeText;

    if (lb2) lb2.textContent = isToday ? '本週' : '';



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
    saveClassSelection();

    renderTable();

}



function clearClasses() {

    selectedClasses = [];

    updateClassUI();
    saveClassSelection();

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

    updateScheduleStats(); // 新增統計



    const emptyState  = document.getElementById('emptyState');

    const tableScroll = document.getElementById('tableScroll');



    // 即使沒選班級也顯示表格，讓使用者看全週賽程

    emptyState.style.display  = 'none';

    tableScroll.style.display = '';



    buildTableHead();

    buildTableBody();



    // --- 顯示行事曆重要事件提醒 ---

    const banner = document.getElementById('conflictBanner');

    if (banner) {

        const dates = getWeekDates();

        const weekEvents = [];

        dates.forEach(d => {

            const dStr = isoDate(d);

            const confs = conflictsForDate(dStr);

            confs.forEach(c => {

                if (!weekEvents.includes(c.label)) weekEvents.push(c.label);

            });

        });



        if (weekEvents.length > 0) {

            banner.style.display = 'flex';

            banner.style.alignItems = 'center';

            banner.style.gap = '8px';

            banner.innerHTML = `<i class="fas fa-exclamation-triangle"></i> <strong>本週重要事項提醒：</strong> ${weekEvents.join('、')}`;

        } else {

            banner.style.display = 'none';

        }

    }

}



function updateScheduleStats() {

    const summary = document.getElementById('scheduledStatsSummary');

    if (!summary) return;

    

    if (scheduledMatches.length === 0) {

        summary.innerHTML = "目前尚無任何已排定賽程。";

        return;

    }



    const counts = {};

    scheduledMatches.forEach(m => {

        counts[m.date] = (counts[m.date] || 0) + 1;

    });



    const currWeekDates = getWeekDates().map(isoDate);

    const sortedDates = Object.keys(counts).sort();

    

    let html = `<strong>📅 全局賽程分布概覽：</strong><br>`;

    sortedDates.forEach(d => {

        const isThisWeek = currWeekDates.includes(d);

        html += `<span style="display:inline-block; margin-right:12px; ${isThisWeek ? 'color:#10b981; font-weight:bold;' : 'color:#6b7280;'}">

            ${isThisWeek ? '📍' : '▫️'} ${d.split('-').slice(1).join('/')}: ${counts[d]}場

        </span>`;

    });

    summary.innerHTML = html;

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

        if (confs.length) {

            th.classList.add('has-conflict');

            const eventLabels = confs.map(c => c.label).join('、');

            th.innerHTML = `${DAY_NAMES[i]}<span class="date-sub">${shortDate(date)} <span style="color:var(--red); font-weight:bold;">⚠ ${eventLabels}</span></span>`;

        } else {

            th.innerHTML = `${DAY_NAMES[i]}<span class="date-sub">${shortDate(date)}</span>`;

        }

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

                // Fuzzy lookup: ignore spaces

                const targetKey = cls.replace(/\s/g, '');

                const actualKey = Object.keys(scheduleData.schedules).find(k => k.replace(/\s/g, '') === targetKey) || cls;

                

                const raw      = (scheduleData.schedules[actualKey]?.[day]?.[p] || '').trim();

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

                    row.className = `class-slot slot-color-${cidx % 10} ${!isSkill ? 'slot-core' : ''}`;



                    const tag   = document.createElement('span');

                    tag.className   = `slot-class-tag tag-color-${cidx % 10}`;

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



            // 顯示此時段的所有已排定賽程

            const dateStr = isoDate(getWeekDates()[di]);

            const matchesInSlot = scheduledMatches.filter(sm => sm.date === dateStr && sm.periodIndex === p);

            if (matchesInSlot.length > 0) {

                td.style.borderLeft = '4px solid #34a853';

                matchesInSlot.forEach(sm => {

                    const matchInfo = matchesData.find(m => m.id === sm.matchId);

                    const b = document.createElement('div');

                    b.style.cssText = `

                        background: #e6f4ea;

                        border: 1px solid #34a853;

                        border-radius: 4px;

                        padding: 3px 6px;

                        margin-top: 3px;

                        font-size: 11px;

                        font-weight: 600;

                        color: #188038;

                    `;

                    b.innerHTML = matchInfo

                        ? `${getSportIcon(matchInfo.category)} ${matchInfo.teamA} vs ${matchInfo.teamB}`

                        : `🏆 已排定（ID: ${sm.matchId}）`;

                    inner.appendChild(b);

                });

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

            else if (tabId === 'overview') renderTournamentOverview();

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



// ===== 賽事載入 (純本地版) =====

async function loadMatches() {

    try {

        console.log("正在從本地載入賽事資料 (matches.json)...");

        const res = await fetch('matches.json?v=' + Date.now());

        if (!res.ok) throw new Error(`無法讀取 matches.json (HTTP ${res.status})`);

        

        const raw = await res.json();

        

        // 讀取已經被「本地刪除」的賽事 ID

        const deletedIds = JSON.parse(localStorage.getItem('classVSclass_deleted_matches') || '[]');

        

        // 依 ID 去重複，確保資料乾淨，同時過濾掉已經刪除的比賽

        const seen = new Set();

        matchesData = raw.filter(m => {

            if (seen.has(m.id)) return false;

            if (deletedIds.includes(String(m.id)) || deletedIds.includes(m.id)) return false;

            seen.add(m.id);

            return true;

        });



        console.log(`✅ 成功載入賽事：目前共有 ${matchesData.length} 場。`);

    } catch (err) {

        console.error("載入賽事失敗:", err);

        alert("錯誤：無法載入賽事清單，請確認 matches.json 檔案是否存在。");

    }

}



function loadScheduledMatches() {
    const saved = localStorage.getItem('classVSclass_scheduled_matches');
    if (saved) {
        try { scheduledMatches = JSON.parse(saved); } catch(e) { scheduledMatches = []; }
    } else if (typeof EMBEDDED_SCHEDULED_DATA !== 'undefined') {
        scheduledMatches = EMBEDDED_SCHEDULED_DATA;
    } else {
        scheduledMatches = [];
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

        

        // 如果開啟了重複檢查模式

        if (showOnlyDupes) {

            const key = [m.category, m.teamA, m.teamB].map(s => s.trim().replace(/\s/g, '')).sort().join('|');

            const isDupe = matchesData.filter(other => {

                const otherKey = [other.category, other.teamA, other.teamB].map(s => s.trim().replace(/\s/g, '')).sort().join('|');

                return key === otherKey;

            }).length > 1;

            if (!isDupe) return false;

        }



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

                <div style="display:flex; gap:8px; align-items:center;">

                    ${isScheduled ? `<span class="match-date-badge">${scheduledInfo.date.split('-').slice(1).join('/')} ${PERIOD_NAMES[scheduledInfo.periodIndex]}</span>` : ''}

                    <button class="match-delete-btn" onclick="event.stopPropagation(); deleteMatch(${match.id})" title="永久刪除此賽事">

                        <i class="fas fa-trash-alt"></i>

                    </button>

                </div>

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

                    const matchDate = parseISO(scheduledInfo.date);

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



function toggleDupeFilter() {

    showOnlyDupes = !showOnlyDupes;

    const btn = document.getElementById('btnFilterDupes');

    if (showOnlyDupes) {

        btn.style.background = 'var(--red)';

        btn.style.color = 'white';

        btn.innerHTML = '<i class="fas fa-times"></i> 關閉檢查模式';

    } else {

        btn.style.background = 'var(--blue-light)';

        btn.style.color = 'var(--blue)';

        btn.innerHTML = '<i class="fas fa-clone"></i> ⚠️ 檢查重複';

    }

    renderMatchList();

}



async function deleteMatch(matchId) {

    const match = matchesData.find(m => String(m.id) === String(matchId));

    if (!match) {

        console.error("Match not found for ID:", matchId);

        return;

    }



    const confirmMsg = `⚠️ 確定要永久刪除此賽事嗎？\n\n盃賽：${match.category}\n對戰：${match.teamA} VS ${match.teamB}\n\n※ 注意：如果此賽事已排入賽程，排程也會一併移除！`;

    if (!confirm(confirmMsg)) return;



    // 1. 【本地優先】統一用字串比對確認刪除

    const idStr = String(matchId);

    matchesData = matchesData.filter(m => String(m.id) !== idStr);

    scheduledMatches = scheduledMatches.filter(sm => String(sm.matchId) !== idStr);

    

    // 【修改】將刪除紀錄永久存入 LocalStorage，確保重整網頁後依然不會出現

    const deletedIds = JSON.parse(localStorage.getItem('classVSclass_deleted_matches') || '[]');

    if (!deletedIds.includes(idStr)) {

        deletedIds.push(idStr);

        localStorage.setItem('classVSclass_deleted_matches', JSON.stringify(deletedIds));

    }

    

    // 儲存本地並刷新所有 UI

    saveScheduledMatches();

    renderMatchList();

    if (String(selectedMatchId) === idStr) {

        selectedMatchId = null;

        renderSchedulingTable();

    }

    renderScheduledGrid();

    renderTable();



    console.log(`✅ 本地已刪除賽事 ID: ${idStr}`);



    // 2. 【同步雲端】

    if (window.db) {

        // 嘗試從可能存在的兩個 collection 中刪除

        try {

            db.collection('matches').doc(idStr).delete().then(() => {

                console.log(`☁️ 雲端 matches 同步刪除成功: ${idStr}`);

            }).catch(e => console.warn("Firestore match delete skip:", e.message));



            db.collection('scheduledMatches').doc(idStr).delete().then(() => {

                console.log(`☁️ 雲端 scheduledMatches 同步刪除成功: ${idStr}`);

            }).catch(e => console.warn("Firestore schedule delete skip:", e.message));

        } catch (e) {

            console.error("Firestore sync error:", e);

        }

    }

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

        if (confs.length) {

            const eventLabels = confs.map(c => c.label).join('、');

            trH.innerHTML += `<th class="has-conflict">${DAY_NAMES[i]}<span class="date-sub">${shortDate(d)} <span style="color:var(--red); font-weight:bold;">⚠ ${eventLabels}</span></span></th>`;

        } else {

            trH.innerHTML += `<th>${DAY_NAMES[i]}<span class="date-sub">${shortDate(d)}</span></th>`;

        }

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

                const targetKey = cls.replace(/\s/g, '');

                const actualKey = Object.keys(scheduleData.schedules).find(k => k.replace(/\s/g, '') === targetKey) || cls;

                

                const raw = (scheduleData.schedules[actualKey]?.[day]?.[p] || '').trim();

                const [subj, teacher] = raw.split('|');

                const norm = (subj || '').normalize('NFKC').replace(/\s/g,'');

                const isSkill = !subj || subj === '---' || allowedSubjects.has(norm);

                const isPE = (subj || '').includes('體育');

                return { cls, subj, teacher: (teacher || '').trim(), isSkill, isPE };

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

                const teacherHtml = s.teacher

                    ? `<span class="slot-teacher">${s.teacher}</span>`

                    : '';

                row.innerHTML = `<span class="slot-class-tag tag-color-${i}">${s.cls.slice(-3)}</span><span class="slot-subject">${s.subj || '—'}</span>${teacherHtml}`;

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

                if (!otherM) return; // 防呆：如果找不到對照賽事資料則跳過

                

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

                <div style="display:flex;justify-content:flex-end;gap:4px;margin-top:4px;">
                    <button class="match-print-btn" title="列印借課通知單" style="background:#1a73e8;color:#fff;border:none;border-radius:4px;padding:2px 6px;font-size:11px;cursor:pointer;">🖨️ 通知單</button>
                    <button class="match-remove-btn" title="取消排程" style="background:transparent;border:none;color:#888;font-size:13px;cursor:pointer;">✕</button>
                </div>

            `;

            div.querySelector('.match-print-btn').onclick = (e) => {

                e.stopPropagation();

                printMatchSlipById(sm.matchId);

            };

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



// ===== 賽事清除工具 =====

function clearAllSchedules() {

    if (!confirm('⚠️ 警告：這將徹底清除雲端與本機的所有排程資料！\n此動作不可復原，確定要執行嗎？')) return;

    if (!confirm('請進行最後確認：資料清除後賽程將全部回到「左側待排清單」。確定？')) return;

    

    scheduledMatches = [];

    saveScheduledMatches();

    

    if (window.db) {

        db.collection('scheduledMatches').get().then(snap => {

            const batch = db.batch();

            snap.forEach(doc => batch.delete(doc.ref));

            return batch.commit();

        }).then(() => {

            alert('資料已成功清空！您可以重新排課了。');

            location.reload();

        });

    } else {

        location.reload();

    }

}



// ===== 診斷工具 =====

function showDiagnostics() {

    const total = matchesData.length;

    const idSet = new Set(matchesData.map(m => m.id));

    const dupes = total - idSet.size;



    // 取得已刪除名單

    const deletedIds = JSON.parse(localStorage.getItem('classVSclass_deleted_matches') || '[]');

    

    const scheduled = scheduledMatches.length;

    const recent = scheduledMatches.slice(-5).map(sm => {

        const m = matchesData.find(x => x.id === sm.matchId);

        return `• ${sm.date} 第${sm.periodIndex}節 ${m ? m.teamA + ' vs ' + m.teamB : '(未知)'}`;

    }).join('\n');



    let msg = `📊 系統診斷與紀錄報告\n` +

              `───────────────────\n` +

              `✅ 目前顯示賽事：${total} 場\n` +

              `⛔ 已手動刪除(隱藏)：${deletedIds.length} 場\n` +

              `📌 已排入課表：${scheduled} 場\n` +

              `───────────────────\n`;

              

    if (deletedIds.length > 0) {

        msg += `\n🗑️ 被刪除的 ID 清單：\n${deletedIds.join(', ')}\n`;

        msg += `\n(若需找回這些比賽，請使用「恢復所有隱藏賽事」功能)\n`;

    }



    msg += `\n🕒 最近排定記錄：\n${recent || '（無排程紀錄）'}`;



    alert(msg);

}



// 恢復所有已刪除赛次

function restoreDeletedMatches() {

    const deletedIds = JSON.parse(localStorage.getItem('classVSclass_deleted_matches') || '[]');

    if (deletedIds.length === 0) {

        alert("目前沒有任何被隱藏的賽事。");

        return;

    }

    

    if (confirm(`確定要恢復這 ${deletedIds.length} 場被隱藏的賽事嗎？`)) {

        localStorage.removeItem('classVSclass_deleted_matches');

        alert("✅ 已成功恢復！網頁將重新整理載入完整資料。");

        location.reload();

    }

}



// ===== 匯出功能 =====

function exportSchedule() { window.print(); }



function shiftDatesOneDay(delta) {

    const label = delta > 0 ? `往後移 ${delta}` : `往前移 ${Math.abs(delta)}`;

    if (!confirm(`📅 確定要把所有賽程${label}天嗎？`)) return;

    

    const repaired = scheduledMatches.map(m => {

        let d = new Date(m.date);

        d.setDate(d.getDate() + delta); 

        const y = d.getFullYear();

        const mm = String(d.getMonth() + 1).padStart(2, '0');

        const dd = String(d.getDate()).padStart(2, '0');

        return { ...m, date: `${y}-${mm}-${dd}` };

    });



    scheduledMatches = repaired;

    saveScheduledMatches();

    

    if (window.db) {

        const batch = db.batch();

        repaired.forEach(m => {

            const ref = db.collection('scheduledMatches').doc(m.matchId.toString());

            batch.set(ref, { date: m.date, periodIndex: m.periodIndex });

        });

        batch.commit().then(() => {

            alert('修正完成！');

            location.reload();

        });

    } else {

        location.reload();

    }

}



function rescue502() {

    if (!confirm('確定要把所有在 5/02 的 63 場賽程通通拉回到 4/27 (週一) 嗎？')) return;

    

    const repaired = scheduledMatches.map(m => {

        if (m.date === '2026-05-02') {

            return { ...m, date: '2026-04-27' };

        }

        return m;

    });



    scheduledMatches = repaired;

    saveScheduledMatches();

    

    if (window.db) {

        const batch = db.batch();

        repaired.forEach(m => {

            const ref = db.collection('scheduledMatches').doc(m.matchId.toString());

            batch.set(ref, { date: m.date, periodIndex: m.periodIndex });

        });

        batch.commit().then(() => {

            alert('已成功將 5/02 的賽程拉回到 4/27！');

            location.reload();

        });

    } else {

        location.reload();

    }

}



// init() 被 DOMContentLoaded 呼叫，此處刪除重複呼叫

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



// ===== 介面收合控制 (對應 index.html 的 onclick) =====

function toggleScheduledPanel() {

    const grid = document.getElementById('scheduledGrid');

    const icon = document.getElementById('scheduledToggleIcon');

    const btn = document.querySelector('.btn-action i.fa-arrows-alt-v'); // 獲取按鈕中的圖示

    

    // 如果目前是 grid 分佈（或是初始狀態），就切換到隱藏

    const isHidden = (grid.style.display === 'none');

    

    if (isHidden) {

        grid.style.display = 'grid';

        if (icon) icon.textContent = '▲ 收合';

        if (btn) btn.style.transform = 'rotate(0deg)';

    } else {

        grid.style.display = 'none';

        if (icon) icon.textContent = '▼ 展開';

        if (btn) btn.style.transform = 'rotate(180deg)';

    }

}


// ===== 列印與通知單系統 =====

let currentEditingMatchId = null;

function getOriginalTeacher(className, dayIdx, periodIdx) {
    // Use scheduleData if loaded, otherwise fall back to EMBEDDED_SCHEDULES (offline mode)
    const sd = (scheduleData && scheduleData.schedules)
        ? scheduleData
        : (typeof EMBEDDED_SCHEDULES !== 'undefined' ? EMBEDDED_SCHEDULES : null);
    if (!sd || !sd.schedules) return '資料未載入';

    const targetKey = className.replace(/\s/g, '');
    const actualKey = Object.keys(sd.schedules).find(k => {
        const kClean = k.replace(/\s/g, '');
        return targetKey.startsWith(kClean) || kClean.startsWith(targetKey);
    }) || className;

    const dayKey = ['Mon','Tue','Wed','Thu','Fri'][dayIdx];
    if (!dayKey) return '日期錯誤';
    const classSched = sd.schedules[actualKey];
    if (!classSched || !classSched[dayKey]) return '無課表資料';
    const raw = (classSched[dayKey][periodIdx] || '').trim();
    if (!raw || raw === '---') return '無課';

    const parts = raw.split('|');
    const subj = (parts[0] || '未命名').trim();
    const teacherRaw = (parts[1] || '').trim();

    // These are course-type descriptions stored in the teacher field, NOT real teacher names
    const NOT_TEACHER = [
        '學習時間', '活動時間', '議題', '探究', '學習時 間', '習時間',
        '教育', '設計', '寫作', '研究', '製作', '檔案製作',
        '與傷害防護', '與法律', '與生涯進路', '生涯進路',
        '與藝術的歷史', '科技應用專題', '與傳播應用', '無人機應用',
        '創客工坊', '程式設計', '簡報力',
        '物質構造與', '力學二與熱學', '電磁現象一', '電磁現象二',
        '化學反應與平衡二', '有機化學與', '生命的起源與植物', '生態、演化及',
        '與文化賞析', '跨域雙語導', '尋寶圖',
        '專題研究', '專題評析', '科技應用', '技術應用',
    ];
    const isFakeTeacher = teacherRaw === '' || NOT_TEACHER.some(kw => teacherRaw.includes(kw));
    const teacher = isFakeTeacher ? '（班導師）' : teacherRaw;
    return subj + ' / ' + teacher;
}


function printMatchSlip() {
    if (currentEditingMatchId) printMatchSlipById(currentEditingMatchId);
}

function printMatchSlipById(matchId) {
    const match = matchesData.find(m => String(m.id) === String(matchId));
    if (!match) { alert('找不到賽事資料！'); return; }

    const scheduled = scheduledMatches.find(sm => String(sm.matchId) === String(matchId));
    if (!scheduled) { alert('此賽事尚未排定時間，無法列印通知單。'); return; }

    const PNAMES = ['早自習','第1節','第2節','第3節','第4節','第5節','第6節','第7節','課業輔導','精進學習'];
    const DNAMES = ['週一','週二','週三','週四','週五'];
    const PTIMES = ['07:40-08:00','08:05-08:50','09:00-09:45','10:00-10:45','11:00-11:45','13:00-13:45','14:00-14:45','15:00-15:45','15:55-16:40','16:45-17:30'];

    const dateObj  = new Date(scheduled.date + 'T00:00:00');
    const dayIdx   = (dateObj.getDay() + 6) % 7;
    const dayName  = DNAMES[dayIdx] || '';
    const pName    = PNAMES[scheduled.periodIndex] || ('第' + scheduled.periodIndex + '節');
    const pTime    = PTIMES[scheduled.periodIndex] || '';

    const rawA = getOriginalTeacher(match.teamA, dayIdx, scheduled.periodIndex);
    const rawB = getOriginalTeacher(match.teamB, dayIdx, scheduled.periodIndex);
    const subjA  = rawA.includes('/') ? rawA.split('/')[0].trim() : '課程';
    const tNameA = rawA.includes('/') ? rawA.split('/')[1].trim() : '任課老師';
    const subjB  = rawB.includes('/') ? rawB.split('/')[0].trim() : '課程';
    const tNameB = rawB.includes('/') ? rawB.split('/')[1].trim() : '任課老師';

    const serialNo = String(matchId).slice(-4).padStart(4,'0');

    const printWin = window.open('', '_blank');
    if (!printWin) { alert('請允許彈出視窗以列印'); return; }

    printWin.document.write(`<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>借課通知單</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
@page { size: A4 portrait; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Noto Sans TC","Microsoft JhengHei","PingFang TC",sans-serif;
  background: #fff; color: #111;
  width: 210mm; height: 297mm;
  padding: 15mm 18mm;
  display: flex; flex-direction: column;
  font-size: 15px;
}
.slip-header {
  text-align: center;
  border-bottom: 3px double #222;
  padding-bottom: 6px;
  margin-bottom: 9px;
}
.slip-title { font-size: 28px; font-weight: 900; letter-spacing: 4px; margin-bottom: 4px; }
.slip-sub { font-size: 13px; color: #666; letter-spacing: 1px; }

.info-grid {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 10px 6px;
  margin-bottom: 16px;
}
.info-label { font-weight: 700; color: #333; padding-top: 3px; white-space: nowrap; font-size: 15px; }
.info-value {
  border-bottom: 1.5px solid #777;
  padding: 3px 8px 4px;
  line-height: 1.6;
  font-size: 15px;
}
.info-value.hl { font-weight: 900; font-size: 20px; color: #1a1a8c; }

.slip-notice {
  background: #fffbec;
  border-left: 5px solid #e6a800;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 2.0;
  margin-bottom: 20px;
  border-radius: 0 6px 6px 0;
}
.slip-notice strong { color: #b35c00; }

.sig-section-title {
  font-size: 13px; font-weight: 700; color: #555;
  letter-spacing: 2px; text-align: center; margin-bottom: 12px;
}
.teacher-boxes {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;
}
.teacher-box {
  border: 2px solid #999;
  border-radius: 8px;
  padding: 16px 18px;
  background: #f8f8f8;
}
.tb-header {
  font-size: 15px; font-weight: 900; color: #1a1a8c;
  border-bottom: 1.5px solid #ccc;
  padding-bottom: 6px; margin-bottom: 12px;
}
.tb-row { font-size: 14px; color: #333; margin-bottom: 8px; line-height: 1.6; }
.tb-row span { font-weight: 700; }
.sig-row {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; margin-top: 14px;
}
.sig-blank { flex: 1; border-bottom: 2px solid #333; height: 32px; }

.admin-row {
  display: flex; gap: 10px; margin-top: auto;
  padding-top: 10px; border-top: 2.5px solid #222;
}
.admin-box {
  flex: 1; text-align: center;
  font-size: 14px; font-weight: 700;
  padding-top: 4px;
}
.admin-box .sig-area {
  height: 50px; border-bottom: 1px solid #888;
  margin-top: 6px;
}
.serial { font-size: 9px; color: #bbb; float: right; }
</style>
</head>
<body>

<div class="slip-header">
  <div class="slip-title">嘉華中學體育競賽借課通知單</div>
  <div class="slip-sub">本通知單由體衛組發出，請妥善保存並請相關老師確認簽名後交回體衛組存查</div>
</div>

<div class="info-grid">
  <div class="info-label">比賽項目：</div>
  <div class="info-value">${match.category}</div>

  <div class="info-label">參賽班級：</div>
  <div class="info-value">
    <strong>${match.teamA}</strong>（${rawA}）
    &ensp;對陣&ensp;
    <strong>${match.teamB}</strong>（${rawB}）
  </div>

  <div class="info-label">借課時間：</div>
  <div class="info-value hl">
    ${scheduled.date}（${dayName}）${pName}　時間：${pTime}
  </div>
</div>

<div class="slip-notice">
  敬請 <strong>${match.teamA}</strong> 及 <strong>${match.teamB}</strong> 之任課老師惠予諒解，同意本節課暫借供體育競賽使用。<br>
  ✦ 參賽學生請<strong>準時</strong>於指定時間至比賽場地集合，並以正確禮儀服從競賽規範，不得無故缺席。<br>
  ✦ 本通知單須經兩位任課老師<strong>親筆簽名確認</strong>後，方具效力，請繳回體衛組妥善存查，感謝配合。
</div>

<div class="sig-section-title">── 任課老師確認簽名欄（敬請親筆簽名） ──</div>
<div class="teacher-boxes">
  <div class="teacher-box">
    <div class="tb-header">【${match.teamA}】任課老師 <span class="serial">No.${serialNo}-A</span></div>
    <div class="tb-row">課程科目：<span>${subjA}</span></div>
    <div class="tb-row">授課老師：<span>${tNameA} 老師</span></div>
    <div class="sig-row">
      老師確認簽名：<span class="sig-blank"></span>
    </div>
  </div>
  <div class="teacher-box">
    <div class="tb-header">【${match.teamB}】任課老師 <span class="serial">No.${serialNo}-B</span></div>
    <div class="tb-row">課程科目：<span>${subjB}</span></div>
    <div class="tb-row">授課老師：<span>${tNameB} 老師</span></div>
    <div class="sig-row">
      老師確認簽名：<span class="sig-blank"></span>
    </div>
  </div>
</div>

<div class="admin-row">
  <div class="admin-box">體衛組承辦人<div class="sig-area"></div></div>
  <div class="admin-box">體衛組長<div class="sig-area"></div></div>
  <div class="admin-box">學務主任<div class="sig-area"></div></div>
  <div class="admin-box">發文日期：<div class="sig-area" style="font-size:11px;padding-top:4px;">　　月　　日</div></div>
</div>

</body>
<script>
window.onload = function() {
  window.print();
  setTimeout(function(){ window.close(); }, 800);
};
<\/script>
</html>`);
    printWin.document.close();
}

function openEditScoreModal(matchId) {
    const m = matchesData.find(match => String(match.id) === String(matchId));
    if (!m) return;
    currentEditingMatchId = matchId;
    document.getElementById('modalTeamA').textContent = m.teamA;
    document.getElementById('modalTeamB').textContent = m.teamB;
    document.getElementById('inputScoreA').value = m.scoreA || 0;
    document.getElementById('inputScoreB').value = m.scoreB || 0;
    document.getElementById('modalStatus').value = m.status || "\u23f3 \u5f85\u6253";
    const scheduled = scheduledMatches.find(sm => String(sm.matchId) === String(matchId));
    const printBtn = document.getElementById('btnSnapshot');
    if (printBtn) printBtn.style.display = scheduled ? 'block' : 'none';
    document.getElementById('matchModal').style.display = 'flex';
}

function closeMatchModal() { document.getElementById('matchModal').style.display = 'none'; }

function saveMatchResult() {
    const m = matchesData.find(match => String(match.id) === String(currentEditingMatchId));
    if (!m) return;
    m.scoreA = parseInt(document.getElementById('inputScoreA').value);
    m.scoreB = parseInt(document.getElementById('inputScoreB').value);
    m.score = m.scoreA + ':' + m.scoreB;
    m.status = document.getElementById('modalStatus').value;
    if (m.status === "\u2705 \u5df2\u7d50\u675f") {
        if (m.scoreA > m.scoreB) m.winner = m.teamA;
        else if (m.scoreB > m.scoreA) m.winner = m.teamB;
        else m.winner = "\u548c\u5c40";
    }
    const localData = JSON.parse(localStorage.getItem('localMatchesData') || '[]');
    const idx = localData.findIndex(lm => String(lm.id) === String(m.id));
    if (idx !== -1) localData[idx] = m; else localData.push(m);
    localStorage.setItem('localMatchesData', JSON.stringify(localData));
    closeMatchModal();
    renderTournamentOverview();
}

function exportSchedule() { window.print(); }

function showDiagnostics() {
    const scheduled = scheduledMatches.length;
    alert('\u5df2\u6392\u5b9a\u8cfd\u4e8b\uff1a' + scheduled + ' \u5834\n\u8f09\u5165\u8cfd\u4e8b\uff1a' + matchesData.length + ' \u5834');
}

function restoreDeletedMatches() {
    const deletedIds = JSON.parse(localStorage.getItem('classVSclass_deleted_matches') || '[]');
    if (deletedIds.length === 0) { alert("\u76ee\u524d\u6c92\u6709\u4efb\u4f55\u88ab\u96b1\u85cf\u7684\u8cfd\u4e8b\u3002"); return; }
    if (confirm("\u78ba\u5b9a\u8981\u6062\u5fa9\u9019 " + deletedIds.length + " \u5834\u88ab\u96b1\u85cf\u7684\u8cfd\u4e8b\u55ce\uff1f")) {
        localStorage.removeItem('classVSclass_deleted_matches');
        alert("\u2705 \u5df2\u6210\u529f\u6062\u5fa9\uff01\u7db2\u9801\u5c07\u91cd\u65b0\u6574\u7406\u8f09\u5165\u5b8c\u6574\u8cc7\u6599\u3002");
        location.reload();
    }
}

// ===== \u8d77\u52d5\u9ede =====

function saveClassSelection() {
    localStorage.setItem(STORAGE_KEY_CLASSES, JSON.stringify(selectedClasses));
}

function loadClassSelection() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY_CLASSES);
        if (saved) selectedClasses = JSON.parse(saved);
    } catch(e) { selectedClasses = []; }
}

document.addEventListener('DOMContentLoaded', () => {
    init().then(() => { setupSubjectSearch(); });
});


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
