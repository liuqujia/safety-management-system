<template>
  <div class="app-container">
    <!-- 头部 -->
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <h1>🏢 安全整改管理系统</h1>
          <div class="header-actions">
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </el-header>

      <el-main class="app-main">
        <!-- 搜索筛选 -->
        <el-card class="filter-card" shadow="hover">
          <el-form :inline="true" :model="queryForm">
            <el-form-item label="状态">
              <el-select v-model="queryForm.status" placeholder="全部状态" clearable style="width: 120px;">
                <el-option label="待整改" value="待整改" />
                <el-option label="整改中" value="整改中" />
                <el-option label="已完成" value="已完成" />
              </el-select>
            </el-form-item>
            <el-form-item label="严重程度">
              <el-select v-model="queryForm.severity" placeholder="全部程度" clearable style="width: 120px;">
                <el-option label="轻微" value="轻微" />
                <el-option label="一般" value="一般" />
                <el-option label="严重" value="严重" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleQuery">
                <el-icon><Search /></el-icon> 查询
              </el-button>
              <el-button @click="resetQuery">
                <el-icon><RefreshLeft /></el-icon> 重置
              </el-button>
            </el-form-item>
          </el-form>
          <div class="action-buttons">
            <el-button type="success" @click="handleExport">
              <el-icon><Download /></el-icon> 导出Excel
            </el-button>
            <el-button type="warning" @click="handleExportRectification">
              <el-icon><Download /></el-icon> 导出整改回复
            </el-button>
          </div>
        </el-card>

        <!-- 问题列表 -->
        <el-card class="table-card" shadow="hover">
          <el-table
            :data="tableData"
            border
            stripe
            v-loading="loading"
            style="width: 100%"
          >
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="title" label="问题标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="location" label="发现位置" width="150" show-overflow-tooltip />
            <el-table-column prop="severity" label="严重程度" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="responsible_person" label="责任人" width="120" />
            <el-table-column prop="deadline" label="整改期限" width="120" />
            <el-table-column label="操作" width="280" fixed="right" align="center">
              <template #default="{ row }">
                <el-button link type="primary" @click="handleView(row)">查看</el-button>
                <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
                <el-button link type="success" @click="handleUploadPhoto(row)">上传照片</el-button>
                <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.limit"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="loadData"
              @current-change="loadData"
            />
          </div>
        </el-card>
      </el-main>
    </el-container>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="问题标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入问题描述" />
        </el-form-item>
        <el-form-item label="发现位置" prop="location">
          <el-input v-model="formData.location" placeholder="请输入发现位置" />
        </el-form-item>
        <el-form-item label="严重程度" prop="severity">
          <el-select v-model="formData.severity" placeholder="请选择严重程度" style="width: 100%;">
            <el-option label="轻微" value="轻微" />
            <el-option label="一般" value="一般" />
            <el-option label="严重" value="严重" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任人" prop="responsible_person">
          <el-input v-model="formData.responsible_person" placeholder="请输入责任人" />
        </el-form-item>
        <el-form-item label="整改期限" prop="deadline">
          <el-date-picker
            v-model="formData.deadline"
            type="date"
            placeholder="选择整改期限"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="formData.notes" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="detailVisible" title="问题详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="问题标题">{{ currentIssue.title }}</el-descriptions-item>
        <el-descriptions-item label="严重程度">
          <el-tag :type="getSeverityType(currentIssue.severity)">{{ currentIssue.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发现位置">{{ currentIssue.location }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentIssue.status)">{{ currentIssue.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="责任人">{{ currentIssue.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="整改期限">{{ currentIssue.deadline }}</el-descriptions-item>
        <el-descriptions-item label="问题描述" :span="2">{{ currentIssue.description }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentIssue.notes }}</el-descriptions-item>
      </el-descriptions>

      <div class="photos-section" v-if="currentIssue.id">
        <h4>📷 问题照片</h4>
        <div class="photo-grid" v-if="currentIssue.issue_photos && currentIssue.issue_photos.length">
          <el-image
            v-for="photo in currentIssue.issue_photos"
            :key="photo.id"
            :src="getPhotoUrl(photo.id)"
            :preview-src-list="currentIssue.issue_photos.map(p => getPhotoUrl(p.id))"
            fit="cover"
            class="photo-item"
          />
        </div>
        <el-empty v-else description="暂无问题照片" />

        <h4>✅ 整改照片</h4>
        <div class="photo-grid" v-if="currentIssue.rectification_photos && currentIssue.rectification_photos.length">
          <el-image
            v-for="photo in currentIssue.rectification_photos"
            :key="photo.id"
            :src="getPhotoUrl(photo.id)"
            :preview-src-list="currentIssue.rectification_photos.map(p => getPhotoUrl(p.id))"
            fit="cover"
            class="photo-item"
          />
        </div>
        <el-empty v-else description="暂无整改照片" />
      </div>
    </el-dialog>

    <!-- 上传照片对话框 -->
    <el-dialog v-model="uploadVisible" title="上传整改照片" width="500px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="10"
        :on-exceed="handleExceed"
        list-type="picture-card"
        accept="image/*"
        :http-request="handleUploadRequest"
      >
        <el-icon><Plus /></el-icon>
      </el-upload>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

// API配置
const API_BASE = 'http://192.168.31.105:9999'

// 状态变量
const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const uploadVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)
const uploadRef = ref(null)
const currentIssue = ref({})
const uploadIssueId = ref(null)
const uploadFileList = ref([])

// 查询表单
const queryForm = reactive({
  status: '',
  severity: ''
})

// 分页
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

// 表单数据
const formData = reactive({
  id: null,
  title: '',
  description: '',
  location: '',
  severity: '一般',
  responsible_person: '',
  deadline: '',
  notes: ''
})

// 表单验证规则
const formRules = {
  title: [{ required: true, message: '请输入问题标题', trigger: 'blur' }]
}

// 生命周期钩子
onMounted(() => {
  loadData()
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      limit: pagination.limit
    }
    if (queryForm.status) params.status = queryForm.status
    if (queryForm.severity) params.severity = queryForm.severity

    const response = await axios.get(`${API_BASE}/api/issues/`, { params })
    tableData.value = response.data
    pagination.total = response.data.length
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 查询
const handleQuery = () => {
  pagination.page = 1
  loadData()
}

// 重置查询
const resetQuery = () => {
  queryForm.status = ''
  queryForm.severity = ''
  handleQuery()
}

// 获取严重程度类型
const getSeverityType = (severity) => {
  const map = { '轻微': 'info', '一般': 'warning', '严重': 'danger' }
  return map[severity] || 'info'
}

// 获取状态类型
const getStatusType = (status) => {
  const map = { '待整改': 'danger', '整改中': 'warning', '已完成': 'success' }
  return map[status] || 'info'
}

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增问题'
  Object.keys(formData).forEach(key => {
    if (key !== 'id') formData[key] = ''
  })
  formData.severity = '一般'
  dialogVisible.value = true
}

// 编辑
const handleEdit = async (row) => {
  dialogTitle.value = '编辑问题'
  try {
    const response = await axios.get(`${API_BASE}/api/issues/${row.id}`)
    Object.assign(formData, response.data)
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

// 查看
const handleView = async (row) => {
  try {
    const response = await axios.get(`${API_BASE}/api/issues/${row.id}`)
    currentIssue.value = response.data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取详情失败')
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个问题吗？', '提示', {
      type: 'warning'
    })
    await axios.delete(`${API_BASE}/api/issues/${row.id}`)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (formData.id) {
          await axios.put(`${API_BASE}/api/issues/${formData.id}`, formData)
          ElMessage.success('更新成功')
        } else {
          await axios.post(`${API_BASE}/api/issues/`, formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  formRef.value?.resetFields()
}

// 上传照片
const handleUploadPhoto = (row) => {
  uploadIssueId.value = row.id
  uploadFileList.value = []
  uploadVisible.value = true
}

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('最多上传10张照片')
}

// 上传请求
const handleUploadRequest = async (options) => {
  const { file } = options
  const formData = new FormData()
  formData.append('photos', file)
  formData.append('photo_type', '整改照片')

  try {
    await axios.post(`${API_BASE}/api/issues/${uploadIssueId.value}/photos`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('上传成功')
    uploadVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

// 提交上传
const submitUpload = () => {
  if (uploadRef.value) {
    uploadRef.value.submit()
  }
}

// 导出Excel
const handleExport = async () => {
  try {
    ElMessage.info('正在导出，请稍候...')
    const params = {}
    if (queryForm.status) params.status = queryForm.status
    if (queryForm.severity) params.severity = queryForm.severity

    const response = await axios.get(`${API_BASE}/api/export/excel`, {
      params,
      responseType: 'blob'
    })

    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `安全问题_${Date.now()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 导出整改回复报告
const handleExportRectification = async () => {
  try {
    ElMessage.info('正在导出整改回复，请稍候...')
    const params = {}
    if (queryForm.status) params.status = queryForm.status

    const response = await axios.get(`${API_BASE}/api/export/excel/rectification`, {
      params,
      responseType: 'blob'
    })

    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `安全隐患整改回复_${Date.now()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

// 获取照片URL
const getPhotoUrl = (photoId) => {
  return `${API_BASE}/api/photos/${photoId}/download`
}

// 刷新数据
const refreshData = () => {
  loadData()
  ElMessage.success('刷新成功')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.app-container {
  min-height: 100vh;
  background: #f0f2f5;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.header-content h1 {
  font-size: 24px;
  font-weight: 600;
}

.app-main {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.table-card {
  background: white;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.photos-section {
  margin-top: 20px;
}

.photos-section h4 {
  margin: 15px 0 10px;
  font-size: 16px;
  color: #409eff;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.photo-item {
  width: 150px;
  height: 150px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
}

.photo-item:hover {
  transform: scale(1.05);
}

/* Element Plus 覆盖样式 */
.el-header {
  line-height: 60px;
}

.el-table {
  font-size: 14px;
}

.el-dialog__body {
  padding: 20px;
}
</style>
