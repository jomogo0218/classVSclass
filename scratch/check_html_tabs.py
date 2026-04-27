import re
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Tab buttons (data-tab):")
for m in re.finditer(r'data-tab="([^"]+)"', html):
    print(f"  {m.group(1)}")

print()
print("Tab content IDs:")
for m in re.finditer(r'id="(tab-[^"]+)"', html):
    print(f"  {m.group(1)}")

print()
print("categorySidebar element:", 'categorySidebar' in html)
print("tournamentContainer element:", 'tournamentContainer' in html)
print("selectedCategoryTitle element:", 'selectedCategoryTitle' in html)
