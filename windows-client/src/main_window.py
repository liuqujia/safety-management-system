import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QFileDialog,
                             QMessageBox, QDateEdit, QGroupBox, QScrollArea,
                             QSplitter, QListWidget, QListWidgetItem, QProgressBar)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QPixmap, QIcon
import requests
from datetime import datetime
import json

class APIClient:
    """API客户端"""
    def __init__(self, base_url):
        self.base_url = base_url

    def get_issues(self, status=None, severity=None):
        """获取问题列表"""
        params = {}
        if status:
            params['status'] = status
        if severity:
            params['severity'] = severity

        response = requests.get(f"{self.base_url}/api/issues/", params=params)
        return response.json() if response.status_code == 200 else []

    def get_issue(self, issue_id):
        """获取单个问题"""
        response = requests.get(f"{self.base_url}/api/issues/{issue_id}")
        return response.json() if response.status_code == 200 else None

    def create_issue(self, data, photos):
        """创建问题"""
        files = [('photos', (photo[0], open(photo[1], 'rb'))) for photo in photos]
        response = requests.post(
            f"{self.base_url}/api/issues/with-photos",
            data=data,
            files=files
        )
        # 关闭文件
        for file_tuple in files:
            file_tuple[1][1].close()
        return response.json() if response.status_code == 200 else None

    def update_issue(self, issue_id, data):
        """更新问题"""
        response = requests.put(f"{self.base_url}/api/issues/{issue_id}", json=data)
        return response.json() if response.status_code == 200 else None

    def delete_issue(self, issue_id):
        """删除问题"""
        response = requests.delete(f"{self.base_url}/api/issues/{issue_id}")
        return response.status_code == 200

    def upload_photo(self, issue_id, photo_type, photos):
        """上传照片"""
        files = [('photos', (photo[0], open(photo[1], 'rb'))) for photo in photos]
        data = {'photo_type': photo_type}
        response = requests.post(
            f"{self.base_url}/api/issues/{issue_id}/photos",
            data=data,
            files=files
        )
        # 关闭文件
        for file_tuple in files:
            file_tuple[1][1].close()
        return response.json() if response.status_code == 200 else None

    def update_status(self, issue_id, status):
        """更新状态"""
        response = requests.put(
            f"{self.base_url}/api/issues/{issue_id}/status",
            params={'status': status}
        )
        return response.json() if response.status_code == 200 else None

    def download_photo(self, photo_id, save_path):
        """下载照片"""
        response = requests.get(f"{self.base_url}/api/photos/{photo_id}/download")
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        return False

    def export_excel(self, status=None, severity=None):
        """导出Excel"""
        params = {}
        if status:
            params['status'] = status
        if severity:
            params['severity'] = severity

        response = requests.get(
            f"{self.base_url}/api/export/excel",
            params=params
        )
        if response.status_code == 200:
            return response.content
        return None

    def export_excel_with_photos(self, status=None, severity=None):
        """导出Excel（带照片）"""
        params = {}
        if status:
            params['status'] = status
        if severity:
            params['severity'] = severity

        response = requests.get(
            f"{self.base_url}/api/export/excel-with-photos",
            params=params
        )
        if response.status_code == 200:
            return response.content
        return None

