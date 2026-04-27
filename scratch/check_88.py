import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open('d:/classVSclass/matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

counts = defaultdict(list)
for m in matches:
    tA = m['teamA'].strip()
    tB = m['teamB'].strip()
    cat = m['category'].strip()
    
    # Placeholder teams should NOT be deduplicated
    if "待定" in tA or "待定" in tB or "待等" in tA or "待等" in tB:
        continue
        
    teams = sorted([tA, tB])
    key = (cat, teams[0], teams[1])
    counts[key].append(m['id'])

print(f"Total matches: {len(matches)}")
print("Duplicate non-placeholder matches:")
dupe_ids = []
for key, ids in counts.items():
    if len(ids) > 1:
        print(f"{key}: {len(ids)} times (IDs: {ids})")
        dupe_ids.extend(ids[1:]) # Keep only the first one

print(f"Total duplicates to remove (non-placeholder): {len(dupe_ids)}")
print(f"Count if removed: {len(matches) - len(dupe_ids)}")
