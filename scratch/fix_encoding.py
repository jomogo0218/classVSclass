import codecs

# 讀取原本正常的上半部
with codecs.open('app.js', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()
    header = lines[:1549]

# 讀取恢復的功能區塊
with codecs.open('scratch/restored_functions.js', 'r', encoding='utf-8') as f:
    restored = f.read()

# 合併並強制輸出為 UTF-8
with codecs.open('app.js', 'w', encoding='utf-8') as f:
    f.writelines(header)
    f.write("\n")
    f.write(restored)

print("✅ app.js encoding fixed and functions restored.")
