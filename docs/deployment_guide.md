# 安全整改管理系统部署指南

## 系统概述
本系统包含三个主要部分：
- **后端API服务**：部署在NAS上，提供数据存储和同步服务
- **安卓手机APP**：用于现场拍照记录安全问题
- **Windows桌面程序**：用于管理问题、导出Excel表格、上传整改照片

## 一、后端服务部署（NAS）

### 1.1 安装Docker
确保您的NAS已安装Docker。如果没有，请参考NAS厂商的文档安装。

### 1.2 构建后端服务
```bash
cd backend
docker-compose up -d
```

### 1.3 验证服务
访问 http://NAS_IP:8000 查看服务是否正常运行。
访问 http://NAS_IP:8000/docs 查看API文档。

### 1.4 配置frp穿透
在frp客户端配置文件中添加：
```ini
[safety-management]
type = tcp
local_ip = 127.0.0.1
local_port = 8000
remote_port = 8000
```

启动frp客户端后，可以通过外网域名访问：http://your-domain:8000

## 二、Windows客户端部署

### 2.1 安装Python环境
安装Python 3.10或更高版本。

### 2.2 安装依赖
```bash
cd windows-client
pip install -r requirements.txt
```

### 2.3 测试运行
```bash
python main.py
```

### 2.4 打包成EXE
```bash
pyinstaller safety_management.spec
```

打包完成后，EXE文件位于 `dist` 目录下。

### 2.5 使用说明
1. 运行EXE文件
2. 配置服务器地址（例如：http://your-domain:8000）
3. 开始使用

## 三、安卓APP部署

### 3.1 安装Flutter环境
安装Flutter SDK和Android Studio。

### 3.2 安装依赖
```bash
cd mobile-app
flutter pub get
```

### 3.3 测试运行
```bash
flutter run
```

### 3.4 打包成APK
```bash
flutter build apk --release
```

打包完成后，APK文件位于 `build/app/outputs/flutter-apk/` 目录下。

### 3.5 安装使用
1. 在安卓手机上安装APK文件
2. 配置服务器地址
3. 开始使用

## 四、完整工作流程

### 4.1 安全检查流程
1. 使用安卓APP现场拍照记录问题
2. 填写问题描述、位置等信息
3. 自动上传到服务器

### 4.2 整改跟踪流程
1. Windows程序查看问题列表
2. 导出Excel表格发送给对方
3. 对方整改完成后，发送整改照片
4. Windows程序上传整改照片
5. 更新问题状态为"已完成"
6. 导出最终表格存档

## 五、常见问题

### 5.1 服务器无法访问
- 检查Docker服务是否正常运行
- 检查frp穿透配置是否正确
- 检查防火墙设置

### 5.2 照片上传失败
- 检查网络连接
- 检查照片大小（建议不超过5MB）
- 检查服务器存储空间

### 5.3 Excel导出失败
- 检查是否有问题数据
- 检查照片是否完整
- 检查Excel软件版本

## 六、数据备份

### 6.1 数据库备份
定期备份 `backend/data/safety_management.db` 文件。

### 6.2 照片备份
定期备份 `backend/data/photos` 目录。

### 6.3 自动备份脚本（可选）
创建定时任务，自动备份数据到其他存储设备。

## 七、安全建议

### 7.1 网络安全
- 使用HTTPS（配置SSL证书）
- 设置API访问密码
- 定期更新frp密码

### 7.2 数据安全
- 定期备份数据
- 设置访问权限
- 记录操作日志

## 八、性能优化

### 8.1 图片优化
- 自动压缩上传的图片
- 设置合理的图片尺寸

### 8.2 数据库优化
- 定期清理过期数据
- 设置数据库索引

## 九、扩展功能（可选）

### 9.1 多用户支持
添加用户认证功能，支持多用户使用。

### 9.2 权限管理
添加角色和权限管理，不同用户有不同的操作权限。

### 9.3 统计分析
添加数据统计和图表展示功能。

### 9.4 移动端优化
开发iOS版本，支持更多移动设备。

## 十、技术支持

如有问题，请查看各组件的README文档：
- 后端服务：backend/README.md
- Windows客户端：windows-client/README.md
- 安卓APP：mobile-app/README.md

或查看项目主文档：README.md