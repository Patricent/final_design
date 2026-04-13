<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiClient } from '../services/api'
import { authState, setTokens } from '../store/authStore'

const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const errorMessage = ref('')
const loading = ref(false)

const submit = async () => {
  errorMessage.value = ''
  if (!username.value.trim() || !password.value) {
    errorMessage.value = '请输入用户名和密码'
    return
  }
  loading.value = true
  try {
    const { data } = await apiClient.post('/auth/login/', {
      username: username.value.trim(),
      password: password.value,
    })
    setTokens(data.access, data.refresh)
    const { data: me } = await apiClient.get('/auth/me/')
    authState.user = me
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.replace(redirect || '/')
  } catch (e) {
    errorMessage.value = e?.response?.data?.detail || '登录失败，请检查用户名或密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="card">
      <h1>登录</h1>
      <p class="hint">登录后查看与管理你的智能体</p>
      <form @submit.prevent="submit">
        <label>
          <span>用户名</span>
          <input v-model.trim="username" type="text" autocomplete="username" />
        </label>
        <label>
          <span>密码</span>
          <input v-model="password" type="password" autocomplete="current-password" />
        </label>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? '登录中…' : '登录' }}
        </button>
      </form>
      <p class="footer">
        没有账号？
        <RouterLink to="/register">注册</RouterLink>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: var(--app-bg);
  color: var(--color-text);
}

.card {
  width: 100%;
  max-width: 400px;
  padding: 2rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
}

h1 {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
}

.hint {
  margin: 0 0 1.25rem;
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

label span {
  font-size: 0.9rem;
}

input {
  border-radius: 10px;
  border: 1px solid var(--border-color);
  padding: 0.65rem 0.85rem;
  font-size: 1rem;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

.error {
  margin: 0;
  color: #dc2626;
  font-size: 0.9rem;
}

button.primary {
  border: none;
  border-radius: 12px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  background: var(--accent-color);
  color: #fff;
}

button.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.footer {
  margin: 1.25rem 0 0;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.footer a {
  color: inherit;
  font-weight: 600;
}
</style>