class MainWindow(QMainWindow):
    """主窗口"""
    def __init__(self):
        super().__init__()
        self.api_client = None
        self.config_file = "config.json"
        self.load_config()
        self.init_ui()
        self.refresh_issues()

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.server_url = config.get('server_url', 'http://localhost:8000')
        else:
            self.server_url = 'http://localhost:8000'

        self.api_client = APIClient(self.server_url)

    def save_config(self):
        """保存配置"""
        config = {'server_url': self.server_url}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("安全整改管理系统")
        self.setGeometry(100, 100, 1400, 800)

        # 创建主窗口部件
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # 顶部工具栏
        toolbar_layout = QHBoxLayout()

        # 服务器配置
        self.server_input = QLineEdit(self.server_url)
        self.server_input.setPlaceholderText("服务器地址")
        toolbar_layout.addWidget(QLabel("服务器:"))
        toolbar_layout.addWidget(self.server_input)

        # 保存配置按钮
        save_config_btn = QPushButton("保存配置")
        save_config_btn.clicked.connect(self.save_server_config)
        toolbar_layout.addWidget(save_config_btn)

        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_issues)
        toolbar_layout.addWidget(refresh_btn)

        # 状态筛选
        toolbar_layout.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "待整改", "整改中", "已完成"])
        self.status_filter.currentTextChanged.connect(self.filter_issues)
        toolbar_layout.addWidget(self.status_filter)

        # 严重程度筛选
        toolbar_layout.addWidget(QLabel("严重程度:"))
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["全部", "轻微", "一般", "严重"])
        self.severity_filter.currentTextChanged.connect(self.filter_issues)
        toolbar_layout.addWidget(self.severity_filter)

        main_layout.addLayout(toolbar_layout)

        # 功能按钮区
        function_layout = QHBoxLayout()

        # 新增问题按钮
        add_issue_btn = QPushButton("新增问题")
        add_issue_btn.clicked.connect(self.add_issue_dialog)
        function_layout.addWidget(add_issue_btn)

        # 导出Excel按钮
        export_btn = QPushButton("导出Excel")
        export_btn.clicked.connect(self.export_excel_dialog)
        function_layout.addWidget(export_btn)

        # 导出Excel（带照片）按钮
        export_with_photos_btn = QPushButton("导出Excel（带照片）")
        export_with_photos_btn.clicked.connect(self.export_excel_with_photos_dialog)
        function_layout.addWidget(export_with_photos_btn)

        main_layout.addLayout(function_layout)

        # 问题列表表格
        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(8)
        self.issues_table.setHorizontalHeaderLabels([
            "ID", "问题标题", "发现位置", "严重程度", "状态", "责任人", "创建时间", "照片数"
        ])
        self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.issues_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.issues_table.setSelectionMode(QTableWidget.SingleSelection)
        self.issues_table.cellClicked.connect(self.show_issue_detail)

        main_layout.addWidget(self.issues_table)

        # 详情区域（使用分割器）
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：问题详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        detail_widget.setLayout(detail_layout)

        detail_layout.addWidget(QLabel("问题详情:"))

        # 详情表单
        detail_form = QFormLayout()

        self.detail_title = QLineEdit()
        self.detail_title.setReadOnly(True)
        detail_form.addRow("标题:", self.detail_title)

        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        detail_form.addRow("描述:", self.detail_description)

        self.detail_location = QLineEdit()
        self.detail_location.setReadOnly(True)
        detail_form.addRow("位置:", self.detail_location)

        self.detail_severity = QLineEdit()
        self.detail_severity.setReadOnly(True)
        detail_form.addRow("严重程度:", self.detail_severity)

        self.detail_status = QComboBox()
        self.detail_status.addItems(["待整改", "整改中", "已完成"])
        self.detail_status.currentTextChanged.connect(self.update_issue_status)
        detail_form.addRow("状态:", self.detail_status)

        self.detail_responsible = QLineEdit()
        self.detail_responsible.setReadOnly(True)
        detail_form.addRow("责任人:", self.detail_responsible)

        self.detail_deadline = QLineEdit()
        self.detail_deadline.setReadOnly(True)
        detail_form.addRow("整改期限:", self.detail_deadline)

        self.detail_create_time = QLineEdit()
        self.detail_create_time.setReadOnly(True)
        detail_form.addRow("创建时间:", self.detail_create_time)

        detail_layout.addLayout(detail_form)

        # 操作按钮
        detail_btn_layout = QHBoxLayout()

        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_issue_dialog)
        detail_btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_issue)
        detail_btn_layout.addWidget(delete_btn)

        detail_layout.addLayout(detail_btn_layout)

        splitter.addWidget(detail_widget)

        # 右侧：照片显示
        photos_widget = QWidget()
        photos_layout = QVBoxLayout()
        photos_widget.setLayout(photos_layout)

        photos_layout.addWidget(QLabel("照片:"))

        # 问题照片列表
        photos_layout.addWidget(QLabel("问题照片:"))
        self.issue_photos_list = QListWidget()
        self.issue_photos_list.itemClicked.connect(self.show_photo_preview)
        photos_layout.addWidget(self.issue_photos_list)

        # 整改照片列表
        photos_layout.addWidget(QLabel("整改照片:"))
        self.rectification_photos_list = QListWidget()
        self.rectification_photos_list.itemClicked.connect(self.show_photo_preview)
        photos_layout.addWidget(self.rectification_photos_list)

        # 上传整改照片按钮
        upload_rectification_btn = QPushButton("上传整改照片")
        upload_rectification_btn.clicked.connect(self.upload_rectification_photo)
        photos_layout.addWidget(upload_rectification_btn)

        splitter.addWidget(photos_widget)

        # 图片预览区域
        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_widget.setLayout(preview_layout)

        preview_layout.addWidget(QLabel("照片预览:"))
        self.photo_preview = QLabel()
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setMinimumSize(300, 300)
        preview_layout.addWidget(self.photo_preview)

        splitter.addWidget(preview_widget)

        # 设置分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)

        main_layout.addWidget(splitter)

    def save_server_config(self):
        """保存服务器配置"""
        self.server_url = self.server_input.text()
        self.api_client = APIClient(self.server_url)
        self.save_config()
        QMessageBox.information(self, "成功", "服务器配置已保存")
        self.refresh_issues()

    def refresh_issues(self):
        """刷新问题列表"""
        try:
            issues = self.api_client.get_issues()
            self.display_issues(issues)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取问题列表失败: {str(e)}")

    def display_issues(self, issues):
        """显示问题列表"""
        self.issues_table.setRowCount(len(issues))

        for row, issue in enumerate(issues):
            self.issues_table.setItem(row, 0, QTableWidgetItem(str(issue['id'])))
            self.issues_table.setItem(row, 1, QTableWidgetItem(issue['title']))
            self.issues_table.setItem(row, 2, QTableWidgetItem(issue.get('location', '')))
            self.issues_table.setItem(row, 3, QTableWidgetItem(issue['severity']))
            self.issues_table.setItem(row, 4, QTableWidgetItem(issue['status']))

            responsible = issue.get('responsible_person', '')
            self.issues_table.setItem(row, 5, QTableWidgetItem(responsible))

            create_time = issue.get('create_time', '')
            if create_time:
                create_time = datetime.fromisoformat(create_time).strftime("%Y-%m-%d %H:%M")
            self.issues_table.setItem(row, 6, QTableWidgetItem(create_time))

            self.issues_table.setItem(row, 7, QTableWidgetItem(str(issue['photo_count'])))

    def filter_issues(self):
        """筛选问题"""
        status = self.status_filter.currentText()
        severity = self.severity_filter.currentText()

        status_param = None if status == "全部" else status
        severity_param = None if severity == "全部" else severity

        try:
            issues = self.api_client.get_issues(status_param, severity_param)
            self.display_issues(issues)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"筛选失败: {str(e)}")

    def show_issue_detail(self, row, col):
        """显示问题详情"""
        issue_id = int(self.issues_table.item(row, 0).text())

        try:
            issue = self.api_client.get_issue(issue_id)
            if issue:
                self.current_issue = issue
                self.display_issue_detail(issue)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取问题详情失败: {str(e)}")

    def display_issue_detail(self, issue):
        """显示问题详情"""
        self.detail_title.setText(issue['title'])
        self.detail_description.setText(issue.get('description', ''))
        self.detail_location.setText(issue.get('location', ''))
        self.detail_severity.setText(issue['severity'])
        self.detail_status.setCurrentText(issue['status'])
        self.detail_responsible.setText(issue.get('responsible_person', ''))

        deadline = issue.get('deadline', '')
        if deadline:
            deadline = datetime.fromisoformat(deadline).strftime("%Y-%m-%d")
        self.detail_deadline.setText(deadline)

        create_time = issue.get('create_time', '')
        if create_time:
            create_time = datetime.fromisoformat(create_time).strftime("%Y-%m-%d %H:%M")
        self.detail_create_time.setText(create_time)

        # 显示照片列表
        self.issue_photos_list.clear()
        for photo in issue.get('issue_photos', []):
            item = QListWidgetItem(f"{photo['id']}: {photo['file_name']}")
            item.setData(Qt.UserRole, photo['id'])
            self.issue_photos_list.addItem(item)

        self.rectification_photos_list.clear()
        for photo in issue.get('rectification_photos', []):
            item = QListWidgetItem(f"{photo['id']}: {photo['file_name']}")
            item.setData(Qt.UserRole, photo['id'])
            self.rectification_photos_list.addItem(item)

    def show_photo_preview(self, item):
        """显示照片预览"""
        photo_id = item.data(Qt.UserRole)

        try:
            # 下载照片到临时文件
            temp_path = f"temp_photo_{photo_id}.jpg"
            if self.api_client.download_photo(photo_id, temp_path):
                # 显示照片
                pixmap = QPixmap(temp_path)
                self.photo_preview.setPixmap(pixmap.scaled(
                    self.photo_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                # 删除临时文件
                os.remove(temp_path)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载照片失败: {str(e)}")

    def update_issue_status(self, status):
        """更新问题状态"""
        if hasattr(self, 'current_issue'):
            try:
                self.api_client.update_status(self.current_issue['id'], status)
                QMessageBox.information(self, "成功", "状态已更新")
                self.refresh_issues()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"更新状态失败: {str(e)}")

    def add_issue_dialog(self):
        """新增问题对话框"""
        dialog = AddIssueDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_issues()

    def edit_issue_dialog(self):
        """编辑问题对话框"""
        if hasattr(self, 'current_issue'):
            dialog = EditIssueDialog(self, self.current_issue)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_issues()

    def delete_issue(self):
        """删除问题"""
        if hasattr(self, 'current_issue'):
            reply = QMessageBox.question(
                self, '确认删除',
                '确定要删除这个问题吗？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                try:
                    self.api_client.delete_issue(self.current_issue['id'])
                    QMessageBox.information(self, "成功", "问题已删除")
                    self.refresh_issues()
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"删除失败: {str(e)}")

    def upload_rectification_photo(self):
        """上传整改照片"""
        if hasattr(self, 'current_issue'):
            files = QFileDialog.getOpenFileNames(
                self, "选择整改照片", "",
                "Images (*.png *.jpg *.jpeg *.bmp)"
            )

            if files[0]:
                try:
                    photos = [(os.path.basename(f), f) for f in files[0]]
                    self.api_client.upload_photo(
                        self.current_issue['id'],
                        "整改照片",
                        photos
                    )
                    QMessageBox.information(self, "成功", "整改照片已上传")
                    self.show_issue_detail(
                        self.issues_table.currentRow(),
                        0
                    )
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"上传失败: {str(e)}")

    def export_excel_dialog(self):
        """导出Excel对话框"""
        file_path = QFileDialog.getSaveFileName(
            self, "保存Excel文件", "",
            "Excel (*.xlsx)"
        )

        if file_path[0]:
            try:
                status = self.status_filter.currentText()
                severity = self.severity_filter.currentText()

                status_param = None if status == "全部" else status
                severity_param = None if severity == "全部" else severity

                content = self.api_client.export_excel(status_param, severity_param)
                if content:
                    with open(file_path[0], 'wb') as f:
                        f.write(content)
                    QMessageBox.information(self, "成功", "Excel文件已导出")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")

    def export_excel_with_photos_dialog(self):
        """导出Excel（带照片）对话框"""
        file_path = QFileDialog.getSaveFileName(
            self, "保存Excel文件（带照片）", "",
            "Excel (*.xlsx)"
        )

        if file_path[0]:
            try:
                status = self.status_filter.currentText()
                severity = self.severity_filter.currentText()

                status_param = None if status == "全部" else status
                severity_param = None if severity == "全部" else severity

                content = self.api_client.export_excel_with_photos(status_param, severity_param)
                if content:
                    with open(file_path[0], 'wb') as f:
                        f.write(content)
                    QMessageBox.information(self, "成功", "Excel文件已导出")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")

