import json
import re

def update_index_local(index_path, matches_path):
    with open(matches_path, 'r', encoding='utf-8') as f:
        matches_json = f.read()
    
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Update EMBEDDED_MATCHES
    # Pattern: const EMBEDDED_MATCHES = [ ... ];
    # Since it's a large block, we look for the start and end
    start_tag = "const EMBEDDED_MATCHES = ["
    end_tag = "];"
    
    # Find the start and then the NEXT ];
    start_idx = content.find(start_tag)
    if start_idx != -1:
        # Find the closing ]; of the array
        # We assume the array ends before the next function or script block
        # Actually, let's look for the specific structure I saw earlier
        end_idx = content.find("];", start_idx)
        if end_idx != -1:
            new_embedded = f"const EMBEDDED_MATCHES = {matches_json};"
            content = content[:start_idx] + new_embedded + content[end_idx+2:]
            print("Updated EMBEDDED_MATCHES")

    # 2. Update the mocked fetch in loadMatches
    # Pattern: const res = ({ ok: true, json: async () => ([ ... ]) });
    mock_start = "const res = ({ ok: true, json: async () => (["
    mock_end = "]) });"
    
    start_idx = content.find(mock_start)
    if start_idx != -1:
        end_idx = content.find(mock_end, start_idx)
        if end_idx != -1:
            new_mock = f"const res = ({{ ok: true, json: async () => ({matches_json}) }});"
            content = content[:start_idx] + new_mock + content[end_idx+len(mock_end):]
            print("Updated mocked fetch in loadMatches")

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("index_local.html updated successfully.")

if __name__ == "__main__":
    update_index_local('d:/classVSclass/index_local.html', 'd:/classVSclass/matches_cleaned.json')
