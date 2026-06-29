import request from '@/utils/request'

/**
 * @description 获取问题列表
 * @param {Object} params
 */
export function getIssues(params) {
  return request({
    url: '/api/issues/',
    method: 'get',
    params
  })
}

/**
 * @description 获取单个问题
 * @param {Number} id
 */
export function getIssue(id) {
  return request({
    url: `/api/issues/${id}`,
    method: 'get'
  })
}

/**
 * @description 创建问题
 * @param {Object} data
 */
export function createIssue(data) {
  return request({
    url: '/api/issues/',
    method: 'post',
    data
  })
}

/**
 * @description 更新问题
 * @param {Number} id
 * @param {Object} data
 */
export function updateIssue(id, data) {
  return request({
    url: `/api/issues/${id}`,
    method: 'put',
    data
  })
}

/**
 * @description 删除问题
 * @param {Number} id
 */
export function deleteIssue(id) {
  return request({
    url: `/api/issues/${id}`,
    method: 'delete'
  })
}

/**
 * @description 更新问题状态
 * @param {Number} id
 * @param {String} status
 */
export function updateIssueStatus(id, status) {
  return request({
    url: `/api/issues/${id}/status`,
    method: 'put',
    params: { status }
  })
}

/**
 * @description 上传照片
 * @param {Number} id
 * @param {String} photoType
 * @param {FormData} formData
 */
export function uploadPhoto(id, photoType, formData) {
  return request({
    url: `/api/issues/${id}/photos`,
    method: 'post',
    data: formData,
    params: { photoType },
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * @description 导出Excel
 * @param {Object} params
 */
export function exportExcel(params) {
  return request({
    url: '/api/export/excel',
    method: 'get',
    params,
    responseType: 'blob'
  })
}

/**
 * @description 下载照片
 * @param {Number} photoId
 */
export function downloadPhoto(photoId) {
  return request({
    url: `/api/photos/${photoId}/download`,
    method: 'get',
    responseType: 'blob'
  })
}

/**
 * @description 删除照片
 * @param {Number} photoId
 */
export function deletePhoto(photoId) {
  return request({
    url: `/api/photos/${photoId}`,
    method: 'delete'
  })
}

/**
 * @description 获取导出模板列表
 */
export function getTemplates() {
  return request({
    url: '/api/export/templates',
    method: 'get'
  })
}

/**
 * @description 创建导出模板
 * @param {Object} data
 */
export function createTemplate(data) {
  return request({
    url: '/api/export/templates',
    method: 'post',
    data
  })
}

/**
 * @description 更新导出模板
 * @param {Number} id
 * @param {Object} data
 */
export function updateTemplate(id, data) {
  return request({
    url: `/api/export/templates/${id}`,
    method: 'put',
    data
  })
}

/**
 * @description 删除导出模板
 * @param {Number} id
 */
export function deleteTemplate(id) {
  return request({
    url: `/api/export/templates/${id}`,
    method: 'delete'
  })
}

/**
 * @description 导出整改回复报告
 * @param {Object} data
 */
export function exportRectificationReply(data) {
  return request({
    url: '/api/export/rectification-reply',
    method: 'post',
    data,
    responseType: 'blob'
  })
}

/**
 * @description 从Word文档导入隐患
 * @param {FormData} formData
 */
export function importFromWord(formData) {
  return request({
    url: '/api/issues/import-from-word',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}