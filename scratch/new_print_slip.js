function getOriginalTeacher(className, dayIdx, periodIdx) {
    if (!scheduleData || !scheduleData.schedules) return '資料缺失';
    const targetKey = className.replace(/\s/g, '');
    const actualKey = Object.keys(scheduleData.schedules).find(k => {
        const kClean = k.replace(/\s/g, '');
        return targetKey.startsWith(kClean) || kClean.startsWith(targetKey);
    }) || className;
    const dayKey = ['Mon','Tue','Wed','Thu','Fri'][dayIdx];
    if (!dayKey) return '日期錯誤';
    const classSched = scheduleData.schedules[actualKey];
    if (!classSched || !classSched[dayKey]) return '無課';
    const raw = (classSched[dayKey][periodIdx] || '').trim();
    if (!raw || raw === '---') return '無課';
    const parts = raw.split('|');
    return (parts[0] || '未命名').trim() + ' / ' + (parts[1] || '未知老師').trim();
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
