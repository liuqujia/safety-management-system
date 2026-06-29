from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
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
    project_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SafetyIssue)

    if status:
        query = query.filter(SafetyIssue.status == status)
    if severity:
        query = query.filter(SafetyIssue.severity == severity)
    if project_name:
        query = query.filter(SafetyIssue.project_name == project_name)

    issues = query.order_by(SafetyIssue.id.asc()).offset(skip).limit(limit).all()
    return [issue.to_dict() for issue in issues]


@router.get("/projects/list")
def get_projects(db: Session = Depends(get_db)):
    """获取所有不重复的项目名称"""
    rows = db.query(SafetyIssue.project_name).filter(
        SafetyIssue.project_name.isnot(None),
        SafetyIssue.project_name != ""
    ).distinct().all()
    return [r[0] for r in rows]

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

def parse_deadline(deadline_str):
    if not deadline_str:
        return None
    match = re.search(r'(\d+)月(\d+)日', deadline_str)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        year = datetime.now().year
        return date(year, month, day)
    return None

def extract_images_from_doc(doc, issue_id):
    images = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_data = rel.target_part.blob
            file_ext = os.path.splitext(rel.target_ref)[1] or '.png'
            file_name = f"{issue_id}_{uuid.uuid4().hex[:8]}{file_ext}"
            images.append((file_name, image_data))
    return images

