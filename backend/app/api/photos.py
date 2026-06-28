from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.database import get_db
from app.models import Photo

router = APIRouter(prefix="/api/photos", tags=["照片管理"])

@router.get("/{photo_id}/download")
def download_photo(photo_id: int, db: Session = Depends(get_db)):
    """下载照片"""
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not db_photo:
        raise HTTPException(status_code=404, detail="照片不存在")

    if not os.path.exists(db_photo.file_path):
        raise HTTPException(status_code=404, detail="照片文件不存在")

    return FileResponse(
        path=db_photo.file_path,
        filename=db_photo.file_name,
        media_type="image/jpeg"
    )

@router.delete("/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """删除照片"""
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not db_photo:
        raise HTTPException(status_code=404, detail="照片不存在")

    # 删除文件
    if os.path.exists(db_photo.file_path):
        os.remove(db_photo.file_path)

    # 删除数据库记录
    db.delete(db_photo)
    db.commit()

    return {"message": "删除成功"}