# 安全整改管理系统 - Windows客户端

## 功能特性

- ✅ 安全问题管理（新增、编辑、删除）
- ✅ 照片上传和预览
- ✅ 状态跟踪（待整改、整改中、已完成）
- ✅ 按状态和严重程度筛选
- ✅ Excel导出（标准格式）
- ✅ Excel导出（带照片）
- ✅ 整改回复导出（符合用户要求的格式）

## 环境要求

- Python 3.8+
- Windows 10/11 64位

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 配置服务器

首次运行时，在顶部工具栏输入服务器地址：
- 默认地址：`http://localhost:8000`
- 您的NAS地址：`http://192.168.31.105:9999`

点击"保存配置"按钮保存设置。

## 打包成EXE

```bash
# 安装pyinstaller
pip install pyinstaller

# 打包
pyinstaller safety_management.spec

# 打包后的文件在 dist/ 目录下
```

## 打包后运行

```bash
# 进入dist目录
cd dist

# 运行程序
安全整改管理系统.exe
```

## 使用说明

1. **新增问题**：点击"新增问题"按钮，填写信息并选择问题照片
2. **查看详情**：点击表格中的任意行查看问题详情
3. **上传整改照片**：在详情区域点击"上传整改照片"
4. **更新状态**：在详情区域下拉选择状态
5. **导出整改回复**：点击"导出整改回复"，填写项目信息后导出Excel

## 导出格式

### 标准Excel格式
包含字段：序号、标题、描述、位置、严重程度、状态、责任人、整改期限、创建时间

### 整改回复格式（用户要求）
包含字段：项目名称、项目负责人、隐患事项、整改措施、整改前照片、整改后照片、回复日期
---
> 构建版本由 GitHub Actions 自动构建，触发条件：`push` 到 `main` 分支且 `windows-client/` 目录有改动。
> 下载：进入 GitHub → Actions → Build Windows EXE → latest run → Artifacts
