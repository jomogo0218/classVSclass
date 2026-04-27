import json

def clean_matches():
    with open('d:/classVSclass/matches.json', 'r', encoding='utf-8') as f:
        matches = json.load(f)

    # 1. Deduplicate by (category, teamA, teamB)
    seen = set()
    unique_matches = []
    
    # Special handle for "待定" - we want to keep all "待定" placeholder matches in elimination
    for m in matches:
        # Standardize team order for comparison to catch (A vs B) and (B vs A)
        teams = sorted([m['teamA'], m['teamB']])
        key = (m['category'], teams[0], teams[1])
        
        if m['teamA'] == "待定" and m['teamB'] == "待定":
            # Always keep placeholders
            unique_matches.append(m)
        elif key not in seen:
            unique_matches.append(m)
            seen.add(key)
        else:
            print(f"Removing duplicate: {m['category']} - {m['teamA']} vs {m['teamB']} (ID: {m['id']})")

    # 2. Refine Names
    for m in unique_matches:
        for key in ['teamA', 'teamB']:
            if m[key]:
                m[key] = m[key].replace("男單：", "").replace("10 ", "").strip()

    # 3. Re-group and Re-ID
    # Order by category and then by round logic
    def get_sort_key(m):
        cat = m['category']
        order = 99
        if "第 1 輪" in cat: order = 1
        elif "第 2 輪" in cat: order = 2
        elif "準決賽" in cat: order = 3
        elif "季軍賽" in cat: order = 4
        elif "決賽" in cat: order = 5
        return (cat.split(' ')[0], order, m['id'])

    unique_matches.sort(key=get_sort_key)

    # Re-assign sequential IDs to keep it clean
    for i, m in enumerate(unique_matches):
        m['id'] = i

    with open('d:/classVSclass/matches.json', 'w', encoding='utf-8') as f:
        json.dump(unique_matches, f, ensure_ascii=False, indent=2)

    print(f"Cleaned up! Total matches: {len(unique_matches)}")

if __name__ == "__main__":
    clean_matches()
