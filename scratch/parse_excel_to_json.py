"""
parse_excel_to_json.py
Reads CHSH_Sports_Matches_2026_4_24.xlsx and converts to matches.json format.
Columns: 賽事ID, 地點, 隊A, 隊B, 比數, 勝者, 狀態, 建立時間
"""
import openpyxl
import json
import sys

filename = 'CHSH_Sports_Matches_2026_4_24.xlsx'
wb = openpyxl.load_workbook(filename, data_only=True)

output_log = []

for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    output_log.append(f'Sheet: {repr(sheet_name)}, rows={ws.max_row}, cols={ws.max_column}')
    
    headers = [str(cell.value) if cell.value is not None else '' for cell in ws[1]]
    output_log.append(f'Headers: {headers}')
    
    all_rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if any(v is not None for v in row):
            all_rows.append(list(row))
    
    output_log.append(f'Total data rows: {len(all_rows)}')
    
    # Show all rows with index
    for i, row in enumerate(all_rows):
        # Convert each cell to string safely
        row_str = []
        for cell in row:
            if cell is None:
                row_str.append('None')
            else:
                row_str.append(repr(str(cell)))
        output_log.append(f'R{i+2}: ' + ' | '.join(row_str))

# Write to a file to avoid terminal encoding issues
with open('scratch/excel_data.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_log))

print('Done. Check scratch/excel_data.txt')
print(f'Total log lines: {len(output_log)}')
