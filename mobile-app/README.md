# 安卓手机APP部署说明

## 环境要求
- Flutter SDK 3.0+
- Android Studio 或 VS Code + Flutter插件
- Android SDK

## 安装依赖
```bash
flutter pub get
```

## 运行应用
```bash
flutter run
```

## 打包成APK

### Debug版本
```bash
flutter build apk --debug
```

### Release版本
```bash
flutter build apk --release
```

打包完成后，APK文件位于 `build/app/outputs/flutter-apk/` 目录下。

## 功能说明
1. **拍照记录问题**: 使用相机拍照，记录安全问题
2. **问题列表**: 查看所有问题，支持按状态和严重程度筛选
3. **问题详情**: 查看问题详细信息，包括照片
4. **上传整改照片**: 为已整改的问题上传整改照片
5. **更新状态**: 更新问题的整改状态
6. **服务器配置**: 配置服务器地址

## 权限要求
- 相机权限（拍照）
- 存储权限（保存照片）
- 网络权限（访问服务器）

## 注意事项
- 首次运行需要配置服务器地址
- 确保服务器地址正确且可访问
- 照片会自动上传到服务器
- 支持离线浏览已缓存的数据

## iOS版本（可选）
如果需要开发iOS版本：
```bash
flutter build ios --release
```

注意：iOS版本需要在Mac电脑上开发，并且需要Xcode。