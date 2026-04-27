"""
read_excel.py - Read the match schedule Excel file and display its contents
"""
try:
    import openpyxl
except ImportError:
    import subprocess
    subprocess.run(['pip', 'install', 'openpyxl'], check=True)
    import openpyxl

import json

# Try the newer file first
filename = 'CHSH_Sports_Matches_2026_4_24.xlsx'

wb = openpyxl.load_workbook(filename, data_only=True)
print(f'Sheets: {wb.sheetnames}')

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    print(f'\n=== Sheet: {sheet_name} ({ws.max_row} rows x {ws.max_column} cols) ===')
    
    # Read headers
    headers = []
    for cell in ws[1]:
        headers.append(str(cell.value) if cell.value is not None else '')
    print('Headers:', headers)
    
    # Read all rows
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if any(v is not None for v in row):
            rows.append(list(row))
    
    print(f'Data rows: {len(rows)}')
    
    # Show first 10 rows
    for i, row in enumerate(rows[:10]):
        print(f'  Row {i+2}: {row}')
    
    if len(rows) > 10:
        print(f'  ... ({len(rows)-10} more rows)')
