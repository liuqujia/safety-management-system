from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import io
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from app.database import get_db
from app.models import SafetyIssue

router = APIRouter(prefix="/api/export", tags=["数据导出"])

class RectificationReplyRequest(BaseModel):
    project_name: str
    project_responsible: str
    reply_date: str
    issue_ids: Optional[List[int]] = None

class ExportTemplate(BaseModel):
    id: Optional[int] = None
    name: str
    title_format: str = "《关于{date}安全隐患整改有关事项回复》"
    columns: List[str] = ["序号", "现场图片", "检查发现的主要隐患或问题", "法规名称、代码和条款号", "整改措施或建议", "备注"]

templates = [
    {
        "id": 1,
        "name": "隐患检查表",
        "columns": ["序号", "现场图片", "检查发现的主要隐患或问题", "法规名称、代码和条款号", "整改措施或建议", "备注"]
    },
    {
        "id": 2,
        "name": "整改回复报告",
        "title_format": "《关于{date}安全隐患整改有关事项回复》",
        "columns": []
    }
]

@router.get("/templates")
def get_templates():
    return templates

@router.post("/templates")
def create_template(template: ExportTemplate):
    new_id = max(t["id"] for t in templates) + 1 if templates else 1
    template_dict = template.dict()
    template_dict["id"] = new_id
    templates.append(template_dict)
    return template_dict

@router.put("/templates/{template_id}")
def update_template(template_id: int, template: ExportTemplate):
    for t in templates:
        if t["id"] == template_id:
            t.update(template.dict(exclude_unset=True))
            return t
    raise HTTPException(status_code=404, detail="模板不存在")

@router.delete("/templates/{template_id}")
def delete_template(template_id: int):
    global templates
    templates = [t for t in templates if t["id"] != template_id]
    return {"message": "删除成功"}

