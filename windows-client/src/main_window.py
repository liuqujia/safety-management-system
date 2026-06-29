import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QTextEdit,
                             QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QFileDialog,
                             QMessageBox, QDateEdit, QGroupBox, QScrollArea,
                             QSplitter, QListWidget, QListWidgetItem, QProgressBar,
                             QToolBar, QAction, QCheckBox, QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
import requests
from datetime import datetime
import json

class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_issues(self, status=None, severity=None):
        params = {}
        if status:
            params['status'] = status
        if severity:
            params['severity'] = severity
        response = requests.get(f"{self.base_url}/api/issues/", params=params, timeout=30)
        return response.json() if response.status_code == 200 else []

    def get_issue(self, issue_id):
        response = requests.get(f"{self.base_url}/api/issues/{issue_id}", timeout=30)
        return response.json() if response.status_code == 200 else None

    def create_issue(self, data, photos):
        files = [('photos', (photo[0], open(photo[1], 'rb'))) for photo in photos]
        response = requests.post(
            f"{self.base_url}/api/issues/with-photos",
            data=data,
            files=files,
            timeout=60
        )
        for file_tuple in files:
            file_tuple[1].close()
        return response.json() if response.status_code == 200 else None

    def update_issue(self, issue_id, data):
        response = requests.put(f"{self.base_url}/api/issues/{issue_id}", json=data, timeout=30)
        return response.json() if response.status_code == 200 else None

    def delete_issue(self, issue_id):
        response = requests.delete(f"{self.base_url}/api/issues/{issue_id}", timeout=30)
        return response.status_code == 200

    def upload_photo(self, issue_id, photo_type, photos):
        files = [('photos', (photo[0], open(photo[1], 'rb'))) for photo in photos]
        data = {'photo_type': photo_type}
        response = requests.post(
            f"{self.base_url}/api/issues/{issue_id}/photos",
            data=data,
            files=files,
            timeout=60
        )
        for file_tuple in files:
            file_tuple[1].close()
        return response.json() if response.status_code == 200 else None

    def update_status(self, issue_id, status):
        response = requests.put(
            f"{self.base_url}/api/issues/{issue_id}/status",
            params={'status': status},
            timeout=30
        )
        return response.json() if response.status_code == 200 else None

    def download_photo(self, photo_id, save_path):
        response = requests.get(f"{self.base_url}/api/photos/{photo_id}/download", timeout=30)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
        return False

    def export_excel(self, status=None, severity=None):
        params = {}
        if status:
            params['status'] = status
        if severity:
            params['severity'] = severity
        response = requests.get(
            f"{self.base_url}/api/export/excel",
            params=params,
            timeout=60
        )
        if response.status_code == 200:
            return response.content
        return None

    def export_excel_with_photos(self, status=None, severity=None):
        params = {}
        if status:
            params['status'] = status
        if severity:
            params['severity'] = severity
        response = requests.get(
            f"{self.base_url}/api/export/excel-with-photos",
            params=params,
            timeout=60
        )
        if response.status_code == 200:
            return response.content
        return None

    def export_rectification_reply(self, project_name, project_responsible, reply_date, issues=None):
        data = {
            'project_name': project_name,
            'project_responsible': project_responsible,
            'reply_date': reply_date
        }
        if issues:
            data['issue_ids'] = issues

        response = requests.post(
            f"{self.base_url}/api/export/rectification-reply",
            json=data,
            timeout=120
        )
        if response.status_code == 200:
            return response.content
        return None

    def preview_from_word(self, file_path):
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(
                f"{self.base_url}/api/issues/preview-from-word",
                files=files,
                timeout=60
            )
        return response.json() if response.status_code == 200 else None

    def import_from_word(self, file_path, skip_indices=None):
        with open(file_path, 'rb') as f:
            data = {}
            if skip_indices:
                data['skip_indices'] = ','.join(str(i) for i in skip_indices)
            files = {'file': (os.path.basename(file_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(
                f"{self.base_url}/api/issues/import-from-word",
                data=data,
                files=files,
                timeout=120
            )
        return response.json() if response.status_code == 200 else None

    def get_templates(self):
        response = requests.get(f"{self.base_url}/api/export/templates", timeout=30)
        return response.json() if response.status_code == 200 else []

    def export_excel_with_template(self, status=None, severity=None, template_id=None):
        params = {}
        if status:
            params['status'] = status
        if severity:
            params['severity'] = severity
        if template_id:
            params['template_id'] = template_id
        response = requests.get(
            f"{self.base_url}/api/export/excel",
            params=params,
            timeout=60
        )
        if response.status_code == 200:
            return response.content
        return None


class ImportPreviewDialog(QDialog):
    def __init__(self, preview_data, parent=None):
        super().__init__(parent)
        self.preview_data = preview_data
        self.items = preview_data.get('items', [])
        self.checkboxes = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("导入预览 - 勾选要导入的隐患")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)

        info_label = QLabel()
        project = self.preview_data.get('project_name', '未识别到项目名称')
        info_label.setText(f"<b>项目：</b>{project}　　<b>共 {len(self.items)} 条隐患（勾选表示导入）</b>")
        info_label.setStyleSheet("padding: 8px; background: #f5f5f5; border-radius: 4px;")
        layout.addWidget(info_label)

        btn_row = QHBoxLayout()
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setStyleSheet("padding: 6px 16px;")
        self.deselect_all_btn = QPushButton("取消全选")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        self.deselect_all_btn.setStyleSheet("padding: 6px 16px;")
        btn_row.addWidget(self.select_all_btn)
        btn_row.addWidget(self.deselect_all_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(6)

        self.item_rows = []  # [(row_widget, checkbox, idx_label)]
        for idx, item in enumerate(self.items):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(8, 4, 8, 4)

            cb = QCheckBox()
            cb.setChecked(True)
            self.checkboxes.append(cb)
            row_layout.addWidget(cb)

            idx_label = QLabel(f"<b>{idx + 1}</b>")
            idx_label.setMinimumWidth(30)
            idx_label.setAlignment(Qt.AlignCenter)
            row_layout.addWidget(idx_label)

            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(0, 0, 0, 0)

            title_label = QLabel(f"<b>{item.get('title', '')}</b>")
            title_label.setWordWrap(True)
            content_layout.addWidget(title_label)

            if item.get('description'):
                desc_label = QLabel(f'<font color="#666" size="-1">描述：{item.get("description", "")[:80]}</font>')
                desc_label.setWordWrap(True)
                content_layout.addWidget(desc_label)
            if item.get('notes'):
                notes_label = QLabel(f'<font color="#888" size="-1">措施：{item.get("notes", "")[:80]}</font>')
                notes_label.setWordWrap(True)
                content_layout.addWidget(notes_label)
            if item.get('deadline'):
                dl_label = QLabel(f'<font color="#E6A23C" size="-1">期限：{item.get("deadline")}</font>')
                content_layout.addWidget(dl_label)

            content_layout.addStretch()
            row_layout.addWidget(content_widget, 1)

            # 删除按钮
            del_btn = QPushButton("删除")
            del_btn.setStyleSheet("background-color: #F56C6C; color: white; padding: 4px 12px; border-radius: 4px; font-size: 12px;")
            del_btn.setMinimumWidth(50)
            del_btn.clicked.connect(lambda checked, r=row, c=cb, lbl=idx_label, dbtn=del_btn: self._remove_item(r, c, lbl, dbtn))
            row_layout.addWidget(del_btn)

            scroll_layout.addWidget(row)
            self.item_rows.append((row, cb, idx_label, del_btn))

    def _remove_item(self, row, cb, idx_label, del_btn):
        """从预览列表中物理删除这一行"""
        row.hide()
        cb.setChecked(False)  # 标记为跳过
        self.update_count()

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        bottom_row = QHBoxLayout()
        self.count_label = QLabel()
        self.count_label.setStyleSheet("color: #409EFF; font-weight: bold;")
        self.update_count()
        bottom_row.addWidget(self.count_label)
        bottom_row.addStretch()

        self.confirm_btn = QPushButton("确认导入")
        self.confirm_btn.setStyleSheet("background-color: #409EFF; color: white; padding: 8px 24px; border-radius: 4px;")
        self.confirm_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("padding: 8px 24px;")
        cancel_btn.clicked.connect(self.reject)
        bottom_row.addWidget(self.confirm_btn)
        bottom_row.addWidget(cancel_btn)
        layout.addLayout(bottom_row)

        for cb in self.checkboxes:
            cb.toggled.connect(self.update_count)

    def update_count(self):
        checked = sum(1 for cb in self.checkboxes if cb.isChecked())
        self.count_label.setText(f"已选 {checked} / {len(self.items)} 条")

    def select_all(self):
        for cb in self.checkboxes:
            cb.setChecked(True)

    def deselect_all(self):
        for cb in self.checkboxes:
            cb.setChecked(False)

    def get_skip_indices(self):
        skip = []
        for idx, cb in enumerate(self.checkboxes):
            if not cb.isChecked():
                skip.append(idx)
        return skip

    def get_checked_count(self):
        return sum(1 for cb in self.checkboxes if cb.isChecked())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_client = None
        self.config_file = "config.json"
        self.load_config()
        self.init_ui()
        self.refresh_issues()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.server_url = config.get('server_url', 'http://localhost:8000')
        else:
            self.server_url = 'http://localhost:8000'
        self.api_client = APIClient(self.server_url)

    def save_config(self):
        config = {'server_url': self.server_url}
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def init_ui(self):
        self.setWindowTitle("安全整改管理系统")
        self.setGeometry(100, 100, 1400, 900)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        toolbar.addWidget(QLabel("服务器:"))
        self.server_input = QLineEdit(self.server_url)
        self.server_input.setFixedWidth(200)
        toolbar.addWidget(self.server_input)

        save_config_btn = QPushButton("保存配置")
        save_config_btn.clicked.connect(self.save_server_config)
        toolbar.addWidget(save_config_btn)

        toolbar.addSeparator()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_issues)
        toolbar.addWidget(refresh_btn)

        toolbar.addSeparator()

        toolbar.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "待整改", "整改中", "已完成"])
        self.status_filter.currentTextChanged.connect(self.filter_issues)
        toolbar.addWidget(self.status_filter)

        toolbar.addWidget(QLabel("严重程度:"))
        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["全部", "轻微", "一般", "严重"])
        self.severity_filter.currentTextChanged.connect(self.filter_issues)
        toolbar.addWidget(self.severity_filter)

        main_layout.addWidget(toolbar)

        function_bar = QToolBar()
        function_bar.setMovable(False)
        self.addToolBar(function_bar)

        add_issue_btn = QPushButton("新增问题")
        add_issue_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px;")
        add_issue_btn.clicked.connect(self.add_issue_dialog)
        function_bar.addWidget(add_issue_btn)

        import_word_btn = QPushButton("导入问题清单")
        import_word_btn.setStyleSheet("background-color: #607D8B; color: white; padding: 8px 16px; border-radius: 4px;")
        import_word_btn.clicked.connect(self.import_word_dialog)
        function_bar.addWidget(import_word_btn)

        export_btn = QPushButton("导出Excel")
        export_reply_btn = QPushButton("导出整改回复")
        export_reply_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px 16px; border-radius: 4px;")
        export_reply_btn.clicked.connect(self.export_rectification_reply_dialog)
        function_bar.addWidget(export_reply_btn)

        template_btn = QPushButton("模板管理")
        template_btn.setStyleSheet("background-color: #00BCD4; color: white; padding: 8px 16px; border-radius: 4px;")
        template_btn.clicked.connect(self.template_management_dialog)
        function_bar.addWidget(template_btn)

        main_layout.addWidget(function_bar)

        splitter = QSplitter(Qt.Horizontal)

        table_widget = QWidget()
        table_layout = QVBoxLayout()
        table_widget.setLayout(table_layout)

        self.issues_table = QTableWidget()
        self.issues_table.setColumnCount(8)
        self.issues_table.setHorizontalHeaderLabels([
            "序号", "项目名称", "问题内容", "严重程度", "责任人", "整改状态", "照片数量", "创建时间"
        ])
        self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.issues_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.issues_table.setSelectionMode(QTableWidget.SingleSelection)
        self.issues_table.cellClicked.connect(self.show_issue_detail)
        table_layout.addWidget(self.issues_table)

        splitter.addWidget(table_widget)

        detail_splitter = QSplitter(Qt.Vertical)

        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        detail_widget.setLayout(detail_layout)

        group_box = QGroupBox("问题详情")
        form_layout = QFormLayout()
        group_box.setLayout(form_layout)

        self.detail_title = QLineEdit()
        self.detail_title.setReadOnly(True)
        form_layout.addRow("标题:", self.detail_title)

        self.detail_description = QTextEdit()
        self.detail_description.setReadOnly(True)
        self.detail_description.setMaximumHeight(80)
        form_layout.addRow("描述:", self.detail_description)

        self.detail_location = QLineEdit()
        self.detail_location.setReadOnly(True)
        form_layout.addRow("位置:", self.detail_location)

        self.detail_severity = QLineEdit()
        self.detail_severity.setReadOnly(True)
        form_layout.addRow("严重程度:", self.detail_severity)

        self.detail_status = QComboBox()
        self.detail_status.addItems(["待整改", "整改中", "已完成"])
        self.detail_status.currentTextChanged.connect(self.update_issue_status)
        form_layout.addRow("状态:", self.detail_status)

        self.detail_responsible = QLineEdit()
        self.detail_responsible.setReadOnly(True)
        form_layout.addRow("责任人:", self.detail_responsible)

        self.detail_deadline = QLineEdit()
        self.detail_deadline.setReadOnly(True)
        form_layout.addRow("整改期限:", self.detail_deadline)

        self.detail_create_time = QLineEdit()
        self.detail_create_time.setReadOnly(True)
        form_layout.addRow("创建时间:", self.detail_create_time)

        detail_layout.addWidget(group_box)

        btn_layout = QHBoxLayout()
        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_issue_dialog)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("color: red;")
        delete_btn.clicked.connect(self.delete_issue)
        btn_layout.addWidget(delete_btn)

        detail_layout.addLayout(btn_layout)

        detail_splitter.addWidget(detail_widget)

        photos_widget = QWidget()
        photos_layout = QVBoxLayout()
        photos_widget.setLayout(photos_layout)

        photos_group = QGroupBox("照片管理")
        photos_group_layout = QVBoxLayout()
        photos_group.setLayout(photos_group_layout)

        photos_group_layout.addWidget(QLabel("问题照片:"))
        self.issue_photos_list = QListWidget()
        self.issue_photos_list.setMaximumHeight(100)
        self.issue_photos_list.itemClicked.connect(self.show_photo_preview)
        photos_group_layout.addWidget(self.issue_photos_list)

        photos_group_layout.addWidget(QLabel("整改照片:"))
        self.rectification_photos_list = QListWidget()
        self.rectification_photos_list.setMaximumHeight(100)
        self.rectification_photos_list.itemClicked.connect(self.show_photo_preview)
        photos_group_layout.addWidget(self.rectification_photos_list)

        upload_btn = QPushButton("上传整改照片")
        upload_btn.setStyleSheet("background-color: #00BCD4; color: white; padding: 6px 12px; border-radius: 4px;")
        upload_btn.clicked.connect(self.upload_rectification_photo)
        photos_group_layout.addWidget(upload_btn)

        photos_layout.addWidget(photos_group)

        detail_splitter.addWidget(photos_widget)

        splitter.addWidget(detail_splitter)

        preview_widget = QWidget()
        preview_layout = QVBoxLayout()
        preview_widget.setLayout(preview_layout)

        preview_group = QGroupBox("照片预览")
        preview_group_layout = QVBoxLayout()
        preview_group.setLayout(preview_group_layout)

        self.photo_preview = QLabel()
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setMinimumSize(300, 300)
        self.photo_preview.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        preview_group_layout.addWidget(self.photo_preview)

        preview_layout.addWidget(preview_group)

        splitter.addWidget(preview_widget)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 2)

        main_layout.addWidget(splitter)

    def save_server_config(self):
        self.server_url = self.server_input.text()
        self.api_client = APIClient(self.server_url)
        self.save_config()
        QMessageBox.information(self, "成功", "服务器配置已保存")
        self.refresh_issues()

    def refresh_issues(self):
        try:
            issues = self.api_client.get_issues()
            self.display_issues(issues)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取问题列表失败: {str(e)}")

    def display_issues(self, issues):
        self.issues_table.setRowCount(len(issues))
        for row, issue in enumerate(issues):
            self.issues_table.setItem(row, 0, QTableWidgetItem(str(issue['id'])))
            self.issues_table.setItem(row, 1, QTableWidgetItem(issue.get('project_name', '')))
            
            content = issue['title']
            if issue.get('description'):
                content += f"\n{issue['description'][:50]}"
            self.issues_table.setItem(row, 2, QTableWidgetItem(content))
            
            self.issues_table.setItem(row, 3, QTableWidgetItem(issue['severity']))
            
            responsible = issue.get('responsible_person', '')
            self.issues_table.setItem(row, 4, QTableWidgetItem(responsible))
            
            status_item = QTableWidgetItem(issue['status'])
            if issue['status'] == "已完成":
                status_item.setForeground(QColor("#4CAF50"))
            elif issue['status'] == "整改中":
                status_item.setForeground(QColor("#FF9800"))
            else:
                status_item.setForeground(QColor("#f44336"))
            self.issues_table.setItem(row, 5, status_item)

            self.issues_table.setItem(row, 6, QTableWidgetItem(str(issue['photo_count'])))

            create_time = issue.get('create_time', '')
            if create_time:
                create_time = datetime.fromisoformat(create_time).strftime("%Y-%m-%d %H:%M")
            self.issues_table.setItem(row, 7, QTableWidgetItem(create_time))

    def filter_issues(self):
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
        issue_id = int(self.issues_table.item(row, 0).text())
        try:
            issue = self.api_client.get_issue(issue_id)
            if issue:
                self.current_issue = issue
                self.display_issue_detail(issue)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取问题详情失败: {str(e)}")

    def display_issue_detail(self, issue):
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

        self.issue_photos_list.clear()
        for photo in issue.get('issue_photos', []):
            item = QListWidgetItem(f"{photo['file_name']}")
            item.setData(Qt.UserRole, photo['id'])
            self.issue_photos_list.addItem(item)

        self.rectification_photos_list.clear()
        for photo in issue.get('rectification_photos', []):
            item = QListWidgetItem(f"{photo['file_name']}")
            item.setData(Qt.UserRole, photo['id'])
            self.rectification_photos_list.addItem(item)

    def show_photo_preview(self, item):
        photo_id = item.data(Qt.UserRole)
        try:
            temp_path = f"temp_photo_{photo_id}.jpg"
            if self.api_client.download_photo(photo_id, temp_path):
                pixmap = QPixmap(temp_path)
                self.photo_preview.setPixmap(pixmap.scaled(
                    self.photo_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                ))
                os.remove(temp_path)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载照片失败: {str(e)}")

    def update_issue_status(self, status):
        if hasattr(self, 'current_issue'):
            try:
                self.api_client.update_status(self.current_issue['id'], status)
                QMessageBox.information(self, "成功", "状态已更新")
                self.refresh_issues()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"更新状态失败: {str(e)}")

    def add_issue_dialog(self):
        dialog = AddIssueDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_issues()

    def edit_issue_dialog(self):
        if hasattr(self, 'current_issue'):
            dialog = EditIssueDialog(self, self.current_issue)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_issues()

    def delete_issue(self):
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

    def import_word_dialog(self):
        file_path = QFileDialog.getOpenFileName(
            self, "选择问题清单Word文件", "",
            "Word文件 (*.docx *.doc)"
        )
        if not file_path[0]:
            return

        # 第一步：预览
        try:
            preview = self.api_client.preview_from_word(file_path[0])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"连接服务器失败: {str(e)}")
            return

        if not preview or not preview.get('success'):
            QMessageBox.warning(self, "预览失败", preview.get('message', '无法读取Word文件内容'))
            return

        items = preview.get('items', [])
        if not items:
            QMessageBox.warning(self, "未识别到隐患", "从Word文件中未识别到任何隐患记录")
            return

        # 弹出预览对话框
        dialog = ImportPreviewDialog(preview, self)
        if dialog.exec_() != QDialog.Accepted:
            return

        skip_indices = dialog.get_skip_indices()
        checked_count = dialog.get_checked_count()

        if checked_count == 0:
            QMessageBox.information(self, "取消", "未选择任何隐患，导入已取消")
            return

        # 第二步：导入（跳过未勾选的）
        try:
            result = self.api_client.import_from_word(file_path[0], skip_indices=skip_indices)
            if result and result.get('success'):
                msg = f"成功导入 {result['imported_count']} 条隐患记录\n项目：{result.get('project_name', '')}"
                QMessageBox.information(self, "导入成功", msg)
                self.refresh_issues()
            elif result:
                QMessageBox.warning(self, "导入部分成功",
                    f"成功 {result.get('imported_count', 0)} 条，错误：{result.get('message', '')}")
            else:
                QMessageBox.warning(self, "导入失败", "API返回为空")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导入失败: {str(e)}")


    def do_export(self, dialog):
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
                
                template_id = self.template_combo.currentData()
                template_id = None if template_id == 0 else template_id
                
                content = self.api_client.export_excel_with_template(status_param, severity_param, template_id)
                if content:
                    with open(file_path[0], 'wb') as f:
                        f.write(content)
                    QMessageBox.information(self, "成功", "Excel文件已导出")
                    dialog.accept()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")

    def template_management_dialog(self):
        dialog = TemplateManagementDialog(self)
        dialog.exec_()


    def export_rectification_reply_dialog(self):
        dialog = ExportReplyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "成功", "整改回复已导出")

class AddIssueDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.photos = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("新增问题")
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)

        form = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("请输入问题标题")
        form.addRow("标题*:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("请输入问题描述")
        self.description_input.setMaximumHeight(100)
        form.addRow("描述:", self.description_input)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("请输入发现位置")
        form.addRow("位置:", self.location_input)

        self.severity_input = QComboBox()
        self.severity_input.addItems(["轻微", "一般", "严重"])
        self.severity_input.setCurrentText("一般")
        form.addRow("严重程度:", self.severity_input)

        self.responsible_input = QLineEdit()
        self.responsible_input.setPlaceholderText("请输入责任人")
        form.addRow("责任人:", self.responsible_input)

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate().addDays(7))
        form.addRow("整改期限:", self.deadline_input)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("请输入备注信息")
        self.notes_input.setMaximumHeight(80)
        form.addRow("备注:", self.notes_input)

        scroll_layout.addLayout(form)

        photo_layout = QHBoxLayout()
        photo_layout.addWidget(QLabel("问题照片:"))
        select_photo_btn = QPushButton("选择照片")
        select_photo_btn.clicked.connect(self.select_photos)
        photo_layout.addWidget(select_photo_btn)
        self.photo_count_label = QLabel("已选择: 0张")
        photo_layout.addWidget(self.photo_count_label)
        scroll_layout.addLayout(photo_layout)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px;")
        save_btn.clicked.connect(self.save_issue)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def select_photos(self):
        files = QFileDialog.getOpenFileNames(
            self, "选择问题照片", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if files[0]:
            self.photos = [(os.path.basename(f), f) for f in files[0]]
            self.photo_count_label.setText(f"已选择: {len(self.photos)}张")

    def save_issue(self):
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
    def __init__(self, parent, issue):
        super().__init__(parent)
        self.parent_window = parent
        self.issue = issue
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("编辑问题")
        self.setGeometry(300, 300, 600, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)

        form = QFormLayout()

        self.title_input = QLineEdit(self.issue['title'])
        form.addRow("标题*:", self.title_input)

        self.description_input = QTextEdit()
        self.description_input.setText(self.issue.get('description', ''))
        self.description_input.setMaximumHeight(100)
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
        self.notes_input.setMaximumHeight(80)
        form.addRow("备注:", self.notes_input)

        scroll_layout.addLayout(form)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px;")
        save_btn.clicked.connect(self.save_issue)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def save_issue(self):
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

class ExportReplyDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("导出整改回复")
        self.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        form = QFormLayout()

        self.project_name_input = QLineEdit()
        self.project_name_input.setPlaceholderText("请输入项目名称")
        form.addRow("项目名称*:", self.project_name_input)

        self.project_responsible_input = QLineEdit()
        self.project_responsible_input.setPlaceholderText("请输入项目负责人")
        form.addRow("项目负责人*:", self.project_responsible_input)

        self.reply_date_input = QDateEdit()
        self.reply_date_input.setCalendarPopup(True)
        self.reply_date_input.setDate(QDate.currentDate())
        form.addRow("回复日期:", self.reply_date_input)

        self.issues_list = QListWidget()
        self.issues_list.setSelectionMode(QListWidget.MultiSelection)
        self.load_issues()
        form.addRow("选择问题:", self.issues_list)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        export_btn = QPushButton("导出")
        export_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 8px 16px; border-radius: 4px;")
        export_btn.clicked.connect(self.export_reply)
        btn_layout.addWidget(export_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def load_issues(self):
        try:
            issues = self.parent_window.api_client.get_issues()
            for issue in issues:
                item = QListWidgetItem(f"#{issue['id']} - {issue['title']} [{issue['status']}]")
                item.setData(Qt.UserRole, issue['id'])
                self.issues_list.addItem(item)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载问题列表失败: {str(e)}")

    def export_reply(self):
        if not self.project_name_input.text():
            QMessageBox.warning(self, "警告", "请填写项目名称")
            return

        selected_ids = []
        for i in range(self.issues_list.count()):
            item = self.issues_list.item(i)
            if item.isSelected():
                selected_ids.append(item.data(Qt.UserRole))

        if not selected_ids:
            reply = QMessageBox.question(
                self, '确认',
                '未选择任何问题，将导出所有问题。是否继续？',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return

        file_path = QFileDialog.getSaveFileName(
            self, "保存整改回复文件", "",
            "Excel (*.xlsx)"
        )

        if file_path[0]:
            try:
                date = self.reply_date_input.date()
                date_str = f"{date.year()}年{date.month()}月{date.day()}日"
                
                content = self.parent_window.api_client.export_rectification_reply(
                    self.project_name_input.text(),
                    self.project_responsible_input.text(),
                    date_str,
                    selected_ids if selected_ids else None
                )
                if content:
                    with open(file_path[0], 'wb') as f:
                        f.write(content)
                    QMessageBox.information(self, "成功", "整改回复已导出")
                    self.accept()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")

class TemplateManagementDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_window = parent
        self.server_url = parent.server_url if hasattr(parent, 'server_url') else parent.base_url
        self.api_client = parent.api_client if hasattr(parent, 'api_client') else None
        self.init_ui()
        self.load_templates()

    def init_ui(self):
        self.setWindowTitle("模板管理")
        self.setGeometry(300, 300, 600, 400)

        layout = QVBoxLayout()

        self.template_table = QTableWidget()
        self.template_table.setColumnCount(3)
        self.template_table.setHorizontalHeaderLabels(["ID", "模板名称", "操作"])
        self.template_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.template_table)

        btn_layout = QHBoxLayout()

        add_btn = QPushButton("新建模板")
        add_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px 12px; border-radius: 4px;")
        add_btn.clicked.connect(self.add_template)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("编辑模板")
        edit_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 6px 12px; border-radius: 4px;")
        edit_btn.clicked.connect(self.edit_template)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("删除模板")
        delete_btn.setStyleSheet("background-color: #f44336; color: white; padding: 6px 12px; border-radius: 4px;")
        delete_btn.clicked.connect(self.delete_template)
        btn_layout.addWidget(delete_btn)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_templates(self):
        try:
            templates = self.api_client.get_templates()
            self.template_table.setRowCount(len(templates))
            for row, template in enumerate(templates):
                self.template_table.setItem(row, 0, QTableWidgetItem(str(template['id'])))
                self.template_table.setItem(row, 1, QTableWidgetItem(template['name']))
                
                delete_btn = QPushButton("删除")
                delete_btn.setStyleSheet("color: red;")
                delete_btn.clicked.connect(lambda checked, tid=template['id']: self.confirm_delete(tid))
                self.template_table.setCellWidget(row, 2, delete_btn)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载模板失败: {str(e)}")

    def add_template(self):
        dialog = TemplateEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_templates()

    def edit_template(self):
        current_row = self.template_table.currentRow()
        if current_row >= 0:
            template_id = int(self.template_table.item(current_row, 0).text())
            template_name = self.template_table.item(current_row, 1).text()
            dialog = TemplateEditDialog(self, template_id, template_name)
            if dialog.exec_() == QDialog.Accepted:
                self.load_templates()

    def confirm_delete(self, template_id):
        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除这个模板吗？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_template_by_id(template_id)

    def delete_template(self):
        current_row = self.template_table.currentRow()
        if current_row >= 0:
            template_id = int(self.template_table.item(current_row, 0).text())
            self.confirm_delete(template_id)

    def delete_template_by_id(self, template_id):
        try:
            response = requests.delete(
                f"{self.server_url}/api/export/templates/{template_id}",
                timeout=30
            )
            if response.status_code == 200:
                QMessageBox.information(self, "成功", "模板已删除")
                self.load_templates()
            else:
                QMessageBox.warning(self, "错误", "删除失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"删除失败: {str(e)}")

class TemplateEditDialog(QDialog):
    def __init__(self, parent, template_id=None, template_name=""):
        super().__init__(parent)
        self.parent_window = parent
        self.template_id = template_id
        self.server_url = parent.server_url if hasattr(parent, 'server_url') else parent.parent_window.server_url
        self.init_ui(template_name)

    def init_ui(self, template_name):
        self.setWindowTitle("编辑模板" if self.template_id else "新建模板")
        self.setGeometry(300, 300, 450, 250)

        layout = QVBoxLayout()

        form = QFormLayout()

        self.name_input = QLineEdit(template_name)
        self.name_input.setPlaceholderText("请输入模板名称")
        form.addRow("模板名称*:", self.name_input)

        self.title_format_input = QLineEdit("《关于{date}安全隐患整改有关事项回复》")
        self.title_format_input.setPlaceholderText("标题格式，{date}会被替换为日期")
        form.addRow("标题格式:", self.title_format_input)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()

        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px;")
        save_btn.clicked.connect(self.save_template)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_template(self):
        if not self.name_input.text():
            QMessageBox.warning(self, "警告", "请填写模板名称")
            return

        data = {
            'name': self.name_input.text(),
            'title_format': self.title_format_input.text()
        }

        try:
            if self.template_id:
                response = requests.put(
                    f"{self.server_url}/api/export/templates/{self.template_id}",
                    json=data,
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{self.server_url}/api/export/templates",
                    json=data,
                    timeout=30
                )

            if response.status_code == 200:
                QMessageBox.information(self, "成功", "模板已保存")
                self.accept()
            else:
                QMessageBox.warning(self, "错误", "保存失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存失败: {str(e)}")

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, QColor(30, 30, 30))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(30, 30, 30))
    palette.setColor(QPalette.Text, QColor(30, 30, 30))
    palette.setColor(QPalette.Button, QColor(245, 245, 245))
    palette.setColor(QPalette.ButtonText, QColor(30, 30, 30))
    palette.setColor(QPalette.Link, QColor(33, 150, 243))
    palette.setColor(QPalette.Highlight, QColor(33, 150, 243))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
