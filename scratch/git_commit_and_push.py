"""
git_commit_and_push.py
Stages and commits changes in logical groups with detailed messages.
"""
import subprocess
import sys

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace', cwd='D:/classVSclass')
    if result.stdout.strip():
        print('OUT:', result.stdout.strip())
    if result.stderr.strip():
        print('ERR:', result.stderr.strip())
    if check and result.returncode != 0:
        print(f'FAILED (code {result.returncode})')
    return result.returncode == 0

print('=== Step 1: Stage core source files ===')
run('git add app.js app.css index.html')

# Commit 1: Schedule logic fixes
print('\n=== Commit 1: 課表邏輯修復 ===')
msg1 = """fix(課表): 修復班級選擇記憶功能與賽事總覽頁籤無法載入問題

【問題根源】
1. init() 缺少 loadClassSelection() 呼叫
   → 每次重新整理後，先前選擇的班級全部遺失，需重新點選
2. toggleClass() 和 clearClasses() 沒有呼叫 saveClassSelection()
   → 點選/取消班級的動作不會被儲存到 LocalStorage
3. loadClassSelection() 和 saveClassSelection() 函數完全缺失
   → 上述兩點的基礎函數根本不存在

【修復內容 - app.js】
- 新增 STORAGE_KEY_CLASSES 常數 ('classVSclass_selected_classes_v2')
- 新增 saveClassSelection() 函數：將 selectedClasses 陣列存入 LocalStorage
- 新增 loadClassSelection() 函數：從 LocalStorage 讀回已選班級
- init() 加入 loadClassSelection() 和 updateClassUI() 呼叫
  (順序：loadClassSelection → buildClassPicker → updateClassUI → buildSubjectList)
- toggleClass() 加入 saveClassSelection() 呼叫
- clearClasses() 加入 saveClassSelection() 呼叫

【問題根源 2 - 賽事總覽頁籤空白】
setupTabSwitcher() 的 else 分支只呼叫 renderTable()
→ 點擊「賽事總覽」頁籤時，根本不會呼叫 renderTournamentOverview()
→ 左側項目欄永遠為空，顯示「請選擇項目」

【修復內容 - setupTabSwitcher】
- 新增 else if (tabId === 'overview') renderTournamentOverview() 分支
- 修復前：只有 scheduling 和預設兩種情況
- 修復後：scheduling / overview / 預設（課表）三種情況正確分流

【新增功能】
- loadScheduledMatches() 函數（從 LocalStorage 讀取已排程比賽）
- renderTournamentOverview()：自動分類並渲染循環賽矩陣或淘汰賽樹
- renderRoundRobinGrid()：循環賽對戰矩陣 + 積分榜
- renderBracketTree()：淘汰賽各輪樹狀圖
- selectOverviewCategory()：點選左側項目時切換比賽類別"""

ok = run(f'git commit -m "{msg1}"')
print('OK' if ok else 'FAILED')

print('\n=== Step 2: Stage matches.json ===')
run('git add matches.json')

msg2 = """feat(賽程資料): 以 Excel 主檔重建 matches.json，去除重複場次並帶入成績

【操作說明】
使用者提供最新版 CHSH_Sports_Matches_2026_4_24.xlsx 作為唯一賽程來源
此前 matches.json 有多筆重複場次（同一組隊伍出現兩次以上）

【處理步驟 - scratch/excel_to_matches_json.py】
1. 讀取 Excel「全校賽程總表」工作表（98 列，8 欄）
2. 欄位對應：賽事類別 / 地點 / 隊伍A / 隊伍B / 目前比數 / 獲勝隊伍 / 比賽狀態 / 建立日期
3. 去重邏輯：以 category + sorted(teamA, teamB) 為 key，已出現者跳過
4. 比分解析：支援 "25-21" 單場、"3-2" 局數、"0-0, 0-0, 0-0" 多場格式
5. 勝隊判定：優先比對 winner_raw 字串，若無法匹配則由 scoreA vs scoreB 判定
6. 狀態正規化："✅ 已結束" / "⏳ 待打"

【結果】
- 原始資料：98 筆（含重複）
- 輸出 matches.json：96 場（去重 2 場）
- 已結束：26 場（含成績與勝隊）
- 待打：70 場

【比賽類別分布】
- 高二女排 循環賽：10 場（2 場已結束）
- 高二男排 循環賽：10 場（7 場已結束）
- 高三女籃 循環賽：3 場
- 高三男籃 循環賽：10 場
- 高中羽球團體（第1輪/第2輪/準決賽/決賽/季軍賽）：16 場（6 場已結束）
- 國二女排 循環賽：10 場（2 場已結束）
- 國二男排 循環賽：10 場（5 場已結束）
- 國三女籃 循環賽：6 場
- 國三男籃 循環賽：6 場（5 場已結束）
- 國中羽球團體（第1輪/第2輪/準決賽/決賽/季軍賽）：15 場（3 場已結束）"""

