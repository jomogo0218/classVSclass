import json

with open('schedules.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Simulate what getOriginalTeacher does for the two classes
# teamA = '高二信 菜沂潔', dayIdx = 2 (Wed), periodIndex = 1 (第1節)

def simulate_get_teacher(className, dayIdx, periodIndex):
    targetKey = className.replace(' ', '')
    
    # Find matching key
    found_key = None
    candidates = []
    for k in data['schedules'].keys():
        kClean = k.replace(' ', '')
        if targetKey.startswith(kClean) or kClean.startswith(targetKey):
            candidates.append((k, kClean))
            if found_key is None:
                found_key = k
    
    print(f'\nInput: className={repr(className)}, dayIdx={dayIdx}, periodIdx={periodIndex}')
    print(f'targetKey={repr(targetKey)}')
    print(f'Candidates found: {candidates}')
    print(f'actualKey (first match): {repr(found_key)}')
    
    if not found_key:
        print('RESULT: No match found!')
        return
    
    day_keys = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    dayKey = day_keys[dayIdx] if dayIdx < len(day_keys) else None
    print(f'dayKey: {repr(dayKey)}')
    
    classSched = data['schedules'].get(found_key, {})
    periods = classSched.get(dayKey, [])
    print(f'Periods on {dayKey}: {len(periods)} entries')
    
    if periodIndex < len(periods):
        raw = (periods[periodIndex] or '').strip()
        print(f'P{periodIndex} raw value: {repr(raw)}')
        if raw and '|' in raw:
            parts = raw.split('|')
            subj = parts[0].strip()
            teacher = parts[1].strip() if len(parts) > 1 else ''
            print(f'→ 科目: {repr(subj)}, 老師: {repr(teacher)}')
        else:
            print(f'→ Raw: {repr(raw)} (no | separator)')
    else:
        print(f'ERROR: periodIndex {periodIndex} out of range (len={len(periods)})')

# Test with the actual team names from the match
print('=== Test cases ===')
simulate_get_teacher('高二信 菜沂潔', 2, 1)  # Wed P1
simulate_get_teacher('高二忠 何品蓉', 2, 1)  # Wed P1
