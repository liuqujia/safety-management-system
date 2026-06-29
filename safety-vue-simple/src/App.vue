<template>
  <div class="app-container">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <h1>🏗️ 安全整改管理系统</h1>
          <div class="header-actions">
            <el-button plain @click="refreshData"><el-icon><Refresh /></el-icon> 刷新</el-button>
          </div>
        </div>
      </el-header>

      <el-main class="app-main">
        <!-- 操作栏 -->
        <el-card class="filter-card" shadow="hover">
          <el-form :inline="true" :model="queryForm">
            <el-form-item label="项目名称">
              <el-select v-model="queryForm.project_name" placeholder="全部项目" clearable filterable style="width: 180px">
                <el-option v-for="p in projectList" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="queryForm.status" placeholder="全部状态" clearable style="width: 120px">
                <el-option label="待整改" value="待整改" />
                <el-option label="整改中" value="整改中" />
                <el-option label="已完成" value="已完成" />
              </el-select>
            </el-form-item>
            <el-form-item label="严重程度">
              <el-select v-model="queryForm.severity" placeholder="全部程度" clearable style="width: 120px">
                <el-option label="轻微" value="轻微" />
                <el-option label="一般" value="一般" />
                <el-option label="严重" value="严重" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleQuery"><el-icon><Search /></el-icon> 查询</el-button>
              <el-button @click="resetQuery"><el-icon><RefreshLeft /></el-icon> 重置</el-button>
            </el-form-item>
          </el-form>
          <div class="action-buttons">
            <el-button type="primary" @click="handleAdd"><el-icon><Plus /></el-icon> 新增问题</el-button>
            <el-button type="info" @click="openImportDialog"><el-icon><Upload /></el-icon> 导入问题清单</el-button>
            <el-button type="warning" @click="openExportReplyDialog"><el-icon><Document /></el-icon> 导出整改回复</el-button>
            <el-button type="success" @click="openExportLedgerDialog"><el-icon><List /></el-icon> 导出检查记录</el-button>
            <el-button plain @click="templateDialogVisible = true"><el-icon><Setting /></el-icon> 模板管理</el-button>
          </div>
        </el-card>

        <!-- 问题列表：按项目分组 -->
        <div class="group-container" v-loading="loading">
          <div v-if="projectGroups.length === 0 && !loading" class="empty-state">
            <el-empty description="暂无问题数据" />
          </div>

          <el-collapse v-model="activeProjects" v-else>
            <el-collapse-item v-for="group in projectGroups" :key="group.project_name" :name="group.project_name">
              <template #title>
                <span class="group-title">
                  📁 {{ group.project_name || '未分类' }}
                  <el-tag size="small" type="info" style="margin-left: 8px">{{ group.issues.length }} 个隐患</el-tag>
                </span>
                <el-button
                  link type="warning" size="small"
                  style="float: right; margin-left: 12px"
                  @click.stop="handleExportProjectReply(group.project_name)"
                >
                  <el-icon><Document /></el-icon> 导出本项目整改回复
                </el-button>
                <el-button
                  link type="danger" size="small"
                  style="float: right; margin-left: 12px"
                  @click.stop="handleDeleteProject(group.project_name || '__EMPTY__')"
                >
                  <el-icon><Delete /></el-icon> 删除项目
                </el-button>
              </template>

              <el-table :data="group.issues" border stripe size="small" @row-click="handleView">
                <el-table-column type="index" label="序号" width="60" align="center" />
                <el-table-column prop="title" label="问题内容" min-width="200" show-overflow-tooltip />
                <el-table-column prop="location" label="地点" width="120" show-overflow-tooltip />
                <el-table-column prop="severity" label="严重程度" width="90" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getSeverityType(row.severity)" size="small">{{ row.severity }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="responsible_person" label="责任人" width="90" />
                <el-table-column prop="create_time" label="创建日期" width="100">
                  <template #default="{ row }">
                    {{ formatDate(row.create_time) }}
                  </template>
                </el-table-column>
                <el-table-column prop="photo_count" label="照片" width="55" align="center" />
                <el-table-column label="操作" width="200" fixed="right" align="center">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click.stop="handleView(row)">查看</el-button>
                    <el-button link type="primary" size="small" @click.stop="handleEdit(row)">编辑</el-button>
                    <el-button link type="success" size="small" @click.stop="handleUploadPhoto(row)">整改照片</el-button>
                    <el-button link type="danger" size="small" @click.stop="handleDelete(row)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-collapse-item>
          </el-collapse>

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
        </div>
      </el-main>
    </el-container>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @close="handleDialogClose">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="项目名称">
          <el-select v-model="formData.project_name" placeholder="请选择/输入项目" filterable allow-create clearable style="width: 100%">
            <el-option v-for="p in projectList" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入问题标题" />
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="含法规条款" />
        </el-form-item>
        <el-form-item label="发现位置">
          <el-input v-model="formData.location" placeholder="请输入发现位置" />
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="formData.severity" style="width: 100%">
            <el-option label="轻微" value="轻微" />
            <el-option label="一般" value="一般" />
            <el-option label="严重" value="严重" />
          </el-select>
        </el-form-item>
        <el-form-item label="责任人" prop="responsible_person">
          <el-input v-model="formData.responsible_person" placeholder="请输入责任人" />
        </el-form-item>
        <el-form-item label="整改期限">
          <el-date-picker v-model="formData.deadline" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="整改措施">
          <el-input v-model="formData.notes" type="textarea" :rows="2" placeholder="整改措施或建议" />
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
        <el-descriptions-item label="项目名称">{{ currentIssue.project_name || '未提供' }}</el-descriptions-item>
        <el-descriptions-item label="严重程度">
          <el-tag :type="getSeverityType(currentIssue.severity)">{{ currentIssue.severity }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="问题标题" :span="2">{{ currentIssue.title }}</el-descriptions-item>
        <el-descriptions-item label="发现位置">{{ currentIssue.location }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentIssue.status)">{{ currentIssue.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="责任人">{{ currentIssue.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="整改期限">{{ currentIssue.deadline }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentIssue.create_time) }}</el-descriptions-item>
        <el-descriptions-item label="问题描述" :span="2">{{ currentIssue.description }}</el-descriptions-item>
        <el-descriptions-item label="整改措施" :span="2">{{ currentIssue.notes }}</el-descriptions-item>
      </el-descriptions>

      <div class="photos-section" v-if="currentIssue.id">
        <h4>📷 问题照片</h4>
        <div class="photo-grid" v-if="currentIssue.issue_photos?.length">
          <el-image v-for="photo in currentIssue.issue_photos" :key="photo.id"
            :src="getPhotoUrl(photo.id)" :preview-src-list="currentIssue.issue_photos.map(p => getPhotoUrl(p.id))"
            fit="cover" class="photo-item" />
        </div>
        <el-empty v-else image-size="60" description="暂无问题照片" />

        <h4>✅ 整改后照片</h4>
        <div class="photo-grid" v-if="currentIssue.rectification_photos?.length">
          <el-image v-for="photo in currentIssue.rectification_photos" :key="photo.id"
            :src="getPhotoUrl(photo.id)" :preview-src-list="currentIssue.rectification_photos.map(p => getPhotoUrl(p.id))"
            fit="cover" class="photo-item" />
        </div>
        <el-empty v-else image-size="60" description="暂无整改照片" />
      </div>
    </el-dialog>

    <!-- 上传整改照片对话框 -->
    <el-dialog v-model="uploadVisible" title="上传整改照片" width="500px">
      <el-upload ref="uploadRef" :auto-upload="false" :limit="10"
        :on-exceed="() => ElMessage.warning('最多10张')" list-type="picture-card"
        accept="image/*" :http-request="handleUploadRequest">
        <el-icon><Plus /></el-icon>
      </el-upload>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">上传</el-button>
      </template>
    </el-dialog>

    <!-- 导入问题清单对话框 -->
    <el-dialog v-model="importDialogVisible" title="导入问题清单" width="700px" @close="resetImportDialog">
      <el-upload ref="wordUploadRef" drag :auto-upload="false" :limit="1"
        accept=".docx,.doc" :on-change="handleWordFileChange" :on-remove="handleWordFileRemove">
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">拖动 Word 文件到此处，或<em>点击选择</em></div>
      </el-upload>

      <!-- 预览区 -->
      <div v-if="importPreview" class="import-preview">
        <h4>📋 识别预览</h4>
        <el-form :inline="true">
          <el-form-item label="项目名称">
            <el-input v-model="importPreview.project_name" style="width: 300px" />
          </el-form-item>
        </el-form>

        <el-table :data="importPreview.items" border size="small" max-height="300">
          <el-table-column type="selection" width="45" />
          <el-table-column type="index" label="#" width="45" />
          <el-table-column prop="project_name" label="项目" width="140" show-overflow-tooltip />
          <el-table-column prop="title" label="隐患描述" min-width="280" show-overflow-tooltip />
          <el-table-column label="位置" width="100">
            <template #default="{ row }">{{ row.location || '-' }}</template>
          </el-table-column>
        </el-table>
        <p style="margin-top: 8px; color: #999; font-size: 12px">
          勾选的条目将被导入，取消勾选则跳过。
        </p>
      </div>

      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" :disabled="!importPreview?.items?.length" @click="doImportWord">
          导入已选 ({{ importPreview?.selectedCount || 0 }} 条)
        </el-button>
      </template>
    </el-dialog>

    <!-- 导出整改回复对话框 -->
    <el-dialog v-model="exportReplyVisible" title="导出整改回复" width="500px">
      <el-form :model="replyForm" label-width="100px">
        <el-form-item label="项目名称">
          <el-select v-model="replyForm.project_name" placeholder="请选择项目" filterable allow-create clearable style="width: 100%">
            <el-option v-for="p in projectList" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目负责人" required :error="!replyForm.project_responsible ? '请填写项目负责人' : ''">
          <el-input v-model="replyForm.project_responsible" placeholder="姓名 电话（必填）" />
          <div v-if="!replyForm.project_responsible" style="color: #F56C6C; font-size: 12px; margin-top: 4px">请填写项目负责人</div>
        </el-form-item>
        <el-form-item label="回复日期">
          <el-date-picker v-model="replyForm.reply_date" type="date" placeholder="选择日期" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportReplyVisible = false">取消</el-button>
        <el-button type="warning" :loading="exportingReply" @click="doExportReply">生成整改回复报告</el-button>
      </template>
    </el-dialog>

    <!-- 导出检查记录对话框 -->
    <el-dialog v-model="exportLedgerVisible" title="导出检查记录（台账）" width="500px">
      <el-form :model="ledgerForm" label-width="100px">
        <el-form-item label="年份">
          <el-select v-model="ledgerForm.year" placeholder="选择年份" style="width: 100%">
            <el-option v-for="y in yearOptions" :key="y" :label="y + '年'" :value="y" />
          </el-select>
        </el-form-item>
        <el-form-item label="检查内容">
          <el-input v-model="ledgerForm.check_content" placeholder="例如：日常检查、集团检查" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exportLedgerVisible = false">取消</el-button>
        <el-button type="success" :loading="exportingLedger" @click="doExportLedger">导出台账</el-button>
      </template>
    </el-dialog>

    <!-- 模板管理对话框 -->
    <el-dialog v-model="templateDialogVisible" title="导出模板管理" width="650px">
      <div class="template-actions" style="margin-bottom: 12px">
        <el-button size="small" type="primary" @click="openTemplateEdit(null)">+ 新建模板</el-button>
      </div>
      <el-table :data="templateList" border size="small">
        <el-table-column prop="name" label="模板名称" min-width="140" />
        <el-table-column label="列配置" min-width="200">
          <template #default="{ row }">
            <span style="font-size: 12px; color: #666">{{ row.columns?.join(', ') || '（默认列）' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="默认" width="60" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="success" size="small">是</el-tag>
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
      <template #footer>
        <el-button @click="templateDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 模板编辑弹窗 -->
    <el-dialog v-model="templateEditVisible" :title="templateEditTitle" width="500px">
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="templateForm.name" placeholder="例如：安全生产检查表" />
        </el-form-item>
        <el-form-item label="标题格式">
          <el-input v-model="templateForm.title_format" placeholder="例如：《关于{date}安全隐患整改有关事项回复》" />
          <span style="font-size: 12px; color: #999">使用 <code>{date}</code> 自动替换日期</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="templateEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTemplate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:9999'

// ── 状态 ──
const loading = ref(false)
const tableData = ref([])
const projectList = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const uploadVisible = ref(false)
const importDialogVisible = ref(false)
const exportReplyVisible = ref(false)
const templateDialogVisible = ref(false)
const templateEditVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref(null)
const uploadRef = ref(null)
const wordUploadRef = ref(null)
const currentIssue = ref({})
const uploadIssueId = ref(null)
const importing = ref(false)
const exportingReply = ref(false)
const activeProjects = ref([])
const selectedWordFile = ref(null)
const importPreview = ref(null)
const templateEditTitle = ref('新建模板')

const queryForm = reactive({
  project_name: '',
  status: '',
  severity: ''
})

const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

const formData = reactive({
  id: null,
  project_name: '',
  title: '',
  description: '',
  location: '',
  severity: '一般',
  responsible_person: '',
  deadline: '',
  notes: ''
})

const formRules = {
  title: [{ required: true, message: '请输入问题标题', trigger: 'blur' }],
  responsible_person: [{ required: true, message: '请输入责任人', trigger: 'blur' }]
}

const replyForm = reactive({
  project_name: '',
  project_responsible: '',
  reply_date: ''
})

// 检查记录台账导出
const exportLedgerVisible = ref(false)
const exportingLedger = ref(false)
const ledgerForm = reactive({
  year: new Date().getFullYear(),
  check_content: '日常检查'
})
const yearOptions = computed(() => {
  const current = new Date().getFullYear()
  return [current, current - 1, current - 2]
})

const templateForm = reactive({
  id: null,
  name: '',
  title_format: '《关于{date}安全隐患整改有关事项回复》',
  columns: []
})

const templateList = ref([])

// ── 计算属性：项目分组 ──
const projectGroups = computed(() => {
  const groups = {}
  for (const issue of tableData.value) {
    const name = issue.project_name || '未分类'
    if (!groups[name]) groups[name] = { project_name: name, issues: [] }
    groups[name].issues.push(issue)
  }
  const result = Object.values(groups)
  // 让"未分类"排最后
  result.sort((a, b) => {
    if (a.project_name === '未分类') return 1
    if (b.project_name === '未分类') return -1
    return a.project_name.localeCompare(b.project_name, 'zh')
  })
  return result
})

onMounted(() => {
  loadData()
  loadProjects()
  loadTemplates()
})

// ── 数据加载 ──
const loadData = async () => {
  loading.value = true
  try {
    const params = { page: pagination.page, limit: pagination.limit }
    if (queryForm.project_name) params.project_name = queryForm.project_name
    if (queryForm.status) params.status = queryForm.status
    if (queryForm.severity) params.severity = queryForm.severity
    const res = await axios.get(`${API_BASE}/api/issues/`, { params })
    tableData.value = res.data?.items || res.data || []
    pagination.total = res.data?.total || tableData.value.length
    // 自动展开所有项目分组
    activeProjects.value = projectGroups.value.map(g => g.project_name)
  } catch (e) {
    ElMessage.error('加载失败: ' + (e.message || ''))
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/issues/projects/list`)
    projectList.value = res.data || []
  } catch (e) { /* 静默失败 */ }
}

const loadTemplates = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/export/templates`)
    templateList.value = res.data || []
  } catch (e) { /* 静默失败 */ }
}

const handleQuery = () => { pagination.page = 1; loadData() }
const resetQuery = () => { queryForm.project_name = ''; queryForm.status = ''; queryForm.severity = ''; handleQuery() }
const refreshData = () => { loadData(); loadProjects(); ElMessage.success('已刷新') }

const getSeverityType = (s) => ({ '轻微': 'info', '一般': 'warning', '严重': 'danger' }[s] || 'info')
const getStatusType = (s) => ({ '待整改': 'danger', '整改中': 'warning', '已完成': 'success' }[s] || 'info')

// 格式化日期：只显示年月日
const formatDate = (d) => {
  if (!d) return ''
  // 处理 "2026-06-29T11:22:33" 或 "2026-06-29 11:22:33" 格式
  return d.substring(0, 10)
}

// ── CRUD ──
const handleAdd = () => {
  dialogTitle.value = '新增问题'
  Object.assign(formData, { id: null, project_name: '', title: '', description: '', location: '', severity: '一般', responsible_person: '', deadline: '', notes: '' })
  dialogVisible.value = true
}

const handleView = async (row) => {
  try {
    const res = await axios.get(`${API_BASE}/api/issues/${row.id}`)
    currentIssue.value = res.data
    detailVisible.value = true
  } catch (e) { ElMessage.error('获取详情失败') }
}

const handleEdit = async (row) => {
  try {
    const res = await axios.get(`${API_BASE}/api/issues/${row.id}`)
    Object.assign(formData, res.data)
    dialogTitle.value = '编辑问题'
    dialogVisible.value = true
  } catch (e) { ElMessage.error('获取失败') }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
    await axios.delete(`${API_BASE}/api/issues/${row.id}`)
    ElMessage.success('已删除')
    loadData()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}

const handleDeleteProject = async (projectName) => {
  try {
    await ElMessageBox.confirm(
      `确定删除项目「${projectName}」下的所有隐患？`,
      '提示',
      { type: 'warning', confirmButtonText: '确定删除', cancelButtonText: '取消' }
    )
    const res = await axios.delete(`${API_BASE}/api/issues/batch/delete`, {
      params: { project_name: projectName }
    })
    ElMessage.success(res.data?.message || '删除成功')
    loadData(); loadProjects()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      if (formData.id) {
        await axios.put(`${API_BASE}/api/issues/${formData.id}`, formData)
        ElMessage.success('已更新')
      } else {
        await axios.post(`${API_BASE}/api/issues/`, formData)
        ElMessage.success('已创建')
      }
      dialogVisible.value = false
      loadData()
      loadProjects()
    } catch (e) { ElMessage.error('操作失败') }
  })
}

