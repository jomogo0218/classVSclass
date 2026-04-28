import json, re

with open('d:\\classVSclass\\matches.json', 'r', encoding='utf-8') as f:
    matches_data = json.load(f)

matches_json_str = json.dumps(matches_data, ensure_ascii=False, indent=2)

with open('d:\\classVSclass\\index_local.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 正確的變數名稱是 EMBEDDED_MATCHES
pattern = r'const EMBEDDED_MATCHES\s*=\s*\[[\s\S]*?\]\s*;'
replacement = f'const EMBEDDED_MATCHES = {matches_json_str};'

new_html, count = re.subn(pattern, replacement, html)
print(f"替換次數: {count}")

if count > 0:
    with open('d:\\classVSclass\\index_local.html', 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"index_local.html 已更新，嵌入 {len(matches_data)} 場比賽")
else:
    print("仍找不到，檢查變數名稱...")
    idx = html.find('EMBEDDED_MATCH')
    print(f"位置附近: {html[idx:idx+60]}")