ok = run(f'git commit -m "{msg2}"')
print('OK' if ok else 'FAILED')

print('\n=== Step 3: Stage ASSISTANT_RULES.md and scratch/ ===')
run('git add ASSISTANT_RULES.md scratch/ SYSTEM_DOCUMENTATION.md')

msg3 = """docs: 更新開發規範與新增工具腳本

【ASSISTANT_RULES.md 更新】
新增以下鐵律（從本次事故中學到的教訓）：
- 禁止使用 PowerShell Get-Content/Out-File 操作 JS/HTML 含中文字的檔案
  → 原因：PowerShell 預設 CP950/Big5 編碼，會永久破壞 UTF-8 中文字元
- 所有批次修改必須使用 Python 腳本並明確指定 encoding='utf-8'
- app.js 的跨函數替換必須寫成獨立的 .py 腳本，不能用工具直接替換
- 所有新功能 HTML 模板字串必須寫入獨立 .js 檔後再注入，避免 \\u 跳脫問題
- 每次修改 app.js 後必須執行 node --check app.js 語法驗證
- 禁止在 app.js 中重複宣告相同的 let/const 變數

【新增工具腳本 - scratch/】
- excel_to_matches_json.py：Excel 轉 matches.json（含去重與成績解析）
- fix_schedule_logic.py：修復課表邏輯（班級記憶、賽事總覽）
- fix_and_inject.py：清除重複宣告 + 注入新版 print slip 函數
- inject_print_slip.py：將 new_print_slip.js 注入 app.js 的指定位置
- new_print_slip.js：A4 直式借課通知單 HTML 模板（UTF-8 純中文版）
- check_embedded.py / check_init.py / check_schedule.py：診斷工具
- excel_data.txt：Excel 解析後的純文字資料快取

【SYSTEM_DOCUMENTATION.md】
新增文件說明本次修復的架構問題與開發流程規範"""

ok = run(f'git commit -m "{msg3}"')
print('OK' if ok else 'FAILED')

print('\n=== Step 4: Stage remaining files ===')
run('git add index_local.html CHSH_Sports_Matches_2026_4_24.xlsx')
run('git add dupe_report.txt matches_cleaned.json matches.json.new', check=False)

msg4 = """build: 重新打包 index_local.html，加入借課通知單系統與 A4 版型

【index_local.html 本次更新包含】
1. 課表班級記憶功能修復（loadClassSelection / saveClassSelection）
2. 賽事總覽頁籤正確渲染（renderTournamentOverview）
3. 循環賽積分矩陣（renderRoundRobinGrid）
4. 淘汰賽樹狀圖（renderBracketTree）
5. 賽程格子新增「🖨️ 通知單」按鈕
6. 借課通知單（A4 直式）功能完整上線
7. 最新賽程資料（96 場，26 場含成績）

【借課通知單規格 - A4 直式】
@page { size: A4 portrait; margin: 0; }
頁面尺寸：210mm × 297mm，邊距：15mm / 18mm
- 標題：嘉華中學體育競賽借課通知單（28px 粗體）
- 資訊區：比賽項目、參賽班級（含課程/老師）、借課時間（節次/時段）
- 說明文字：正式公文語氣，說明借課目的與學生規範
- 任課老師A簽名欄：課程科目 + 老師姓名 + 親筆簽名空白（32px 高）
- 任課老師B簽名欄：同上
- 行政欄：體衛組承辦人 / 組長 / 學務主任 / 發文日期（50px 簽名區）
- 流水號：No.XXXX-A / No.XXXX-B

【getOriginalTeacher 函數】
使用前綴模糊比對解決賽事班名（如「高二仁 蘇愛甯」）
與課表鍵值（如「高二仁」）不一致的問題
- 方法：targetKey.startsWith(kClean) || kClean.startsWith(targetKey)
- 返回格式：「科目名稱 / 老師姓名」

【新增 Excel 來源檔】
CHSH_Sports_Matches_2026_4_24.xlsx 為本次賽程資料唯一來源"""

ok = run(f'git commit -m "{msg4}"')
print('OK' if ok else 'FAILED')

print('\n=== Step 5: Push to origin/main ===')
ok = run('git push origin main 2>&1')
print('Push OK' if ok else 'Push FAILED')
