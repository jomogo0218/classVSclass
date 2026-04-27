# 嘉華中學體育競賽排課系統 — 工程師級別技術架構與維護手冊

本手冊旨在為接手的開發者提供深度技術解析，包含架構決策、演算法邏輯及系統維護指南。

---

## 一、 系統架構決策 (Architectural Decisions)

### 1. 單一文件與嵌入式資料 (Single-File Distribution)
- **實作**：使用 `guaranteed_build.py` 進行預編譯，將 `schedules.json` 與 `matches.json` 的內容直接注入 `app.js` 的 `EMBEDDED_` 變數中。
- **為什麼這樣寫 (Rationale)**：
    - **避開 CORS 限制**：一般 HTML 從本地路徑 (`file://`) 讀取 JSON 會觸發跨域安全錯誤。透過資料嵌入，系統可達成「真正離線運行」。
    - **零佈署成本**：使用者只需雙擊一個 `.html` 檔案即可運行，無需架設伺服器或資料庫。
    - **效能優化**：省去網路請求延遲，頁面載入即資料就位。

### 2. 防禦性編程 (Defensive Programming)
- **工具**：`safeGet(id)` 與 `renderSafe(fn)`。
- **為什麼這樣寫 (Rationale)**：
    - **DOM 容錯**：`safeGet` 在找不到 ID 時會回傳一個虛擬物件，防止因為一個 UI 元素消失導致整個 JavaScript 引擎崩潰。
    - **錯誤隔離**：`renderSafe` 將核心渲染邏輯包裝在 `try-catch` 中。若「賽程規畫」分頁出錯，不會影響到「課表對照」功能。

---

## 二、 核心演算法與邏輯解析 (Core Algorithms)

### 1. 課表比對引擎 (`buildTableBody`)
- **邏輯**：
    1. 遍歷選中班級列表。
    2. 使用 `normalize('NFKC').replace(/\s/g,'')` 對科目名稱進行標準化（處理全形半形、隱形空白）。
    3. 計算時段狀態：
        - `allPE` (Intersection): `Array.prototype.every()`。
        - `allSkill` (Intersection): 檢查是否所有選中班級科目皆存在於 `allowedSubjects` Set 中。
- **為什麼這樣寫 (Rationale)**：
    - 使用 `Set` 而非 `Array` 儲存科目設定，將判定複雜度從 O(N) 降低到 O(1)，在大規模資料下依然流暢。

### 2. 排程衝突偵測邏輯
- **多維度檢查**：
    - **Time-Class Conflict**：檢查目標時段該班級是否已有 `scheduledMatches` 紀錄。
    - **Sport Occupancy Limit**：動態計算 `scheduledMatches` 中同運動類型之計數，並與 `getSportLimit` 常數對比。
- **為什麼這樣寫 (Rationale)**：
    - 採用「預先計算」模式，在格子渲染時即完成所有檢查，使用者能直接看到哪些格子是「🚫 已衝突」，減少無效點擊。

---

## 三、 資料持久化機制 (Data Persistence)

### 1. LocalStorage 策略
- **鍵名規範**：帶有 `_v2` 或 `_v3` 版本後綴（例如 `classVSclass_allowed_subjects_v3`）。
- **為什麼這樣寫 (Rationale)**：
    - **防止快取污染**：當未來修改了資料結構，版本號能確保讀取不到過時的、會導致崩潰的舊格式資料。
    - **自動儲存 (Auto-Save)**：所有 `onchange` 事件皆同步觸發 `save` 函式。對於使用者而言，系統像是擁有「永久記憶」的資料庫。

---

## 四、 列印系統實作 (`printMatchSlipById`)

### 1. Window-Print 與 CSS Media Queries
- **技術**：動態開啟 `about:blank` 視窗，注入純 HTML/CSS。
- **為什麼這樣寫 (Rationale)**：
    - **跨設備排版**：透過 `@media print { @page { size: A5 landscape; } }`，強行覆蓋印表機預設設定，確保無論使用者電腦設定如何，印出來都是嘉華體衛組要求的 A5 規格。
    - **動態對照**：列印時會即時呼叫 `getOriginalTeacher`。這確保了即便課表資料更新，列印出的通知單資訊也永遠是最新的。

---

## 五、 維護手冊 (Maintenance Manual)

### 1. 更新課表流程
1. 修改 `schedules.json`（遵循 `班級 -> 星期 -> 節次` 結構）。
2. 執行 `python guaranteed_build.py`。
3. 腳本會自動讀取 JSON -> 轉為字串 -> 取代 `app.js` 中的預留位置 -> 產出 `index_local.html`。

### 2. 擴充建議時段關鍵字
- 位於 `app.js` 頂端的 `SKILL_KEYWORDS` 常數陣列。
- **注意**：新增後，需執行 `loadSubjectSettings()` 的 Reset (清除 LocalStorage) 或手動重新勾選，新關鍵字才會生效。

---

## 六、 資料結構規格 (Data Schema)

