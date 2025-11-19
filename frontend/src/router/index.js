import { createRouter, createWebHistory } from 'vue-router'

import AgentListView from '../views/AgentListView.vue'
import AgentWorkspaceView from '../views/AgentWorkspaceView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'agent-home',
      component: AgentListView,
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

export default router


