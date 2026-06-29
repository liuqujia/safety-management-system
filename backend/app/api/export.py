from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io
import os
from datetime import datetime
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

from app.database import get_db
from app.models import SafetyIssue

router = APIRouter(prefix="/api/export", tags=["数据导出"])

@router.get("/excel")
def export_to_excel(
    status: str = None,
    severity: str = None,
    db: Session = Depends(get_db)
):
    """导出问题到Excel（标准表格格式）"""
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
        'A': 8,   'B': 30, 'C': 40, 'D': 20, 'E': 12, 'F': 12,
        'G': 15,  'H': 15, 'I': 40, 'J': 20, 'K': 50, 'L': 50,
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    headers = ["序号", "问题标题", "问题描述", "发现位置", "严重程度", "状态", "责任人", "整改期限", "备注", "创建时间", "问题照片", "整改照片"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    for row_num, issue in enumerate(issues, 2):
        ws.cell(row=row_num, column=1, value=row_num - 1)
        ws.cell(row=row_num, column=2, value=issue.title)
        ws.cell(row=row_num, column=3, value=issue.description)
        ws.cell(row=row_num, column=4, value=issue.location)
        ws.cell(row=row_num, column=5, value=issue.severity)
        ws.cell(row=row_num, column=6, value=issue.status)
        ws.cell(row=row_num, column=7, value=issue.responsible_person)
        ws.cell(row=row_num, column=8, value=issue.deadline.isoformat() if issue.deadline else "")
        ws.cell(row=row_num, column=9, value=issue.notes)
        ws.cell(row=row_num, column=10, value=issue.create_time.strftime("%Y-%m-%d %H:%M:%S") if issue.create_time else "")

        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        if issue_photos:
            photo_info = "\n".join([f"{idx+1}. {p.file_name}" for idx, p in enumerate(issue_photos)])
            ws.cell(row=row_num, column=11, value=photo_info)

        rectification_photos = [p for p in issue.photos if p.photo_type == "整改照片"]
        if rectification_photos:
            photo_info = "\n".join([f"{idx+1}. {p.file_name}" for idx, p in enumerate(rectification_photos)])
            ws.cell(row=row_num, column=12, value=photo_info)

    for row in range(2, len(issues) + 2):
        ws.row_dimensions[row].height = 60

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"安全问题_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


@router.get("/excel/rectification")
def export_rectification_report(
    status: str = None,
    project_name: str = None,
    responsible_person: str = None,
    db: Session = Depends(get_db)
):
    """导出安全隐患整改回复报告（按用户提供的格式）"""
    query = db.query(SafetyIssue)
    if status:
        query = query.filter(SafetyIssue.status == status)
    if project_name:
        query = query.filter(SafetyIssue.location.like(f"%{project_name}%"))

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
    ws.column_dimensions['B'].width = 60
    ws.column_dimensions['C'].width = 60

    title_font = Font(bold=True, size=16)
    title_alignment = Alignment(horizontal="center", vertical="center")
    header_font = Font(bold=True, size=11)
    header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")

    current_row = 1

    ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
    title_cell = ws.cell(row=current_row, column=1, value="《关于安全隐患整改有关事项回复》")
    title_cell.font = title_font
    title_cell.alignment = title_alignment
    ws.row_dimensions[current_row].height = 35
    current_row += 1

    def add_info_row(label, value):
        nonlocal current_row
        ws.cell(row=current_row, column=1, value=label).font = header_font
        ws.cell(row=current_row, column=2, value=value)
        ws.merge_cells(start_row=current_row, start_column=2, end_row=current_row, end_column=3)
        ws.row_dimensions[current_row].height = 25
        for col in range(1, 4):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

    add_info_row("项目名称", project_name or "请填写项目名称")
    add_info_row("项目负责人", responsible_person or issues[0].responsible_person or "请填写负责人")

    for idx, issue in enumerate(issues, 1):
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        ws.cell(row=current_row, column=1, value=f"隐患事项{idx}：{issue.title}").font = Font(bold=True, size=11)
        ws.row_dimensions[current_row].height = 25
        for col in range(1, 4):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        ws.cell(row=current_row, column=1, value=f"整改措施：{issue.notes if issue.notes else '已整改'}")
        ws.row_dimensions[current_row].height = 25
        for col in range(1, 4):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        ws.cell(row=current_row, column=1, value="整改前照片：").font = header_font
        ws.cell(row=current_row, column=2, value="")
        ws.cell(row=current_row, column=3, value="整改后照片：").font = header_font
        for col in range(1, 4):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        rect_photos = [p for p in issue.photos if p.photo_type == "整改照片"]

        max_photos = max(len(issue_photos), len(rect_photos), 1)
        photo_height = 150

        for photo_idx in range(max_photos):
            ws.cell(row=current_row, column=1, value="")
            ws.cell(row=current_row, column=2, value="")
            ws.cell(row=current_row, column=3, value="")

            if photo_idx < len(issue_photos):
                photo = issue_photos[photo_idx]
                try:
                    if os.path.exists(photo.file_path):
                        img = XLImage(photo.file_path)
                        img.width = 180
                        img.height = 140
                        ws.add_image(img, f'B{current_row}')
                except Exception as e:
                    print(f"Error adding image {photo.file_path}: {e}")

            if photo_idx < len(rect_photos):
                photo = rect_photos[photo_idx]
                try:
                    if os.path.exists(photo.file_path):
                        img = XLImage(photo.file_path)
                        img.width = 180
                        img.height = 140
                        ws.add_image(img, f'C{current_row}')
                except Exception as e:
                    print(f"Error adding image {photo.file_path}: {e}")

            ws.row_dimensions[current_row].height = photo_height
            for col in range(1, 4):
                ws.cell(row=current_row, column=col).border = thin_border
            current_row += 1

        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=3)
        ws.cell(row=current_row, column=1, value="整改事项回复")
        ws.row_dimensions[current_row].height = photo_height
        for col in range(1, 4):
            ws.cell(row=current_row, column=col).border = thin_border
        current_row += 1

        current_row += 1

    add_info_row("回复日期", datetime.now().strftime("%Y年%m月%d日"))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"安全隐患整改回复_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


