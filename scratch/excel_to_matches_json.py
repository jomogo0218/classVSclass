"""
excel_to_matches_json.py
Converts CHSH_Sports_Matches_2026_4_24.xlsx to matches.json
"""
import openpyxl
import json

filename = 'CHSH_Sports_Matches_2026_4_24.xlsx'
wb = openpyxl.load_workbook(filename, data_only=True)
ws = wb.active

matches = []
seen = set()  # to deduplicate

for row in ws.iter_rows(min_row=2, values_only=True):
    category, location, teamA, teamB, score_raw, winner_raw, status_raw, created = row
    if not category or not teamA or not teamB:
        continue

    category = str(category).strip()
    teamA    = str(teamA).strip()
    teamB    = str(teamB).strip()
    score_raw   = str(score_raw).strip() if score_raw else '0-0'
    winner_raw  = str(winner_raw).strip() if winner_raw else ''
    status_raw  = str(status_raw).strip() if status_raw else '⏳ 待打'

    # Dedup key: category + sorted teams
    key = category + '|' + '|'.join(sorted([teamA, teamB]))
    if key in seen:
        continue
    seen.add(key)

    # Parse score - handle formats like "25-21", "3-2", "0-0, 0-0, 0-0", "0-21, 0-0, 0-0"
    score_display = score_raw
    scoreA = 0
    scoreB = 0
    # Use first segment for simple score
    first_seg = score_raw.split(',')[0].strip()
    parts = first_seg.replace('–','-').split('-')
    if len(parts) == 2:
        try:
            scoreA = int(parts[0])
            scoreB = int(parts[1])
        except:
            pass

    # Normalize score display to A:B format
    score = f'{scoreA}:{scoreB}'

    # Status normalization
    if '已結束' in status_raw:
        status = '✅ 已結束'
    elif '待打' in status_raw or status_raw == '⏳ 待打':
        status = '⏳ 待打'
    else:
        status = '⏳ 待打'

    # Winner
    winner = None
    if status == '✅ 已結束':
        w = winner_raw.strip()
        # Match winner to teamA or teamB (fuzzy)
        if w == teamA or teamA.startswith(w) or w.startswith(teamA.split()[0]):
            winner = teamA
        elif w == teamB or teamB.startswith(w) or w.startswith(teamB.split()[0]):
            winner = teamB
        elif scoreA > scoreB:
            winner = teamA
        elif scoreB > scoreA:
            winner = teamB
        else:
            winner = '和局'

    # Build ID from category + index
    match_id = category + '_' + str(len(matches))

    match = {
        'id': match_id,
        'category': category,
        'teamA': teamA,
        'teamB': teamB,
        'score': score,
        'scoreA': scoreA,
        'scoreB': scoreB,
        'winner': winner,
        'status': status
    }
    matches.append(match)

# Write to matches.json
with open('matches.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

print(f'Done. Total matches: {len(matches)}')
print()

# Summary by category
from collections import Counter
cats = Counter(m['category'] for m in matches)
finished = Counter(m['category'] for m in matches if m['status'] == '✅ 已結束')
print('Category summary:')
for cat, total in sorted(cats.items()):
    done = finished.get(cat, 0)
    print(f'  {cat}: {total} 場, 已結束 {done} 場')
