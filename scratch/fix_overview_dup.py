with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# All variables that might be re-declared by the new module
TARGETS = [
    'let currentOverviewCategory',
    'let overviewViewMode',
]

for TARGET in TARGETS:
    count = content.count(TARGET)
    print(f'{repr(TARGET)}: {count} declaration(s)')
    first = content.find(TARGET)
    second = content.find(TARGET, first + 1)
    while second > 0:
        line_start = content.rfind('\n', 0, second) + 1
        line_end   = content.find('\n', second) + 1
        removed = content[line_start:line_end]
        print(f'  Removing: {repr(removed[:80])}')
        content = content[:line_start] + content[line_end:]
        second = content.find(TARGET, first + 1)
    print(f'  Remaining: {content.count(TARGET)}')

with open('app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('\nAll done. Saved app.js')
