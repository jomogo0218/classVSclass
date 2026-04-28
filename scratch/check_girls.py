import json

with open('d:\\classVSclass\\matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

from collections import defaultdict
categories = defaultdict(set)
for m in matches:
    cat = m.get('category', '')
    categories[cat].add(m['teamA'])
    categories[cat].add(m['teamB'])

output = []
output.append("=== 高三女籃 ===")
for cat, teams in sorted(categories.items()):
    if '高三女籃' in cat:
        output.append(f"{cat}: {sorted(teams)}")

output.append("\n=== 國三女籃 ===")
for cat, teams in sorted(categories.items()):
    if '國三女籃' in cat:
        output.append(f"{cat}: {sorted(teams)}")

output.append("\n=== 高三男籃（對比）===")
for cat, teams in sorted(categories.items()):
    if '高三男籃' in cat:
        output.append(f"{cat}: {sorted(teams)}")

output.append("\n=== 國三男籃（對比）===")
for cat, teams in sorted(categories.items()):
    if '國三男籃' in cat:
        output.append(f"{cat}: {sorted(teams)}")

with open('d:\\classVSclass\\scratch\\girls_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
