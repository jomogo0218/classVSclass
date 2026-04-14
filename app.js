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

// Default subjects that should be checked initially
const defaultSkillKeywords = [
    "體育", "音樂", "美術", "視覺藝術", "表演藝術", "童軍", "家政", "生活科技", "資訊科技", "機器人", "社團", "週會", "輔導", "健康教育", "軍訓", "生命教育", "藝術生活", "創客", "Maker", "表演創作", "自習", "空堂"
];

async function init() {
    try {
        const response = await fetch('schedules.json');
        if (!response.ok) throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
        scheduleData = await response.json();
        
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
    const subjectsMap = getSubjectsMap();
    subjectsMap.forEach((display, norm) => {
        if (checked) allowedSubjects.add(norm);
        else allowedSubjects.delete(norm);
    });
    populateFilterList();
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

    Array.from(subjectsMap.entries())
        .filter(([norm, display]) => display.toLowerCase().includes(searchTerm))
        .sort((a, b) => a[1].localeCompare(b[1]))
        .forEach(([norm, display]) => {
            const div = document.createElement('label');
            div.className = 'filter-item';
            const isChecked = allowedSubjects.has(norm);
            
            div.innerHTML = `
                <input type="checkbox" value="${norm}" ${isChecked ? 'checked' : ''}>
                <span>${display}</span>
            `;
            
            div.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) allowedSubjects.add(norm);
                else allowedSubjects.delete(norm);
                updateTable();
            });
            
            container.appendChild(div);
        });
}

function populateSelectors() {
    const classA = document.getElementById('classA');
    const classB = document.getElementById('classB');
    
    // Clear
    classA.innerHTML = '<option value="">請選擇班級...</option>';
    classB.innerHTML = '<option value="">請選擇班級...</option>';
    
    scheduleData.classes.sort().forEach(className => {
        const optA = document.createElement('option');
        optA.value = className;
        optA.textContent = className;
        classA.appendChild(optA);
        
        const optB = document.createElement('option');
        optB.value = className;
        optB.textContent = className;
        classB.appendChild(optB);
    });

    // Set defaults if available
    if (scheduleData.classes.length >= 2) {
        classA.selectedIndex = 1;
        classB.selectedIndex = 2;
        updateTable();
    }
}

function setupEventListeners() {
    document.getElementById('classA').addEventListener('change', updateTable);
    document.getElementById('classB').addEventListener('change', updateTable);
}

function updateTable() {
    renderTable();
}

function renderTable() {
    const classAName = document.getElementById('classA').value;
    const classBName = document.getElementById('classB').value;
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';

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
