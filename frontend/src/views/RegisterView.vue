<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '../services/api'
import { authState, setTokens } from '../store/authStore'

const router = useRouter()

const username = ref('')
const email = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')
const errorMessage = ref('')
const loading = ref(false)

const submit = async () => {
  errorMessage.value = ''
  if (!username.value.trim() || !password.value) {
    errorMessage.value = '用户名和密码为必填'
    return
  }
  if (password.value !== passwordConfirm.value) {
    errorMessage.value = '两次密码不一致'
    return
  }
  loading.value = true
  try {
    const { data } = await apiClient.post('/auth/register/', {
      username: username.value.trim(),
      email: email.value.trim() || '',
      nickname: nickname.value.trim() || '',
      password: password.value,
      password_confirm: passwordConfirm.value,
    })
    setTokens(data.access, data.refresh)
    authState.user = data.user
    router.replace('/')
  } catch (e) {
    const d = e?.response?.data
    if (typeof d === 'object' && d) {
      const first = Object.entries(d).find(([, v]) => v)
      errorMessage.value = first ? String(Array.isArray(first[1]) ? first[1][0] : first[1]) : '注册失败'
    } else {
      errorMessage.value = '注册失败'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="card">
      <h1>注册</h1>
      <p class="hint">创建账号后，智能体列表仅对你可见</p>
      <form @submit.prevent="submit">
        <label>
          <span>用户名</span>
          <input v-model.trim="username" type="text" autocomplete="username" />
        </label>
        <label>
          <span>邮箱（可选）</span>
          <input v-model.trim="email" type="email" autocomplete="email" />
        </label>
        <label>
          <span>昵称（可选）</span>
          <input v-model.trim="nickname" type="text" />
        </label>
        <label>
          <span>密码（至少 8 位）</span>
          <input v-model="password" type="password" autocomplete="new-password" />
        </label>
        <label>
          <span>确认密码</span>
          <input v-model="passwordConfirm" type="password" autocomplete="new-password" />
        </label>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? '注册中…' : '注册' }}
        </button>
      </form>
      <p class="footer">
        已有账号？
        <RouterLink to="/login">登录</RouterLink>
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