const handleDialogClose = () => formRef.value?.resetFields()

// ── 照片 ──
const handleUploadPhoto = (row) => { uploadIssueId.value = row.id; uploadVisible.value = true }

const handleUploadRequest = async (options) => {
  const fd = new FormData()
  fd.append('photos', options.file)
  fd.append('photo_type', '整改照片')
  try {
    await axios.post(`${API_BASE}/api/issues/${uploadIssueId.value}/photos`, fd)
    ElMessage.success('上传成功')
    uploadVisible.value = false
    loadData()
  } catch (e) { ElMessage.error('上传失败') }
}

const submitUpload = () => uploadRef.value?.submit()

const getPhotoUrl = (id) => `${API_BASE}/api/photos/${id}/download`

// ── 导入问题清单 ──
const openImportDialog = async () => {
  importDialogVisible.value = true
  await loadProjects()
}

const handleWordFileChange = async (uploadFile) => {
  selectedWordFile.value = uploadFile.raw
  importPreview.value = null
  try {
    const fd = new FormData()
    fd.append('file', uploadFile.raw)
    const res = await axios.post(`${API_BASE}/api/issues/preview-from-word`, fd)
    if (res.data?.success) {
      importPreview.value = res.data
      importPreview.value.selectedCount = res.data.items?.length || 0
    } else {
      ElMessage.warning('预览失败：' + (res.data?.message || ''))
    }
  } catch (e) { ElMessage.warning('预览失败') }
}

