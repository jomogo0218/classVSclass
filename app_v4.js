let scheduleData = null;

const periodTimes = [
    "07:40 - 08:00", // 0: 早自習
    "08:05 - 08:50", // 1
    "09:00 - 09:45", // 2
    "10:00 - 10:45", // 3
    "11:00 - 11:45", // 4
    "13:00 - 13:45", // 5
    "14:00 - 14:45", // 6
    "15:00 - 15:45", // 7
    "15:55 - 16:40", // 8
    "16:45 - 17:30"  // 9
];

const periodNames = [
    "早自習",
    "第 1 節",
    "第 2 節",
    "第 3 節",
    "第 4 節",
    "第 5 節",
    "第 6 節",
    "第 7 節",
    "第 8 節",
    "第 9 節"
];

let allowedSubjects = new Set();
let allUniqueSubjects = [];
let currentMonday = getMonday(new Date()); // 追蹤目前顯示的週一日期

function getMonday(d) {
    const date = new Date(d);
    date.setHours(0,0,0,0);
    const day = date.getDay();
    const diff = date.getDate() - day + (day === 0 ? -6 : 1); 
    return new Date(date.setDate(diff));
}

function changeWeek(days) {
    currentMonday.setDate(currentMonday.getDate() + days);
    renderTable();
}

function resetWeek() {
    currentMonday = getMonday(new Date());
    renderTable();
}

// Default subjects that should be checked initially
const defaultSkillKeywords = [
    "體育", "音樂", "美術", "視覺藝術", "表演藝術", "童軍", "家政", "生活科技", "資訊科技", "機器人", "社團", "週會", "輔導", "健康教育", "軍訓", "生命教育", "藝術生活", "創客", "Maker", "表演創作", "自習", "空堂"
];

// 🆕 行事曆衝突資料 (由 PDF 解析)
const SCHOOL_CONFLICTS = [
    { start: "2026-03-25", end: "2026-03-26", label: "全校第一次段考", type: "exam" },
    { start: "2026-04-15", end: "2026-04-17", label: "高二畢旅/高一公訓/國二隔宿", type: "event" },
    { start: "2026-04-21", end: "2026-04-22", label: "國三模擬考", type: "exam" },
    { start: "2026-04-23", end: "2026-04-24", label: "高三畢業考", type: "exam" },
    { start: "2026-05-01", end: "2026-05-01", label: "勞動節 (全校放假)", type: "holiday" },
    { start: "2026-05-05", end: "2026-05-06", label: "國三第二次段考", type: "exam" },
    { start: "2026-05-08", end: "2026-05-08", label: "高一國一母親節合唱比賽", type: "event" },
    { start: "2026-05-14", end: "2026-05-15", label: "全校第二次段考", type: "exam" },
    { start: "2026-05-16", end: "2026-05-17", label: "國中教育會考", type: "exam" },
    { start: "2026-05-22", end: "2026-05-22", label: "國三生涯發展講座", type: "event" },
    { start: "2026-06-05", end: "2026-06-05", label: "畢業典禮", type: "event" },
    { start: "2026-06-19", end: "2026-06-19", label: "端午節 (放假)", type: "holiday" },
    { start: "2026-06-26", end: "2026-06-30", label: "全校期末考", type: "exam" }
];

async function init() {
    try {
        const response = await fetch('schedules.json');
        if (!response.ok) throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
        scheduleData = await response.json();
        
        initCalendarAlerts(); // 🆕 初始化提醒
        extractUniqueSubjects();
        populateSelectors();
        populateFilterList();
        setupEventListeners();
        setupSearch();
        renderTable(); 
    } catch (error) {
        console.error("Failed to load schedule data:", error);
        showError(error);
    }
}

// 🆕 動態顯示行事曆提醒
function initCalendarAlerts() {
    const container = document.getElementById('calendarAlerts');
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];
    
    // 過濾出「今天以後」或「正在進行中」的活動
    const activeConflicts = SCHOOL_CONFLICTS.filter(c => {
        return c.end >= todayStr;
    }).slice(0, 3); // 只顯示最近 3 個

    if (activeConflicts.length === 0) {
        container.style.display = 'none';
        return;
    }

    container.innerHTML = `
        <div class="alert-header">🚨 重要日程提醒</div>
        ${activeConflicts.map(c => {
            const isOngoing = todayStr >= c.start && todayStr <= c.end;
            return `
                <div class="alert-item ${c.type} ${isOngoing ? 'ongoing' : ''}">
                    <span class="alert-date">${c.start === c.end ? c.start.slice(5) : c.start.slice(5) + '~' + c.end.slice(5)}</span>
                    <span class="alert-label">${c.label}</span>
                </div>
            `;
        }).join('')}
    `;
}

