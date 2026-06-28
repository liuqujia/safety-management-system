/**
 * @author https://github.com/zxwk1998/vue-admin-better
 * @description router全局配置
 */

import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layouts'
import EmptyLayout from '@/layouts/EmptyLayout'
import { publicPath, routerMode } from '@/config'

Vue.use(VueRouter)
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true,
  },
  {
    path: '/register',
    component: () => import('@/views/register/index'),
    hidden: true,
  },
  {
    path: '/401',
    name: '401',
    component: () => import('@/views/401'),
    hidden: true,
  },
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/404'),
    hidden: true,
  },
]

export const asyncRoutes = [
  {
    path: '/',
    component: Layout,
    redirect: '/index',
    children: [
      {
        path: 'index',
        name: 'Index',
        component: () => import('@/views/index/index'),
        meta: {
          title: '首页',
          icon: 'home',
          affix: true,
        },
      },
      {
        path: 'safety',
        name: 'Safety',
        component: () => import('@/views/safety/index'),
        meta: {
          title: '安全管理',
          icon: 'shield-alt',
          affix: true,
        },
      },
    ],
  },
  {
    path: '/error',
    component: EmptyLayout,
    redirect: 'noRedirect',
    name: 'Error',
    meta: { title: '错误页', icon: 'bug' },
    children: [
      {
        path: '401',
        name: 'Error401',
        component: () => import('@/views/401'),
        meta: { title: '401' },
      },
      {
        path: '404',
        name: 'Error404',
        component: () => import('@/views/404'),
        meta: { title: '404' },
      },
    ],
  },
  {
    path: '*',
    redirect: '/404',
    hidden: true,
  },
]

const router = new VueRouter({
  base: publicPath,
  mode: routerMode,
  scrollBehavior: () => ({
    y: 0,
  }),
  routes: constantRoutes,
})

export function resetRouter() {
  location.reload()
}

export default router
