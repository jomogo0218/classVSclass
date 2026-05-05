import os
import json

def generate_final_html():
    print("Generating final self-contained HTML...")
    
    # 讀取所有組件
    with open('index.html', 'r', encoding='utf-8') as f: html = f.read()
    with open('app.css', 'r', encoding='utf-8') as f: css = f.read()
    with open('app.js', 'r', encoding='utf-8') as f: js = f.read()
    with open('matches.json', 'r', encoding='utf-8') as f: matches = f.read()
    with open('schedules.json', 'r', encoding='utf-8') as f: schedules = f.read()
    with open('firebase-config.js', 'r', encoding='utf-8') as f: firebase_config = f.read()

    # --- 1. 強制 CSS 主題色 (Orange & Navy) ---
    css = css.replace('#1a73e8', '#f5750a')
    css = css.replace('#e8f0fe', '#fff7ed')
    css = css.replace('#2563eb', '#f5750a')
    
    # --- 2. 處理 JS 資料嵌入 ---
    js_data = f"const EMBEDDED_MATCHES = {matches};\nconst EMBEDDED_SCHEDULES = {schedules};\nconst EMBEDDED_SCHEDULED_DATA = [];\n"
    # 模擬 Fetch（離線時讀嵌入資料）
    js = js.replace("await fetch('schedules.json')", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})")
    js = js.replace("await fetch('matches.json?v=' + Date.now())", "({ok:true, json:async()=>EMBEDDED_MATCHES})")
    
    if "function loadScheduledMatches" not in js:
        js += "\nfunction loadScheduledMatches(){ console.log('Using embedded data'); }\n"

    # --- 3. 組合 HTML (過濾掉既有的內嵌 Script) ---
    import re
    # 移除所有 <script>...</script> 區塊，但保留 Firebase CDN 的引用
    # 我們只移除包含內置邏輯的腳本（通常比較長或不含 src）
    cleaned_html = re.sub(r'<script\b[^>]*>(?:(?!src=).)*?</script>', '', html, flags=re.DOTALL)
    
    new_html_lines = []
    for line in cleaned_html.splitlines():
        # 移除本地 CSS 引用
        if 'href="app.css' in line: continue
        # 移除可能殘留的 src 引用
        if 'src="app.js' in line: continue
        if 'src="firebase-config.js' in line: continue
        new_html_lines.append(line)
    
    final_html = "\n".join(new_html_lines)
    
    # 注入 Style
    style_block = f"<style>\n{css}\n</style>"
    
    # firebase-config.js 內嵌
    firebase_inline = f"<script>\n{firebase_config}\n</script>"
    
    # app.js 和資料嵌入
    script_block = f"<script>\n{js_data}\n{js}\n</script>"
    
    # 確保注入在正確位置
    if '</head>' in final_html:
        final_html = final_html.replace('</head>', f'{style_block}\n</head>')
    
    # 在 </body> 前插入
    if '</body>' in final_html:
        final_html = final_html.replace('</body>', f'{firebase_inline}\n{script_block}\n</body>')

    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("Success! Final index_local.html is generated (with Firebase sync).")

if __name__ == "__main__":
    generate_final_html()
