"""
rewrite_print_slip.py
Replaces the printMatchSlipById function with a properly formatted,
respectful notification slip for teacher signatures.
All Chinese content is written directly as UTF-8 (no \uXXXX escapes).
"""

NEW_PRINT_FUNC = r"""
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
    const subj = (parts[0] || '未命名').trim();
    const teacher = (parts[1] || '未知老師').trim();
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

    const dateObj = new Date(scheduled.date + 'T00:00:00');
    const dayIdx  = (dateObj.getDay() + 6) % 7;
    const dayName = DNAMES[dayIdx] || '';
    const periodName = PNAMES[scheduled.periodIndex] || ('第' + scheduled.periodIndex + '節');
    const periodTime = PTIMES[scheduled.periodIndex] || '';

    // 取得任課老師資料
    const teacherRawA = getOriginalTeacher(match.teamA, dayIdx, scheduled.periodIndex);
    const teacherRawB = getOriginalTeacher(match.teamB, dayIdx, scheduled.periodIndex);

    const subjA  = teacherRawA.includes('/') ? teacherRawA.split('/')[0].trim() : '課程';
    const tNameA = teacherRawA.includes('/') ? teacherRawA.split('/')[1].trim() : '任課老師';
    const subjB  = teacherRawB.includes('/') ? teacherRawB.split('/')[0].trim() : '課程';
    const tNameB = teacherRawB.includes('/') ? teacherRawB.split('/')[1].trim() : '任課老師';

    const printWin = window.open('', '_blank');
    if (!printWin) { alert('請允許彈出視窗以列印'); return; }

    const html = `<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>借課通知單 — ${match.teamA} vs ${match.teamB}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  @page { size: A5 landscape; margin: 0; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: "Noto Sans TC", "Microsoft JhengHei", "PingFang TC", sans-serif;
    background: #fff; color: #111;
    width: 210mm; height: 148mm;
    padding: 10mm 12mm;
    display: flex; flex-direction: column;
    font-size: 13px;
  }

  /* ── 標題區 ── */
  .slip-header {
    text-align: center;
    border-bottom: 3px double #222;
    padding-bottom: 6px;
    margin-bottom: 10px;
  }
  .slip-title {
    font-size: 21px;
    font-weight: 900;
    letter-spacing: 3px;
    margin-bottom: 2px;
  }
  .slip-sub {
    font-size: 11px;
    color: #555;
    letter-spacing: 1px;
  }

  /* ── 資訊列 ── */
  .info-grid {
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 6px 4px;
    margin-bottom: 10px;
  }
  .info-label {
    font-weight: 700;
    color: #333;
    padding-top: 2px;
    white-space: nowrap;
  }
  .info-value {
    border-bottom: 1px solid #666;
    padding: 2px 6px 2px;
    line-height: 1.4;
  }
  .info-value.highlight {
    font-weight: 900;
    font-size: 16px;
    color: #1a1a8c;
    letter-spacing: 0.5px;
  }

  /* ── 說明文字 ── */
  .slip-notice {
    background: #fff8e8;
    border-left: 4px solid #e6a800;
    padding: 6px 10px;
    font-size: 11.5px;
    line-height: 1.7;
    margin-bottom: 10px;
    border-radius: 0 4px 4px 0;
  }
  .slip-notice strong { color: #b35c00; }

  /* ── 任課老師簽名欄 ── */
  .teacher-section-title {
    font-size: 11px;
    font-weight: 700;
    color: #444;
    letter-spacing: 1px;
    margin-bottom: 5px;
    text-align: center;
  }
  .teacher-boxes {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 10px;
  }
  .teacher-box {
    border: 1.5px solid #888;
    border-radius: 5px;
    padding: 8px 10px;
    background: #f9f9f9;
  }
  .teacher-box-header {
    font-size: 11px;
    font-weight: 900;
    color: #1a1a8c;
    border-bottom: 1px solid #ccc;
    padding-bottom: 4px;
    margin-bottom: 8px;
  }
  .teacher-course {
    font-size: 12px;
    color: #333;
    margin-bottom: 4px;
  }
  .teacher-course span { font-weight: 700; }
  .teacher-sig-label {
    font-size: 12px;
    color: #333;
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .sig-blank {
    flex: 1;
    border-bottom: 1.5px solid #333;
    height: 24px;
    display: inline-block;
    min-width: 80px;
  }

  /* ── 底部行政簽核 ── */
  .admin-row {
    display: flex;
    gap: 8px;
    margin-top: auto;
    padding-top: 6px;
    border-top: 2px solid #222;
  }
  .admin-box {
    flex: 1;
    text-align: center;
    padding-top: 4px;
    font-size: 12px;
    font-weight: 700;
    position: relative;
  }
  .admin-box::after {
    content: '';
    display: block;
    height: 28px;
    border-bottom: 1px solid #888;
    margin-top: 4px;
  }
  .serial-no {
    position: absolute;
    top: 0; right: 0;
    font-size: 10px;
    color: #aaa;
  }
</style>
</head>
<body>

  <div class="slip-header">
    <div class="slip-title">嘉華中學體育競賽借課通知單</div>
    <div class="slip-sub">本通知單由體衛組發出，請妥善保存並請相關老師確認簽名後交回</div>
  </div>

  <div class="info-grid">
    <div class="info-label">比賽項目：</div>
    <div class="info-value">${match.category}</div>

    <div class="info-label">參賽班級：</div>
    <div class="info-value">
      <strong>${match.teamA}</strong>
      &nbsp;（${teacherRawA}）
      &emsp;對&emsp;
      <strong>${match.teamB}</strong>
      &nbsp;（${teacherRawB}）
    </div>

    <div class="info-label">借課時間：</div>
    <div class="info-value highlight">
      ${scheduled.date}（${dayName}）${periodName}［${periodTime}］
    </div>
  </div>

  <div class="slip-notice">
    敬請 <strong>${match.teamA}</strong> 及 <strong>${match.teamB}</strong> 之任課老師惠予諒解，同意本節課暫借供體育競賽使用。<br>
    ✦ 參賽學生請<strong>準時</strong>至指定場地集合，不得無故缺席，並以正確禮儀服從競賽規範。<br>
    ✦ 本通知單須經兩位任課老師<strong>親筆簽名確認</strong>後，方具效力，請交回體衛組存查。
  </div>

  <div class="teacher-section-title">── 任課老師確認簽名欄（請務必親簽） ──</div>
  <div class="teacher-boxes">
    <div class="teacher-box">
      <div class="teacher-box-header">【${match.teamA}】任課老師</div>
      <div class="teacher-course">課程科目：<span>${subjA}</span></div>
      <div class="teacher-course">授課老師：<span>${tNameA} 老師</span></div>
      <div class="teacher-sig-label" style="margin-top:8px;">
        老師簽名：<span class="sig-blank"></span>
      </div>
    </div>
    <div class="teacher-box">
      <div class="teacher-box-header">【${match.teamB}】任課老師</div>
      <div class="teacher-course">課程科目：<span>${subjB}</span></div>
      <div class="teacher-course">授課老師：<span>${tNameB} 老師</span></div>
      <div class="teacher-sig-label" style="margin-top:8px;">
        老師簽名：<span class="sig-blank"></span>
      </div>
    </div>
  </div>

  <div class="admin-row">
    <div class="admin-box">體衛組承辦人<div class="serial-no">No.${String(matchId).slice(-4).padStart(4,'0')}</div></div>
    <div class="admin-box">體衛組長</div>
    <div class="admin-box">學務主任</div>
    <div class="admin-box">發文日期：&ensp;&ensp;月&ensp;&ensp;日</div>
  </div>

</body>
<script>
  window.onload = function() {
    window.print();
    setTimeout(function() { window.close(); }, 800);
  };
<\/script>
</html>`;

    printWin.document.write(html);
    printWin.document.close();
}
"""

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the entire section from getOriginalTeacher to end of printMatchSlipById
# Anchor: start of getOriginalTeacher (our added version)
START_ANCHOR = 'function getOriginalTeacher(className, dayIdx, periodIdx) {'
END_ANCHOR = '\nfunction openEditScoreModal'

start_idx = content.rfind(START_ANCHOR)
if start_idx < 0:
    # Try finding it differently
    start_idx = content.find('function getOriginalTeacher')
    print(f'Found getOriginalTeacher at {start_idx}')

end_idx = content.find(END_ANCHOR, start_idx)
if end_idx < 0:
    print('ERROR: Could not find end anchor')
    exit(1)

print(f'Replacing from {start_idx} to {end_idx}')
print(f'Old section length: {end_idx - start_idx} chars')

content = content[:start_idx] + NEW_PRINT_FUNC.strip() + '\n' + content[end_idx:]

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. Final: {len(content)} chars')

# Verify the Chinese is now in the file
if '請允許彈出視窗以列印' in content:
    print('OK: Chinese text is directly embedded')
else:
    print('WARNING: Chinese text not found - may still have unicode escapes')
