import json
import sys

# Force UTF-8 for output
sys.stdout.reconfigure(encoding='utf-8')

with open('d:/classVSclass/matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)
for m in matches:
    if m['id'] in range(10, 20) or m['id'] in range(30, 40):
        print(f"{m['id']}: {m['category']} {m['teamA']} vs {m['teamB']}")
