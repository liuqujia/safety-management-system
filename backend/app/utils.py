import os
import uuid
from datetime import datetime
from fastapi import UploadFile
from PIL import Image
import io

# 照片存储根目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "photos")

async def save_upload_file(file: UploadFile, issue_id: int, photo_type: str) -> tuple:
    """
    保存上传的文件
    返回: (file_path, file_name)
    """
    # 创建存储目录
    issue_dir = os.path.join(UPLOAD_DIR, str(issue_id))
    os.makedirs(issue_dir, exist_ok=True)

    # 生成唯一文件名
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_ext}"
    file_path = os.path.join(issue_dir, unique_filename)

    # 读取并保存文件
    contents = await file.read()

    # 压缩图片
    try:
        image = Image.open(io.BytesIO(contents))
        # 如果图片太大，进行压缩
        if len(contents) > 1024 * 1024:  # 大于1MB
            # 调整大小，保持宽高比
            max_size = (1920, 1920)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

        # 保存图片
        image.save(file_path, quality=85, optimize=True)
    except Exception as e:
        # 如果不是图片或处理失败，直接保存原文件
        with open(file_path, "wb") as f:
            f.write(contents)

    return file_path, file.filename

def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False

def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0