function showError(error) {
    const overlay = document.getElementById('errorOverlay');
    const msg = document.getElementById('errorMessage');
    overlay.style.display = 'flex';
    msg.textContent = `${error.name}: ${error.message}\n${error.stack || ""}`;
}

function extractUniqueSubjects() {
    const subjectsMap = new Map(); // normalized -> display
    Object.values(scheduleData.schedules).forEach(classSched => {
        Object.values(classSched).forEach(days => {
            days.forEach(sub => {
                if (sub && sub !== "---" && sub.trim() !== "") {
                    const [subject, teacher] = sub.split('|');
                    const strictlyNormalized = (subject || "").normalize('NFKC').replace(/\s/g, '');
                    const cleanDisplay = (subject || "").normalize('NFKC').trim().replace(/\s+/g, '');
                    
                    if (strictlyNormalized && !subjectsMap.has(strictlyNormalized)) {
                        subjectsMap.set(strictlyNormalized, cleanDisplay);
                    }
                }
            });
        });
    });
    allUniqueSubjects = Array.from(subjectsMap.values()).sort();
    
    // Set initial allowed list
    subjectsMap.forEach((display, norm) => {
        if (defaultSkillKeywords.some(keyword => display.includes(keyword))) {
            allowedSubjects.add(norm);
        }
    });
    
    allUniqueSubjects = Array.from(subjectsMap.values()).sort();
}

function selectAllFilters(checked) {
    const searchTerm = document.getElementById('subjectSearch').value.toLowerCase();
    const subjectsMap = getSubjectsMap();
    
    subjectsMap.forEach((display, norm) => {
        // 只有符合搜尋條件的科目才會被勾選/取消勾選
        if (display.toLowerCase().includes(searchTerm)) {
            if (checked) allowedSubjects.add(norm);
            else allowedSubjects.delete(norm);
        }
    });
    populateFilterList(searchTerm);
    updateTable();
}

function setupSearch() {
    document.getElementById('subjectSearch').addEventListener('input', (e) => {
        populateFilterList(e.target.value.toLowerCase());
    });
}

function getSubjectsMap() {
    const subjectsMap = new Map();
    Object.values(scheduleData.schedules).forEach(classSched => {
        Object.values(classSched).forEach(days => {
            days.forEach(sub => {
                if (sub && sub !== "---" && sub.trim() !== "") {
                    const strictlyNormalized = sub.normalize('NFKC').replace(/\s/g, '');
                    const cleanDisplay = sub.normalize('NFKC').trim().replace(/\s+/g, '');
                    if (!subjectsMap.has(strictlyNormalized)) subjectsMap.set(strictlyNormalized, cleanDisplay);
                }
            });
        });
    });
    return subjectsMap;
}

function populateFilterList(searchTerm = "") {
    const container = document.getElementById('subjectFilters');
    container.innerHTML = '';
    
    const subjectsMap = getSubjectsMap();
    const sortedEntries = Array.from(subjectsMap.entries()).sort((a, b) => a[1].localeCompare(b[1]));

    let foundCount = 0;
    sortedEntries.forEach(([norm, display]) => {
        if (display.toLowerCase().includes(searchTerm)) {
            foundCount++;
            const div = document.createElement('label');
            div.className = 'filter-item';
            const isChecked = allowedSubjects.has(norm);
            
            div.innerHTML = `
                <input type="checkbox" value="${norm}" ${isChecked ? 'checked' : ''}>
                <span class="custom-checkbox"></span>
                <span class="subject-name">${display}</span>
            `;
            
            div.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) allowedSubjects.add(norm);
                else allowedSubjects.delete(norm);
                updateTable();
            });
            
            container.appendChild(div);
        }
    });

    if (foundCount === 0) {
        container.innerHTML = `<div style="color: var(--text-dim); text-align: center; padding: 2rem; font-size: 0.9rem;">找不到相符科目</div>`;
    }
}

let selectedClassA = "";
let selectedClassB = "";

