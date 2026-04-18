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
    '資訊科技','機器人','社團','班週會','輔導','健康教育','軍訓','生命教育','藝術','創客','Maker','自習','空堂'];

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

const STORAGE_KEY_SUBJECTS = 'classVSclass_allowed_subjects_v2';

// ===== 狀態 =====
let scheduleData    = null;
let selectedClasses = [];       // array of class names
let allowedSubjects = new Set();
let currentMonday   = getMonday(new Date());

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
        renderTable();
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
    document.getElementById('btnPrevWeek').onclick = () => { currentMonday.setDate(currentMonday.getDate()-7); renderTable(); };
    document.getElementById('btnNextWeek').onclick = () => { currentMonday.setDate(currentMonday.getDate()+7); renderTable(); };
    document.getElementById('btnToday').onclick    = () => { currentMonday = getMonday(new Date()); renderTable(); };
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

    // 依學群分組
    const groups = {};
    scheduleData.classes.forEach(cls => {
        const grp = cls.match(/[^\d]+/)[0].trim(); // e.g. '國一', '高三'
        if (!groups[grp]) groups[grp] = [];
        groups[grp].push(cls);
    });

    Object.entries(groups).forEach(([grp, classes]) => {
        const groupEl = document.createElement('div');
        groupEl.className = 'grade-group';
        groupEl.innerHTML = `<div class="grade-label">${grp}</div>`;

        const btnsEl = document.createElement('div');
        btnsEl.className = 'grade-buttons';

        classes.sort().forEach(cls => {
            const btn = document.createElement('button');
            btn.className   = 'class-btn';
            btn.textContent = cls.replace(/[^\d]+/,''); // just the number+name part
            btn.title       = cls;
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

// ===== 啟動 =====
document.addEventListener('DOMContentLoaded', () => {
    init().then(() => {
        setupSubjectSearch();
    });
});
