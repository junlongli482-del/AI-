import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
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
      component: () => import('@/views/v1/Home.vue'),
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