function populateSelectors() {
    const gridA = document.getElementById('gridA');
    const gridB = document.getElementById('gridB');
    
    gridA.innerHTML = '';
    gridB.innerHTML = '';
    
    // 按年級分組 (首位數字)
    const grades = {};
    scheduleData.classes.forEach(className => {
        const grade = className.charAt(0);
        if (!grades[grade]) grades[grade] = [];
        grades[grade].push(className);
    });

    Object.keys(grades).sort().forEach(grade => {
        const groupLabel = document.createElement('div');
        groupLabel.className = 'grid-grade-label';
        groupLabel.textContent = `第 ${grade} 學群`;
        
        const containerA = document.createElement('div');
        containerA.className = 'grade-row';
        const containerB = document.createElement('div');
        containerB.className = 'grade-row';

        grades[grade].sort().forEach(className => {
            const btnA = createGridBtn(className, 'A');
            const btnB = createGridBtn(className, 'B');
            containerA.appendChild(btnA);
            containerB.appendChild(btnB);
        });

        gridA.appendChild(groupLabel.cloneNode(true));
        gridA.appendChild(containerA);
        gridB.appendChild(groupLabel.cloneNode(true));
        gridB.appendChild(containerB);
    });

    // 預選兩個班級
    if (scheduleData.classes.length >= 2) {
        selectClass('A', scheduleData.classes[0]);
        selectClass('B', scheduleData.classes[1]);
    }
}

function createGridBtn(className, type) {
    const btn = document.createElement('button');
    btn.className = `grid-btn btn-${type}`;
    btn.textContent = className;
    btn.dataset.class = className;
    btn.onclick = () => selectClass(type, className);
    return btn;
}

function selectClass(type, className) {
    if (type === 'A') {
        selectedClassA = className;
        document.getElementById('selectedA').textContent = className;
        updateGridHighlight('A', className);
    } else {
        selectedClassB = className;
        document.getElementById('selectedB').textContent = className;
        updateGridHighlight('B', className);
    }
    updateTable();
}

function updateGridHighlight(type, className) {
    const btns = document.querySelectorAll(`.grid-btn.btn-${type}`);
    btns.forEach(btn => {
        if (btn.dataset.class === className) btn.classList.add('active');
        else btn.classList.add('inactive'); // 沒選中的變淡
        if (btn.dataset.class !== className) btn.classList.remove('active');
        if (btn.dataset.class === className) btn.classList.remove('inactive');
    });
}

function setupEventListeners() {
    // Grid buttons have their own click listeners
}

function updateTable() {
    renderTable();
}

