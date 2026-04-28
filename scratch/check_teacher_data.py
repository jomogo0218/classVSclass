import json

with open('schedules.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Show ALL data for 高二信 and 高二忠 properly
target = ['高二信', '高二忠']

for cls in data['classes']:
    cls_clean = cls.replace(' ', '')
    if not any(cls_clean.startswith(t.replace(' ', '')) for t in target):
        continue
    
    print(f'\n=== {cls} ===')
    sched = data['schedules'].get(cls, {})
    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
        periods = sched.get(day, [])
        for i, p in enumerate(periods):
            if p and p.strip() and p != '---':
                parts = p.split('|')
                subj = parts[0].strip() if parts else ''
                teacher = parts[1].strip() if len(parts) > 1 else '(無)'
                print(f'  {day} P{i}: 科目="{subj}" 老師="{teacher}"')
