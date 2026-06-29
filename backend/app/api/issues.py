from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import os
import uuid
from PIL import Image
import io
import re

from app.database import get_db
from app.models import SafetyIssue, Photo
from app.schemas import IssueCreate, IssueUpdate, IssueResponse
from app.utils import save_upload_file

router = APIRouter(prefix="/api/issues", tags=["问题管理"])

@router.get("/", response_model=List[IssueResponse])
def get_issues(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SafetyIssue)

    if status:
        query = query.filter(SafetyIssue.status == status)
    if severity:
        query = query.filter(SafetyIssue.severity == severity)

    issues = query.order_by(SafetyIssue.create_time.desc()).offset(skip).limit(limit).all()
    return [issue.to_dict() for issue in issues]

@router.get("/{issue_id}", response_model=IssueResponse)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(SafetyIssue).filter(SafetyIssue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")
    return issue.to_dict()

@router.post("/", response_model=IssueResponse)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    db_issue = SafetyIssue(**issue.dict())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue.to_dict()

@router.post("/with-photos", response_model=IssueResponse)
async def create_issue_with_photos(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    severity: str = Form("一般"),
    responsible_person: Optional[str] = Form(None),
    deadline: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    photos: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    db_issue = SafetyIssue(
        title=title,
        description=description,
        location=location,
        severity=severity,
        responsible_person=responsible_person,
        deadline=date.fromisoformat(deadline) if deadline else None,
        notes=notes
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)

    for photo in photos:
        if photo.filename:
            file_path, file_name = await save_upload_file(photo, db_issue.id, "问题照片")
            db_photo = Photo(
                issue_id=db_issue.id,
                photo_type="问题照片",
                file_path=file_path,
                file_name=file_name
            )
            db.add(db_photo)

    db.commit()
    db.refresh(db_issue)
    return db_issue.to_dict()

@router.put("/{issue_id}", response_model=IssueResponse)
def update_issue(issue_id: int, issue: IssueUpdate, db: Session = Depends(get_db)):
    db_issue = db.query(SafetyIssue).filter(SafetyIssue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    update_data = issue.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_issue, key, value)

    db.commit()
    db.refresh(db_issue)
    return db_issue.to_dict()

@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    db_issue = db.query(SafetyIssue).filter(SafetyIssue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    for photo in db_issue.photos:
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)

    db.delete(db_issue)
    db.commit()
    return {"message": "删除成功"}

@router.post("/{issue_id}/photos", response_model=IssueResponse)
async def upload_photo(
    issue_id: int,
    photo_type: str = Form(...),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    db_issue = db.query(SafetyIssue).filter(SafetyIssue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    for photo in photos:
        if photo.filename:
            file_path, file_name = await save_upload_file(photo, issue_id, photo_type)
            db_photo = Photo(
                issue_id=issue_id,
                photo_type=photo_type,
                file_path=file_path,
                file_name=file_name
            )
            db.add(db_photo)

    db.commit()
    db.refresh(db_issue)
    return db_issue.to_dict()

@router.put("/{issue_id}/status")
def update_status(
    issue_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    db_issue = db.query(SafetyIssue).filter(SafetyIssue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    if status not in ["待整改", "整改中", "已完成"]:
        raise HTTPException(status_code=400, detail="状态值无效")

    db_issue.status = status
    db.commit()
    db.refresh(db_issue)
    return db_issue.to_dict()

@router.post("/import-from-word")
async def import_from_word(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        from docx import Document
        
        contents = await file.read()
        doc = Document(io.BytesIO(contents))
        
        imported_count = 0
        errors = []
        project_name = ""
        
        debug_info = []
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                debug_info.append(f"段落: {text[:100]}")
            if "企业名称" in text:
                project_name = text.replace("企业名称：", "").replace("企业名称:", "").strip()
            if "项目名称" in text:
                project_name = text.replace("项目名称：", "").replace("项目名称:", "").strip()
        
        debug_info.append(f"项目名称: {project_name}")
        debug_info.append(f"表格数量: {len(doc.tables)}")
        
        for table_idx, table in enumerate(doc.tables):
            debug_info.append(f"表格{table_idx}: {len(table.rows)}行 x {len(table.columns)}列")
            for row_idx, row in enumerate(table.rows):
                cells = row.cells
                row_texts = []
                for cell_idx, cell in enumerate(cells):
                    cell_text = cell.text.strip()
                    row_texts.append(f"[{cell_idx}]={cell_text[:50]}")
                debug_info.append(f"  行{row_idx}: {', '.join(row_texts)}")
                
                if row_idx == 0:
                    continue
                
                try:
                    title = ""
                    description = ""
                    notes = ""
                    deadline = None
                    
                    for cell in cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            if "隐患" in cell_text or "问题" in cell_text or len(cell_text) > 10:
                                if not title:
                                    title = cell_text
                                else:
                                    description = description + "\n" + cell_text
                            elif "法规" in cell_text or "条款" in cell_text or "标准" in cell_text:
                                description = description + "\n" + cell_text
                            elif "整改" in cell_text:
                                notes = notes + "\n" + cell_text
                            elif "时限" in cell_text or "期限" in cell_text:
                                match = re.search(r'(\d+月\d+日)', cell_text)
                                if match:
                                    deadline = match.group(1)
                    
                    if not title:
                        for cell in cells:
                            cell_text = cell.text.strip()
                            if cell_text and len(cell_text) > 5:
                                title = cell_text
                                break
                    
                    if title:
                        issue_data = {
                            'title': title[:200],
                            'description': description[:500] if description else None,
                            'location': '',
                            'severity': '一般',
                            'deadline': deadline,
                            'project_name': project_name,
                            'responsible_person': '',
                            'status': '待整改',
                            'notes': notes[:500] if notes else None
                        }
                        
                        db_issue = SafetyIssue(**issue_data)
                        db.add(db_issue)
                        db.commit()
                        db.refresh(db_issue)
                        imported_count += 1
                        debug_info.append(f"  -> 成功导入: {title[:50]}")
                    else:
                        debug_info.append(f"  -> 跳过（无标题）")
                except Exception as e:
                    errors.append(f"第{row_idx}行导入失败: {str(e)}")
        
        db.commit()
        
        return {
            'success': True,
            'imported_count': imported_count,
            'errors': errors,
            'project_name': project_name,
            'tables_found': len(doc.tables),
            'paragraphs_count': len(doc.paragraphs),
            'debug': debug_info[:50]
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}
