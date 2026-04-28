import json

with open('schedules.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Collect all unique teacher-field values
from collections import Counter
teacher_values = Counter()
subj_teacher_pairs = {}

for cls, sched in data['schedules'].items():
    for day, periods in sched.items():
        for i, p in enumerate(periods):
            if not p or '|' not in p:
                continue
            parts = p.split('|')
            subj = parts[0].strip()
            teacher = parts[1].strip() if len(parts) > 1 else ''
            teacher_values[teacher] += 1
            if subj not in subj_teacher_pairs:
                subj_teacher_pairs[subj] = set()
            subj_teacher_pairs[subj].add(teacher)

# Write results
lines = []
lines.append('=== All unique "teacher" field values (sorted by frequency) ===\n')
for t, count in teacher_values.most_common():
    lines.append(f'  ({count:3d}x) {repr(t)}')

lines.append('\n=== Subject → Teacher mappings ===')
for subj in sorted(subj_teacher_pairs.keys()):
    teachers = subj_teacher_pairs[subj]
    lines.append(f'\n  {repr(subj)}:')
    for t in sorted(teachers):
        lines.append(f'    → {repr(t)}')

with open('scratch/all_teachers.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('Done. Check scratch/all_teachers.txt')
print(f'Unique teacher values: {len(teacher_values)}')
