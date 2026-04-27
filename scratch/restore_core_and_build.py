
import os

def restore_core_and_build():
    print("Restoring Core Functions...")
    
    js_path = 'd:/classVSclass/app.js'
    js = open(js_path, 'r', encoding='utf-8').read()

    # 1. 補回遺失的本地儲存核心函數
    core_functions = """
// CORE: Local Storage Functions
function loadScheduledMatches() {
    const saved = localStorage.getItem('scheduledMatches');
    if (saved) {
        try {
            scheduledMatches = JSON.parse(saved);
            console.log('Loaded matches from localStorage:', scheduledMatches.length);
        } catch(e) {
            console.error('Error parsing scheduledMatches:', e);
            scheduledMatches = [];
        }
    } else if (typeof EMBEDDED_SCHEDULED_DATA !== 'undefined') {
        scheduledMatches = EMBEDDED_SCHEDULE_DATA;
    } else {
        scheduledMatches = [];
    }
}

function saveScheduledMatches() {
    localStorage.setItem('scheduledMatches', JSON.stringify(scheduledMatches));
}

function loadSubjectSettings() {
    const saved = localStorage.getItem('subjectSettings');
    if (saved) {
        try {
            const settings = JSON.parse(saved);
            Object.keys(settings).forEach(id => {
                const cb = document.querySelector(`.subject-checkbox[data-id="${id}"]`);
                if (cb) cb.checked = settings[id];
            });
        } catch(e) {}
    }
}

function saveSubjectSettings() {
    const settings = {};
    document.querySelectorAll('.subject-checkbox').forEach(cb => {
        settings[cb.dataset.id] = cb.checked;
    });
    localStorage.setItem('subjectSettings', JSON.stringify(settings));
}
"""
    if "function loadScheduledMatches" not in js:
        js += core_functions

    # 2. 確保 initApp 的數據載入邏輯正確 (不依賴外部 fetch)
    # 這裡我們手動修正 initApp 內部的 fetch 調用 (如果有的話)
    js = js.replace("await fetch('schedules.json')", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})")
    js = js.replace('await fetch("schedules.json")', "({ok:true, json:async()=>EMBEDDED_SCHEDULES})")
    js = js.replace("await fetch('matches.json?v=' + Date.now())", "({ok:true, json:async()=>EMBEDDED_MATCHES})")
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js)

    # 3. 執行最終編譯
    print("Rebuilding index_local.html...")
    os.system('python d:/classVSclass/scratch/final_victory_brute_force.py')
    print("Done!")

if __name__ == "__main__":
    restore_core_and_build()