class AddIssueDialog(QDialog):
    """新增问题对话框"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.photos = []
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("新增问题")
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 表单
        form = QFormLayout()

        self.title_input = QLineEdit()
        form.addRow("标题*:", self.title_input)

        self.description_input = QTextEdit()
        form.addRow("描述:", self.description_input)

        self.location_input = QLineEdit()
        form.addRow("位置:", self.location_input)

        self.severity_input = QComboBox()
        self.severity_input.addItems(["轻微", "一般", "严重"])
        self.severity_input.setCurrentText("一般")
        form.addRow("严重程度:", self.severity_input)

        self.responsible_input = QLineEdit()
        form.addRow("责任人:", self.responsible_input)

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate().addDays(7))
        form.addRow("整改期限:", self.deadline_input)

        self.notes_input = QTextEdit()
        form.addRow("备注:", self.notes_input)

        layout.addLayout(form)

        # 照片选择
        photo_layout = QHBoxLayout()
        photo_layout.addWidget(QLabel("问题照片:"))

        select_photo_btn = QPushButton("选择照片")
        select_photo_btn.clicked.connect(self.select_photos)
        photo_layout.addWidget(select_photo_btn)

        self.photo_count_label = QLabel("已选择: 0张")
        photo_layout.addWidget(self.photo_count_label)

        layout.addLayout(photo_layout)

        # 按钮
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_issue)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def select_photos(self):
        """选择照片"""
        files = QFileDialog.getOpenFileNames(
            self, "选择问题照片", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if files[0]:
            self.photos = [(os.path.basename(f), f) for f in files[0]]
            self.photo_count_label.setText(f"已选择: {len(self.photos)}张")

    def save_issue(self):
        """保存问题"""
        if not self.title_input.text():
            QMessageBox.warning(self, "警告", "请填写标题")
            return

        data = {
            'title': self.title_input.text(),
            'description': self.description_input.toPlainText(),
            'location': self.location_input.text(),
            'severity': self.severity_input.currentText(),
            'responsible_person': self.responsible_input.text(),
            'deadline': self.deadline_input.date().toString("yyyy-MM-dd"),
            'notes': self.notes_input.toPlainText()
        }

        try:
            self.parent_window.api_client.create_issue(data, self.photos)
            QMessageBox.information(self, "成功", "问题已创建")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"创建失败: {str(e)}")

class EditIssueDialog(QDialog):
    """编辑问题对话框"""
    def __init__(self, parent, issue):
        super().__init__(parent)
        self.parent_window = parent
        self.issue = issue
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("编辑问题")
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # 表单
        form = QFormLayout()

        self.title_input = QLineEdit(self.issue['title'])
        form.addRow("标题*:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setText(self.issue.get('description', ''))
        form.addRow("描述:", self.description_input)

        self.location_input = QLineEdit(self.issue.get('location', ''))
        form.addRow("位置:", self.location_input)

        self.severity_input = QComboBox()
        self.severity_input.addItems(["轻微", "一般", "严重"])
        self.severity_input.setCurrentText(self.issue['severity'])
        form.addRow("严重程度:", self.severity_input)

        self.responsible_input = QLineEdit(self.issue.get('responsible_person', ''))
        form.addRow("责任人:", self.responsible_input)

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        deadline = self.issue.get('deadline', '')
        if deadline:
            self.deadline_input.setDate(QDate.fromString(deadline.split('T')[0], "yyyy-MM-dd"))
        form.addRow("整改期限:", self.deadline_input)

        self.notes_input = QTextEdit()
        self.notes_input.setText(self.issue.get('notes', ''))
        form.addRow("备注:", self.notes_input)

        layout.addLayout(form)

        # 按钮
        btn_layout = QHBoxLayout()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_issue)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def save_issue(self):
        """保存问题"""
        if not self.title_input.text():
            QMessageBox.warning(self, "警告", "请填写标题")
            return

        data = {
            'title': self.title_input.text(),
            'description': self.description_input.toPlainText(),
            'location': self.location_input.text(),
            'severity': self.severity_input.currentText(),
            'responsible_person': self.responsible_input.text(),
            'deadline': self.deadline_input.date().toString("yyyy-MM-dd"),
            'notes': self.notes_input.toPlainText()
        }

        try:
            self.parent_window.api_client.update_issue(self.issue['id'], data)
            QMessageBox.information(self, "成功", "问题已更新")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"更新失败: {str(e)}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()