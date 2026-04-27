with open('schedules.json', 'rb') as f:
    data = f.read()

# Check BOM
if data[:3] == b'\xef\xbb\xbf':
    print('BOM: UTF-8 with BOM')
elif data[:2] == b'\xff\xfe':
    print('BOM: UTF-16 LE')
else:
    print('No BOM')

# Try to detect by finding known Chinese class name
# 高二仁 in UTF-8 is e9 ab 98 e4 ba 8c e4 bb 81
utf8_pattern = b'\xe9\xab\x98\xe4\xba\x8c'  # 高二
cp950_pattern = b'\xb0\xaa\xa4\xf3'  # 高二 in Big5

utf8_found = utf8_pattern in data
cp950_found = cp950_pattern in data

print(f'UTF-8 "高二" found: {utf8_found}')
print(f'Big5 "高二" found: {cp950_found}')

if cp950_found:
    print('=> File is BIG5/CP950 encoded')
    # Show sample decoded as Big5
    idx = data.find(cp950_pattern)
    sample = data[idx:idx+30].decode('cp950', errors='replace')
    print(f'Sample (Big5 decoded): {sample}')
elif utf8_found:
    print('=> File is UTF-8 encoded')
    idx = data.find(utf8_pattern)
    sample = data[idx:idx+30].decode('utf-8', errors='replace')
    print(f'Sample (UTF-8 decoded): {sample}')
else:
    print('=> Cannot determine encoding')
    print('First 50 bytes:', data[:50].hex())
