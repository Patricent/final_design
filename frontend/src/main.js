import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { apiClient } from './services/api'
import { authState, clearTokens, isLoggedIn } from './store/authStore'

if (isLoggedIn()) {
  apiClient
    .get('/auth/me/')
    .then(({ data }) => {
      authState.user = data
    })
    .catch(() => {
      clearTokens()
      router.replace({ name: 'login' })
    })
}

const app = createApp(App)

app.use(router)
app.mount('#app')
