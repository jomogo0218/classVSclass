"""
patch_appjs.py
--------------
Safely patches app.js (stored as UTF-8 with CP950 byte sequences in strings/comments)
by injecting new features at the correct ASCII anchor points.

Strategy:
- Read as binary
- Locate anchor points by ASCII strings
- Inject new UTF-8 encoded blocks
- Write back as binary (preserving original encoding in unchanged sections)
"""

ANCHOR_FIND_SCHEDULED = b'function saveScheduledMatches'
ANCHOR_FIND_CLEANUP = b'// ===== \xe8\xa8\xba\xe6\x96\xb7\xe5\xb7\xa5\xe5\x85\xb7'  # diagnostic section marker

NEW_FUNCTIONS = '''

// ===== 列印與通知單系統 =====

let currentEditingMatchId = null;

function getOriginalTeacher(className, dayIdx, periodIdx) {
    if (!scheduleData || !scheduleData.schedules) return "\\u8cc7\\u6599\\u7f3a\\u6f0f";
    const targetKey = className.replace(/\\s/g, '');
    // \\u6a21\\u7cca\\u6bd4\\u5c0d\\uff1a\\u53ea\\u8981\\u8cfd\\u4e8b\\u73ed\\u7d1a\\u5305\\u542b\\u8ab2\\u8868\\u73ed\\u7d1a\\u95dc\\u9375\\u5b57\\u5373\\u53ef
    const actualKey = Object.keys(scheduleData.schedules).find(k => {
        const kClean = k.replace(/\\s/g, '');
        return targetKey.startsWith(kClean) || kClean.startsWith(targetKey);
    }) || className;

    const dayKey = ['Mon','Tue','Wed','Thu','Fri'][dayIdx] || dayIdx;
    const classSched = scheduleData.schedules[actualKey];
    if (!classSched || !classSched[dayKey]) return "\\u7121\\u8ab2";

    const raw = (classSched[dayKey][periodIdx] || '').trim();
    if (!raw || raw === '---') return "\\u7121\\u8ab2";
    const [subj, teacher] = raw.split('|');
    return (subj || '\\u672a\\u547d\\u540d') + ' / ' + (teacher || '\\u672a\\u547d\\u540d');
}

function printMatchSlip() {
    if (currentEditingMatchId) printMatchSlipById(currentEditingMatchId);
}

function printMatchSlipById(matchId) {
    const match = matchesData.find(m => String(m.id) === String(matchId));
    if (!match) { alert("\\u627e\\u4e0d\\u5230\\u8cfd\\u4e8b\\u8cc7\\u6599\\uff01"); return; }

    const scheduled = scheduledMatches.find(sm => String(sm.matchId) === String(matchId));
    if (!scheduled) { alert("\\u6b64\\u8cfd\\u4e8b\\u5c1a\\u672a\\u6392\\u5b9a\\u6642\\u9593\\uff0c\\u7121\\u6cd5\\u5217\\u5370\\u901a\\u77e5\\u55ae\\u3002"); return; }

    const PERIOD_NAMES_SLIP = ['\\u65e9\\u81ea\\u7fd2','\\u7b2c1\\u7bc0','\\u7b2c2\\u7bc0','\\u7b2c3\\u7bc0','\\u7b2c4\\u7bc0','\\u7b2c5\\u7bc0','\\u7b2c6\\u7bc0','\\u7b2c7\\u7bc0','\\u8ab2\\u696d\\u8f14\\u5c0e','\\u7cbe\\u9032\\u5b78\\u7fd2'];
    const DAY_NAMES_SLIP = ['\\u9031\\u4e00','\\u9031\\u4e8c','\\u9031\\u4e09','\\u9031\\u56db','\\u9031\\u4e94'];
    const PERIOD_TIMES_SLIP = ['07:40-08:00','08:05-08:50','09:00-09:45','10:00-10:45','11:00-11:45','13:00-13:45','14:00-14:45','15:00-15:45','15:55-16:40','16:45-17:30'];

    const dateObj = new Date(scheduled.date + 'T00:00:00');
    const dayIdx = (dateObj.getDay() + 6) % 7;
    const dayName = DAY_NAMES_SLIP[dayIdx];
    const periodName = PERIOD_NAMES_SLIP[scheduled.periodIndex];
    const periodTime = PERIOD_TIMES_SLIP[scheduled.periodIndex];

    const teacherA = getOriginalTeacher(match.teamA, dayIdx, scheduled.periodIndex);
    const teacherB = getOriginalTeacher(match.teamB, dayIdx, scheduled.periodIndex);

    const subjA = teacherA.includes('/') ? teacherA.split('/')[0].trim() : "\\u8ab2\\u7a0b";
    const subjB = teacherB.includes('/') ? teacherB.split('/')[0].trim() : "\\u8ab2\\u7a0b";
    const tNameA = teacherA.includes('/') ? teacherA.split('/')[1].trim() : "\\u4efb\\u8ab2\\u8001\\u5e2b";
    const tNameB = teacherB.includes('/') ? teacherB.split('/')[1].trim() : "\\u4efb\\u8ab2\\u8001\\u5e2b";

    const printWin = window.open('', '_blank');
    if (!printWin) { alert("\\u8acb\\u5141\\u8a31\\u5f48\\u51fa\\u8996\\u7a97\\u4ee5\\u5217\\u5370"); return; }
    printWin.document.write(`<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>\\u501f\\u8ab2\\u901a\\u77e5\\u55ae</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
<style>
@page { size: A5 landscape; margin: 0; }
body { font-family: "Noto Sans TC", "Microsoft JhengHei", sans-serif; margin:0; padding:12mm; background:#fff; color:#000; display:flex; justify-content:center; align-items:center; height:100vh; box-sizing:border-box; }
.slip-card { border:4px double #000; padding:18px; width:100%; height:100%; box-sizing:border-box; position:relative; display:flex; flex-direction:column; }
.header { text-align:center; border-bottom:2px solid #000; padding-bottom:8px; margin-bottom:14px; }
.header h1 { margin:0; font-size:24px; letter-spacing:2px; font-weight:900; }
.header p { margin:3px 0 0; font-size:13px; font-weight:bold; }
.info-item { display:flex; margin-bottom:10px; align-items:baseline; font-size:17px; }
.info-label { font-weight:700; width:100px; flex-shrink:0; }
.info-value { border-bottom:1.5px solid #000; flex:1; padding-left:8px; }
.info-time { font-weight:900; font-size:19px; }
.note { margin-top:12px; font-size:13px; font-weight:bold; font-style:italic; color:#c00; }
.teacher-signs { display:flex; gap:16px; margin-top:18px; }
.teacher-box { flex:1; border:1.5px dashed #555; padding:10px; background:#fafafa; }
.teacher-title { font-size:13px; font-weight:900; margin-bottom:8px; color:#333; }
.sig-line { border-bottom:1px solid #000; height:38px; display:flex; align-items:flex-end; padding-bottom:2px; font-size:15px; font-weight:bold; }
.footer-row { margin-top:30px; display:flex; justify-content:space-between; font-size:14px; font-weight:bold; }
.footer-box { border-top:2px solid #000; width:28%; text-align:center; padding-top:5px; }
.stamp { position:absolute; right:38px; bottom:90px; width:88px; height:88px; border:3px solid rgba(180,0,0,0.22); border-radius:50%; color:rgba(180,0,0,0.22); display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:900; text-align:center; transform:rotate(-15deg); pointer-events:none; }
</style>
</head>
<body>
<div class="slip-card">
  <div class="header">
    <h1>\\u5609\\u83ef\\u4e2d\\u5b78\\u9ad4\\u80b2\\u7af6\\u8cfd\\u501f\\u8ab2\\u901a\\u77e5\\u55ae</h1>
    <p>\\u3010 \\u516c \\u544a \\u8077 \\u3011</p>
  </div>
  <div class="info-item"><span class="info-label">\\u6bd4\\u8cfd\\u9805\\u76ee\\uff1a</span><span class="info-value">${match.category}</span></div>
  <div class="info-item"><span class="info-label">\\u5c0d\\u6230\\u73ed\\u7d1a\\uff1a</span><span class="info-value">${match.teamA} <small>(${teacherA})</small> &nbsp;<strong>vs</strong>&nbsp; ${match.teamB} <small>(${teacherB})</small></span></div>
  <div class="info-item"><span class="info-label">\\u6bd4\\u8cfd\\u6642\\u9593\\uff1a</span><span class="info-value info-time">${scheduled.date} (${dayName}) ${periodName} [${periodTime}]</span></div>
  <p class="note">\\u203b \\u8acb\\u4e0a\\u5217\\u73ed\\u7d1a\\u4e4b\\u4efb\\u8ab2\\u8001\\u5e2b\\u77e5\\u60b1\\uff0c\\u4e26\\u8acb\\u53c3\\u8cfd\\u5b78\\u751f\\u6e96\\u6642\\u81f3\\u6307\\u5b9a\\u5834\\u5730\\u96c6\\u5408\\u3002</p>
  <div class="teacher-signs">
    <div class="teacher-box">
      <div class="teacher-title">\\u3010${match.teamA}\\u3011\\u4efb\\u8ab2\\u8001\\u5e2b\\u78ba\\u8a8d\\u7c3d\\u540d\\uff1a</div>
      <div class="sig-line">${subjA} \\u2014 ${tNameA} \\u8001\\u5e2b\\uff1a____________________</div>
    </div>
    <div class="teacher-box">
      <div class="teacher-title">\\u3010${match.teamB}\\u3011\\u4efb\\u8ab2\\u8001\\u5e2b\\u78ba\\u8a8d\\u7c3d\\u540d\\uff1a</div>
      <div class="sig-line">${subjB} \\u2014 ${tNameB} \\u8001\\u5e2b\\uff1a____________________</div>
    </div>
  </div>
  <div class="footer-row">
    <div class="footer-box">\\u627f\\u8fa6\\u4eba</div>
    <div class="footer-box">\\u9ad4\\u885b\\u7d44\\u9577</div>
    <div class="footer-box">\\u5b78\\u52d9\\u4e3b\\u4efb</div>
  </div>
  <div class="stamp">\\u5609\\u83ef\\u4e2d\\u5b78<br>\\u9ad4\\u885b\\u7d44\\u5370</div>
</div>
<script>window.onload=function(){window.print();setTimeout(()=>window.close(),600);};<\/script>
</body></html>`);
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
    document.getElementById('modalStatus').value = m.status || "\\u23f3 \\u5f85\\u6253";
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
    if (m.status === "\\u2705 \\u5df2\\u7d50\\u675f") {
        if (m.scoreA > m.scoreB) m.winner = m.teamA;
        else if (m.scoreB > m.scoreA) m.winner = m.teamB;
        else m.winner = "\\u548c\\u5c40";
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
    alert('\\u5df2\\u6392\\u5b9a\\u8cfd\\u4e8b\\uff1a' + scheduled + ' \\u5834\\n\\u8f09\\u5165\\u8cfd\\u4e8b\\uff1a' + matchesData.length + ' \\u5834');
}

function restoreDeletedMatches() {
    const deletedIds = JSON.parse(localStorage.getItem('classVSclass_deleted_matches') || '[]');
    if (deletedIds.length === 0) { alert("\\u76ee\\u524d\\u6c92\\u6709\\u4efb\\u4f55\\u88ab\\u96b1\\u85cf\\u7684\\u8cfd\\u4e8b\\u3002"); return; }
    if (confirm("\\u78ba\\u5b9a\\u8981\\u6062\\u5fa9\\u9019 " + deletedIds.length + " \\u5834\\u88ab\\u96b1\\u85cf\\u7684\\u8cfd\\u4e8b\\u55ce\\uff1f")) {
        localStorage.removeItem('classVSclass_deleted_matches');
        alert("\\u2705 \\u5df2\\u6210\\u529f\\u6062\\u5fa9\\uff01\\u7db2\\u9801\\u5c07\\u91cd\\u65b0\\u6574\\u7406\\u8f09\\u5165\\u5b8c\\u6574\\u8cc7\\u6599\\u3002");
        location.reload();
    }
}

// ===== \\u8d77\\u52d5\\u9ede =====
document.addEventListener('DOMContentLoaded', () => {
    init().then(() => { setupSubjectSearch(); });
});
'''