@router.post("/preview-from-word")
async def preview_from_word(file: UploadFile = File(...)):
    """仅解析 Word，不写库；返回识别到的项目名称和隐患条目预览。"""
    try:
        from docx import Document

        contents = await file.read()
        doc = Document(io.BytesIO(contents))

        project_name = ""
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
            if "企业名称" in text:
                project_name = text.replace("企业名称：", "").replace("企业名称:", "").strip()
                project_name = project_name.split("隐患条数")[0].strip()
            if "项目名称" in text and not project_name:
                project_name = text.replace("项目名称：", "").replace("项目名称:", "").strip()

        items = []
        for table in doc.tables:
            for row_idx, row in enumerate(table.rows):
                if row_idx == 0:
                    continue
                cells = row.cells
                if len(cells) < 3:
                    continue
                title = cells[2].text.strip() if len(cells) >= 3 else ""
                description = cells[3].text.strip() if len(cells) >= 4 else ""
                notes = cells[4].text.strip() if len(cells) >= 5 else ""
                remarks = cells[5].text.strip() if len(cells) >= 6 else ""
                deadline = parse_deadline(remarks) if remarks else None
                if not title:
                    continue
                items.append({
                    "title": title[:200],
                    "description": description[:500] if description else None,
                    "notes": notes[:500] if notes else None,
                    "deadline": deadline.isoformat() if deadline else None,
                })

        return {
            "success": True,
            "project_name": project_name,
            "items": items,
            "tables_found": len(doc.tables),
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/import-from-word")
async def import_from_word(
    file: UploadFile = File(...),
    project_name: Optional[str] = Form(None),
    skip_indices: Optional[str] = Form(None),  # 逗号分隔的行索引，跳过这些行不导入
    db: Session = Depends(get_db)
):
    try:
        from docx import Document
        
        contents = await file.read()
        doc = Document(io.BytesIO(contents))
        
        imported_count = 0
        errors = []
        detected_project_name = ""
        
        debug_info = []
        
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:
                debug_info.append(f"段落: {text[:100]}")
            if "企业名称" in text:
                detected_project_name = text.replace("企业名称：", "").replace("企业名称:", "").strip()
                detected_project_name = detected_project_name.split("隐患条数")[0].strip()
            if "项目名称" in text:
                detected_project_name = text.replace("项目名称：", "").replace("项目名称:", "").strip()
        
        # 优先用前端传的 project_name（用户在预览框里可能改过），否则用文档里识别到的
        final_project_name = (project_name or detected_project_name or "").strip()
        
        debug_info.append(f"项目名称: {final_project_name}")
        debug_info.append(f"表格数量: {len(doc.tables)}")
        
        all_images = extract_images_from_doc(doc, 0)
        debug_info.append(f"文档中提取到图片数量: {len(all_images)}")
        
        image_idx = 0
        
        # 解析要跳过的行索引
        skip_set = set()
        if skip_indices:
            for idx_str in skip_indices.split(','):
                try:
                    skip_set.add(int(idx_str.strip()))
                except ValueError:
                    pass

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

                # 计算全局行索引
                global_row_idx = (table_idx * 1000) + row_idx
                if skip_set and global_row_idx in skip_set:
                    debug_info.append(f"  跳过（用户在预览中已删除）")
                    continue
                
                try:
                    title = ""
                    description = ""
                    notes = ""
                    deadline = None
                    
                    debug_info.append(f"  cells长度: {len(cells)}")
                    
                    # 表格列对应关系（标准隐患检查表模板）：
                    # cells[0]=序号, cells[1]=现场图片, cells[2]=检查发现的主要隐患或问题(title),
                    # cells[3]=法规名称/代码/条款号(description), cells[4]=整改措施或建议(notes),
                    # cells[5]=备注(内含"整改时限：X月X日"，用于解析 deadline)
                    if len(cells) >= 3:
                        title = cells[2].text.strip()
                        debug_info.append(f"  title值: '{title}'")
                    if len(cells) >= 4:
                        description = cells[3].text.strip()
                    if len(cells) >= 5:
                        notes = cells[4].text.strip()
                    if len(cells) >= 6:
                        remarks = cells[5].text.strip()
                        deadline = parse_deadline(remarks)
                        debug_info.append(f"  deadline值: {deadline}, remarks: '{remarks[:60]}'")
                    
                    if not title:
                        debug_info.append(f"  title为空，尝试查找")
                        for cell in cells:
                            cell_text = cell.text.strip()
                            if cell_text and len(cell_text) > 2:
                                title = cell_text
                                debug_info.append(f"  找到title: '{title}'")
                                break
                    
                    if title:
                        issue_data = {
                            'title': title[:200],
                            'description': description[:500] if description else None,
                            'location': '',
                            'severity': '一般',
                            'deadline': deadline,
                            'project_name': final_project_name,
                            'responsible_person': '',
                            'status': '待整改',
                            'notes': notes[:500] if notes else None
                        }
                        
                        try:
                            db_issue = SafetyIssue(**issue_data)
                            db.add(db_issue)
                            db.commit()
                            db.refresh(db_issue)
                            
                            if image_idx < len(all_images):
                                file_name, image_data = all_images[image_idx]
                                photos_dir = os.path.join("data", "photos", str(db_issue.id))
                                os.makedirs(photos_dir, exist_ok=True)
                                file_path = os.path.join(photos_dir, file_name)
                                with open(file_path, "wb") as f:
                                    f.write(image_data)
                                db_photo = Photo(
                                    issue_id=db_issue.id,
                                    photo_type="问题照片",
                                    file_path=file_path,
                                    file_name=file_name
                                )
                                db.add(db_photo)
                                debug_info.append(f"  -> 关联图片: {file_name}")
                                image_idx += 1
                            
                            imported_count += 1
                            debug_info.append(f"  -> 成功导入: {title[:50]}")
                        except Exception as db_err:
                            db.rollback()
                            debug_info.append(f"  -> 数据库错误: {str(db_err)}")
                            errors.append(f"第{row_idx}行数据库错误: {str(db_err)}")
                    else:
                        debug_info.append(f"  -> 跳过（无标题）")
                except Exception as e:
                    errors.append(f"第{row_idx}行导入失败: {str(e)}")
                    debug_info.append(f"  -> 错误: {str(e)}")
        
        db.commit()
        
        return {
            'success': True,
            'imported_count': imported_count,
            'errors': errors,
            'project_name': final_project_name,
            'tables_found': len(doc.tables),
            'paragraphs_count': len(doc.paragraphs),
            'images_found': len(all_images),
            'debug': debug_info[:100]
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}
