# Windows客户端部署说明

## 环境要求
- Python 3.10+
- Windows操作系统

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行程序
```bash
python main.py
```

## 打包成EXE文件

### 方法1: 使用pyinstaller直接打包
```bash
pyinstaller --onefile --windowed --name "安全整改管理系统" main.py
```

### 方法2: 使用spec文件打包（推荐）
```bash
pyinstaller safety_management.spec
```

打包完成后，EXE文件位于`dist`目录下。

## 配置
首次运行时，需要配置服务器地址。在界面顶部输入服务器地址（例如：http://your-nas-domain:8000），然后点击"保存配置"按钮。

## 功能说明
1. **问题列表**: 显示所有安全问题，支持按状态和严重程度筛选
2. **新增问题**: 创建新的安全问题，可以上传问题照片
3. **编辑问题**: 编辑已存在的问题信息
4. **删除问题**: 删除问题及其关联的照片
5. **上传整改照片**: 为已整改的问题上传整改照片
6. **更新状态**: 更新问题的整改状态（待整改/整改中/已完成）
7. **导出Excel**: 导出问题列表为Excel表格（不包含照片）
8. **导出Excel（带照片）**: 导出问题列表为Excel表格，包含嵌入的照片

## 注意事项
- 确保服务器地址正确且可访问
- 照片上传支持jpg、jpeg、png、bmp格式
- 导出的Excel文件包含所有筛选后的问题