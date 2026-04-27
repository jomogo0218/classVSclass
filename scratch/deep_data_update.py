
import json
import os

def deep_data_update():
    print("Executing Deep Data Update from Excel screenshot...")
    
    path = 'd:/classVSclass/matches.json'
    with open(path, 'r', encoding='utf-8') as f:
        matches = json.load(f)

    # 完整掃描截圖中所有已結束的比賽
    all_results = [
        # 高二女排
        {"cat": "高二女排", "a": "高二仁 蘇愛甯", "b": "高二孝 顏怡勲", "s": "25:21", "w": "高二仁 蘇愛甯"},
        {"cat": "高二女排", "a": "高二孝 顏怡勲", "b": "高二忠 何品蓉", "s": "25:16", "w": "高二孝 顏怡勲"},
        {"cat": "高二女排", "a": "高二信 蔡沂潔", "b": "高二愛 方奕婷", "s": "15:25", "w": "高二愛 方奕婷"},
        {"cat": "高二女排", "a": "高二仁 蘇愛甯", "b": "高二愛 方奕婷", "s": "21:25", "w": "高二愛 方奕婷"},
        
        # 高二男排
        {"cat": "高二男排", "a": "高二仁 馮宥鑫", "b": "高二愛 胡廷安", "s": "19:25", "w": "高二愛 胡廷安"},
        {"cat": "高二男排", "a": "高二信 方晙昊", "b": "高二愛 胡廷安", "s": "25:21", "w": "高二愛 胡廷安"},
        
        # 國二女排
        {"cat": "國二女排", "a": "國二4 陳一汝", "b": "國二2 方倚喬", "s": "5:25", "w": "國二2 方倚喬"},
        {"cat": "國二女排", "a": "國二4 陳一汝", "b": "國二1 徐嘉儀", "s": "25:23", "w": "國二4 陳一汝"},
        
        # 國二男排 (這一組資料非常多)
        {"cat": "國二男排", "a": "國二5 方騰毅", "b": "國二2 安立生", "s": "18:25", "w": "國二2 安立生"},
        {"cat": "國二男排", "a": "國二5 方騰毅", "b": "國二3 陳冠文", "s": "21:25", "w": "國二3 陳冠文"},
        {"cat": "國二男排", "a": "國二2 安立生", "b": "國二1 莊明燊", "s": "25:18", "w": "國二2 安立生"},
        {"cat": "國二男排", "a": "國二2 安立生", "b": "國二3 陳冠文", "s": "25:15", "w": "國二2 安立生"},
        {"cat": "國二男排", "a": "國二2 安立生", "b": "國二4 沈鈺哲", "s": "25:19", "w": "國二2 安立生"},
        {"cat": "國二男排", "a": "國二1 莊明燊", "b": "國二4 沈鈺哲", "s": "21:25", "w": "國二4 沈鈺哲"},
        {"cat": "國二男排", "a": "國二3 陳冠文", "b": "國二4 沈鈺哲", "s": "25:21", "w": "國二3 陳冠文"},
        
        # 國三男籃
        {"cat": "國三男籃", "a": "國三4 張育瑞", "b": "國三3 林暄恒", "s": "25:42", "w": "國三4 張育瑞"},
        {"cat": "國三男籃", "a": "國三3 林暄恒", "b": "國三2 張嵩豪", "s": "18:45", "w": "國三2 張嵩豪"},
        {"cat": "國三男籃", "a": "國三5 劉得名", "b": "國三3 林暄恒", "s": "42:42", "w": "國三5 劉得名"},
    ]

    for res in all_results:
        found = False
        for m in matches:
            # 寬鬆匹配隊伍名稱（包含部分字元即可）
            if (res['a'] in m['teamA'] and res['b'] in m['teamB']) or \
               (res['a'] in m['teamB'] and res['b'] in m['teamA']):
                m['status'] = "✅ 已結束"
                m['score'] = res['s']
                m['winner'] = res['w']
                p = res['s'].split(':')
                m['scoreA'] = int(p[0])
                m['scoreB'] = int(p[1])
                found = True
        if not found:
            print(f"Match not found in JSON: {res['a']} vs {res['b']}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    
    print("Deep Update Complete.")

if __name__ == "__main__":
    deep_data_update()
