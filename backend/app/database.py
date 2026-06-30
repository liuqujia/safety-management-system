from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库文件路径
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'safety_management.db')}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    from app import models
    Base.metadata.create_all(bind=engine)

    # 轻量级迁移：为已存在的表补充新列（SQLite ALTER TABLE ADD COLUMN）
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    if 'safety_issues' in inspector.get_table_names():
        existing_cols = {c['name'] for c in inspector.get_columns('safety_issues')}
        with engine.begin() as conn:
            if 'check_date' not in existing_cols:
                conn.execute(text("ALTER TABLE safety_issues ADD COLUMN check_date DATE"))
                print("✅ 迁移：safety_issues.check_date 列已添加")