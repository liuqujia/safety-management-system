# 快速开始指南

## 项目已完成！

您已经拥有了一个完整的安全整改管理系统，包含以下三个主要部分：

### 📱 安卓手机APP
用于现场拍照记录安全问题，支持：
- 拍照上传问题照片
- 录入问题详细信息
- 查看问题列表
- 上传整改照片
- 更新问题状态

### 💻 Windows桌面程序（单个EXE）
用于管理问题和导出表格，支持：
- 查看和管理所有问题
- 上传整改照片
- 导出Excel表格（普通版和带照片版）
- 按状态和严重程度筛选
- 更新问题状态

### 🔧 后端API服务（部署到NAS）
提供数据存储和同步，支持：
- 问题数据管理
- 照片文件存储
- Excel导出功能
- RESTful API接口

## 下一步操作

### 第一步：部署后端服务（NAS）
```bash
cd backend
docker-compose up -d
```

### 第二步：打包Windows程序
```bash
cd windows-client
pip install -r requirements.txt
pyinstaller safety_management.spec
```

### 第三步：打包安卓APP
```bash
cd mobile-app
flutter pub get
flutter build apk --release
```

### 第四步：配置frp穿透
在frp配置文件中添加端口映射，使外网可以访问NAS上的服务。

### 第五步：开始使用
1. 安装安卓APP，配置服务器地址
2. 运行Windows EXE，配置服务器地址
3. 开始记录安全问题

## 项目目录结构

```
safety-management/
├── backend/              # 后端API服务
│   ├── app/              # 应用代码
│   ├── requirements.txt  # Python依赖
│   ├── Dockerfile        # Docker配置
│   └── docker-compose.yml
├── windows-client/       # Windows桌面程序
│   ├── src/              # 源代码
│   ├── requirements.txt  # Python依赖
│   ├── safety_management.spec  # 打包配置
│   └── README.md         # 使用说明
├── mobile-app/           # 安卓手机APP
│   ├── lib/              # Flutter代码
│   ├── pubspec.yaml      # Flutter配置
│   └── README.md         # 使用说明
├── docs/                 # 文档
│   ├── deployment_guide.md  # 部署指南
│   └ quick_start.md      # 快速开始
└── README.md             # 项目主文档
```

## 主要功能特性

✅ 现场拍照记录安全问题
✅ 问题信息完整记录（标题、描述、位置、严重程度等）
✅ 整改照片上传
✅ 问题状态跟踪（待整改/整改中/已完成）
✅ Excel表格导出（普通版和带照片版）
✅ 数据云端同步
✅ 多设备协同工作
✅ 数据本地存储，自主控制

## 技术栈

### 后端
- FastAPI (Python)
- SQLite数据库
- Docker容器化部署

### Windows客户端
- PyQt5桌面应用
- Requests网络请求
- Openpyxl Excel处理
- PyInstaller打包

### 安卓APP
- Flutter跨平台框架
- Provider状态管理
- Dio网络请求
- Image Picker拍照

## 完整工作流程

1. **安全检查**
   - 安卓APP拍照记录问题 → 自动上传到服务器

2. **整改跟踪**
   - Windows程序导出Excel → 发送给对方
   - 对方整改完成 → 发送整改照片
   - Windows程序上传整改照片 → 更新状态

3. **存档管理**
   - 导出最终表格 → 存档备查

## 需要帮助？

查看详细文档：
- 📘 [部署指南](docs/deployment_guide.md)
- 📗 [后端服务说明](backend/README.md)
- 📙 [Windows客户端说明](windows-client/README.md)
- 📕 [安卓APP说明](mobile-app/README.md)

祝您使用愉快！🎉