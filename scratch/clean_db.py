import json
from collections import defaultdict

def clean_matches(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    seen_matches = {} # (cat, teamA, teamB) -> first_id
    unique_matches = []
    removed_ids = []
    
    for m in matches:
        # Create a canonical key (teams sorted)
        teams = sorted([m['teamA'].strip(), m['teamB'].strip()])
        key = (m['category'].strip(), teams[0], teams[1])
        
        if key in seen_matches:
            removed_ids.append(m['id'])
            continue
        
        seen_matches[key] = m['id']
        unique_matches.append(m)
    
    print(f"Original matches: {len(matches)}")
    print(f"Unique matches: {len(unique_matches)}")
    print(f"Removed duplicate IDs: {removed_ids}")
    
    return unique_matches

if __name__ == "__main__":
    cleaned = clean_matches('d:/classVSclass/matches.json')
    with open('d:/classVSclass/matches_cleaned.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print("Cleaned data saved to matches_cleaned.json")
