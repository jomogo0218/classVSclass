import json

with open('matches.json', encoding='utf-8') as f:
    data = json.load(f)

seen = {}
dupes = []
for m in data:
    key = str(m.get('teamA','')) + '|' + str(m.get('teamB','')) + '|' + str(m.get('category',''))
    if key in seen:
        dupes.append((seen[key], m))
    else:
        seen[key] = m

print('總場次：' + str(len(data)))
print('內容重複（不同ID）：' + str(len(dupes)) + ' 組')
for a, b in dupes[:10]:
    print('  ID ' + str(a['id']) + ' vs ID ' + str(b['id']) + '：' + str(a['teamA']) + ' vs ' + str(a['teamB']) + ' (' + str(a['category']) + ')')
