import AppShellView from '@/views/AppShellView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: ()=> 
        import('../views/LoginView.vue')
    },
    {
      path: '/app',
      name: 'app-shell',
      component: () => 
        import('../views/AppShellView.vue')
    }
  ],
})

export default router
