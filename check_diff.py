import pandas as pd
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

df = pd.read_excel('CHSH_Sports_Matches_2026_4_19.xlsx')
with open('matches.json', encoding='utf-8') as f:
    matches = json.load(f)

diffs = []
for i, row in df.iterrows():
    if i >= len(matches):
        diffs.append(f'New match added: {row["賽事類別"]} {row["隊伍 A"]} vs {row["隊伍 B"]}')
        continue
    
    m = matches[i]
    if str(row['賽事類別']).strip() != str(m.get('category')).strip():
        diffs.append(f'Match {i} category changed: {m.get("category")} -> {row["賽事類別"]}')
    if str(row['隊伍 A']).strip() != str(m.get('teamA')).strip():
        diffs.append(f'Match {i} Team A changed: {m.get("teamA")} -> {row["隊伍 A"]}')
    if str(row['隊伍 B']).strip() != str(m.get('teamB')).strip():
        diffs.append(f'Match {i} Team B changed: {m.get("teamB")} -> {row["隊伍 B"]}')
    if str(row['比賽狀態']).strip() != str(m.get('status')).strip():
        diffs.append(f'Match {i} Status changed: {m.get("status")} -> {row["比賽狀態"]}')

if not diffs:
    print('No differences found!')
else:
    for d in diffs:
        print(d)