const handleWordFileRemove = () => { selectedWordFile.value = null; importPreview.value = null }

const resetImportDialog = () => {
  selectedWordFile.value = null
  importPreview.value = null
  wordUploadRef.value?.clearFiles()
}

const doImportWord = async () => {
  if (!selectedWordFile.value) { ElMessage.warning('请选择文件'); return }
  importing.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedWordFile.value)
    if (importPreview.value?.project_name) fd.append('project_name', importPreview.value.project_name)
    const res = await axios.post(`${API_BASE}/api/issues/import-from-word`, fd)
    if (res.data?.success) {
      ElMessage.success(`成功导入 ${res.data.imported_count} 条隐患`)
      importDialogVisible.value = false
      resetImportDialog()
      loadData()
      loadProjects()
    } else {
      ElMessage.error(res.data?.message || '导入失败')
    }
  } catch (e) { ElMessage.error('导入失败') }
  finally { importing.value = false }
}

// ── 导出整改回复 ──
const openExportReplyDialog = () => { exportReplyVisible.value = true; loadProjects() }

// ── 导出检查记录 ──
const openExportLedgerDialog = () => {
  exportLedgerVisible.value = true
  ledgerForm.year = new Date().getFullYear()
  ledgerForm.check_content = '日常检查'
}

const handleExportProjectReply = (projectName) => {
  if (!projectName || projectName === '__EMPTY__') { ElMessage.warning('请先为该项目设置名称'); return }
  replyForm.project_name = projectName
  replyForm.project_responsible = ''
  replyForm.reply_date = ''
  exportReplyVisible.value = true
}

