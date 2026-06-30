from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ExportTemplate(Base):
    """导出模板表"""
    __tablename__ = "export_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="模板名称")
    title_format = Column(String(200), default="《关于{date}安全隐患整改有关事项回复》", comment="标题格式")
    # columns 配置存储为 JSON 字符串
    columns_config = Column(Text, default="[]", comment="列配置JSON")
    is_default = Column(Boolean, default=False, comment="是否默认模板")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def to_dict(self):
        import json
        try:
            columns = json.loads(self.columns_config)
        except Exception:
            columns = []
        return {
            "id": self.id,
            "name": self.name,
            "title_format": self.title_format,
            "columns": columns,
            "is_default": self.is_default,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }


class SafetyIssue(Base):
    """安全问题表"""
    __tablename__ = "safety_issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(200), nullable=False, comment="问题标题")
    description = Column(Text, comment="问题描述")
    location = Column(String(200), comment="发现位置")
    severity = Column(String(20), default="一般", comment="严重程度：轻微/一般/严重")
    status = Column(String(20), default="待整改", comment="状态：待整改/整改中/已完成")
    responsible_person = Column(String(100), comment="责任人")
    deadline = Column(Date, comment="整改期限")
    notes = Column(Text, comment="备注")
    project_name = Column(String(200), comment="项目名称")
    check_date = Column(Date, comment="检查日期（每次上传/每次检查的日期）")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    photos = relationship("Photo", back_populates="issue", cascade="all, delete-orphan")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "severity": self.severity,
            "status": self.status,
            "responsible_person": self.responsible_person,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "check_date": self.check_date.isoformat() if self.check_date else None,
            "notes": self.notes,
            "project_name": self.project_name,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
            "photo_count": len(self.photos),
            "issue_photos": [p.to_dict() for p in self.photos if p.photo_type == "问题照片"],
            "rectification_photos": [p.to_dict() for p in self.photos if p.photo_type == "整改照片"]
        }

class Photo(Base):
    """照片表"""
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    issue_id = Column(Integer, ForeignKey("safety_issues.id"), nullable=False, comment="关联问题ID")
    photo_type = Column(String(20), nullable=False, comment="照片类型：问题照片/整改照片")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_name = Column(String(200), nullable=False, comment="文件名")
    upload_time = Column(DateTime, default=datetime.now, comment="上传时间")
    description = Column(Text, comment="照片说明")

    issue = relationship("SafetyIssue", back_populates="photos")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "issue_id": self.issue_id,
            "photo_type": self.photo_type,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "description": self.description,
            "url": f"/api/photos/{self.id}/download"
        }

class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    hashed_password = Column(String(200), nullable=False, comment="加密密码")
    api_key = Column(String(100), unique=True, nullable=False, comment="API密钥")
    role = Column(String(20), default="user", comment="角色：admin/user")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "create_time": self.create_time.isoformat() if self.create_time else None
        }
