# 系統修改日誌 (2026-04-22 救援行動)

這份文件記錄了為了解決「賽道消失」、「白畫面」與「雲端刪除報錯」所做出的所有系統重大變更。您可以隨時參考此文件回顧我們做了什麼。

## 🛠️ 重大修改項目

### 1. 斷開雲端同步 (轉向全單機操作)
*   **修改檔案**：`index.html`, `app.js`
*   **修改內容**：
    *   在 `index.html` 移除了所有 Firebase (雲端資料庫) 的載入腳本。
    *   在 `app.js` 移除了 `deleteMatch` 與 `loadMatches` 裡的雲端同步邏輯。
*   **用途 / 何時回復**：為了避免網路延遲與伺服器互相覆蓋導致「載入中」畫面卡死。若未來想要將排程功能重新放上網路多人協作，請參考這份日誌重新加回 Firebase 腳本。

### 2. 生成終極單機版 (index_local.html)
*   **新增檔案**：`mega_build.py` (編譯腳本), `index_local.html` (生成結果)
*   **修改內容**：
    *   寫了一支 Python 腳本 `mega_build.py`。
    *   這支腳本負責把 106 場比賽 (`matches.json`)、學校課表 (`schedules.json`)、排程紀錄、樣式 (`app.css`) 與腳本 (`app.js`) **全部揉合** 成一個單一檔案：`index_local.html`。
*   **用途 / 何時回復**：因為瀏覽器直接開啟 HTML 檔案會因為安全限制（CORS）無法讀取本地的其他檔案，這個單一檔案是「隨開即用」的保證。如果您不使用了，保留原本的 `.js` 和 `.css` 開發依然是好的。

### 3. 恢復 106 場賽事與排程進度
*   **修改內容**：
    *   原本為了解決重複賽程，我移除了 `matches.json` 中的 25 筆重複賽程。**（已因您的要求使用 Git 指令 `git restore matches.json` 完全復原回 106 場）**。
    *   在 `mega_build.py` 中寫死了您之前排好的 64 場歷史進度，確保每次產生 HTML 時，原本的排表心血都不會白費。
*   **用途 / 何時回復**：保障資料庫完整性。若您後來反悔、想再使用我寫好的清理邏輯，可以在終端機輸入：`python -c "import json; f=open('matches.json','r',encoding='utf-8'); m=json.load(f); unique={tuple(sorted([x.get('category','').replace(' ',''), x.get('teamA','').replace(' ',''), x.get('teamB','').replace(' ','')])):x for x in m}.values(); json.dump(list(unique), open('matches.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)"`。

## 💾 備份與還原提示
由於目前整個專案（包含賽程與檔案）都位於您的電腦中：
1. **程式碼備份**：如果您覺得現在的這個 `index_local.html` 加上所有的 `.js` 檔案非常完美，建議您可以將整個資料夾（`d:\classVSclass\`）複製並壓縮為 `classVSclass_backup_0422.zip` 留存。
2. **賽程備份**：即使是現在的單機版 HTML，您在上面排好的所有比賽也都存在瀏覽器的 `LocalStorage` 裡。若要清空，只需要在瀏覽器清除站台資料即可。
