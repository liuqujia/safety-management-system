import paramiko
import io

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.31.105', port=22, username='Kirito', password='Jia501688921')

sftp = ssh.open_sftp()

print("读取issues.py...")
with sftp.file('/vol2/1000/Docker/anquan/backend/app/api/endpoints/issues.py', 'r') as f:
    content = f.read().decode('utf-8')

import_code = '''

@router.post("/import-from-word")
async def import_from_word(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        doc = Document(io.BytesIO(contents))
        
        imported_count = 0
        errors = []
        project_name = ""
        
        for paragraph in doc.paragraphs:
            if "企业名称" in paragraph.text:
                project_name = paragraph.text.replace("企业名称：", "").replace("企业名称:", "").strip()
        
        for table in doc.tables:
            for row_idx, row in enumera            for row_idx, row in if row_idx == 0:
                    continue
                
                try:
                    cells = row.cells
                    if len(cells) < 6:
                        continue
                    
                    title = cells[2].text.strip() if len(cells) > 2 else ""
                    if not title:
                        continue
                    
                    description = cells[3].text.strip() if len(cells) > 3 else ""
                    rectification = cells[4].text.strip() if len(cells) > 4 else ""
                    remarks = cells[5].text.strip() if len(cells) > 5 else ""
                    
                    deadline = None
                    if "时限" in remarks:
                        import re
                        match = re.search(r'(\d+月\d+日)', remarks)
                        if match:
                            deadline = match.group(1)
                    
                    issue_data = {
                        'title': title,
                        'description': description,
                        'location': '',
                        'severity': '一般',
                        'deadline': deadline,
                        'project_name': project_name,
                        'responsible_person': '',
                        'status': '待整改'
                    }
                    
                    db_issue = Issue(**issue_data)
                    db.add(db_issue)
                    db.commit()
                    db.refresh(db_issue)
                    imported_count += 1
                except Exception as e:
                    errors.append(f"第{row_idx}行导入失败: {str(e)}")
        
        db.commit()
        
        return {
            'success': True,
            'imported_count': imported_count,
            'errors': errors
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}
'''

content = content + import_code

if 'from docx import Document' not in content:
    content = content.replace('from fastapi import', 'from docx import Document\nfrom fastapi import')

print("写入issues.py...")
with sftp.file('/vol2/1000/Docker/anquan/backend/app/api/endpoints/issues.py', 'w') as f:
    f.write(content.encode('utf-8'))

print("读取requirements.txt...")
with sftp.file('/vol2/1000/Docker/anquan/backend/requirements.txt', 'r') as f:
    req_content = f.read().decode('utf-8')

if 'python-docx' not in req_content:
    req_content = req_content + '\npython-docx==1.1.0\n'
    print("写入requirements.txt...")
    with sftp.file('/vol2/1000/Docker/anquan/backend/requirements.txt', 'w') as f:
        f.write(req_content.encode('utf-8'))

sftp.close()

print("重启Docker服务...")
stdin, stdout, stderr = ssh.exec_command('cd /vol2/1000/Docker/anquan/backend && docker compose down && docker compose up -d --build')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

ssh.close()
print('后端修改完成！')
