import json
import re
import os

def build():
    # 讀取所有零件
    with open('matches.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    with open('schedules.json', 'r', encoding='utf-8') as f:
        schedules = json.load(f)
    with open('app.css', 'r', encoding='utf-8') as f:
        css = f.read()
    with open('app.js', 'r', encoding='utf-8') as f:
        js = f.read()
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. 注入 CSS (替換 link 標籤)
    css_tag = f'<style>\n{css}\n</style>'
    html = html.replace('<link rel="stylesheet" href="app.css">', css_tag)

    # 2. 注入資料並修改 JS 邏輯使其讀取內置變數
    # 我們將 fetch 原始碼替換成直接回傳 JSON 內容
    js_mod = f'const EMBEDDED_MATCHES = {json.dumps(matches, ensure_ascii=False)};\n'
    js_mod += f'const EMBEDDED_SCHEDULES = {json.dumps(schedules, ensure_ascii=False)};\n'
    
    # 替換 schedules.json 的 fetch
    js_mod += js.replace("await fetch('schedules.json')", "{ 'ok': true, 'json': async () => EMBEDDED_SCHEDULES }") \
                .replace("await fetch('matches.json?v=' + Date.now())", "{ 'ok': true, 'json': async () => EMBEDDED_MATCHES }")

    # 3. 注入 JS 腳本 (避免使用 re.sub 以免對 JS 中的反斜線報錯)
    js_tag = f'<script>\n{js_mod}\n</script>'
    
    # 手動尋找並替換原本的 app.js script 標籤
    marker = '<!-- JS_MARKER -->'
    # 先在 index.html 裡找一個明顯的地方標記，或者直接針對原本的版號做取代
    # 既然我們知道版號是 LOCAL_MODE_V1 或 20260422-RECOVERY
    html = re.sub(r'<script src="app\.js\?v=.*?"></script>', marker, html)
    html = html.replace(marker, js_tag)

    # 移除 Firebase 相關腳本
    html = re.sub(r'<script src="https://www\.gstatic\.com/firebasejs/.*?"></script>', '', html)
    html = html.replace('<script src="firebase-config.js"></script>', '')

    # 4. 存檔
    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✨ 單機終極版 HTML 已裝成！請查看 index_local.html")

if __name__ == "__main__":
    build()
