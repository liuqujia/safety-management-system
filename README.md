# Safety Management System

安全检查与整改跟踪系统，包含 FastAPI 后端和 Vue 前端。

## Features

- Word 问题清单导入预览与导入
- 检查日期、项目、隐患问题分层展示
- 问题照片与整改照片管理
- 整改期限与逾期筛选
- 检查记录、整改回复等 Excel 导出
- 批量更新整改状态
- 重复导入检测

## Project Structure

```text
.
├── backend/             # FastAPI API service
└── safety-vue-simple/   # Vue 3 frontend
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The backend stores runtime data under `backend/data/` by default. This directory is ignored by Git.

Optional ledger export templates are loaded from:

```text
backend/templates/safety_ledger_template.xlsx
```

Template files are intentionally not included because they may contain private business content.

## Frontend

```bash
cd safety-vue-simple
npm install
npm run dev
```

For production:

```bash
npm run build
```

## Docker

Backend example:

```bash
cd backend
docker compose up -d --build
```

Frontend example:

```bash
cd safety-vue-simple
npm run build
docker compose up -d
```

Adjust `safety-vue-simple/nginx.conf` for your own backend address.

## Privacy

This repository excludes:

- Real Word/Excel templates and generated reports
- SQLite databases and uploaded photos
- Deployment scripts with private server addresses
- Company names, project names, personal names, and internal paths
