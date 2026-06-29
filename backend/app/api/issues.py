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

@router.get("/")
def get_issues(
    page: int = 1,
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

    total = query.count()
    skip = (page - 1) * limit
    issues = query.order_by(SafetyIssue.id.asc()).offset(skip).limit(limit).all()
    return {"items": [issue.to_dict() for issue in issues], "total": total}


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


@router.delete("/batch/delete")
def batch_delete_issues(
    project_name: Optional[str] = None,
    issue_ids: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """批量删除：按项目名删除 或 按 ID 列表删除"""
    query = db.query(SafetyIssue)
    
    if project_name:
        # "未分类" 特别处理：匹配 NULL/空字符串
        if project_name in ('未分类', '__EMPTY__'):
            from sqlalchemy import or_
            query = query.filter(or_(
                SafetyIssue.project_name.is_(None),
                SafetyIssue.project_name == '',
                SafetyIssue.project_name == '未分类'
            ))
        else:
            query = query.filter(SafetyIssue.project_name == project_name)
    
    if issue_ids:
        ids = []
        for sid in issue_ids.split(','):
            try:
                ids.append(int(sid.strip()))
            except ValueError:
                pass
        if ids:
            query = query.filter(SafetyIssue.id.in_(ids))
    
    issues = query.all()
    if not issues:
        raise HTTPException(status_code=404, detail="没有可删除的问题")
    
    deleted_count = 0
    for issue in issues:
        for photo in issue.photos:
            if os.path.exists(photo.file_path):
                os.remove(photo.file_path)
        db.delete(issue)
        deleted_count += 1
    
    db.commit()
    return {"message": f"成功删除 {deleted_count} 条问题", "deleted_count": deleted_count}


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

def extract_images_from_cell(cell, issue_id):
    """从表格单元格中提取图片（精确匹配）"""
    images = []
    try:
        from lxml import etree
        cell_xml = cell._element
        # 查找所有图片关系 ID
        for blip in cell_xml.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
            embed = blip.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
            if embed and embed in cell.part.rels:
                rel = cell.part.rels[embed]
                image_part = rel.target_part
                image_data = image_part.blob
                file_ext = os.path.splitext(rel.target_ref)[1] or '.png'
                file_name = f"{issue_id}_{len(images) + 1}{file_ext}"
                images.append((file_name, image_data))
    except Exception as e:
        pass
    return images

def extract_images_from_doc(doc, issue_id):
    """旧版：从文档全局提取图片（备用）"""
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

        result = _parse_word_doc(doc)

        # 展平为 items 列表（带 project_name 字段）
        items = []
        for project_name, issues in result:
            for issue in issues:
                issue["project_name"] = project_name
                items.append(issue)

        all_projects = [pn for pn, _ in result]
        first_project = all_projects[0] if all_projects else ""

        return {
            "success": True,
            "project_name": first_project,
            "project_list": all_projects,
            "items": items,
            "tables_found": len(doc.tables),
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@router.post("/import-from-word")
async def import_from_word(
    file: UploadFile = File(...),
    skip_indices: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    try:
        from docx import Document

        contents = await file.read()
        doc = Document(io.BytesIO(contents))

        result = _parse_word_doc(doc)

        # 解析要跳过的行索引
        skip_set = set()
        if skip_indices:
            for idx_str in skip_indices.split(','):
                try:
                    skip_set.add(int(idx_str.strip()))
                except ValueError:
                    pass

        imported_count = 0
        errors = []

        for project_name, issues in result:
            for issue_dict in issues:
                skip_key = f"{project_name}_{issue_dict['title'][:30]}"
                if skip_key in skip_set:
                    continue
                try:
                    db_issue = SafetyIssue(
                        project_name=project_name or None,
                        title=issue_dict['title'][:200],
                        description=issue_dict.get('description', '')[:500],
                        location='',
                        severity='一般',
                        deadline=issue_dict.get('deadline'),
                        status='待整改',
                        notes=issue_dict.get('notes', '')[:500],
                        responsible_person='',
                    )
                    db.add(db_issue)
                    db.commit()
                    db.refresh(db_issue)

                    # 从该行的 cells[1]（现场图片列）提取图片 —— 精确匹配
                    try:
                        tbl_idx = issue_dict.get('_table_idx', 0)
                        row_idx = issue_dict.get('_row_idx', 0)
                        if tbl_idx < len(doc.tables):
                            table = doc.tables[tbl_idx]
                            if row_idx < len(table.rows):
                                row = table.rows[row_idx]
                                cells = row.cells
                                if len(cells) >= 2:
                                    cell_b = cells[1]  # 现场图片列
                                    images = extract_images_from_cell(cell_b, db_issue.id)
                                    for file_name, image_data in images:
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
                    except Exception as img_e:
                        errors.append(f"图片提取失败: {str(img_e)}")

                    imported_count += 1
                except Exception as e:
                    db.rollback()
                    errors.append(str(e))

        db.commit()

        all_projects = [pn for pn, _ in result]
        return {
            'success': True,
            'imported_count': imported_count,
            'errors': errors,
            'project_name': all_projects[0] if all_projects else "",
            'project_list': all_projects,
            'tables_found': len(doc.tables),
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}


def _parse_word_doc(doc):
    """
    按文档 XML 顺序遍历 body 子元素：
    - 遇到 <w:p>：检测「企业名称」/「项目名称」，更新 current_project
    - 遇到 <w:tbl>：取 doc.tables[table_cursor]，分配 current_project
    返回 [ (project_name, [{"title":..., "description":..., "notes":..., "deadline":...}]) ]
    """
    current_project = ""
    table_cursor = 0
    result = []   # [(project_name, [issue_dicts])]
    current_issues = []

    body = doc.element.body
    for child in body:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'p':   # 段落
            texts = [node.text for node in child.iter() if node.text and node.text.strip()]
            text = ' '.join(texts)
            for prefix in ["企业名称", "项目名称"]:
                if prefix in text:
                    val = re.search(
                        r'' + prefix + r'[：:]\s+(.+?)(?:\s{2,}隐患|\s{2,}检查|$)',
                        text, re.DOTALL
                    )
                    if val:
                        # 遇到新项目：先把当前项目的 issues 存起来
                        if current_issues:
                            result.append((current_project, current_issues))
                        current_project = val.group(1).strip()
                        current_issues = []
                        break

        elif tag == 'tbl':   # 表格
            if table_cursor >= len(doc.tables):
                break
            table = doc.tables[table_cursor]
            table_cursor += 1

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
                current_issues.append({
                    "title": title,
                    "description": description,
                    "notes": notes,
                    "deadline": deadline,
                    "_table_idx": table_cursor - 1,
                    "_row_idx": row_idx,
                })

    # 最后一个项目
    if current_issues:
        result.append((current_project, current_issues))
    return result
