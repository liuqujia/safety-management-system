import glob
import re

files = glob.glob('/Users/kirito/Downloads/12/111/**/export.py', recursive=True)
if files:
    with open(files[0], 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(
        'headers={"Content-Disposition": f"attachment; filename*=UTF-8\'\'{filename}"}',
        'headers={"Content-Disposition": f"attachment; filename={filename}"}'
    )
    
    if 'from urllib.parse import quote' not in content:
        content = content.replace(
            'from datetime import datetime',
            'from datetime import datetime\nfrom urllib.parse import quote'
        )
    
    content = content.replace(
        'filename = f"安全问题_{timestamp}.xlsx"',
        'filename = f"safety_issues_{timestamp}.xlsx"'
    )
    
    content = content.replace(
        'filename = f"整改回复_{timestamp}.xlsx"',
        'filename = f"rectification_{timestamp}.xlsx"'
    )
    
    content = content.replace(
        'filename = f"安全问题汇总_{timestamp}.xlsx"',
        'filename = f"safety_summary_{timestamp}.xlsx"'
    )
    
    with open(files[0], 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复完成！")