function renderTable() {
    const classAName = selectedClassA;
    const classBName = selectedClassB;
    const tbody = document.getElementById('tableBody');
    const thead = document.getElementById('tableHead');
    const weekDisplay = document.getElementById('currentWeekDisplay');
    const conflictNotice = document.getElementById('weekConflictNotice');
    
    tbody.innerHTML = '';
    thead.innerHTML = '';
    conflictNotice.innerHTML = '';

    // 計算本週日期
    const dateList = [];
    for(let i=0; i<5; i++) {
        const d = new Date(currentMonday);
        d.setDate(d.getDate() + i);
        dateList.push(d);
    }

    // 更新上方週數顯示
    const dStart = dateList[0];
    const dEnd = dateList[4];
    weekDisplay.textContent = `${dStart.getFullYear()} / ${String(dStart.getMonth()+1).padStart(2,'0')} / ${String(dStart.getDate()).padStart(2,'0')} ~ ${String(dEnd.getMonth()+1).padStart(2,'0')} / ${String(dEnd.getDate()).padStart(2,'0')}`;

    // 檢查本週是否有全校性大活動並顯示提示
    const weekConflicts = [];
    const dateStrings = dateList.map(d => d.toISOString().split('T')[0]);
    
    // 生成表頭
    const headTr = document.createElement('tr');
    const thPeriod = document.createElement('th');
    thPeriod.style.width = '10%';
    thPeriod.textContent = '節次';
    headTr.appendChild(thPeriod);
    
    const dayNames = ["週一", "週二", "週三", "週四", "週五"];
    dateList.forEach((date, i) => {
        const th = document.createElement('th');
        const dStr = date.toISOString().split('T')[0];
        const conflict = SCHOOL_CONFLICTS.find(c => dStr >= c.start && dStr <= c.end);
        
        const shortDate = `${date.getMonth()+1}/${date.getDate()}`;
        if (conflict) {
            th.innerHTML = `${dayNames[i]}<br><span style="font-size: 0.7rem; color: #f43f5e;">(${shortDate}) ${conflict.label}</span>`;
            th.style.color = "#f43f5e";
            if (!weekConflicts.some(c => c.label === conflict.label)) weekConflicts.push(conflict);
        } else {
            th.innerHTML = `${dayNames[i]}<br><span style="font-size: 0.7rem; opacity: 0.6;">(${shortDate})</span>`;
        }
        headTr.appendChild(th);
    });
    thead.appendChild(headTr);

    // 顯示週衝突摘要
    if (weekConflicts.length > 0) {
        conflictNotice.innerHTML = `⚠️ 本週有重要日程：${weekConflicts.map(c => `<span class="${c.type}">${c.label}</span>`).join('、')}`;
        conflictNotice.style.display = 'block';
    } else {
        conflictNotice.style.display = 'none';
    }

    if (!classAName && !classBName) {
        tbody.innerHTML = '<tr><td colspan="6" style="padding: 4rem; color: var(--text-dim); text-align: center; font-size: 2vh;">請在左側選擇班級...</td></tr>';
        return;
    }

    const schedA = classAName ? scheduleData.schedules[classAName] : null;
    const schedB = classBName ? scheduleData.schedules[classBName] : null;
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
    let matchCount = 0;

    for (let pIdx = 0; pIdx < 10; pIdx++) {
        const tr = document.createElement('tr');
        
        const tdPeriod = document.createElement('td');
        tdPeriod.innerHTML = `<span class="period-num">${periodNames[pIdx]}</span><span class="period-time">${periodTimes[pIdx]}</span>`;
        tr.appendChild(tdPeriod);

        days.forEach(day => {
            const td = document.createElement('td');
            const subAraw = schedA ? (schedA[day][pIdx] || "").trim() : "";
            const subBraw = schedB ? (schedB[day][pIdx] || "").trim() : "";

            const [subA, teacherA] = subAraw.split('|');
            const [subB, teacherB] = subBraw.split('|');

            const normA = (subA || "").normalize('NFKC').replace(/\s/g, '');
            const normB = (subB || "").normalize('NFKC').replace(/\s/g, '');

            const isSkillA = allowedSubjects.has(normA) || subA === "" || subA === "---" || !subA;
            const isSkillB = allowedSubjects.has(normB) || subB === "" || subB === "---" || !subB;
            
            let cellClass = "";
            let matchTag = "";

            if (classAName && classBName) {
                const isPEMatch = subA && subB && subA.includes("體育") && subB.includes("體育");
                const isPlayableMatch = isSkillA && isSkillB && (subA || subB) && (subA !== "---" || subB !== "---");
                const trulyEmpty = (!subA || subA === "---") && (!subB || subB === "---");

                if (isPEMatch) {
                    cellClass = "cell-pe-match";
                    matchTag = `<span class="match-tag pe-badge">✨ 雙班體育</span>`;
                } else if (isPlayableMatch && !trulyEmpty) {
                    cellClass = "cell-potential";
                    matchTag = `<span class="match-tag potential-badge">🎨 雙藝能課</span>`;
                } else if (!isSkillA || !isSkillB) {
                    cellClass = "cell-clash";
                    matchTag = `<span class="match-tag clash-badge">🚫 包含正課</span>`;
                    td.style.opacity = "0.3";
                }
                if (isPlayableMatch && !trulyEmpty) matchCount++;
            }

            td.className = cellClass;
            td.innerHTML = `
                <div class="cell-content">
                    ${classAName ? `
                        <div class="subject-item class-a-sub ${subA && subA.includes("體育") ? 'pe-highlight' : ''} ${classBName && !isSkillA ? 'core-class' : ''}">
                            ${subA || "---"} ${teacherA ? `<span class="teacher-name">${teacherA}</span>` : ''}
                        </div>
                    ` : ''}
                    ${classBName ? `
                        <div class="subject-item class-b-sub ${subB && subB.includes("體育") ? 'pe-highlight' : ''} ${classAName && !isSkillB ? 'core-class' : ''}">
                            ${subB || "---"} ${teacherB ? `<span class="teacher-name">${teacherB}</span>` : ''}
                        </div>
                    ` : ''}
                    ${matchTag}
                </div>
            `;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    }

    document.getElementById('matchStats').textContent = (classAName && classBName) 
        ? `找到 ${matchCount} 個推薦時段` 
        : `預覽模式: ${classAName || classBName}`;
}

init();
