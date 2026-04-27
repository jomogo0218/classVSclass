import json

def cleanup_to_96(matches_path):
    with open(matches_path, 'r', encoding='utf-8') as f:
        matches = json.load(f)
    
    # User says there should be 96. Original is 106.
    # We remove the 10 duplicates from "高二女排" (IDs 10-19).
    to_remove = set(range(10, 20))
    cleaned = [m for m in matches if m['id'] not in to_remove]
    
    print(f"Original count: {len(matches)}")
    print(f"Cleaned count: {len(cleaned)}")
    
    with open(matches_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    
    return cleaned

if __name__ == "__main__":
    cleanup_to_96('d:/classVSclass/matches.json')
