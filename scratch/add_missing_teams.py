import json

with open('d:\\classVSclass\\matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

# 找目前最大的數字序號
max_num = 0
for m in matches:
    parts = m['id'].split('_')
    if len(parts) >= 2:
        try:
            num = int(parts[-1])
            if num > max_num:
                max_num = num
        except:
            pass

print(f"目前最大序號: {max_num}")
next_num = max_num + 1

# 目前高三女籃有的隊伍
hs3_girls_existing = ['高三仁 黃暄婷', '高三信 歐品妤', '高三愛 蔣瑋珈']
# 要新增的隊伍（只用班級名）
new_hs3 = ['高三忠', '高三孝']

# 目前國三女籃有的隊伍
jh3_girls_existing = ['國三2 林優秦', '國三3 黃佳佳', '國三4 楊于萱', '國三5 龔品諭']
# 要新增的隊伍
new_jh3 = ['國三1']

new_matches = []

# ── 高三女籃：新加入 高三忠 和 高三孝 ──
all_hs3 = hs3_girls_existing + new_hs3
existing_hs3_pairs = set()
for m in matches:
    if m['category'] == '高三女籃 循環賽':
        existing_hs3_pairs.add(frozenset([m['teamA'], m['teamB']]))

added_hs3 = 0
for i, t1 in enumerate(all_hs3):
    for t2 in all_hs3[i+1:]:
        pair = frozenset([t1, t2])
        if pair not in existing_hs3_pairs:
            new_matches.append({
                "id": f"高三女籃 循環賽_{next_num}",
                "category": "高三女籃 循環賽",
                "teamA": t1,
                "teamB": t2,
                "score": "0:0",
                "scoreA": 0,
                "scoreB": 0,
                "winner": None,
                "status": "⏳ 待打"
            })
            print(f"新增 ID={next_num}: 高三女籃 {t1} vs {t2}")
            next_num += 1
            added_hs3 += 1

# ── 國三女籃：新加入 國三1 ──
all_jh3 = jh3_girls_existing + new_jh3
existing_jh3_pairs = set()
for m in matches:
    if m['category'] == '國三女籃 循環賽':
        existing_jh3_pairs.add(frozenset([m['teamA'], m['teamB']]))

added_jh3 = 0
for i, t1 in enumerate(all_jh3):
    for t2 in all_jh3[i+1:]:
        pair = frozenset([t1, t2])
        if pair not in existing_jh3_pairs:
            new_matches.append({
                "id": f"國三女籃 循環賽_{next_num}",
                "category": "國三女籃 循環賽",
                "teamA": t1,
                "teamB": t2,
                "score": "0:0",
                "scoreA": 0,
                "scoreB": 0,
                "winner": None,
                "status": "⏳ 待打"
            })
            print(f"新增 ID={next_num}: 國三女籃 {t1} vs {t2}")
            next_num += 1
            added_jh3 += 1

print(f"\n總計新增 {len(new_matches)} 場 (高三女籃+{added_hs3}場, 國三女籃+{added_jh3}場)")

# 寫入 matches.json
all_matches = matches + new_matches
with open('d:\\classVSclass\\matches.json', 'w', encoding='utf-8') as f:
    json.dump(all_matches, f, ensure_ascii=False, indent=2)

print(f"matches.json 已更新，總場數: {len(all_matches)}")
