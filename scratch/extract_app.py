with open('index_local.html', 'rb') as f:
    data = f.read()

html = data.decode('utf-8', errors='replace')

# Find the app code - look for the function renderTable marker
start_marker = "function renderTable"
app_start = html.rfind(start_marker)
if app_start == -1:
    print("ERROR: renderTable not found")
else:
    # Go back to find the start of 'use strict'
    section = html[:app_start]
    strict_pos = section.rfind("'use strict'")
    if strict_pos == -1:
        strict_pos = app_start
    
    # Find the closing script tag
    end_tag = html.find('</script>', app_start)
    if end_tag == -1:
        print("ERROR: closing script tag not found")
    else:
        app_code = html[strict_pos:end_tag]
        with open('app.js', 'w', encoding='utf-8') as out:
            out.write(app_code)
        print(f"SUCCESS: Extracted {len(app_code)} chars of app code")
        print("First 300 chars:")
        print(app_code[:300])
