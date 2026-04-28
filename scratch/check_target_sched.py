import json

with open('schedules.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# We need to find what's in the schedule for 高二信 and 高二忠
# The match was scheduled on Wednesday (4/29), period index 1 (第1節)
# dayIdx for Wednesday = 2 (Mon=0,Tue=1,Wed=2,Thu=3,Fri=4)
# periodIndex = 1 (早自習=0, 第1節=1, 第2節=2...)
# dayKey = 'Wed', periods[1]

target_classes = {
    '高二信': ['高二信', '高二信 菜沂潔', '高二信菜沂潔'],
    '高二忠': ['高二忠', '高二忠 何品蓉', '高二忠何品蓉'],
}

day_key = 'Wed'  # 週三

results = []

for cls, variants in target_classes.items():
    found_key = None
    for k in data['schedules'].keys():
        k_clean = k.replace(' ', '')
        for v in variants:
            if k_clean.startswith(v.replace(' ', '')) or v.replace(' ', '').startswith(k_clean):
                found_key = k
                break
        if found_key:
            break
    
    results.append(f'\n=== Searching for: {cls} ===')
    if found_key:
        results.append(f'  Found key: {repr(found_key)}')
        sched = data['schedules'][found_key]
        periods = sched.get(day_key, [])
        results.append(f'  {day_key} schedule ({len(periods)} periods):')
        for i, p in enumerate(periods):
            marker = ' ← TARGET' if i == 1 else ''
            results.append(f'    P{i}: {repr(p)}{marker}')
    else:
        results.append(f'  NOT FOUND in schedules!')
        results.append(f'  Available keys containing 高二:')
        for k in sorted(data['schedules'].keys()):
            if '高二' in k:
                results.append(f'    {repr(k)}')

with open('scratch/target_schedule_check.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print('Done. See scratch/target_schedule_check.txt')
