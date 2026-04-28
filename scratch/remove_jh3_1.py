import json, re

with open('d:\\classVSclass\\matches.json', 'r', encoding='utf-8') as f:
    matches = json.load(f)

before = len(matches)

# 刪除所有含 國三1 的 國三女籃 循環賽
matches = [
    m for m in matches
    if not (m['category'] == '國三女籃 循環賽' and '國三1' in (m['teamA'] + m['teamB']))
]

after = len(matches)
print(f"刪除 {before - after} 場，剩餘 {after} 場")

with open('d:\\classVSclass\\matches.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f, ensure_ascii=False, indent=2)

# 重新嵌入 index_local.html
matches_json_str = json.dumps(matches, ensure_ascii=False, indent=2)

with open('d:\\classVSclass\\index_local.html', 'r', encoding='utf-8') as f:
    html = f.read()

pattern = r'const EMBEDDED_MATCHES\s*=\s*\[[\s\S]*?\]\s*;'
new_html, count = re.subn(pattern, f'const EMBEDDED_MATCHES = {matches_json_str};', html)
print(f"HTML 替換次數: {count}")

with open('d:\\classVSclass\\index_local.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("完成")
