
import json
import os

def update_results_from_excel():
    print("Updating match results from the provided spreadsheet data...")
    
    path = 'd:/classVSclass/matches.json'
    with open(path, 'r', encoding='utf-8') as f:
        matches = json.load(f)

    # 模擬從圖片解析出的關鍵結果數據
    results = [
        # 高二女排
        {"teamA": "高二仁 蘇愛甯", "teamB": "高二孝 顏怡勲", "score": "25:21", "winner": "高二仁 蘇愛甯"},
        {"teamA": "高二孝 顏怡勲", "teamB": "高二忠 何品蓉", "score": "25:16", "winner": "高二孝 顏怡勲"},
        {"teamA": "高二信 蔡沂潔", "teamB": "高二愛 方奕婷", "score": "15:25", "winner": "高二愛 方奕婷"},
        {"teamA": "高二仁 蘇愛甯", "teamB": "高二愛 方奕婷", "score": "21:25", "winner": "高二愛 方奕婷"},
        
        # 高二男排
        {"teamA": "高二仁 馮宥鑫", "teamB": "高二愛 胡廷安", "score": "19:25", "winner": "高二愛 胡廷安"},
        {"teamA": "高二信 方晙昊", "teamB": "高二愛 胡廷安", "score": "25:21", "winner": "高二愛 胡廷安"}, # 圖片顯示胡廷安贏
        
        # 國二女排
        {"teamA": "國二4 陳一汝", "teamB": "國二2 方倚喬", "score": "5:25", "winner": "國二2 方倚喬"},
        {"teamA": "國二4 陳一汝", "teamB": "國二1 徐嘉儀", "score": "25:23", "winner": "國二4 陳一汝"},
        
        # 國二男排
        {"teamA": "國二5 方騰毅", "teamB": "國二2 安立生", "score": "18:25", "winner": "國二2 安立生"},
        {"teamA": "國二5 方騰毅", "teamB": "國二3 陳冠文", "score": "21:25", "winner": "國二3 陳冠文"},
        {"teamA": "國二2 安立生", "teamB": "國二1 莊明燊", "score": "25:18", "winner": "國二2 安立生"},
        {"teamA": "國二2 安立生", "teamB": "國二3 陳冠文", "score": "25:15", "winner": "國二2 安立生"},
        {"teamA": "國二2 安立生", "teamB": "國二4 沈鈺哲", "score": "25:19", "winner": "國二2 安立生"},
        {"teamA": "國二1 莊明燊", "teamB": "國二4 沈鈺哲", "score": "21:25", "winner": "國二4 沈鈺哲"},
        {"teamA": "國二3 陳冠文", "teamB": "國二4 沈鈺哲", "score": "25:21", "winner": "國二3 陳冠文"},
        
        # 國三男籃
        {"teamA": "國三4 張育瑞", "teamB": "國三3 林暄恒", "score": "25:42", "winner": "國三4 張育瑞"},
        {"teamA": "國三3 林暄恒", "teamB": "國三2 張嵩豪", "score": "18:45", "winner": "國三2 張嵩豪"},
        {"teamA": "國三5 劉得名", "teamB": "國三3 林暄恒", "score": "42:42", "winner": "國三5 劉得名"},
        
        # 羽球晉級結果
        {"teamA": "高三孝 李宇恩", "teamB": "高二信 蘇宥嘉", "score": "5:2", "winner": "高三孝 李宇恩"},
        {"teamA": "高二愛 蔡矅宇", "teamB": "高一忠 郭育綸", "score": "5:0", "winner": "高二愛 蔡矅宇"},
        {"teamA": "高一愛", "teamB": "高二忠 陳冠志", "score": "5:1", "winner": "高一愛"},
        {"teamA": "輪空", "teamB": "高三信 王威喆", "score": "0:21", "winner": "高三信 王威喆"},
        {"teamA": "輪空", "teamB": "高三愛 王宏益", "score": "0:21", "winner": "高三愛 王宏益"},
        {"teamA": "高二愛 蔡矅宇", "teamB": "高三信 王威喆", "score": "4:1", "winner": "高二愛 蔡矅宇"},
        {"teamA": "國二1 蘇品乂", "teamB": "國二5", "score": "2:3", "winner": "國二5"},
        {"teamA": "輪空", "teamB": "國三4 蕭逸傑", "score": "0:21", "winner": "國三4 蕭逸傑"}
    ]

    for res in results:
        found = False
        for m in matches:
            # 匹配隊伍 (不論 A/B 順序)
            if (m['teamA'] == res['teamA'] and m['teamB'] == res['teamB']) or \
               (m['teamA'] == res['teamB'] and m['teamB'] == res['teamA']):
                m['status'] = "✅ 已結束"
                m['score'] = res['score']
                m['winner'] = res['winner']
                # 解析分數
                parts = res['score'].split(':')
                m['scoreA'] = int(parts[0])
                m['scoreB'] = int(parts[1])
                found = True
                break
    
    # 儲存更新後的資料
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)

    print("Data entry complete. Standings will update automatically.")

if __name__ == "__main__":
    update_results_from_excel()
