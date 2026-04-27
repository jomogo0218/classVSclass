with open('index_local.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find the init function in the HTML
idx = html.find("async function init()")
if idx < 0:
    print("ERROR: init() not found in HTML")
else:
    # Extract init function (find the closing brace at the same level)
    snippet = html[idx:idx+2000]
    print("init() function in index_local.html:")
    print(snippet[:2000])
