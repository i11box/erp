import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/components/Layout/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard/index.vue'),
        meta: { title: '仪表板', requiresAuth: true }
      },
      {
        path: '/suppliers',
        name: 'Suppliers',
        component: () => import('@/views/Suppliers/index.vue'),
        meta: { title: '供应商管理', requiresAuth: true }
      },
      {
        path: '/customers',
        name: 'Customers',
        component: () => import('@/views/Customers/index.vue'),
        meta: { title: '客户管理', requiresAuth: true }
      },
      {
        path: '/products',
        name: 'Products',
        component: () => import('@/views/Products/index.vue'),
        meta: { title: '商品管理', requiresAuth: true }
      },
      {
        path: '/inventory',
        name: 'Inventory',
        component: () => import('@/views/Inventory/index.vue'),
        meta: { title: '库存管理', requiresAuth: true }
      },
      {
        path: '/purchases',
        name: 'Purchases',
        component: () => import('@/views/Purchases/index.vue'),
        meta: { title: '采购管理', requiresAuth: true }
      },
      {
        path: '/sales',
        name: 'Sales',
        component: () => import('@/views/Sales/index.vue'),
        meta: { title: '销售管理', requiresAuth: true }
      },
      {
        path: '/analytics',
        name: 'Analytics',
        component: () => import('@/views/Analytics/index.vue'),
        meta: { title: '统计分析', requiresAuth: true }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: { title: '登录' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // Check if the route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      // Redirect to login page
      next('/login')
    } else {
      // Proceed to route
      next()
    }
  } else {
    // If user is already authenticated and trying to access login page
    if (to.name === 'Login' && authStore.isAuthenticated) {
      next('/')
    } else {
      next()
    }
  }
})

export default router