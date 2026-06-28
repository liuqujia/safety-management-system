<template>
  <div class="safety-management">
    <!-- 搜索和操作栏 -->
    <div class="filter-container">
      <el-form :inline="true" :model="queryParams" class="filter-form">
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择状态" clearable @change="handleQuery">
            <el-option label="全部" value="" />
            <el-option label="待整改" value="待整改" />
            <el-option label="整改中" value="整改中" />
            <el-option label="已完成" value="已完成" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="queryParams.severity" placeholder="请选择严重程度" clearable @change="handleQuery">
            <el-option label="全部" value="" />
            <el-option label="轻微" value="轻微" />
            <el-option label="一般" value="一般" />
            <el-option label="严重" value="严重" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" icon="Search" @click="handleQuery">查询</el-button>
          <el-button icon="Refresh" @click="resetQuery">重置</el-button>
        </el-form-item>
      </el-form>
      <div class="action-buttons">
        <el-button type="primary" icon="Plus" @click="handleAdd">新增问题</el-button>
        <el-button type="success" icon="Download" @click="handleExport">导出Excel</el-button>
      </div>
    </div>

    <!-- 问题列表 -->
    <el-table :data="issueList" border stripe v-loading="loading">
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
      <el-table-column prop="photo_count" label="照片数" width="80" align="center" />
      <el-table-column label="操作" width="250" fixed="right" align="center">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleView(row)">查看</el-button>
          <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
          <el-button link type="success" @click="handleUploadPhoto(row)">上传整改照片</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-model:current-page="queryParams.page"
      v-model:page-size="queryParams.limit"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="getList"
      @current-change="getList"
    />

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="handleDialogClose">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="问题标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入问题描述" />
        </el-form-item>
        <el-form-item label="发现位置" prop="location">
          <el-input v-model="form.location" placeholder="请输入发现位置" />
        </el-form-item>
        <el-form-item label="严重程度" prop="severity">
          <el-select v-model="form.severity" placeholder="请选择严重程度">
            <el-option label="轻微" value="轻微" />
            <el-option label="一般" value="一般" />
            <el-option label="严重" value="严重" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任人" prop="responsible_person">
          <el-input v-model="form.responsible_person" placeholder="请输入责任人" />
        </el-form-item>
        <el-form-item label="整改期限" prop="deadline">
          <el-date-picker v-model="form.deadline" type="date" placeholder="选择整改期限" format="YYYY-MM-DD" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="请输入备注" />
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

      <div class="photos-section">
        <h4>问题照片</h4>
        <div class="photo-list" v-if="currentIssue.issue_photos && currentIssue.issue_photos.length">
          <el-image
            v-for="photo in currentIssue.issue_photos"
            :key="photo.id"
            :src="getPhotoUrl(photo.id)"
            :preview-src-list="currentIssue.issue_photos.map(p => getPhotoUrl(p.id))"
            fit="cover"
            style="width: 150px; height: 150px; margin-right: 10px;"
          />
        </div>
        <el-empty v-else description="暂无问题照片" />

        <h4>整改照片</h4>
        <div class="photo-list" v-if="currentIssue.rectification_photos && currentIssue.rectification_photos.length">
          <el-image
            v-for="photo in currentIssue.rectification_photos"
            :key="photo.id"
            :src="getPhotoUrl(photo.id)"
            :preview-src-list="currentIssue.rectification_photos.map(p => getPhotoUrl(p.id))"
            fit="cover"
            style="width: 150px; height: 150px; margin-right: 10px;"
          />
        </div>
        <el-empty v-else description="暂无整改照片" />
      </div>
    </el-dialog>

    <!-- 上传整改照片对话框 -->
    <el-dialog v-model="uploadVisible" title="上传整改照片" width="400px">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="10"
        :on-exceed="handleExceed"
        :http-request="handleUploadRequest"
        list-type="picture-card"
        accept="image/*"
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
import { Plus } from '@element-plus/icons-vue'
import { getIssues, getIssue, createIssue, updateIssue, deleteIssue, updateIssueStatus, uploadPhoto, exportExcel, downloadPhoto } from '@/api/safety'

const loading = ref(false)
const issueList = ref([])
const total = ref(0)
const queryParams = reactive({
  page: 1,
  limit: 20,
  status: '',
  severity: ''
})

const dialogVisible = ref(false)
const detailVisible = ref(false)
const uploadVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)
const uploadRef = ref(null)
const currentIssue = ref({})
const uploadIssueId = ref(null)
const photoType = '整改照片'

const form = reactive({
  title: '',
  description: '',
  location: '',
  severity: '一般',
  responsible_person: '',
  deadline: '',
  notes: ''
})

const rules = {
  title: [{ required: true, message: '请输入问题标题', trigger: 'blur' }]
}

onMounted(() => {
  getList()
})

const getList = async () => {
  loading.value = true
  try {
    const res = await getIssues(queryParams)
    issueList.value = res
    total.value = res.length
  } catch (error) {
    ElMessage.error('获取问题列表失败')
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  queryParams.page = 1
  getList()
}

const resetQuery = () => {
  queryParams.status = ''
  queryParams.severity = ''
  handleQuery()
}

const getSeverityType = (severity) => {
  const map = { '轻微': 'info', '一般': 'warning', '严重': 'danger' }
  return map[severity] || 'info'
}

const getStatusType = (status) => {
  const map = { '待整改': 'danger', '整改中': 'warning', '已完成': 'success' }
  return map[status] || 'info'
}

const handleAdd = () => {
  dialogTitle.value = '新增问题'
  Object.keys(form).forEach(key => form[key] = '')
  form.severity = '一般'
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  dialogTitle.value = '编辑问题'
  try {
    const res = await getIssue(row.id)
    Object.assign(form, res)
    dialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取问题详情失败')
  }
}

const handleView = async (row) => {
  try {
    const res = await getIssue(row.id)
    currentIssue.value = res
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取问题详情失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个问题吗？', '提示', {
      type: 'warning'
    })
    await deleteIssue(row.id)
    ElMessage.success('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleUploadPhoto = (row) => {
  uploadIssueId.value = row.id
  uploadVisible.value = true
}

const handleExceed = () => {
  ElMessage.warning('最多上传10张照片')
}

const handleUploadRequest = async (options) => {
  const { file } = options
  const formData = new FormData()
  formData.append('photos', file)
  formData.append('photo_type', photoType)

  try {
    await uploadPhoto(uploadIssueId.value, photoType, formData)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    getList()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const submitUpload = async () => {
  if (uploadRef.value) {
    uploadRef.value.submit()
  }
}

const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (form.id) {
          await updateIssue(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createIssue(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        getList()
      } catch (error) {
        ElMessage.error('操作失败')
      }
    }
  })
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
}

const handleExport = async () => {
  try {
    ElMessage.info('正在导出，请稍候...')
    const res = await exportExcel(queryParams)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
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

const getPhotoUrl = (photoId) => {
  return `http://192.168.31.105:9999/api/photos/${photoId}/download`
}
</script>

<style scoped>
.safety-management {
  padding: 20px;
}

.filter-container {
  margin-bottom: 20px;
}

.filter-form {
  display: inline-block;
}

.action-buttons {
  float: right;
  margin-bottom: 20px;
}

.photos-section {
  margin-top: 20px;
}

.photos-section h4 {
  margin: 20px 0 10px;
  font-size: 16px;
}

.photo-list {
  display: flex;
  flex-wrap: wrap;
}
</style>
