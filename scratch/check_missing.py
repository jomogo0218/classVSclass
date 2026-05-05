# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('const EMBEDDED_MATCHES = [')
end = content.find('];', start) + 2
json_str = content[start + len('const EMBEDDED_MATCHES = '):end-1]
matches = json.loads(json_str)

print('=== 檢查使用者提到的四場比賽狀態 ===\n')

targets = [
    ("高二女排 循環賽", "高二信 菜沂潔", "高二愛 方奕婷"),
    ("高二女排 循環賽", "高二仁 蘇愛甯", "高二孝 顏怡勲"),
    ("高二男排 循環賽", "高二忠 吳承奕", "高二愛 胡廷安"),
    ("高二男排 循環賽", "高二仁 馮宥鑫", "高二愛 胡廷安")
]

for cat, a, b in targets:
    found = [m for m in matches if m['category'] == cat and 
             ((m['teamA'] == a and m['teamB'] == b) or (m['teamA'] == b and m['teamB'] == a))]
    if found:
        m = found[0]
        print(f"找到：{cat} | {m['teamA']} vs {m['teamB']} | 狀態：{m['status']}")
    else:
        print(f"❌ 找不到：{cat} | {a} vs {b}")
