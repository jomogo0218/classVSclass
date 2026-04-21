import json

with open('matches.json', encoding='utf-8') as f:
    data = json.load(f)

updated = 0
for m in data:
    if m['id'] == 65 and m.get('teamA') == '待定':
        print('修改前:', m['teamA'], 'VS', m['teamB'])
        m['teamA'] = '高一仁'
        print('修改後:', m['teamA'], 'VS', m['teamB'])
        updated += 1

with open('matches.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'共更新 {updated} 筆')
