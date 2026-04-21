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

## 🟢 檔案結構

```
d:\classVSclass\
├── index.html          ← CSS link 必須指向 app.css
├── app.css             ← 唯一有效的 CSS 檔
├── app.js              ← init 只呼叫一次
├── firebase-config.js  ← 不要動
├── matches.json        ← ID 不可重複
├── schedule_data.json  ← 課表資料
└── CHANGELOG.md        ← 每次改動都要記錄
```

> **`style_v4.css` 和 `app_v4.js`** 是舊版備份，不要載入，不要當作範本。

---

## 📋 修改後檢查清單

- [ ] 介面正常顯示（不是全白、不是報錯）
- [ ] Console 無 `ReferenceError` 或 `TypeError`
- [ ] 所有 Tab 能正常切換
- [ ] 比賽清單能正常載入
- [ ] 課表格子顯示「科目 + 老師」
- [ ] 在 `CHANGELOG.md` 記錄這次改了什麼

---

## 📌 版本狀態（最後更新：2026-04-21）

| 項目 | 數量 |
|------|------|
| 總賽事數 | 106 場 |
| 已排定 | 57 場 |
| 幽靈排程 | 0 筆（已清除）|
| 重複 ID | 0 筆 |

---

*每次新增錯誤，請更新本文件並在底部的版本狀態更新日期。*
