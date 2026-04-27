import os
import re

# paths
css_path  = 'd:/classVSclass/app.css'
js_path   = 'd:/classVSclass/app.js'
html_path = 'd:/classVSclass/index.html'

# 1. Force Orange Theme in app.css
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Replace all blue-ish colors with reference site orange (#f5750a)
css = css.replace('#1a73e8', '#f5750a')
css = css.replace('#e8f0fe', '#fff7ed')
css = css.replace('#1557b0', '#e66a09')
css = css.replace('#2563eb', '#f5750a')
css = css.replace('#eff6ff', '#fff7ed')

# Ensure the bracket tree CSS is correct and includes lines
bracket_css = """
/* ═══════════════ 對戰表 (參考網站風格) ═══════════════ */
.overview-layout { display: flex; height: calc(100vh - var(--topbar-h)); width: 100%; background: var(--white); }
.category-sidebar { width: 240px; border-right: 1px solid var(--border); background: var(--white); overflow-y: auto; flex-shrink: 0; }
.category-tab { padding: 16px 20px; cursor: pointer; border-bottom: 1px solid var(--border-light); display: flex; align-items: center; gap: 12px; font-weight: 600; color: var(--text-2); }
.category-tab:hover { background: var(--orange-light); color: var(--orange); }
.category-tab.active { background: var(--orange-light); color: var(--orange); border-right: 4px solid var(--orange); }
.overview-main { flex: 1; overflow: auto; padding: 30px; background: var(--bg); }
.overview-header-card { background: var(--white); border-radius: 12px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 6px solid var(--orange); }
.bracket-tree { display: flex; gap: 60px; padding: 20px 0; min-width: max-content; }
.bracket-round { display: flex; flex-direction: column; justify-content: space-around; min-width: 220px; gap: 40px; }
.round-header { text-align: center; font-size: 12px; font-weight: 800; color: var(--text-3); text-transform: uppercase; margin-bottom: 20px; border-bottom: 3px solid var(--orange); padding-bottom: 8px; width: 100%; }
.tree-match { position: relative; background: var(--white); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.06); width: 100%; z-index: 1; }
.tree-team { padding: 10px 14px; font-weight: 600; font-size: 14px; color: var(--text-1); border-bottom: 1px solid var(--border-light); }
.tree-team.bottom { border-bottom: none; }
.tree-footer { padding: 6px 14px; font-size: 11px; background: var(--orange-light); color: var(--orange); font-weight: 700; border-top: 1px solid #fee2e2; }

/* 連接線系統 */
.tree-match::after { content: ''; position: absolute; right: -60px; top: 50%; width: 60px; height: 2px; background: #cbd5e1; z-index: -1; }
.bracket-round:last-child .tree-match::after { display: none; }
.bracket-round:not(:last-child) .tree-match:nth-child(odd)::before { content: ''; position: absolute; right: -60px; top: 50%; width: 2px; height: calc(100% + 42px); background: #cbd5e1; z-index: -1; }
"""
if '.bracket-tree' not in css:
    css += bracket_css

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

# 2. Re-write mega_build.py to be bulletproof
with open('mega_build.py', 'w', encoding='utf-8') as f:
    f.write("""
import json
import os
import re

def build_final():
    print("Running bulletproof build script...")
    
    def read_f(name):
        with open(name, 'r', encoding='utf-8') as f:
            return f.read()

    matches_data = read_f('matches.json')
    schedules_data = read_f('schedules.json')
    css = read_f('app.css')
    js = read_f('app.js')
    html = read_f('index.html')

    # 1. Replace CSS
    css_block = f"<style>\\n{css}\\n</style>"
    html = re.sub(r'<link.*href=["\\']app\.css["\\'].*?>', css_block, html)

    # 2. Inject Data into JS
    js_header = f"const EMBEDDED_MATCHES = {matches_data};\\nconst EMBEDDED_SCHEDULES = {schedules_data};\\n"
    
    # 3. Handle data loading in JS
    js = re.sub(r"await\s+fetch\s*\\(['\\\"].*?schedules\.json.*?\\)", "({ ok: true, json: async () => (EMBEDDED_SCHEDULES) })", js)
    js = re.sub(r"await\s+fetch\s*\\(['\\\"].*?matches\.json.*?\\)", "({ ok: true, json: async () => (EMBEDDED_MATCHES) })", js)
    
    # 4. Remove external JS tags and inject full JS
    html = re.sub(r'<script.*src=["\\'].*?app\.js.*?["\\'].*?></script>', f"<script>\\n{js_header}\\n{js}\\n</script>", html)
    html = re.sub(r'<script.*src=["\\']https://www\\.gstatic\\.com/firebasejs/.*?</script>', "", html)
    html = re.sub(r'<script.*src=["\\']firebase-config\\.js.*?["\\'].*?></script>', "", html)

    # 5. Output
    with open('index_local.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Build Success! index_local.html is now self-contained and updated.")

if __name__ == "__main__":
    build_final()
""")

print("Cleaned and prepared all files.")
