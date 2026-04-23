import json
from collections import Counter
import sys

# 強制輸出為 UTF-8 避免 Windows 編碼錯誤
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check():
    with open('matches.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    # 比對邏輯：類別 + 排序後的隊伍名稱
    def get_key(m):
        teams = sorted([m.get('teamA', '').strip(), m.get('teamB', '').strip()])
        return (m.get('category', '').strip(), teams[0], teams[1])

    registry = {}
    for m in matches:
        key = get_key(m)
        if key not in registry:
            registry[key] = []
        registry[key].append(m)

    print("=== 重複對戰組合清單 ===")
    count = 0
    for key, items in registry.items():
        if len(items) > 1:
            count += 1
            print(f"\n{count}. 【{key[0]}】")
            print(f"   對戰：{key[1]} VS {key[2]}")
            for i in items:
                print(f"   - [ID: {i.get('id')}] 狀態: {i.get('status')} | 場地: {i.get('location')}")
    
    if count == 0:
        print("\n✅ 沒有發現任何重複的對戰組合！")

if __name__ == "__main__":
    check()
