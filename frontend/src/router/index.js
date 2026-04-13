import { createRouter, createWebHistory } from 'vue-router'

import AgentListView from '../views/AgentListView.vue'
import AgentWorkspaceView from '../views/AgentWorkspaceView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileLayout from '../views/ProfileLayout.vue'
import ProfileHomeView from '../views/ProfileHomeView.vue'
import ProfileApiKeysView from '../views/ProfileApiKeysView.vue'
import ProfilePasswordView from '../views/ProfilePasswordView.vue'
import AgentSquareView from '../views/AgentSquareView.vue'
import AdminAgentsView from '../views/AdminAgentsView.vue'
import { apiClient } from '../services/api'
import { authState, isLoggedIn } from '../store/authStore'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { public: true },
    },
    {
      path: '/',
      name: 'agent-home',
      component: AgentListView,
    },
    {
      path: '/square',
      name: 'agent-square',
      component: AgentSquareView,
    },
    {
      path: '/admin/agents',
      name: 'admin-agents',
      component: AdminAgentsView,
      meta: { requiresAdmin: true },
    },
    {
      path: '/profile',
      component: ProfileLayout,
      redirect: { name: 'profile-home' },
      children: [
        {
          path: 'home',
          name: 'profile-home',
          component: ProfileHomeView,
        },
        {
          path: 'api-keys',
          name: 'profile-api-keys',
          component: ProfileApiKeysView,
        },
        {
          path: 'password',
          name: 'profile-password',
          component: ProfilePasswordView,
        },
      ],
    },
    {
      path: '/agents/new',
      name: 'agent-create',
      component: AgentWorkspaceView,
      props: { isNew: true, showEditor: true },
    },
    {
      path: '/agents/:id(\\d+)',
      name: 'agent-workspace',
      component: AgentWorkspaceView,
      props: (route) => ({
        id: Number(route.params.id),
        showEditor: route.query.edit === '1',
      }),
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.public) {
    if (isLoggedIn() && (to.name === 'login' || to.name === 'register')) {
      return { path: '/' }
    }
    return true
  }
  if (!isLoggedIn()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (!authState.user) {
    try {
      const { data } = await apiClient.get('/auth/me/')
      authState.user = data
    } catch {
      /* 忽略，各页自行处理未登录 */
    }
  }
  if (to.meta.requiresAdmin && !authState.user?.is_staff) {
    return { path: '/' }
  }
  return true
})

export default router


