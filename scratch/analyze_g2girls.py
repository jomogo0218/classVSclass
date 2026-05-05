# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('const EMBEDDED_MATCHES = [')
end = content.find('];', start) + 2
json_str = content[start + len('const EMBEDDED_MATCHES = '):end-1]
matches = json.loads(json_str)

print('=== 高二女排 循環賽 場次 ===\n')
target = [m for m in matches if '高二女排' in m['category']]
if not target:
    print('【找不到任何「高二女排」相關場次！】')
else:
    teams = set()
    for m in target:
        teams.add(m['teamA'])
        teams.add(m['teamB'])
    print(f'共 {len(target)} 場, 隊伍: {sorted(teams)}\n')
    for m in target:
        status = m['status']
        print(f"  ID:{m['id']} | {m['teamA']} vs {m['teamB']} | {status}")

print()
print('=== 目前系統所有 循環賽 類別 ===')
cats = sorted(set(m['category'] for m in matches if '循環賽' in m['category']))
for c in cats:
    count = sum(1 for m in matches if m['category'] == c)
    teams = set()
    for m in matches:
        if m['category'] == c:
            teams.add(m['teamA'])
            teams.add(m['teamB'])
    print(f"  {c}: {count}場, {len(teams)}隊 → {', '.join(sorted(teams))}")

print()
print('=== 「待打」狀態的高二女排場次 ===')
pending = [m for m in matches if '高二女排' in m['category'] and '待打' in m['status']]
for m in pending:
    print(f"  {m['id']}: {m['teamA']} vs {m['teamB']}")
if not pending:
    print('  (無待打場次)')