@router.get("/excel-with-photos")
def export_excel_with_photos(
    status: str = None,
    severity: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(SafetyIssue)
    if status:
        query = query.filter(SafetyIssue.status == status)
    if severity:
        query = query.filter(SafetyIssue.severity == severity)

    issues = query.order_by(SafetyIssue.create_time.desc()).all()

    if not issues:
        raise HTTPException(status_code=404, detail="没有可导出的问题")

    wb = Workbook()
    ws = wb.active
    ws.title = "安全问题"

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    column_widths = {
        'A': 8,   'B': 30, 'C': 40, 'D': 50, 'E': 40, 'F': 20,
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    headers = ["序号", "现场图片", "检查发现的主要隐患或问题", "法规名称、代码和条款号", "整改措施或建议", "备注"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border

    current_row = 2
    for idx, issue in enumerate(issues, 1):
        ws.cell(row=current_row, column=1, value=idx).border = thin_border
        
        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        rect_photos = [p for p in issue.photos if p.photo_type == "整改照片"]
        
        max_photos = max(len(issue_photos), len(rect_photos), 1)
        
        for photo_idx in range(max_photos):
            if photo_idx < len(issue_photos):
                photo = issue_photos[photo_idx]
                try:
                    if os.path.exists(photo.file_path):
                        img = XLImage(photo.file_path)
                        img.width = 150
                        img.height = 120
                        ws.add_image(img, f'B{current_row}')
                except Exception as e:
                    pass
        
        ws.cell(row=current_row, column=3, value=issue.title).border = thin_border
        ws.cell(row=current_row, column=4, value=issue.description).border = thin_border
        ws.cell(row=current_row, column=5, value=issue.notes).border = thin_border
        
        remark_parts = []
        if issue.severity:
            remark_parts.append(f"严重程度: {issue.severity}")
        if issue.deadline:
            remark_parts.append(f"整改时限: {issue.deadline.isoformat()}")
        if issue.status:
            remark_parts.append(f"状态: {issue.status}")
        if issue.responsible_person:
            remark_parts.append(f"责任人: {issue.responsible_person}")
        if issue.location:
            remark_parts.append(f"位置: {issue.location}")
        
        ws.cell(row=current_row, column=6, value="; ".join(remark_parts)).border = thin_border
        
        ws.row_dimensions[current_row].height = 120
        current_row += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"safety_report_with_photos_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/excel")
def export_to_excel(
    status: str = None,
    severity: str = None,
    template_id: int = 1,
    db: Session = Depends(get_db)
):
    template = next((t for t in templates if t["id"] == template_id), templates[0])
    
    query = db.query(SafetyIssue)
    if status:
        query = query.filter(SafetyIssue.status == status)
    if severity:
        query = query.filter(SafetyIssue.severity == severity)

    issues = query.order_by(SafetyIssue.create_time.desc()).all()

    if not issues:
        raise HTTPException(status_code=404, detail="没有可导出的问题")

    wb = Workbook()
    ws = wb.active
    ws.title = "安全问题"

    column_widths = {
        'A': 8,   'B': 30, 'C': 40, 'D': 50, 'E': 40, 'F': 20,
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    headers = template.get("columns", ["序号", "现场图片", "检查发现的主要隐患或问题", "法规名称、代码和条款号", "整改措施或建议", "备注"])
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    current_row = 2
    for idx, issue in enumerate(issues, 1):
        ws.cell(row=current_row, column=1, value=idx)
        
        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        if issue_photos:
            photo = issue_photos[0]
            try:
                if os.path.exists(photo.file_path):
                    img = XLImage(photo.file_path)
                    img.width = 100
                    img.height = 80
                    ws.add_image(img, f'B{current_row}')
            except Exception as e:
                pass
        
        ws.cell(row=current_row, column=3, value=issue.title)
        ws.cell(row=current_row, column=4, value=issue.description)
        ws.cell(row=current_row, column=5, value=issue.notes)
        
        remark_parts = []
        if issue.severity:
            remark_parts.append(f"严重程度: {issue.severity}")
        if issue.deadline:
            remark_parts.append(f"整改时限: {issue.deadline.isoformat()}")
        if issue.status:
            remark_parts.append(f"状态: {issue.status}")
        if issue.responsible_person:
            remark_parts.append(f"责任人: {issue.responsible_person}")
        if issue.location:
            remark_parts.append(f"位置: {issue.location}")
        
        ws.cell(row=current_row, column=6, value="; ".join(remark_parts))
        
        ws.row_dimensions[current_row].height = 80
        current_row += 1

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"safety_report_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/excel/rectification")
def export_rectification_report(
    status: str = None,
    project_name: str = None,
    responsible_person: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(SafetyIssue)
    if status:
        query = query.filter(SafetyIssue.status == status)
    if project_name:
        query = query.filter(SafetyIssue.project_name.like(f"%{project_name}%"))

    issues = query.order_by(SafetyIssue.create_time.desc()).all()

    if not issues:
        raise HTTPException(status_code=404, detail="没有可导出的问题")

    wb = Workbook()
    ws = wb.active
    ws.title = "整改回复"

    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 80

    title_font = Font(bold=True, size=16)
    title_alignment = Alignment(horizontal="center", vertical="center")
    header_font = Font(bold=True, size=11)

    current_row = 1

    today = datetime.now().strftime("%Y年%m月%d日")
    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=2)
    title_cell = ws.cell(row=current_row, column=1, value=f"《关于{today}安全隐患整改有关事项回复》")
    title_cell.font = title_font
    title_cell.alignment = title_alignment
    ws.row_dimensions[current_row].height = 35
    current_row += 1

    def add_info_row(label, value):
        nonlocal current_row
        ws.cell(row=current_row, column=1, value=label).font = header_font
        ws.cell(row=current_row, column=2, value=value)
        ws.row_dimensions[current_row].height = 25
        for col in range(1, 3):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

    add_info_row("项目名称", project_name or issues[0].project_name or "请填写项目名称")
    add_info_row("项目负责人", responsible_person or issues[0].responsible_person or "请填写负责人")

    for idx, issue in enumerate(issues, 1):
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=2)
        ws.cell(row=current_row, column=1, value=f"隐患事项{idx}：{issue.title}").font = Font(bold=True, size=11)
        ws.row_dimensions[current_row].height = 25
        for col in range(1, 3):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=2)
        ws.cell(row=current_row, column=1, value=f"整改措施：{issue.notes if issue.notes else '已整改'}")
        ws.row_dimensions[current_row].height = 25
        for col in range(1, 3):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        ws.cell(row=current_row, column=1, value="整改前照片：").font = header_font
        ws.cell(row=current_row, column=2, value="整改后照片：").font = header_font
        for col in range(1, 3):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        rect_photos = [p for p in issue.photos if p.photo_type == "整改照片"]

        max_photos = max(len(issue_photos), len(rect_photos), 1)
        photo_height = 150

        for photo_idx in range(max_photos):
            ws.cell(row=current_row, column=1, value="")
            ws.cell(row=current_row, column=2, value="")

            if photo_idx < len(issue_photos):
                photo = issue_photos[photo_idx]
                try:
                    if os.path.exists(photo.file_path):
                        img = XLImage(photo.file_path)
                        img.width = 200
                        img.height = 150
                        ws.add_image(img, f'A{current_row}')
                except Exception as e:
                    pass

            if photo_idx < len(rect_photos):
                photo = rect_photos[photo_idx]
                try:
                    if os.path.exists(photo.file_path):
                        img = XLImage(photo.file_path)
                        img.width = 200
                        img.height = 150
                        ws.add_image(img, f'B{current_row}')
                except Exception as e:
                    pass

            ws.row_dimensions[current_row].height = photo_height
            for col in range(1, 3):
                ws.cell(row=current_row, column=col).border = thin_border
            current_row += 1

        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=2)
        ws.cell(row=current_row, column=1, value="整改事项回复")
        ws.row_dimensions[current_row].height = photo_height
        for col in range(1, 3):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        current_row += 1

    add_info_row("回复日期", datetime.now().strftime("%Y年%m月%d日"))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rectification_reply_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.post("/rectification-reply")
