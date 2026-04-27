import pandas as pd
import json
import sys
import os

def sync():
    xlsx_path = 'd:/classVSclass/CHSH_Sports_Matches_2026_4_24.xlsx'
    matches_path = 'd:/classVSclass/matches.json'
    
    print(f"Reading {xlsx_path}...")
    df = pd.read_excel(xlsx_path)
    
    matches = []
    for i, row in df.iterrows():
        # Clean up category and team names
        cat = str(row['賽事類別']).strip()
        teamA = str(row['隊伍 A']).strip()
        teamB = str(row['隊伍 B']).strip()
        status = str(row['比賽狀態']).strip()
        score_raw = str(row['目前比數']).strip().replace('-', ':')
        winner = str(row['獲勝隊伍']).strip()
        
        m = {
            "id": f"{cat}_{i}",
            "category": cat,
            "teamA": teamA,
            "teamB": teamB,
            "status": status,
            "score": score_raw,
            "winner": winner if winner != "進行中" else None
        }
        
        if ":" in score_raw:
            try:
                parts = score_raw.split(':')
                m["scoreA"] = int(parts[0])
                m["scoreB"] = int(parts[1])
            except:
                pass
        
        matches.append(m)

    print(f"Syncing {len(matches)} matches...")
    with open(matches_path, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    
    print("Success! matches.json updated.")

if __name__ == "__main__":
    sync()
