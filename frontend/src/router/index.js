import { createRouter, createWebHistory } from 'vue-router'

import AgentListView from '../views/AgentListView.vue'
import AgentWorkspaceView from '../views/AgentWorkspaceView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileEditView from '../views/ProfileEditView.vue'
import { isLoggedIn } from '../store/authStore'

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
      path: '/profile',
      name: 'profile-edit',
      component: ProfileEditView,
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

router.beforeEach((to) => {
  if (to.meta.public) {
    if (isLoggedIn() && (to.name === 'login' || to.name === 'register')) {
      return { path: '/' }
    }
    return true
  }
  if (!isLoggedIn()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  return true
})

export default router


