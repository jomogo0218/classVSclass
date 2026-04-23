import json
import os

def build_final():
    print("Running build script...")
    
    # 強制使用 utf-8 讀取所有檔案
    def read_f(name):
        with open(name, 'r', encoding='utf-8') as f:
            return f.read()

    matches_data = read_f('matches.json')
    schedules_data = read_f('schedules.json')
    # 注入使用者提供的最新賽程進度
    user_scheduled_data = """[
  { "matchId": 0, "date": "2026-04-21", "periodIndex": 9 },
  { "matchId": 10, "date": "2026-04-27", "periodIndex": 9 },
  { "matchId": 105, "date": "2026-04-23", "periodIndex": 7 },
  { "matchId": 106, "date": "2026-04-23", "periodIndex": 1 },
  { "matchId": 107, "date": "2026-05-18", "periodIndex": 3 },
  { "matchId": 109, "date": "2026-04-28", "periodIndex": 1 },
  { "matchId": 11, "date": "2026-04-29", "periodIndex": 1 },
  { "matchId": 110, "date": "2026-04-27", "periodIndex": 5 },
  { "matchId": 117, "date": "2026-05-21", "periodIndex": 2 },
  { "matchId": 118, "date": "2026-04-22", "periodIndex": 5 },
  { "matchId": 119, "date": "2026-04-27", "periodIndex": 2 },
  { "matchId": 12, "date": "2026-04-29", "periodIndex": 7 },
  { "matchId": 13, "date": "2026-04-30", "periodIndex": 7 },
  { "matchId": 14, "date": "2026-04-30", "periodIndex": 1 },
  { "matchId": 15, "date": "2026-04-28", "periodIndex": 3 },
  { "matchId": 16, "date": "2026-04-30", "periodIndex": 6 },
  { "matchId": 18, "date": "2026-04-30", "periodIndex": 2 },
  { "matchId": 19, "date": "2026-04-27", "periodIndex": 5 },
  { "matchId": 2, "date": "2026-04-22", "periodIndex": 9 },
  { "matchId": 20, "date": "2026-04-30", "periodIndex": 2 },
  { "matchId": 21, "date": "2026-04-29", "periodIndex": 1 },
  { "matchId": 22, "date": "2026-04-22", "periodIndex": 1 },
  { "matchId": 23, "date": "2026-04-28", "periodIndex": 9 },
  { "matchId": 24, "date": "2026-04-27", "periodIndex": 1 },
  { "matchId": 25, "date": "2026-04-28", "periodIndex": 9 },
  { "matchId": 26, "date": "2026-04-24", "periodIndex": 2 },
  { "matchId": 27, "date": "2026-04-22", "periodIndex": 1 },
  { "matchId": 28, "date": "2026-04-29", "periodIndex": 9 },
  { "matchId": 29, "date": "2026-04-27", "periodIndex": 4 },
  { "matchId": 3, "date": "2026-04-24", "periodIndex": 9 },
  { "matchId": 30, "date": "2026-04-24", "periodIndex": 1 },
  { "matchId": 31, "date": "2026-05-06", "periodIndex": 1 },
  { "matchId": 32, "date": "2026-04-30", "periodIndex": 1 },
  { "matchId": 33, "date": "2026-04-30", "periodIndex": 9 },
  { "matchId": 34, "date": "2026-04-29", "periodIndex": 2 },
  { "matchId": 35, "date": "2026-04-27", "periodIndex": 5 },
  { "matchId": 36, "date": "2026-04-28", "periodIndex": 2 },
  { "matchId": 37, "date": "2026-05-04", "periodIndex": 9 },
  { "matchId": 38, "date": "2026-05-05", "periodIndex": 9 },
  { "matchId": 39, "date": "2026-05-06", "periodIndex": 9 },
  { "matchId": 4, "date": "2026-04-22", "periodIndex": 9 },
  { "matchId": 5, "date": "2026-04-24", "periodIndex": 9 },
  { "matchId": 55, "date": "2026-04-21", "periodIndex": 5 },
  { "matchId": 56, "date": "2026-04-27", "periodIndex": 1 },
  { "matchId": 57, "date": "2026-04-22", "periodIndex": 7 },
  { "matchId": 58, "date": "2026-04-22", "periodIndex": 2 },
  { "matchId": 6, "date": "2026-04-23", "periodIndex": 9 },
  { "matchId": 65, "date": "2026-04-27", "periodIndex": 9 },
  { "matchId": 66, "date": "2026-04-22", "periodIndex": 6 },
  { "matchId": 69, "date": "2026-04-24", "periodIndex": 5 },
  { "matchId": 7, "date": "2026-04-21", "periodIndex": 9 },
  { "matchId": 70, "date": "2026-04-29", "periodIndex": 3 },
  { "matchId": 71, "date": "2026-04-27", "periodIndex": 2 },
  { "matchId": 72, "date": "2026-04-21", "periodIndex": 6 },
  { "matchId": 73, "date": "2026-04-24", "periodIndex": 7 },
  { "matchId": 74, "date": "2026-04-24", "periodIndex": 1 },
  { "matchId": 75, "date": "2026-04-29", "periodIndex": 2 },
  { "matchId": 76, "date": "2026-04-21", "periodIndex": 1 },
  { "matchId": 77, "date": "2026-04-27", "periodIndex": 7 },
  { "matchId": 78, "date": "2026-04-28", "periodIndex": 1 },
  { "matchId": 80, "date": "2026-04-30", "periodIndex": 7 },
  { "matchId": 82, "date": "2026-04-24", "periodIndex": 5 },
  { "matchId": 83, "date": "2026-04-21", "periodIndex": 1 },
  { "matchId": 84, "date": "2026-04-22", "periodIndex": 5 },
  { "matchId": 87, "date": "2026-04-21", "periodIndex": 6 },
  { "matchId": 88, "date": "2026-04-27", "periodIndex": 7 },
  { "matchId": 9, "date": "2026-04-28", "periodIndex": 2 }
]"""
    css = read_f('app.css')
    js = read_f('app.js')
    html = read_f('index.html')

    # 1. 處理 CSS
    css_block = f"<style>\n{css}\n</style>"
    html = html.replace('<link rel="stylesheet" href="app.css">', css_block)

    # 2. 處理 JS 與資料 (使用 regex 強力取代 fetch，不論引號或空格)
    import re
    # 替換 schedules.json
    js = re.sub(r"await\s+fetch\s*\(['\"]schedules\.json['\"]\+?.*?\)","({ ok: true, json: async () => (" + schedules_data + ") })", js)
    # 替換 matches.json
    js = re.sub(r"await\s+fetch\s*\(['\"]matches\.json\?v=['\"]\s*\+\s*Date\.now\(\)\s*\)","({ ok: true, json: async () => (" + matches_data + ") })", js)
    
    # 強制將使用者提供的賽程紀錄注入到啟動邏輯中
    js = js.replace("loadScheduledMatches();", f"scheduledMatches = {user_scheduled_data}; saveScheduledMatches();")

    # 注入嵌入式資料
    js_header = f"const EMBEDDED_MATCHES = {matches_data};\nconst EMBEDDED_SCHEDULES = {schedules_data};\n"
    js_block = f"<script>\n{js_header}\n{js}\n</script>"

    # 3. 清理 HTML 標籤
    # 移除原本的 JS 引用的那幾行
    lines = html.splitlines()
    new_lines = []
    for line in lines:
        if 'firebase' in line or 'firebase-config' in line or 'app.js' in line:
            continue
        new_lines.append(line)
    
    # 在 </body> 前注入我們的巨大 JS 塊
    final_html = "\n".join(new_lines)
    final_html = final_html.replace('</body>', f'{js_block}\n</body>')

    # 4. 產出
    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print("Build Success! Please check index_local.html")

if __name__ == "__main__":
    try:
        build_final()
    except Exception as e:
        print(f"Error: {e}")
