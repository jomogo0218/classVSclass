import json

with open('matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

lines = []
lines.append(f'Total matches: {len(matches)}')

# Check all unique status values
from collections import Counter
statuses = Counter(m.get('status','') for m in matches)
lines.append('\nStatus distribution:')
for s, count in statuses.most_common():
    lines.append(f'  {count}x: {repr(s)}')

# Show matches that are finished - check if they have teams that also appear as pending
finished = [m for m in matches if '已結束' in m.get('status','')]
pending  = [m for m in matches if '已結束' not in m.get('status','')]

lines.append(f'\nFinished: {len(finished)}, Pending: {len(pending)}')

# Check if any finished match has the same teamA/teamB combo as pending matches
lines.append('\n=== 已結束的比賽（前15筆）===')
for m in finished[:15]:
    lines.append(f'  [{m["category"]}] {m["teamA"]} vs {m["teamB"]}  score={m.get("score","")}  status={repr(m["status"])}')

# Cross-check: are any teams from finished matches also in pending list?
lines.append('\n=== 檢查：已結束比賽的隊伍是否出現在待排清單中 ===')
finished_pairs = set()
for m in finished:
    key = tuple(sorted([m['teamA'].strip(), m['teamB'].strip()])) + (m['category'],)
    finished_pairs.add(key)

for m in pending:
    key = tuple(sorted([m['teamA'].strip(), m['teamB'].strip()])) + (m['category'],)
    if key in finished_pairs:
        lines.append(f'  DUPE: [{m["category"]}] {m["teamA"]} vs {m["teamB"]}  status={repr(m["status"])}')

with open('scratch/status_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Done')
