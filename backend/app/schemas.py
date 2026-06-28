from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class IssueCreate(BaseModel):
    """创建问题的数据模型"""
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    severity: str = "一般"
    responsible_person: Optional[str] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None

class IssueUpdate(BaseModel):
    """更新问题的数据模型"""
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    responsible_person: Optional[str] = None
    deadline: Optional[date] = None
    notes: Optional[str] = None

class PhotoResponse(BaseModel):
    """照片响应模型"""
    id: int
    issue_id: int
    photo_type: str
    file_name: str
    upload_time: Optional[datetime] = None
    description: Optional[str] = None
    url: str

class IssueResponse(BaseModel):
    """问题响应模型"""
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    severity: str
    status: str
    responsible_person: Optional[str] = None
    deadline: Optional[str] = None
    notes: Optional[str] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    photo_count: int = 0
    issue_photos: List[PhotoResponse] = []
    rectification_photos: List[PhotoResponse] = []

    class Config:
        from_attributes = True