import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open('d:/classVSclass/matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

counts = defaultdict(list)
for m in matches:
    teams = sorted([m['teamA'].strip(), m['teamB'].strip()])
    key = (m['category'].strip(), teams[0], teams[1])
    counts[key].append(m['id'])

print("Matches appearing more than once:")
for key, ids in counts.items():
    if len(ids) > 1:
        print(f"{key}: {len(ids)} times (IDs: {ids})")
