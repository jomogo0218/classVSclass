# 🛡️ ClassVSClass 修改守則 — 每次動手前必讀

> **⚠️ 強制規定：每次修改程式碼之前，必須通過本文件所有檢查點。**
> 本文件紀錄所有在開發過程中實際犯過的錯誤，絕對不能重蹈覆轍。

---

## 🚨 第一關：動手前確認清單（每次必做）

修改前在心裡逐項打勾：

- [ ] 我知道我要改的是哪個檔案（`app.js` / `app.css` / `index.html` 擇一，不是三個一起亂改）
- [ ] 我不會把不相關的程式碼刪掉
- [ ] 我不會截斷任何檔案（不能只寫前半段）
- [ ] 我知道這個函數是否在 HTML 裡有被呼叫
- [ ] 我沒有重複呼叫 `init()`
- [ ] **我確認不使用 PowerShell 來處理含中文的 JS 檔案**（見錯誤 #10）
- [ ] **修改完成後，我會用 `python scratch/guaranteed_build.py` 重新打包，不手動改 `index_local.html`**

---

## 🔴 已犯過的錯誤（絕對禁止重蹈）

### 【錯誤 #1】CSS 路徑寫錯
- **發生情況**：`index.html` 的 `<link>` 寫的是 `index.css`，但實際檔案是 `app.css`
- **後果**：整個介面全白，無任何樣式
- **規則**：**修改 HTML 前，先確認 CSS 檔案名稱是 `app.css`，link 路徑必須是 `app.css`**

```html
<!-- ✅ 正確 -->
<link rel="stylesheet" href="app.css">

<!-- ❌ 錯誤 — 檔案根本不存在 -->
<link rel="stylesheet" href="index.css">
```

---

### 【錯誤 #2】刪掉全域常數 `DAYS`
- **發生情況**：重構時誤刪 `const DAYS = [...]` 定義
- **後果**：`ReferenceError: DAYS is not defined`，整個程式停止運作
- **規則**：**重構 `app.js` 時，頂部的常數區塊絕對不能碰：`DAYS`、`PERIODS`、`SPORTS`、`VENUES` 等**

---

### 【錯誤 #3】HTML 被截斷（只寫了上半部）
- **發生情況**：重寫 `index.html` 時只輸出了前 133 行，下半部按鈕全部消失
- **後果**：所有 Tab 按鈕、清除按鈕、篩選器全部點不了
- **規則**：**每次重寫 HTML，必須確保從 `<!DOCTYPE html>` 到 `</html>` 完整輸出，不能分批**

---

### 【錯誤 #4】刪掉 `clearAllSchedules()` 函數
- **發生情況**：重構時誤刪此函數，但 HTML 的清除按鈕還在呼叫它
- **後果**：按清除按鈕沒有反應（靜默失敗）
- **規則**：**刪除任何函數前，先用 Ctrl+F 搜尋 HTML 和 JS 裡是否有人在呼叫它**

---

### 【錯誤 #5】`init()` 被呼叫兩次
- **發生情況**：`DOMContentLoaded` 裡呼叫了一次 `init()`，檔案結尾又呼叫了一次
- **後果**：資料競爭（Race Condition），Firestore 資料被覆寫或讀取兩次
- **規則**：**`init()` 只能在 `DOMContentLoaded` 事件裡呼叫一次，檔案末尾不得再次呼叫**

```javascript
// ✅ 正確 — 只在這裡呼叫
document.addEventListener('DOMContentLoaded', init);

// ❌ 錯誤 — 不能在檔案末尾再呼叫
init(); // 刪掉這行！
```

---

### 【錯誤 #6】HTML 重構時遺失元素 ID
- **發生情況**：重構 `index.html` 時，`id="sidebarToggle"` 按鈕被遺忘沒有放進去
- **後果**：`setupMobileSidebar()` 報錯 `TypeError: Cannot set properties of null`
- **規則**：**重構 HTML 前，先確認所有 JS 裡用到的 getElementById / querySelector ID 都存在於新 HTML**

必須存在的 ID（截至最新版）：
- `#sidebarToggle`（隱藏的漢堡按鈕）
- `#scheduleTable`
- `#matchList`
- `#weekDisplay`
- `#currentWeek`
- `#btnSnapshot`（列印通知單按鈕，位於成績編輯 Modal 內）
- `#matchModal`
- `#modalTeamA` / `#modalTeamB`
- `#inputScoreA` / `#inputScoreB`
- `#modalStatus`

---

