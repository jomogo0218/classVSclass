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

    # --- 1. 強制 CSS 主題色 (Orange & Navy) ---
    css = css.replace('#1a73e8', '#f5750a')  # Blue -> Orange
    css = css.replace('#e8f0fe', '#fff7ed')  # Blue Light -> Orange Light
    css = css.replace('#2563eb', '#f5750a')  # Indigo -> Orange
    
    # --- 2. 處理 JS 資料嵌入 ---
    js_data = f"const EMBEDDED_MATCHES = {matches};\nconst EMBEDDED_SCHEDULES = {schedules};\nconst EMBEDDED_SCHEDULED_DATA = [];\n"
    # 模擬 Fetch
    js = js.replace("await fetch('schedules.json')", "({ok:true, json:async()=>EMBEDDED_SCHEDULES})")
    js = js.replace("await fetch('matches.json?v=' + Date.now())", "({ok:true, json:async()=>EMBEDDED_MATCHES})")
    
    # 確保 loadScheduledMatches 不會噴錯 (如果它不在 js 裡，我們補一個 dummy)
    if "function loadScheduledMatches" not in js:
        js += "\\nfunction loadScheduledMatches(){ console.log('Using embedded data'); }\\n"

    # --- 3. 組合 HTML ---
    # 移除原本的連結標籤
    new_html_lines = []
    for line in html.splitlines():
        if 'href="app.css' in line or 'src="app.js' in line or 'src="firebase' in line:
            continue
        new_html_lines.append(line)
    
    final_html = "\n".join(new_html_lines)
    
    # 注入 Style 與 Script
    style_block = f"<style>\n{css}\n</style>"
    script_block = f"<script>\n{js_data}\n{js}\n</script>"
    
    final_html = final_html.replace('</head>', f'{style_block}\n</head>')
    final_html = final_html.replace('</body>', f'{script_block}\n</body>')

    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("Success! Final index_local.html is generated.")

if __name__ == "__main__":
    generate_final_html()