def export_rectification_reply(
    request: RectificationReplyRequest,
    db: Session = Depends(get_db)
):
    """
    按照用户模板格式导出整改回复
    模板结构：
    - 行1: 标题（合并A1:E1）
    - 行2: 项目名称
    - 行3: 项目负责人
    - 行4-7: 隐患事项1（整改事项回复、整改措施、整改前/后照片）
    - ... 每个隐患占4行
    - 最后: 回复日期
    """
    query = db.query(SafetyIssue)
    if request.issue_ids:
        query = query.filter(SafetyIssue.id.in_(request.issue_ids))

    issues = query.order_by(SafetyIssue.create_time.desc()).all()

    if not issues:
        raise HTTPException(status_code=404, detail="没有可导出的问题")

    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    # 设置列宽（与模板一致）
    ws.column_dimensions['A'].width = 14.875
    ws.column_dimensions['B'].width = 9.625
    ws.column_dimensions['C'].width = 25.625
    ws.column_dimensions['D'].width = 9.625
    ws.column_dimensions['E'].width = 25.625

    # 边框样式
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # 字体样式
    title_font = Font(bold=True, size=16)
    header_font = Font(bold=True, size=11)
    normal_font = Font(size=11)
    center_alignment = Alignment(horizontal="center", vertical="center")
    left_alignment = Alignment(horizontal="left", vertical="center")

    current_row = 1

    # 行1: 标题
    ws.merge_cells(f'A{current_row}:E{current_row}')
    title_cell = ws.cell(row=current_row, column=1, value=f"《关于{request.reply_date}安全隐患整改有关事项回复》")
    title_cell.font = title_font
    title_cell.alignment = center_alignment
    ws.row_dimensions[current_row].height = 30
    for col in range(1, 6):
        ws.cell(row=current_row, column=col).border = thin_border
    current_row += 1

    # 行2: 项目名称
    ws.cell(row=current_row, column=1, value="项目名称").font = header_font
    ws.cell(row=current_row, column=1).alignment = left_alignment
    ws.cell(row=current_row, column=1).border = thin_border
    ws.merge_cells(f'B{current_row}:E{current_row}')
    ws.cell(row=current_row, column=2, value=request.project_name).font = normal_font
    ws.cell(row=current_row, column=2).alignment = left_alignment
    for col in range(2, 6):
        ws.cell(row=current_row, column=col).border = thin_border
    ws.row_dimensions[current_row].height = 22
    current_row += 1

    # 行3: 项目负责人
    ws.cell(row=current_row, column=1, value="项目负责人").font = header_font
    ws.cell(row=current_row, column=1).alignment = left_alignment
    ws.cell(row=current_row, column=1).border = thin_border
    ws.merge_cells(f'B{current_row}:E{current_row}')
    ws.cell(row=current_row, column=2, value=request.project_responsible).font = normal_font
    ws.cell(row=current_row, column=2).alignment = left_alignment
    for col in range(2, 6):
        ws.cell(row=current_row, column=col).border = thin_border
    ws.row_dimensions[current_row].height = 22
    current_row += 1

    # 每个隐患事项（占4行）
    for idx, issue in enumerate(issues, 1):
        # 行4: 整改事项回复 + 隐患标题
        ws.merge_cells(f'A{current_row}:A{current_row+3}')
        ws.cell(row=current_row, column=1, value="整改事项回复").font = header_font
        ws.cell(row=current_row, column=1).alignment = center_alignment
        ws.cell(row=current_row, column=1).border = thin_border
        for r in range(current_row, current_row+4):
            ws.cell(row=r, column=1).border = thin_border

        ws.merge_cells(f'B{current_row}:E{current_row}')
        ws.cell(row=current_row, column=2, value=f"隐患事项{idx}：{issue.title}").font = header_font
        ws.cell(row=current_row, column=2).alignment = left_alignment
        for col in range(2, 6):
            ws.cell(row=current_row, column=col).border = thin_border
        ws.row_dimensions[current_row].height = 32
        current_row += 1

        # 行5: 整改措施
        ws.merge_cells(f'B{current_row}:E{current_row}')
        ws.cell(row=current_row, column=2, value=f"整改措施：{issue.notes if issue.notes else '已整改'}").font = normal_font
        ws.cell(row=current_row, column=2).alignment = left_alignment
        for col in range(2, 6):
            ws.cell(row=current_row, column=col).border = thin_border
        ws.row_dimensions[current_row].height = 22
        current_row += 1

        # 行6: 照片标签
        ws.cell(row=current_row, column=2, value="整改前照片：").font = header_font
        ws.cell(row=current_row, column=2).alignment = left_alignment
        ws.cell(row=current_row, column=2).border = thin_border
        ws.cell(row=current_row, column=3).border = thin_border
        ws.cell(row=current_row, column=4, value="整改后照片：").font = header_font
        ws.cell(row=current_row, column=4).alignment = left_alignment
        ws.cell(row=current_row, column=4).border = thin_border
        ws.cell(row=current_row, column=5).border = thin_border
        ws.row_dimensions[current_row].height = 19
        current_row += 1

        # 行7: 照片区域
        ws.merge_cells(f'B{current_row-1}:C{current_row}')
        ws.merge_cells(f'D{current_row-1}:E{current_row}')

        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        rect_photos = [p for p in issue.photos if p.photo_type == "整改照片"]

        # 整改前照片（B-C列）
        if issue_photos:
            photo = issue_photos[0]
            try:
                if os.path.exists(photo.file_path):
                    img = XLImage(photo.file_path)
                    img.width = 150
                    img.height = 100
                    ws.add_image(img, f'B{current_row}')
            except Exception as e:
                pass

        # 整改后照片（D-E列）
        if rect_photos:
            photo = rect_photos[0]
            try:
                if os.path.exists(photo.file_path):
                    img = XLImage(photo.file_path)
                    img.width = 150
                    img.height = 100
                    ws.add_image(img, f'D{current_row}')
            except Exception as e:
                pass

        for col in range(2, 6):
            ws.cell(row=current_row, column=col).border = thin_border
        ws.row_dimensions[current_row].height = 106
        current_row += 1

    # 回复日期
    ws.cell(row=current_row, column=1, value="回复日期").font = header_font
    ws.cell(row=current_row, column=1).alignment = left_alignment
    ws.cell(row=current_row, column=1).border = thin_border
    ws.merge_cells(f'B{current_row}:E{current_row}')
    ws.cell(row=current_row, column=2, value=request.reply_date).font = normal_font
    ws.cell(row=current_row, column=2).alignment = left_alignment
    for col in range(2, 6):
        ws.cell(row=current_row, column=col).border = thin_border
    ws.row_dimensions[current_row].height = 22

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rectification_reply_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
