import json
import re
import sys
import io
import datetime

# 強制 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check():
    # 1. 讀取資料
    with open('matches.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)
    with open('schedules.json', 'r', encoding='utf-8') as f:
        class_schedules = json.load(f)
    with open('mega_build.py', 'r', encoding='utf-8') as f:
        build_content = f.read()
        # 抓取 user_scheduled_data
        match = re.search(r'user_scheduled_data = """(.*?)"""', build_content, re.DOTALL)
        if match:
            scheduled = json.loads(match.group(1))
        else:
            print("找不到排程資料。")
            return

    matches_map = {m['id']: m for m in matches}
    DAY_MAP = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri'}
    PERIOD_NAMES = ['早','1','2','3','4','5','6','7','課輔','精進']

    def get_classes(match_data):
        res = []
        for t in [match_data.get('teamA', ''), match_data.get('teamB', '')]:
            # 匹配例如 "高二仁"
            m = re.search(r'([國高][一二三][\u4e00-\u9fa5\d]+)', t)
            if m: res.append(m.group(1))
        return res

    # 3. 掃描
    print('=== 音樂課衝突檢查報告 ===\n')
    found_conflict = False
    for s in scheduled:
        mid = s['matchId']
        date_str = s['date']
        p_idx = s['periodIndex']
        
        y, m, d = map(int, date_str.split('-'))
        dt = datetime.date(y, m, d)
        if dt.weekday() >= 5: continue 
        day_key = DAY_MAP[dt.weekday()]
        
        match_data = matches_map.get(mid)
        if not match_data: continue
        
        classes = get_classes(match_data)
        for cls in classes:
            # 找到對應的班級課表
            cls_key = next((k for k in class_schedules['schedules'].keys() if cls in k), None)
            if cls_key:
                day_sched = class_schedules['schedules'][cls_key].get(day_key, [])
                if p_idx < len(day_sched):
                    cell = day_sched[p_idx]
                    if cell and '音樂' in cell:
                        found_conflict = True
                        print(f"🚨 發現衝突！")
                        print(f"   日期：{date_str} ({day_key}) 第 {PERIOD_NAMES[p_idx]} 節")
                        print(f"   賽事：{match_data.get('category')} | {match_data.get('teamA')} VS {match_data.get('teamB')}")
                        print(f"   衝突：{cls} 此時段為「{cell.split('|')[0]}」")
                        print("-" * 45)

    if not found_conflict:
        print("✅ 目前所有已排定賽程都沒有撞到音樂課。")

if __name__ == "__main__":
    check()