const doExportReply = async () => {
  if (!replyForm.project_responsible) { ElMessage.warning('请填写项目负责人'); return }
  if (!replyForm.reply_date) { ElMessage.warning('请选择回复日期'); return }
  exportingReply.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/export/rectification-reply`, {
      project_name: replyForm.project_name || undefined,
      project_responsible: replyForm.project_responsible || '',
      reply_date: replyForm.reply_date
    }, { responseType: 'blob' })
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `整改回复_${replyForm.reply_date}.xlsx`; a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
    exportReplyVisible.value = false
  } catch (e) { ElMessage.error('导出失败') }
  finally { exportingReply.value = false }
}

// ── 导出检查记录（台账） ──
const doExportLedger = async () => {
  if (!ledgerForm.year) { ElMessage.warning('请选择年份'); return }
  exportingLedger.value = true
  try {
    const res = await axios.post(`${API_BASE}/api/export/ledger`, {
      year: ledgerForm.year,
      check_content: ledgerForm.check_content || '日常检查'
    }, {
      responseType: 'blob'
    })
    const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = `检查记录台账_${ledgerForm.year}年.xlsx`; a.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
    exportLedgerVisible.value = false
  } catch (e) { ElMessage.error('导出失败')
  } finally { exportingLedger.value = false }
}

// ── 模板管理 ──
const openTemplateEdit = (row) => {
  if (row) {
    Object.assign(templateForm, { id: row.id, name: row.name, title_format: row.title_format || '《关于{date}安全隐患整改有关事项回复》', columns: row.columns || [] })
    templateEditTitle.value = '编辑模板'
  } else {
    Object.assign(templateForm, { id: null, name: '', title_format: '《关于{date}安全隐患整改有关事项回复》', columns: [] })
    templateEditTitle.value = '新建模板'
  }
  templateEditVisible.value = true
}

const saveTemplate = async () => {
  try {
    if (templateForm.id) {
      await axios.put(`${API_BASE}/api/export/templates/${templateForm.id}`, templateForm)
      ElMessage.success('模板已更新')
    } else {
      await axios.post(`${API_BASE}/api/export/templates`, templateForm)
      ElMessage.success('模板已创建')
    }
    templateEditVisible.value = false
    loadTemplates()
  } catch (e) { ElMessage.error('保存失败') }
}

const deleteTemplate = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
    await axios.delete(`${API_BASE}/api/export/templates/${id}`)
    ElMessage.success('已删除')
    loadTemplates()
  } catch (e) { if (e !== 'cancel') ElMessage.error('删除失败') }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f0f2f5; }

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white; padding: 0; box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.header-content {
  display: flex; justify-content: space-between; align-items: center;
  height: 100%; padding: 0 20px;
}
.header-content h1 { font-size: 22px; font-weight: 600; }
.app-main { padding: 20px; }
.filter-card { margin-bottom: 20px; }
.action-buttons { display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; }
.group-container { min-height: 200px; }
.group-title { font-weight: 600; font-size: 15px; }
.pagination-container { display: flex; justify-content: flex-end; margin-top: 16px; }
.photos-section { margin-top: 20px; }
.photos-section h4 { margin: 15px 0 10px; font-size: 15px; color: #409eff; }
.photo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
.photo-item { width: 140px; height: 140px; border-radius: 6px; cursor: pointer; transition: transform 0.2s; }
.photo-item:hover { transform: scale(1.04); }
.import-preview { margin-top: 16px; padding: 12px; background: #fafafa; border-radius: 6px; }
.import-preview h4 { margin-bottom: 10px; font-size: 14px; }
.empty-state { padding: 60px 0; }
.el-header { line-height: 60px; }
.el-descriptions__cell { padding: 8px 12px; }
.el-collapse-item__header { font-weight: 500; }
</style>
