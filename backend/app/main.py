from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import init_db
from app.api import issues, photos, export

# 创建FastAPI应用
app = FastAPI(
    title="安全整改管理系统API",
    description="安全检查整改管理系统后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(issues.router)
app.include_router(photos.router)
app.include_router(export.router)

# 启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)

    # 初始化数据库
    init_db()
    print("数据库初始化完成")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "安全整改管理系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)