# -*- coding: utf-8 -*-
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('const EMBEDDED_MATCHES = [')
end = content.find('];', start) + 2
json_str = content[start + len('const EMBEDDED_MATCHES = '):end-1]
matches = json.loads(json_str)

# Find all round-robin categories
rr_cats = {}
for m in matches:
    cat = m['category']
    if '循環賽' in cat or '預賽' in cat:
        if cat not in rr_cats:
            rr_cats[cat] = []
        rr_cats[cat].append(m)

print(f'=== 循環賽類別共 {len(rr_cats)} 個 ===\n')
problems = []
for cat, ms in sorted(rr_cats.items()):
    teams = set()
    for m in ms:
        teams.add(m['teamA'])
        teams.add(m['teamB'])
    n = len(teams)
    expected = n * (n-1) // 2
    actual = len(ms)
    if actual == expected:
        status = 'OK'
    else:
        status = f'MISSING {expected-actual}'
    print(f'[{status}] {cat}: {n}隊, 應{expected}場, 實{actual}場')
    if actual != expected:
        teams_list = sorted(teams)
        existing = set()
        for m in ms:
            key = tuple(sorted([m['teamA'], m['teamB']]))
            existing.add(key)
        missing = []
        for i in range(len(teams_list)):
            for j in range(i+1, len(teams_list)):
                key = (teams_list[i], teams_list[j])
                if key not in existing:
                    missing.append(key)
        print(f'   隊伍: {", ".join(teams_list)}')
        for a, b in missing:
            print(f'   [缺少] {a} vs {b}')
        problems.append((cat, missing))
    print()

print(f'\n=== 總結: {len(problems)} 個循環賽有缺場 ===')
for cat, missing in problems:
    print(f'  {cat}: 缺 {len(missing)} 場')
