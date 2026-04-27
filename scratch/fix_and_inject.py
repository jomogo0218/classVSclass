"""
fix_and_inject.py
1. Remove duplicate let currentEditingMatchId declarations
2. Replace getOriginalTeacher/printMatchSlip/printMatchSlipById with new_print_slip.js content
"""

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

with open('scratch/new_print_slip.js', 'r', encoding='utf-8') as f:
    new_code = f.read().strip()

# Step 1: Fix duplicate let currentEditingMatchId
# Find the section with the two declarations
DOUBLE = 'let currentEditingMatchId = null;\n\nlet currentEditingMatchId = null;'
SINGLE = 'let currentEditingMatchId = null;'
if DOUBLE in content:
    content = content.replace(DOUBLE, SINGLE)
    print('Step 1: Removed duplicate currentEditingMatchId declaration')
else:
    print('Step 1: No duplicate found - checking manually')
    # Count occurrences
    count = content.count(SINGLE)
    print(f'  Found {count} occurrence(s) of let currentEditingMatchId')

# Step 2: Replace the function block
# Find from getOriginalTeacher to just before openEditScoreModal
START = 'function getOriginalTeacher(className, dayIdx, periodIdx) {'
END   = '\nfunction openEditScoreModal('

start_idx = content.rfind(START)
end_idx   = content.find(END, start_idx)

if start_idx < 0 or end_idx < 0:
    print(f'ERROR: start={start_idx}, end={end_idx}')
    exit(1)

print(f'Step 2: Replacing chars {start_idx} to {end_idx} ({end_idx-start_idx} chars)')
content = content[:start_idx] + new_code + '\n' + content[end_idx:]

# Step 3: Verify no duplicates remain
count_now = content.count('let currentEditingMatchId')
print(f'Step 3: currentEditingMatchId declarations remaining: {count_now}')

if count_now > 1:
    # Force remove duplicates by finding second occurrence
    idx1 = content.find('let currentEditingMatchId')
    idx2 = content.find('let currentEditingMatchId', idx1 + 1)
    while idx2 > 0:
        # Remove the line at idx2
        line_start = content.rfind('\n', 0, idx2) + 1
        line_end   = content.find('\n', idx2) + 1
        print(f'  Removing duplicate at char {idx2} (line chars {line_start}-{line_end})')
        content = content[:line_start] + content[line_end:]
        idx2 = content.find('let currentEditingMatchId', idx1 + 1)
    print(f'  After cleanup: {content.count("let currentEditingMatchId")} declaration(s)')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\nDone. Final file: {len(content)} chars')
