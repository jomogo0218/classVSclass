import json
import sys
import io

# 強制 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def list_it():
    with open('matches.json', 'r', encoding='utf-8') as f:
        m = json.load(f)
    
    print(f"目前總數：{len(m)} 場")
    print("\n--- 清單最後 15 場 (106-15 = 91~106) ---")
    # 列出最後的資料，看看有沒有重複的 ID 或明顯錯誤的內容
    for i in m[91:]:
        print(f"ID: {i.get('id'):<4} | {i.get('category'):<15} | {i.get('teamA')} VS {i.get('teamB')}")

if __name__ == "__main__":
    list_it()
