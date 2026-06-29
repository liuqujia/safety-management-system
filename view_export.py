import glob

files = glob.glob('/Users/kirito/Downloads/12/111/**/export.py', recursive=True)
if files:
    with open(files[0], 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines[1:150], start=1):
            print(f"{i}: {line}")