@router.get("/excel-with-photos")
def export_to_excel_with_photos(
    status: str = None,
    severity: str = None,
    db: Session = Depends(get_db)
):
    """导出问题到Excel（包含嵌入的照片）"""
    from PIL import Image as PILImage

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
        'A': 8,   'B': 30, 'C': 40, 'D': 20, 'E': 12, 'F': 12,
        'G': 15,  'H': 15, 'I': 40, 'J': 20, 'K': 50, 'L': 50,
    }
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    headers = ["序号", "问题标题", "问题描述", "发现位置", "严重程度", "状态", "责任人", "整改期限", "备注", "创建时间", "问题照片", "整改照片"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=row_num, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    current_row = 2
    for issue in issues:
        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        rectification_photos = [p for p in issue.photos if p.photo_type == "整改照片"]

        max_photos = max(
            (len(issue_photos) + 2) // 3,
            (len(rectification_photos) + 2) // 3,
            1
        )

        if max_photos > 1:
            end_row = current_row + max_photos - 1
            for col in range(1, 11):
                ws.merge_cells(start_row=current_row, start_column=col, end_row=end_row, end_column=col)

        ws.cell(row=current_row, column=1, value=current_row - 1)
        ws.cell(row=current_row, column=2, value=issue.title)
        ws.cell(row=current_row, column=3, value=issue.description)
        ws.cell(row=current_row, column=4, value=issue.location)
        ws.cell(row=current_row, column=5, value=issue.severity)
        ws.cell(row=current_row, column=6, value=issue.status)
        ws.cell(row=current_row, column=7, value=issue.responsible_person)
        ws.cell(row=current_row, column=8, value=issue.deadline.isoformat() if issue.deadline else "")
        ws.cell(row=current_row, column=9, value=issue.notes)
        ws.cell(row=current_row, column=10, value=issue.create_time.strftime("%Y-%m-%d %H:%M:%S") if issue.create_time else "")

        for idx, photo in enumerate(issue_photos):
            try:
                if os.path.exists(photo.file_path):
                    img = XLImage(photo.file_path)
                    img.width = 100
                    img.height = 80
                    photo_row = current_row + idx // 3
                    ws.add_image(img, f'K{photo_row}')
            except Exception as e:
                print(f"Error adding image {photo.file_path}: {e}")

        for idx, photo in enumerate(rectification_photos):
            try:
                if os.path.exists(photo.file_path):
                    img = XLImage(photo.file_path)
                    img.width = 100
                    img.height = 80
                    photo_row = current_row + idx // 3
                    ws.add_image(img, f'L{photo_row}')
            except Exception as e:
                print(f"Error adding image {photo.file_path}: {e}")

        for row in range(current_row, current_row + max_photos):
            ws.row_dimensions[row].height = 60

        current_row += max_photos

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"安全问题_带照片_{timestamp}.xlsx"

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )