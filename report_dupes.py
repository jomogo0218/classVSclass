import json
import re
import sys
import io

# 強制輸出為 UTF-8 避免編碼錯誤
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def gen_report():
    # 1. 讀取比賽資料
    with open('matches.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    # 2. 讀取排程進度 (從編譯腳本抓取)
    try:
        with open('mega_build.py', 'r', encoding='utf-8') as f:
            content = f.read()
            match = re.search(r'user_scheduled_data = """(.*?)"""', content, re.DOTALL)
            if match:
                scheduled = json.loads(match.group(1))
            else:
                scheduled = []
    except:
        scheduled = []

    # 建立 ID 與賽程對照表 (Key: int)
    sched_map = {int(s['matchId']): s for s in scheduled}
    
    # 節次名稱對照
    PERIOD_NAMES = ['早','1','2','3','4','5','6','7','課輔','精進']

    # 3. 找出重複賽事 (改用絕對全名模式)
    registry = {}
    for m in matches:
        # 完全保留原始字串，只做基本的前後空格清理
        cat = str(m.get('category', '')).strip()
        tA  = str(m.get('teamA', '')).strip()
        tB  = str(m.get('teamB', '')).strip()
        
        # 為了比對，將兩隊名稱排序 (確保 A vs B == B vs A)
        teams = sorted([tA, tB])
        key = (cat, teams[0], teams[1])
        
        if key not in registry: registry[key] = []
        registry[key].append(m)

    # 4. 輸出報表
    with open('FULL_NAME_REPORT.txt', 'w', encoding='utf-8') as out:
        out.write("=== 【全名精確模式】重複賽事 與 課表排定時間 對照表 ===\n\n")
        out.write(f"{'詳細對戰組合資訊 (全名)':<60} | {'ID':<5} | {'課表狀態'}\n")
        out.write("-" * 105 + "\n")

        for key, items in registry.items():
            if len(items) > 1:
                title = f"【{key[0]}】 {key[1]} VS {key[2]}"
                for idx, i in enumerate(items):
                    mid = int(i.get('id'))
                    s = sched_map.get(mid)
                    if s:
                        p_name = PERIOD_NAMES[s['periodIndex']] if s['periodIndex'] < len(PERIOD_NAMES) else str(s['periodIndex'])
                        status = f"✅ {s['date']} 第 {p_name} 節"
                    else:
                        status = "❌ 尚未排定"
                    
                    display_title = title if idx == 0 else ""
                    out.write(f"{display_title:<60} | {mid:<5} | {status}\n")
                out.write("-" * 105 + "\n")
    
    print("一秒對照清單已完成！請開啟檔案：FULL_NAME_REPORT.txt")

if __name__ == "__main__":
    gen_report()
