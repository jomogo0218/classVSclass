function printMatchSlipById(matchId) {
    const match = matchesData.find(m => String(m.id) === String(matchId));
    if (!match) {
        alert("找不到賽事資料！");
        return;
    }

    const scheduled = scheduledMatches.find(sm => String(sm.matchId) === String(matchId));
    if (!scheduled) {
        alert("此賽事尚未排定時間，無法列印通知單。");
        return;
    }

    const dateObj = parseISO(scheduled.date);
    const dayIdx = (dateObj.getDay() + 6) % 7; // 0=Mon
    const dayName = DAY_NAMES[dayIdx];
    const periodName = PERIOD_NAMES[scheduled.periodIndex];
    const periodTime = PERIOD_TIMES[scheduled.periodIndex];

    const teacherA = getOriginalTeacher(match.teamA, dayIdx, scheduled.periodIndex);
    const teacherB = getOriginalTeacher(match.teamB, dayIdx, scheduled.periodIndex);

    // 提取課程與老師姓名 (假設格式為 "科目 / 老師")
    const subjA = teacherA.includes('/') ? teacherA.split('/')[0].trim() : "課程";
    const subjB = teacherB.includes('/') ? teacherB.split('/')[0].trim() : "課程";
    const tNameA = teacherA.includes('/') ? teacherA.split('/')[1].trim() : "任課老師";
    const tNameB = teacherB.includes('/') ? teacherB.split('/')[1].trim() : "任課老師";

    const printWin = window.open('', '_blank');
    printWin.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>借課通知單 - ${match.teamA} vs ${match.teamB}</title>
            <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700;900&display=swap" rel="stylesheet">
            <style>
                @page { size: A5 landscape; margin: 0; }
                body { 
                    font-family: "Noto Sans TC", sans-serif; 
                    margin: 0; padding: 12mm; 
                    background: #fff; color: #000;
                    display: flex; justify-content: center; align-items: center;
                    height: 100vh; box-sizing: border-box;
                }
                .slip-card {
                    border: 4px double #000;
                    padding: 20px;
                    width: 100%; height: 100%;
                    box-sizing: border-box;
                    position: relative;
                    display: flex; flex-direction: column;
                }
                .header {
                    text-align: center;
                    border-bottom: 2px solid #000;
                    padding-bottom: 8px;
                    margin-bottom: 15px;
                }
                .header h1 { margin: 0; font-size: 26px; letter-spacing: 2px; font-weight: 900; }
                .header p { margin: 3px 0 0 0; font-size: 14px; font-weight: bold; }
                
                .main-content { flex: 1; font-size: 19px; line-height: 1.6; }
                .info-item { display: flex; margin-bottom: 12px; align-items: baseline; }
                .info-label { font-weight: 700; width: 110px; flex-shrink: 0; }
                .info-value { border-bottom: 1.5px solid #000; flex: 1; padding-left: 10px; }
                
                /* 任課老師簽名專區 */
                .teacher-signs {
                    display: flex;
                    justify-content: space-between;
                    gap: 20px;
                    margin-top: 25px;
                }
                .teacher-box {
                    flex: 1;
                    border: 1.5px dashed #333;
                    padding: 12px;
                    background: #fcfcfc;
                }
                .teacher-title { font-size: 14px; font-weight: 900; margin-bottom: 10px; color: #333; }
                .signature-line { border-bottom: 1px solid #000; height: 40px; display: flex; align-items: flex-end; padding-bottom: 2px; font-size: 16px; font-weight: bold; }

                .note { margin-top: 15px; font-size: 15px; font-weight: bold; font-style: italic; color: #d93025; }
                
                .footer-row {
                    margin-top: 40px;
                    display: flex;
                    justify-content: space-between;
                    font-size: 15px;
                    font-weight: bold;
                }
                .footer-box { border-top: 2px solid #000; width: 28%; text-align: center; padding-top: 5px; }
                
                .stamp {
                    position: absolute; right: 40px; bottom: 100px;
                    width: 90px; height: 90px;
                    border: 3px solid rgba(255,0,0,0.25);
                    border-radius: 50%;
                    color: rgba(255,0,0,0.25);
                    display: flex; align-items: center; justify-content: center;
                    font-size: 13px; font-weight: 900; text-align: center;
                    transform: rotate(-15deg);
                    pointer-events: none;
                }
            </style>
        </head>
        <body>
            <div class="slip-card">
                <div class="header">
                    <h1>嘉華中學體育競賽借課通知單</h1>
                    <p>【 公 告 聯 】</p>
                </div>
                <div class="main-content">
                    <div class="info-item">
                        <span class="info-label">比賽項目：</span>
                        <span class="info-value">${match.category}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">對戰班級：</span>
                        <span class="info-value">
                            ${match.teamA} <span style="font-size:0.8em">(${teacherA})</span> 
                            <span style="margin: 0 15px; font-weight:900;">vs</span> 
                            ${match.teamB} <span style="font-size:0.8em">(${teacherB})</span>
                        </span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">比賽時間：</span>
                        <span class="info-value" style="font-weight:900; font-size:1.1em;">
                            ${scheduled.date} (${dayName}) ${periodName} [${periodTime}]
                        </span>
                    </div>
                    <p class="note">※ 請上列班級之任課老師知悉，並請參賽學生準時至指定場地集合。</p>
                </div>

                <div class="teacher-signs">
                    <div class="teacher-box">
                        <div class="teacher-title">【${match.teamA}】任課老師確認簽名：</div>
                        <div class="signature-line">${subjA} — ${tNameA} 老師：____________________</div>
                    </div>
                    <div class="teacher-box">
                        <div class="teacher-title">【${match.teamB}】任課老師確認簽名：</div>
                        <div class="signature-line">${subjB} — ${tNameB} 老師：____________________</div>
                    </div>
                </div>

                <div class="footer-row">
                    <div class="footer-box">承辦人</div>
                    <div class="footer-box">體衛組長</div>
                    <div class="footer-box">學務主任</div>
                </div>
                
                <div class="stamp">嘉華中學<br>體衛組印</div>
            </div>
            <script>
                window.onload = function() {
                    window.print();
                    setTimeout(() => { window.close(); }, 500);
                };
            <\/script>
        </body>
        </html>
    `);
    printWin.document.close();
}

function printMatchSlip() {
    if (currentEditingMatchId) {
        printMatchSlipById(currentEditingMatchId);
    }
}

function exportSchedule() {
    window.print();
}
