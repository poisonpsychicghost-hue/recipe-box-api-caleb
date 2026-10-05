import AppShellView from '@/views/AppShellView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import LoginView  from '../views/LoginView.vue'
import { useAuth } from '@/tools/useAuth.ts'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/app',
      name: 'app-shell',
      component: AppShellView
    }
  ],
});

router.beforeEach((to, from, next) => {
  const { authToken } = useAuth();

  const isProtected = to.path.startsWith('/app');

  if (isProtected && !authToken.value) {
    next(('/login'));
  } else {
    next();
  }
});

export default router
