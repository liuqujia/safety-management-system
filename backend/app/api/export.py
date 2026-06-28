from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
import io
from datetime import datetime
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

from app.database import get_db
from app.models import SafetyIssue

router = APIRouter(prefix="/api/export", tags=["数据导出"])

@router.get("/excel")
def export_to_excel(
    status: str = None,
    severity: str = None,
    db: Session = Depends(get_db)
):
    """导出问题到Excel"""
    # 查询问题
    query = db.query(SafetyIssue)
    if status:
        query = query.filter(SafetyIssue.status == status)
    if severity:
        query = query.filter(SafetyIssue.severity == severity)

    issues = query.order_by(SafetyIssue.create_time.desc()).all()

    if not issues:
        raise HTTPException(status_code=404, detail="没有可导出的问题")

    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "安全问题"

    # 设置列宽
    column_widths = {
        'A': 8,   # 序号
        'B': 30,  # 问题标题
        'C': 40,  # 问题描述
        'D': 20,  # 发现位置
        'E': 12,  # 严重程度
        'F': 12,  # 状态
        'G': 15,  # 责任人
        'H': 15,  # 整改期限
        'I': 40,  # 备注
        'J': 20,  # 创建时间
        'K': 50,  # 问题照片
        'L': 50,  # 整改照片
    }

    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # 设置标题行样式
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    # 标题行
    headers = ["序号", "问题标题", "问题描述", "发现位置", "严重程度", "状态", "责任人", "整改期限", "备注", "创建时间", "问题照片", "整改照片"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # 数据行
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

        # 添加照片
        # 问题照片列
        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        if issue_photos:
            photo_info = "\n".join([f"{idx+1}. {p.file_name}" for idx, p in enumerate(issue_photos)])
            ws.cell(row=row_num, column=11, value=photo_info)

        # 整改照片列
        rectification_photos = [p for p in issue.photos if p.photo_type == "整改照片"]
        if rectification_photos:
            photo_info = "\n".join([f"{idx+1}. {p.file_name}" for idx, p in enumerate(rectification_photos)])
            ws.cell(row=row_num, column=12, value=photo_info)

    # 设置行高（为照片预留空间）
    for row in range(2, len(issues) + 2):
        ws.row_dimensions[row].height = 60

    # 保存到内存
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"安全问题_{timestamp}.xlsx"

    # 返回文件流
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

    # 查询问题
    query = db.query(SafetyIssue)
    if status:
        query = query.filter(SafetyIssue.status == status)
    if severity:
        query = query.filter(SafetyIssue.severity == severity)

    issues = query.order_by(SafetyIssue.create_time.desc()).all()

    if not issues:
        raise HTTPException(status_code=404, detail="没有可导出的问题")

    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    ws.title = "安全问题"

    # 设置列宽
    column_widths = {
        'A': 8,   # 序号
        'B': 30,  # 问题标题
        'C': 40,  # 问题描述
        'D': 20,  # 发现位置
        'E': 12,  # 严重程度
        'F': 12,  # 状态
        'G': 15,  # 责任人
        'H': 15,  # 整改期限
        'I': 40,  # 备注
        'J': 20,  # 创建时间
        'K': 50,  # 问题照片
        'L': 50,  # 整改照片
    }

    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    # 设置标题行样式
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_alignment = Alignment(horizontal="center", vertical="center")

    # 标题行
    headers = ["序号", "问题标题", "问题描述", "发现位置", "严重程度", "状态", "责任人", "整改期限", "备注", "创建时间", "问题照片", "整改照片"]
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # 数据行
    current_row = 2
    for issue in issues:
        # 计算该行需要的行数（根据照片数量）
        issue_photos = [p for p in issue.photos if p.photo_type == "问题照片"]
        rectification_photos = [p for p in issue.photos if p.photo_type == "整改照片"]

        # 每行最多显示3张照片
        max_photos = max(
            (len(issue_photos) + 2) // 3,
            (len(rectification_photos) + 2) // 3,
            1
        )

        # 合并单元格（除了照片列）
        if max_photos > 1:
            end_row = current_row + max_photos - 1
            for col in range(1, 11):
                ws.merge_cells(start_row=current_row, start_column=col, end_row=end_row, end_column=col)

        # 填充数据
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

        # 添加问题照片
        for idx, photo in enumerate(issue_photos):
            try:
                if os.path.exists(photo.file_path):
                    img = XLImage(photo.file_path)
                    # 缩放图片
                    img.width = 100
                    img.height = 80
                    # 计算位置
                    photo_row = current_row + idx // 3
                    photo_col = 11 + (idx % 3) * 0.5
                    ws.add_image(img, f'K{photo_row}')
            except Exception as e:
                print(f"Error adding image {photo.file_path}: {e}")

        # 添加整改照片
        for idx, photo in enumerate(rectification_photos):
            try:
                if os.path.exists(photo.file_path):
                    img = XLImage(photo.file_path)
                    # 缩放图片
                    img.width = 100
                    img.height = 80
                    # 计算位置
                    photo_row = current_row + idx // 3
                    photo_col = 12 + (idx % 3) * 0.5
                    ws.add_image(img, f'L{photo_row}')
            except Exception as e:
                print(f"Error adding image {photo.file_path}: {e}")

        # 设置行高
        for row in range(current_row, current_row + max_photos):
            ws.row_dimensions[row].height = 60

        current_row += max_photos

    # 保存到内存
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"安全问题_带照片_{timestamp}.xlsx"

    # 返回文件流
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )