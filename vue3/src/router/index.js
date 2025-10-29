import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [

    //
    // V1开发需求路由
    //
    {
      path: '/',
      redirect: '/home' // 改为重定向到主页
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/v1/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/v1/Register.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/home',
      name: 'Home',
      component: () => import('@/views/v1/Home.vue'), // 保持V1，但会修改内容
      meta: { requiresAuth: true }
    },
    {
      path: '/user-center',
      name: 'UserCenter',
      component: () => import('@/views/v1/UserCenter.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/change-password',
      name: 'ChangePassword',
      component: () => import('@/views/v1/ChangePassword.vue'),
      meta: { requiresAuth: true }
    },


    //
    // V2版本路由
    // 新增：AI开发平台页面（V2版本）
    //
    {
      path: '/ai-platform',
      name: 'AIPlatform',
      component: () => import('@/views/v2/AIPlatform.vue'),
      meta: { requiresAuth: true }
    },

    //
    // V2版本路由 - 文档管理系统
    //
    {
      path: '/document-manager',
      name: 'DocumentManager',
      component: () => import('@/views/v2/DocumentManager/index.vue'),
      meta: { requiresAuth: true }
    },
    // 预留：文档编辑器路由（第二阶段开发）
    {
      path: '/document-editor',
      name: 'DocumentEditor',
      component: () => import('@/views/v2/DocumentEditor/index.vue'),
      meta: { requiresAuth: true }
    },
    // 在V2版本路由部分添加
    {
      path: '/tech-square',
      name: 'TechSquare',
      component: () => import('@/views/v2/TechSquare/index.vue'),
      meta: { requiresAuth: false } // 技术广场公开访问
    },
    {
      path: '/tech-square/document/:id',
      name: 'TechSquareDocument',
      component: () => import('@/views/v2/TechSquare/DocumentDetail.vue'),
      meta: { requiresAuth: false }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = getToken()

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (!to.meta.requiresAuth && token && (to.path === '/login' || to.path === '/register')) {
    next('/home')
  } else {
    next()
  }
})

export default router
