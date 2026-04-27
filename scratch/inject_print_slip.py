"""
inject_print_slip.py
Safely replaces getOriginalTeacher, printMatchSlip, and printMatchSlipById
in app.js with the new UTF-8 version from scratch/new_print_slip.js
"""

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

with open('scratch/new_print_slip.js', 'r', encoding='utf-8') as f:
    new_code = f.read().strip()

# Find start: the line with "let currentEditingMatchId = null;"
# then the getOriginalTeacher block
START_MARKER = 'function getOriginalTeacher(className, dayIdx, periodIdx) {'
END_MARKER   = '\nfunction openEditScoreModal('

start_idx = content.rfind(START_MARKER)
if start_idx < 0:
    print('ERROR: could not find START_MARKER')
    exit(1)

# Also include let currentEditingMatchId if it's right before
ci_marker = 'let currentEditingMatchId = null;'
ci_idx = content.rfind(ci_marker, 0, start_idx)
if ci_idx > 0 and (start_idx - ci_idx) < 20:
    start_idx = ci_idx
    print('Including currentEditingMatchId declaration in replacement range')

end_idx = content.find(END_MARKER, start_idx)
if end_idx < 0:
    print('ERROR: could not find END_MARKER')
    exit(1)

print(f'Replacing chars {start_idx} to {end_idx} ({end_idx-start_idx} chars)')

# Build replacement: new code only (currentEditingMatchId declaration stays from original)
replacement = new_code + '\n'

content = content[:start_idx] + replacement + content[end_idx:]

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Done. New file: {len(content)} chars')

# Verify
checks = [
    '請允許彈出視窗以列印',
    '嘉華中學體育競賽借課通知單',
    '任課老師確認簽名欄',
    '課程科目：',
    '授課老師：',
    '老師確認簽名：',
    'function printMatchSlipById',
    'function getOriginalTeacher',
]
print('Content verification:')
for c in checks:
    print(f'  {"OK" if c in content else "MISSING"}: {c}')