### 【錯誤 #7】賽程顯示缺少任課老師
- **發生情況**：`renderSchedulingTable` 中 `raw.split('|')` 只取了科目，沒取到老師欄位
- **後果**：格子只顯示科目名稱，任課老師消失
- **規則**：**課表格子的資料格式是 `科目|老師`，split 後兩個欄位都要用**

```javascript
// ✅ 正確
const [subject, teacher] = raw.split('|');
cell.innerHTML = `${subject}<br><small>${teacher}</small>`;

// ❌ 錯誤
const subject = raw.split('|')[0]; // 老師不見了
```

---

### 【錯誤 #8 & #9】幽靈排程（指向不存在 matchId）
- **發生情況**：Firestore 中有排程記錄，但對應的比賽 ID 在 `matches.json` 中不存在
- **後果**：待排清單出現重複場次，或出現「未知」比賽名稱
- **規則**：
  1. `init()` 啟動時必須自動掃描並刪除幽靈排程
  2. 每次新增排程前，先驗證 matchId 是否存在

---

### 【錯誤 #10】⚠️ 使用 PowerShell 操作含中文的 JS 檔案導致永久亂碼
- **發生情況（2026-04-27）**：使用 `Get-Content` 合併 `app.js`，PowerShell 預設以 CP950 (Big5) 讀取 UTF-8 中文字元
- **後果**：整個 `app.js` 的中文字元全部變成亂碼（`蝛拙??扯??脩戌?` 等），且無法逆轉。所有 Git commits 也因此受污染。最終必須從 Git 還原基底再用 Python 重新注入功能。
- **規則**：
  - ❌ **絕對禁止**使用 PowerShell 的 `Get-Content` / `Out-File` / `>>` 來讀寫 `app.js`
  - ❌ **絕對禁止**使用 PowerShell pipe（`|`）傳遞含中文的 JS 內容
  - ✅ **所有對 `app.js` 的批次操作，必須用 Python 腳本，並明確指定 `encoding='utf-8'`**

```powershell
# ❌ 致命錯誤 — 會永久破壞中文字元
Get-Content app.js | ... | Set-Content app_new.js
git show HEAD:app.js | Out-File app.js -Encoding utf8

# ✅ 正確做法
python scratch/patch_appjs.py
```

---

### 【錯誤 #11】用 `replace_file_content` 替換含有模板字串 (`${}`) 的大段程式碼
- **發生情況（2026-04-27）**：嘗試用工具替換整個 `printMatchSlipById` 函數，目標字串對不上（因有特殊字元），導致多次失敗，且每次失敗都部分破壞了檔案
- **後果**：函數內出現孤立的語法片段，`app.js` 無法執行
- **規則**：
  - 整個大函數的替換（>30 行），應改用 **Python 腳本操作**，而非工具的文字替換
  - 替換前必須先 `view_file` 確認目標內容**一字不差**地存在

---

### 【錯誤 #12】`guaranteed_build.py` 的過濾邏輯誤刪外部 CDN 連結
- **發生情況**：構建腳本的 `rel="stylesheet"` 過濾條件把 FontAwesome CDN 的 `<link>` 也一起刪掉
- **後果**：`index_local.html` 載入後找不到圖示，所有 `<i class="fas fa-*">` 變成空白
- **規則**：`guaranteed_build.py` 的過濾只能針對本地 `app.css`，不能用 `rel="stylesheet"` 作為通用篩選條件

```python
# ❌ 錯誤 — 會連 CDN 連結都刪掉
if 'rel="stylesheet"' in line:
    continue

# ✅ 正確 — 只刪本地 css
if 'href="app.css' in line:
    continue
```

---

### 【錯誤 #13】賽事班級名稱帶有選手名稱，導致課表比對失敗
- **發生情況**：比賽資料的 `teamA` 是 `"高二仁 蘇愛甯"`，但課表 key 是 `"高二仁"`，精確比對失敗
- **後果**：`getOriginalTeacher()` 永遠回傳 `"無課"`，借課通知單無法顯示原任課老師
- **規則**：`getOriginalTeacher()` 必須使用**模糊前綴比對**，而非精確比對

```javascript
// ✅ 正確 — 模糊比對
const actualKey = Object.keys(scheduleData.schedules).find(k => {
    const kClean = k.replace(/\s/g, '');
    return targetKey.startsWith(kClean) || kClean.startsWith(targetKey);
}) || className;

// ❌ 錯誤 — 精確比對會找不到
const actualKey = Object.keys(scheduleData.schedules)
    .find(k => k.replace(/\s/g, '') === targetKey);
```

---

## 🟡 UI 設計規範（不得推翻）

