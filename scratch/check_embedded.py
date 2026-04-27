with open('index_local.html', 'r', encoding='utf-8') as f:
    html = f.read()

checks = [
    'EMBEDDED_SCHEDULES',
    'EMBEDDED_MATCHES',
    'EMBEDDED_SCHEDULED_DATA',
    'fetch(',
    'schedules.json',
    'loadScheduledMatches',
    'renderTournamentOverview',
]
print('=== index_local.html content check ===')
for c in checks:
    count = html.count(c)
    print(f'  {"YES" if count else "NO "} ({count}x): {c}')

# Check the guaranteed_build.py to understand what it embeds
with open('scratch/guaranteed_build.py', 'r', encoding='utf-8') as f:
    build = f.read()

print()
print('=== guaranteed_build.py check ===')
build_checks = ['EMBEDDED_SCHEDULES', 'EMBEDDED_MATCHES', 'schedules.json', 'matches.json']
for c in build_checks:
    print(f'  {"YES" if c in build else "NO "}: {c}')