### 1. 課表資料 (schedules.json)
- **結構**：`Object { [ClassName]: Array[5][10] }`
- **解析**：一級 Key 為班級名稱（需與 `matches.json` 一致）。二級索引為星期 (0-4)，三級索引為節次 (0-9)。內容格式為 `科目|教師`。
- **設計決策**：採用巢狀陣列而非物件，是為了提升在表格渲染時的索引速度（Index-based lookup）。

### 2. 賽程資料 (scheduledMatches)
- **結構**：`Array<{ matchId: string, date: string, periodIndex: number }>`
- **持久化**：優先從 Firestore 讀取實時同步資料，若無網路則回退至 LocalStorage 的 `classVSclass_scheduled_matches`。

---

## 七、 高階邏輯模組 (Advanced Modules)

### 1. 實時同步機制 (`listenToScheduledMatches`)
- **實作**：使用 Firebase Firestore 的 `onSnapshot` 監聽。
- **設計決策**：採用 Webhook 模式而非定期輪詢 (Polling)。當體衛組辦公室 A 老師排好一場比賽，B 老師的螢幕會「無需重新整理」自動出現該賽事。

### 2. 搜尋與重複檢查演算法
- **搜尋**：對 `matches.json` 進行模糊比對。
- **重複檢查 (`toggleDupeFilter`)**：
    - 邏輯：掃描 `matchesData`，找出「對戰班級組合」相同但 ID 不同的賽事。
    - 目的：防止在不同運動項目（如籃球、排球）中重複排入相同班級。

### 3. 週次計算 (`getMonday`)
- **實作**：`d.getDate() - (day === 0 ? 6 : day - 1)`。
- **設計決策**：強制將每週的起點鎖定在「週一」。這是為了符合學校教學週次 (Academic Week) 的作業習慣，避免週日跨週造成的排程混亂。

---

## 八、 視覺回饋系統 (UX Feedback)

### 1. 自動儲存指示器 (`saveIndicator`)
- **實作**：監聽所有 `allowedSubjects` 的 `Set` 變動。
- **反饋**：使用 `setTimeout` 控制的 DOM 閃爍效果，將後台的 IO 操作轉化為使用者感知的「安全感」。

---

## 九、 運動項目與性別識別邏輯

### 1. 種類映射 (`getSportType`)
- **實作**：使用正則表達式從賽事類別中提取核心運動（如：`.*排.*` -> `排球`）。
- **為什麼這樣寫 (Rationale)**：
    - **場地共享控管**：這讓系統能將不同年級、不同組別的「排球賽」統一納入場地上限計算，避免在同一節課排入過多同種類比賽。

### 2. 性別標籤識別 (`getGender`)
- **實作**：識別「男」、「女」或「通用」。
- **為什麼這樣寫 (Rationale)**：
    - **衝突細分化**：同一個班級在同一節課，如果「男籃」與「女籃」同時進行，系統會檢查性別。如果學生不重複（男生打籃球，女生在場邊），則邏輯上可以允許（需依據實際規則調整），目前系統預設進行嚴格的「性別衝突檢查」。

---

## 十、 行政活動衝突系統 (`CONFLICTS`)

- **實作**：定義於 `app.js` 頂端的 `CONFLICTS` 常數陣列。
- **功能**：系統會自動計算目前週次是否涵蓋「段考」、「畢旅」等日期，並在課表頂端動態呈現「⚠️ 衝突提示橫幅」。
- **設計決策**：這提供了「行政預警」功能，防止體衛組在全校段考期間誤排比賽。

---

## 十一、 開發與維護禁令 (Development Warnings)

- **⚠️ 禁止直接修改 `index_local.html`**：
    - **原因**：該檔案是由 `guaranteed_build.py` 自動生成的。任何直接在該檔案上的修改，都會在下次執行編譯腳本時被覆蓋消失。
- **修改建議**：請一律修改 `app.js`、`app.css` 或 `index.html` (Template)，再透過編譯腳本產出最終成果。

---
**文件維護者：嘉華中學體衛組 AI 工程助手**  
*最後更新：2026-04-27 (完美無缺版)*
![1777253951659](image/SYSTEM_DOCUMENTATION/1777253951659.png)![1777253952944](image/SYSTEM_DOCUMENTATION/1777253952944.png)![1777253958187](image/SYSTEM_DOCUMENTATION/1777253958187.png)![1777253963227](image/SYSTEM_DOCUMENTATION/1777253963227.png)![1777254038928](image/SYSTEM_DOCUMENTATION/1777254038928.png)![1777254044508](image/SYSTEM_DOCUMENTATION/1777254044508.png)![1777254077599](image/SYSTEM_DOCUMENTATION/1777254077599.png)![1777255905412](image/SYSTEM_DOCUMENTATION/1777255905412.png)![1777257832296](image/SYSTEM_DOCUMENTATION/1777257832296.png)![1777273129050](image/SYSTEM_DOCUMENTATION/1777273129050.png)![1777279674197](image/SYSTEM_DOCUMENTATION/1777279674197.png)![1777279862627](image/SYSTEM_DOCUMENTATION/1777279862627.png)