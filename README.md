# 安全整改管理系统

## 系统概述

这是一个安全检查整改管理系统，包含三个主要组成部分：
- **后端API服务**：部署在NAS上，提供数据存储和同步服务
- **安卓手机APP**：用于现场拍照记录安全问题
- **Windows桌面程序**：用于管理问题、导出Excel表格、上传整改照片

## 技术架构

### 整体架构
```
┌─────────────────┐
│   安卓手机APP   │
│  (现场拍照记录)  │
└────────┬────────┘
         │
         │ HTTPS/REST API
         │
┌────────▼────────┐      ┌──────────────┐
│   后端API服务    │◄────►│  文件存储    │
│  (FastAPI)      │      │  (照片等)     │
│  部署在NAS上     │      └──────────────┘
└────────┬────────┘
         │         ┌──────────────┐
         └────────►│  SQLite数据库  │
                   └──────────────┘
         ▲
         │ HTTPS/REST API
         │
┌────────┴────────┐
│ Windows桌面程序 │
│  (管理和导出)    │
└─────────────────┘
```

### 技术栈

#### 后端服务
- **框架**：FastAPI (Python 3.10+)
- **数据库**：SQLite
- **文件存储**：本地文件系统
- **部署**：Docker容器 + NAS + frp穿透

#### Windows桌面程序
- **框架**：PyQt5
- **打包工具**：pyinstaller (生成单个EXE文件)
- **Excel处理**：openpyxl
- **图片处理**：Pillow

#### 安卓手机APP
- **框架**：Flutter (跨平台)
- **状态管理**：Provider
- **网络请求**：dio
- **图片处理**：image_picker

## 功能模块

### 1. 后端API服务
- 用户认证（简单的API Key或基础认证）
- 问题记录管理（增删改查）
- 照片上传下载
- 整改状态更新
- Excel导出接口

### 2. 安卓手机APP
- 拍照功能
- 问题录入（描述、位置、等级等）
- 问题列表查看
- 本地缓存（离线可用）
- 数据同步

### 3. Windows桌面程序
- 问题管理（查看、编辑、删除）
- 整改状态管理
- 上传整改照片
- 导出Excel表格（包含照片）
- 导入/导出数据

## 数据库设计

### 数据表结构

#### 安全问题表 (safety_issues)
```sql
CREATE TABLE safety_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,                -- 问题标题
    description TEXT,                   -- 问题描述
    location TEXT,                      -- 发现位置
    severity TEXT,                      -- 严重程度 (轻微/一般/严重)
    status TEXT DEFAULT '待整改',        -- 状态 (待整改/整改中/已完成)
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    responsible_person TEXT,           -- 责任人
    deadline DATE,                      -- 整改期限
    notes TEXT                          -- 备注
);
```

#### 照片表 (photos)
```sql
CREATE TABLE photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,         -- 关联问题ID
    photo_type TEXT NOT NULL,           -- 照片类型 (问题照片/整改照片)
    file_path TEXT NOT NULL,            -- 文件存储路径
    file_name TEXT NOT NULL,            -- 文件名
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    description TEXT,                   -- 照片说明
    FOREIGN KEY (issue_id) REFERENCES safety_issues(id)
);
```

#### 用户表 (users) - 可选
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    api_key TEXT NOT NULL,              -- API密钥
    role TEXT DEFAULT 'user',           -- 角色
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 工作流程

### 1. 安全检查流程
1. 安卓APP拍照记录问题
2. 填写问题描述、位置等信息
3. 上传到后端服务器
4. Windows程序同步查看问题列表

### 2. 整改跟踪流程
1. Windows程序导出Excel表格发送给对方
2. 对方整改完成后，发送整改照片
3. 在Windows程序中上传整改照片
4. 更新问题状态为"已完成"
5. 导出最终表格存档

## 部署说明

### NAS部署
1. 安装Docker
2. 拉取后端服务镜像
3. 配置数据卷映射
4. 启动服务
5. 配置frp穿透

### Windows程序
1. 下载EXE文件
2. 配置服务器地址
3. 运行程序

### 安卓APP
1. 安装APK文件
2. 配置服务器地址
3. 开始使用

## 安全考虑
- API Key认证
- HTTPS加密传输（通过frp）
- 文件访问权限控制
- 数据备份策略

## 项目结构
```
safety-management/
├── backend/              # 后端API服务
│   ├── app/
│   ├── requirements.txt
│   └── Dockerfile
├── windows-client/       # Windows桌面程序
│   ├── src/
│   ├── requirements.txt
│   └── build.spec
├── mobile-app/           # 安卓手机APP
│   ├── lib/
│   └── pubspec.yaml
└── docs/                 # 文档
    ├── api.md
    ├── deployment.md
    └── user-guide.md
```