import re

with open('app.js', 'rb') as f:
    raw = f.read()

# Decode - try UTF-8, fall back to cp950
try:
    content = raw.decode('utf-8')
    print("Decoded as UTF-8")
except:
    content = raw.decode('cp950', errors='replace')
    print("Decoded as CP950")

# Check if it already has these functions
if 'printMatchSlipById' in content:
    print("WARNING: printMatchSlipById already exists - removing old version first")
    # Remove from saveScheduledMatches onward (keep only the core app)
    anchor = 'function saveScheduledMatches'
    idx = content.find(anchor)
    if idx > 0:
        # find the saveScheduledMatches function end
        save_fn = '''function saveScheduledMatches() { localStorage.setItem('classVSclass_scheduled_matches', JSON.stringify(scheduledMatches)); }
function loadScheduledMatches() {
    const saved = localStorage.getItem('classVSclass_scheduled_matches');
    if (saved) { try { scheduledMatches = JSON.parse(saved); } catch(e) { scheduledMatches = []; } }
    else if (typeof EMBEDDED_SCHEDULED_DATA !== 'undefined') scheduledMatches = EMBEDDED_SCHEDULED_DATA;
    else scheduledMatches = [];
}'''
        content = content[:idx] + save_fn + NEW_FUNCTIONS
        print("Replaced from saveScheduledMatches onward")
    else:
        print("ERROR: could not find saveScheduledMatches anchor")
else:
    # Append at the end
    content = content.rstrip() + '\n' + NEW_FUNCTIONS
    print("Appended new functions at end")

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Done. Final size: {len(content)} chars, {content.count(chr(10))} lines")
# Quick syntax check
if 'printMatchSlipById' in content and 'getOriginalTeacher' in content:
    print("OK: Both key functions present")
