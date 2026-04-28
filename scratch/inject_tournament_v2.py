"""
inject_tournament_v2.py
Replace the old renderTournamentOverview / renderRoundRobinGrid / renderBracketTree
functions with the new v2 module, and inject the new CSS into app.css.
"""

with open('app.js', 'r', encoding='utf-8') as f:
    js = f.read()

with open('app.css', 'r', encoding='utf-8') as f:
    css = f.read()

with open('scratch/tournament_overview_v2.js', 'r', encoding='utf-8') as f:
    new_js = f.read().strip()

with open('scratch/tournament_overview_v2.css', 'r', encoding='utf-8') as f:
    new_css = f.read().strip()

# ── 1. Replace JS functions ────────────────────────────────────
# Find the start of the old block
START_MARKER = 'function renderTournamentOverview() {'
END_MARKER   = None   # goes to end of file

start_idx = js.rfind(START_MARKER)
if start_idx < 0:
    print('ERROR: Cannot find renderTournamentOverview in app.js')
    exit(1)

# Also find selectOverviewCategory that comes before it
# We want to replace from selectOverviewCategory onwards
BEFORE_MARKER = 'function selectOverviewCategory(cat) {'
before_idx = js.rfind(BEFORE_MARKER)
if before_idx > 0 and before_idx < start_idx:
    start_idx = before_idx

print(f'JS: Replacing from char {start_idx} to end ({len(js)-start_idx} chars)')
js_new = js[:start_idx] + new_js + '\n'

# ── 2. Inject CSS (replace old RR/bracket CSS) ────────────────
# Find old tournament-related CSS and replace, or just append
CSS_MARKER = '/* ═══════════════════════════════════════════════════════════'
old_css_start = css.find(CSS_MARKER)
if old_css_start >= 0:
    print(f'CSS: Replacing existing tournament section at char {old_css_start}')
    css_new = css[:old_css_start] + new_css + '\n'
else:
    print('CSS: Appending new tournament CSS at end')
    css_new = css + '\n\n' + new_css + '\n'

# ── 3. Write back ─────────────────────────────────────────────
with open('app.js', 'w', encoding='utf-8') as f:
    f.write(js_new)

with open('app.css', 'w', encoding='utf-8') as f:
    f.write(css_new)

print(f'Done. app.js: {len(js_new)} chars, app.css: {len(css_new)} chars')