### 現行設計：Google Calendar 極簡風（第三版）

| 項目 | 規格 |
|------|------|
| 字型 | Roboto + Noto Sans TC |
| 背景色 | `#f8f9fa` |
| 主邊框 | `#dadce0` |
| 主色 | `#1a73e8` |
| 格子狀態 | 橘/綠/黃 淡彩（不刺眼） |
| 週次按鈕 | 36×36px 圓形，今天=藍底白字膠囊 |

> **⛔ 禁止**：深色背景、科幻風、霓虹發光風（第一版被否決）

---

## 🟠 Firestore 操作規範

1. 寫入前驗證 matchId 存在
2. 禁止未經確認大量刪除文件
3. 有問題先用「🔍 診斷」按鈕查，不要直接改資料
4. `init()` 必須包含幽靈排程自動清理邏輯

---

## 🟢 檔案結構與修改流程

```
d:\classVSclass\
├── index.html              ← CSS link 必須指向 app.css
├── app.css                 ← 唯一有效的 CSS 檔
├── app.js                  ← 唯一合法的修改對象（用 Python 操作）
├── schedules.json          ← 課表資料（格式：班級 > 星期 > 節次 > 科目|老師）
├── matches.json            ← 比賽資料（ID 不可重複）
├── scratch/
│   ├── guaranteed_build.py ← 唯一合法的打包方式
│   └── patch_appjs.py      ← 安全注入新函數的範本腳本
└── index_local.html        ← ⛔ 禁止直接修改！由 guaranteed_build.py 自動生成
```

### 正確的修改流程（三步驟，缺一不可）：

```
1. 修改 app.js（或 app.css / index.html）
         ↓
2. python scratch/guaranteed_build.py
         ↓
3. 開啟 index_local.html 驗證（按 F5 強制重整）
```

---

## 🔵 借課通知單系統規範

### 函數說明：
- `printMatchSlipById(matchId)` — 從比賽 ID 查詢所有資訊並列印 A5 橫式通知單
- `printMatchSlip()` — 從 Modal 的 `currentEditingMatchId` 呼叫上面的函數
- `getOriginalTeacher(className, dayIdx, periodIdx)` — 返回格式 `"科目 / 老師姓名"`

### 通知單規格：
- 紙張：**A5 橫式（landscape）**
- 包含：比賽項目、對戰班級（含原任課資訊）、時間（日期+星期+節次+精確時間）
- **兩個任課老師簽名欄**，格式：`課程名稱 — 老師姓名 老師：____`
- 行政簽核：承辦人、體衛組長、學務主任

### 關鍵限制：
- 列印按鈕（`#btnSnapshot`）只在比賽**已排程**後才顯示（`display: block`）
- 所有字串常數必須使用 Unicode escape（`\uXXXX`）寫入 Python 腳本，避免編碼問題

---

## 📋 修改後檢查清單

- [ ] `node --check app.js` 語法驗證通過（無報錯）
- [ ] `python scratch/guaranteed_build.py` 成功執行（輸出 "Success!"）
- [ ] 瀏覽器開啟 `index_local.html`，Console 無 `ReferenceError` / `TypeError`
- [ ] 所有 Tab 能正常切換
- [ ] 比賽清單能正常載入
- [ ] 課表格子顯示「科目 + 老師」
- [ ] 列印按鈕對已排程比賽正常運作

---

## 📌 版本狀態（最後更新：2026-04-27）

| 項目 | 數量 |
|------|------|
| 總賽事數 | 91 場（依實際資料為準）|
| 已排定 | 依 Firestore 即時同步 |
| 幽靈排程 | 0 筆（init 自動清除）|
| 重複 ID | 0 筆 |
| 已記錄錯誤 | 13 種 |

---

## ⚡ 快速恢復程序（當 app.js 損壞時）

```bash
# 步驟 1：從 git 還原基底（必須用 git，不能用 PowerShell 複製）
git checkout f133361 -- app.js

# 步驟 2：用 Python 安全注入新功能（範本在 scratch/patch_appjs.py）
python scratch/patch_appjs.py

# 步驟 3：語法檢查
node --check app.js

# 步驟 4：重新打包
python scratch/guaranteed_build.py
```

> ⚠️ **如果 git 版本也是亂碼**（Big5 儲存問題），從 `index_local.html` 萃取：
> ```python
> # 用 scratch/extract_app.py 從 HTML 中萃取 JS 邏輯區塊
> python scratch/extract_app.py
> ```

---

*每次新增錯誤，請在對應位置補充說明並更新底部版本狀態日期。*
