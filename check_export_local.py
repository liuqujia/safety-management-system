import glob

files = glob.glob('/Users/kirito/Downloads/12/111/**/export.py', recursive=True)
print(f"找到文件: {files}")

if files:
    with open(files[0], 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines[280:300], start=281):
            print(f"{i}: {line}")
