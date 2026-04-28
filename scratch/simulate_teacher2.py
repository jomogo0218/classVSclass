import json

with open('schedules.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

lines = []

def simulate_get_teacher(className, dayIdx, periodIndex):
    targetKey = className.replace(' ', '')
    found_key = None
    candidates = []
    for k in data['schedules'].keys():
        kClean = k.replace(' ', '')
        if targetKey.startswith(kClean) or kClean.startswith(targetKey):
            candidates.append(k)
            if found_key is None:
                found_key = k
    
    lines.append(f'\nInput: className={repr(className)}, dayIdx={dayIdx}, periodIdx={periodIndex}')
    lines.append(f'targetKey={repr(targetKey)}')
    lines.append(f'Candidates: {candidates}')
    lines.append(f'actualKey: {repr(found_key)}')
    
    if not found_key:
        lines.append('RESULT: No match!')
        return
    
    day_keys = ['Mon','Tue','Wed','Thu','Fri']
    dayKey = day_keys[dayIdx]
    classSched = data['schedules'].get(found_key, {})
    periods = classSched.get(dayKey, [])
    lines.append(f'dayKey={dayKey}, total periods={len(periods)}')
    
    if periodIndex < len(periods):
        raw = (periods[periodIndex] or '').strip()
        lines.append(f'P{periodIndex} = {repr(raw)}')
        if '|' in raw:
            parts = raw.split('|')
            lines.append(f'  科目={repr(parts[0].strip())}')
            lines.append(f'  老師={repr(parts[1].strip() if len(parts)>1 else "")}')
    else:
        lines.append(f'periodIndex {periodIndex} out of range!')

simulate_get_teacher('高二信 菜沂潔', 2, 1)
simulate_get_teacher('高二忠 何品蓉', 2, 1)

with open('scratch/sim_result2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Done')
