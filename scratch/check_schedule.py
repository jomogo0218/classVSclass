import json
with open('schedules.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== schedules.json structure ===')
print(f'Top-level keys: {list(data.keys())}')
print(f'Number of classes: {len(data["classes"])}')
print(f'All class names:')
for c in data['classes']:
    print(f'  "{c}"')

print()
print('=== Sample schedule for first class ===')
first_class = data['classes'][0]
sched = data['schedules'].get(first_class, {})
print(f'Class: "{first_class}"')
for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
    periods = sched.get(day, [])
    if periods:
        print(f'  {day}: {periods[:3]}')  # Show first 3 periods

print()
print('=== Checking for class with 高二仁 ===')
for c in data['classes']:
    if '2' in c or '二' in c:
        print(f'  Found: "{c}"')
