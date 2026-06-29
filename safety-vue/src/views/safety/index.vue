<template>
  <div class="safety-management">
    <!-- 搜索和操作栏 -->
    <div class="filter-container">
      <el-form :inline="true" :model="queryParams" class="filter-form">
        <el-form-item label="项目名称">
          <el-select v-model="queryParams.project_name" placeholder="全部项目" clearable filterable @change="handleQuery" style="width: 180px">
            <el-option v-for="p in projectOptions" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
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
        <el-button type="info" icon="Upload" @click="openImportDialog">导入问题清单</el-button>
        <el-button type="warning" icon="Document" @click="openExportReplyDialog">导出整改回复</el-button>
        <el-button type="primary" icon="Setting" @click="templateDialogVisible = true" plain>模板管理</el-button>
      </div>
    </div>

    <!-- 问题列表 -->
    <el-table :data="issueList" border stripe v-loading="loading">
      <el-table-column prop="id" label="序号" width="70" align="center" />
      <el-table-column prop="project_name" label="项目名称" width="180" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.project_name">{{ row.project_name }}</span>
          <span v-else style="color: #c0c4cc">未提供</span>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="问题标题" min-width="220" show-overflow-tooltip />
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
        <el-descriptions-item label="项目名称">{{ currentIssue.project_name || '未提供' }}</el-descriptions-item>
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

    <!-- 导出整改回复对话框 -->
    <el-dialog v-model="replyDialogVisible" title="导出整改回复报告" width="520px">
      <el-form label-width="100px">
        <el-form-item label="项目名称" required>
          <el-input v-model="replyForm.project_name" placeholder="如未自动填充，请手动输入">
            <template #append>
              <el-dropdown @command="(p) => replyForm.project_name = p">
                <el-button>
                  从已有项目选 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item v-for="p in projectOptions" :key="p" :command="p">{{ p }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="项目负责人" required>
          <el-input v-model="replyForm.project_responsible" placeholder="请输入项目负责人" />
        </el-form-item>
        <el-form-item label="回复日期">
          <el-date-picker
            v-model="replyForm.reply_date"
            type="date"
            placeholder="选择日期（默认今天）"
            format="YYYY年MM月DD日"
            value-format="YYYY年MM月DD日"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="选择隐患">
          <el-select v-model="replyForm.issue_ids" multiple placeholder="默认导出已勾选问题；不选则包含当前筛选下所有问题" style="width: 100%">
            <el-option
              v-for="issue in issueList"
              :key="issue.id"
              :label="`#${issue.id} ${issue.title}`"
              :value="issue.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="replyDialogVisible = false">取消</el-button>
        <el-button type="warning" @click="doExportReply">导出整改回复</el-button>
      </template>
    </el-dialog>

    <!-- 模板管理对话框 -->
    <el-dialog v-model="templateDialogVisible" title="模板管理" width="700px">
      <div style="margin-bottom: 12px">
        <el-button type="primary" size="small" @click="openTemplateEdit()">新建模板</el-button>
      </div>

      <el-table :data="templateList" border stripe>
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="name" label="模板名称" min-width="150" />
        <el-table-column prop="title_format" label="标题格式" min-width="200" show-overflow-tooltip />
        <el-table-column label="是否默认" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
            <span v-else style="color: #999">否</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openTemplateEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" :disabled="row.is_default" @click="deleteTemplate(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 模板编辑对话框 -->
      <el-dialog v-model="templateEditVisible" :title="templateEditTitle" width="450px" append-to-body>
        <el-form :model="templateForm" label-width="100px">
          <el-form-item label="模板名称" required>
            <el-input v-model="templateForm.name" placeholder="如：整改回复报告" />
          </el-form-item>
          <el-form-item label="标题格式">
            <el-input v-model="templateForm.title_format" placeholder="如：关于{date}安全隐患整改回复" />
          </el-form-item>
          <el-form-item label="设为默认">
            <el-switch v-model="templateForm.is_default" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="templateEditVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate">保存</el-button>
        </template>
      </el-dialog>
    </el-dialog>

    <!-- 导入问题清单对话框（先预览再确认导入） -->
    <el-dialog v-model="importDialogVisible" title="导入问题清单" width="640px" @close="resetImportDialog">
      <el-alert
        title="使用说明"
        description="上传隐患检查表 .docx 文件，系统会从文档标题区识别出【企业名称/项目名称】，从表格中识别出隐患条目。如识别有误可手动修改后导入。"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-upload
        ref="wordUploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".docx"
        :on-change="handleWordFileChange"
        :on-remove="handleWordFileRemove"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">将Word文件拖到此处，或 <em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">只支持 .docx 文件</div>
        </template>
      </el-upload>

      <el-divider v-if="importPreview" />

      <div v-if="importPreview" class="import-preview">
        <el-form label-width="100px" v-loading="previewLoading">
          <el-form-item label="识别隐患数">
            <el-tag type="success" size="large">{{ importPreview.items?.length || 0 }} 条</el-tag>
            <span v-if="importPreview.project_name" style="margin-left: 12px; color: #909399">项目：{{ importPreview.project_name }}</span>
          </el-form-item>
          <el-form-item label="隐患预览" v-if="importPreview.items?.length">
            <div class="preview-items">
              <div v-for="(it, i) in importPreview.items" :key="i" class="preview-item">
                <div class="preview-title">隐患{{ i + 1 }}：{{ it.title }}</div>
                <div v-if="it.description" class="preview-desc">描述：{{ it.description }}</div>
                <div v-if="it.notes" class="preview-desc">措施：{{ it.notes }}</div>
                <div v-if="it.deadline" class="preview-desc">期限：{{ it.deadline }}</div>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" :disabled="!selectedWordFile || !importPreview?.items?.length" @click="doImportWord">确认导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled, ArrowDown } from '@element-plus/icons-vue'
import {
  getIssues, getIssue, createIssue, updateIssue, deleteIssue,
  uploadPhoto, downloadPhoto,
  getTemplates, createTemplate, updateTemplate, deleteTemplate,
  exportRectificationReply, importFromWord, previewFromWord, getProjects
} from '@/api/safety'

const loading = ref(false)
const issueList = ref([])
const total = ref(0)
const templateList = ref([])
const projectOptions = ref([])
const queryParams = reactive({
  page: 1,
  limit: 100,
  status: '',
  severity: '',
  project_name: ''
})

// 对话框状态
const dialogVisible = ref(false)
const detailVisible = ref(false)
const uploadVisible = ref(false)
const replyDialogVisible = ref(false)
const templateDialogVisible = ref(false)
const templateEditVisible = ref(false)
const importDialogVisible = ref(false)

const dialogTitle = ref('')
const formRef = ref(null)
const uploadRef = ref(null)
const wordUploadRef = ref(null)
const currentIssue = ref({})
const uploadIssueId = ref(null)
const importing = ref(false)
const previewLoading = ref(false)
const selectedTemplateId = ref(1)
const photoType = '整改照片'
const templateEditTitle = ref('新建模板')

// 导入预览
const selectedWordFile = ref(null)
const importPreview = ref(null)

// 整改回复表单
const replyForm = reactive({
  project_name: '',
  project_responsible: '',
  reply_date: '',
  issue_ids: []
})

// 模板编辑表单
const templateForm = reactive({
  id: null,
  name: '',
  title_format: '《关于{date}安全隐患整改有关事项回复》',
  is_default: false
})

const form = reactive({
  id: null,
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
  loadTemplates()
  loadProjects()
})

const loadProjects = async () => {
  try {
    const res = await getProjects()
    projectOptions.value = res || []
  } catch (error) {
    console.warn('获取项目列表失败', error)
  }
}

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

const loadTemplates = async () => {
  try {
    const res = await getTemplates()
    templateList.value = res
    if (res.length > 0 && !selectedTemplateId.value) {
      selectedTemplateId.value = res[0].id
    }
  } catch (error) {
    console.warn('获取模板列表失败', error)
  }
}

const handleQuery = () => {
  queryParams.page = 1
  getList()
}

const resetQuery = () => {
  queryParams.status = ''
  queryParams.severity = ''
  queryParams.project_name = ''
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
  Object.keys(form).forEach(key => { form[key] = key === 'severity' ? '一般' : '' })
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
    await ElMessageBox.confirm('确定要删除这个问题吗？', '提示', { type: 'warning' })
    await deleteIssue(row.id)
    ElMessage.success('删除成功')
    getList()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleUploadPhoto = (row) => {
  uploadIssueId.value = row.id
  uploadVisible.value = true
}

const handleExceed = () => ElMessage.warning('最多上传10张照片')

const handleUploadRequest = async (options) => {
  const { file } = options
  const fd = new FormData()
  fd.append('photos', file)
  fd.append('photo_type', photoType)
  try {
    await uploadPhoto(uploadIssueId.value, photoType, fd)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    getList()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

const submitUpload = async () => {
  if (uploadRef.value) uploadRef.value.submit()
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

const handleDialogClose = () => formRef.value?.resetFields()

// ── 导出整改回复 ────────────────────────────────────────────────────────────

const openExportReplyDialog = () => {
  // 预填项目名称：当前筛选下若只有一种项目名则自动填入
  const projects = [...new Set(issueList.value.map(i => i.project_name).filter(Boolean))]
  if (projects.length === 1) {
    replyForm.project_name = projects[0]
  } else {
    replyForm.project_name = ''
  }
  replyForm.project_responsible = ''
  replyForm.reply_date = ''
  replyForm.issue_ids = []
  replyDialogVisible.value = true
}

const doExportReply = async () => {
  if (!replyForm.project_name) {
    ElMessage.warning('请填写项目名称')
    return
  }
  if (!replyForm.project_responsible) {
    ElMessage.warning('请填写项目负责人')
    return
  }
  try {
    ElMessage.info('正在导出整改回复，请稍候...')
    const data = { ...replyForm }
    if (!data.reply_date) {
      const now = new Date()
      data.reply_date = `${now.getFullYear()}年${String(now.getMonth() + 1).padStart(2, '0')}月${String(now.getDate()).padStart(2, '0')}日`
    }
    const res = await exportRectificationReply(data)
    const blob = new Blob([res], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `整改回复_${Date.now()}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    replyDialogVisible.value = false
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出整改回复失败：' + (error.message || '未知错误'))
  }
}

// ── 模板管理 ────────────────────────────────────────────────────────────────

const openTemplateEdit = (row = null) => {
  if (row) {
    templateEditTitle.value = '编辑模板'
    Object.assign(templateForm, {
      id: row.id,
      name: row.name,
      title_format: row.title_format,
      is_default: row.is_default
    })
  } else {
    templateEditTitle.value = '新建模板'
    Object.assign(templateForm, {
      id: null,
      name: '',
      title_format: '《关于{date}安全隐患整改有关事项回复》',
      is_default: false
    })
  }
  templateEditVisible.value = true
}

const saveTemplate = async () => {
  if (!templateForm.name) {
    ElMessage.warning('请填写模板名称')
    return
  }
  try {
    if (templateForm.id) {
      await updateTemplate(templateForm.id, templateForm)
      ElMessage.success('模板已更新')
    } else {
      await createTemplate(templateForm)
      ElMessage.success('模板已创建')
    }
    templateEditVisible.value = false
    await loadTemplates()
  } catch (error) {
    ElMessage.error('保存模板失败')
  }
}

const deleteTemplate = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个模板吗？', '提示', { type: 'warning' })
    await deleteTemplate(id)
    ElMessage.success('模板已删除')
    await loadTemplates()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

// ── 导入Word ────────────────────────────────────────────────────────────────

const openImportDialog = async () => {
  importDialogVisible.value = true
  await loadProjects()
}

const handleWordFileChange = async (uploadFile) => {
  selectedWordFile.value = uploadFile.raw
  importPreview.value = null
  previewLoading.value = true
  try {
    const fd = new FormData()
    fd.append('file', uploadFile.raw)
    const res = await previewFromWord(fd)
    if (res && res.success) {
      importPreview.value = res
    } else {
      ElMessage.warning('预览失败：' + (res?.message || '未知错误'))
    }
  } catch (error) {
    ElMessage.warning('预览失败：' + (error.message || '未知错误'))
  } finally {
    previewLoading.value = false
  }
}

const handleWordFileRemove = () => {
  selectedWordFile.value = null
  importPreview.value = null
}

const resetImportDialog = () => {
  selectedWordFile.value = null
  importPreview.value = null
  if (wordUploadRef.value) wordUploadRef.value.clearFiles()
}


const doImportWord = async () => {
  if (!selectedWordFile.value) {
    ElMessage.warning('请先选择Word文件')
    return
  }
  importing.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedWordFile.value)
    const result = await importFromWord(fd)
    if (result && result.success) {
      const msg = `成功导入 ${result.imported_count} 条隐患记录\n项目：${result.project_name || '未知'}`
      ElMessage.success({ message: msg, duration: 5000 })
      importDialogVisible.value = false
      resetImportDialog()
      getList()
      loadProjects()
    } else {
      ElMessage.error(result?.message || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败：' + (error.message || '未知错误'))
  } finally {
    importing.value = false
  }
}

const getPhotoUrl = (photoId) => {
  return `${import.meta.env.VITE_API_BASE_URL || 'http://192.168.31.105:9999'}/api/photos/${photoId}/download`
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
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
/* 导入预览 */
.import-preview {
  margin-top: 12px;
}
.preview-items {
  max-height: 280px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 8px;
}
.preview-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.preview-item:last-child {
  border-bottom: none;
}
.preview-title {
  font-weight: 600;
  color: #303133;
  font-size: 13px;
}
.preview-desc {
  color: #909399;
  font-size: 12px;
  margin-top: 2px;
  line-height: 1.4;
}
</style>
