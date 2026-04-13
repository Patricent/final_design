<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '../services/api'
import { clearTokens } from '../store/authStore'

const router = useRouter()

const oldPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const pwdLoading = ref(false)
const pwdError = ref('')
const pwdOk = ref('')

const submitPassword = async () => {
  pwdError.value = ''
  pwdOk.value = ''
  if (!oldPassword.value || !newPassword.value) {
    pwdError.value = '请填写当前密码和新密码'
    return
  }
  if (newPassword.value !== newPasswordConfirm.value) {
    pwdError.value = '两次新密码不一致'
    return
  }
  pwdLoading.value = true
  try {
    await apiClient.post('/auth/change-password/', {
      old_password: oldPassword.value,
      new_password: newPassword.value,
      new_password_confirm: newPasswordConfirm.value,
    })
    pwdOk.value = '密码已更新，请重新登录'
    oldPassword.value = ''
    newPassword.value = ''
    newPasswordConfirm.value = ''
    clearTokens()
    setTimeout(() => {
      router.replace({ name: 'login', query: {} })
    }, 800)
  } catch (e) {
    const d = e?.response?.data
    if (typeof d === 'object' && d) {
      const parts = []
      for (const [k, v] of Object.entries(d)) {
        if (Array.isArray(v)) parts.push(...v.map(String))
        else if (typeof v === 'string') parts.push(v)
        else parts.push(`${k}: ${JSON.stringify(v)}`)
      }
      pwdError.value = parts[0] || '修改密码失败'
    } else {
      pwdError.value = '修改密码失败'
    }
  } finally {
    pwdLoading.value = false
  }
}
</script>

<template>
  <section class="profile-card">
    <p class="hint">修改成功后将退出登录，请用新密码重新登录。</p>
    <form class="pwd-form" @submit.prevent="submitPassword">
      <label class="field">
        <span>当前密码</span>
        <input v-model="oldPassword" type="password" autocomplete="current-password" />
      </label>
      <label class="field">
        <span>新密码</span>
        <input v-model="newPassword" type="password" autocomplete="new-password" />
      </label>
      <label class="field">
        <span>确认新密码</span>
        <input v-model="newPasswordConfirm" type="password" autocomplete="new-password" />
      </label>
      <p v-if="pwdError" class="msg msg--error">{{ pwdError }}</p>
      <p v-if="pwdOk" class="msg msg--ok">{{ pwdOk }}</p>
      <button type="submit" class="secondary" :disabled="pwdLoading">
        {{ pwdLoading ? '提交中…' : '更新密码' }}
      </button>
    </form>
  </section>
</template>

<style scoped>
.profile-card {
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
}

.hint {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.pwd-form {
  margin-top: 0.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1rem;
}

.field span {
  font-size: 0.95rem;
}

input {
  border-radius: 10px;
  border: 1px solid var(--border-color);
  padding: 0.65rem 0.85rem;
  font-size: 0.95rem;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

.msg {
  margin: 0 0 1rem;
  font-size: 0.9rem;
}

.msg--error {
  color: #dc2626;
}

.msg--ok {
  color: #15803d;
}

.secondary {
  margin-top: 0.5rem;
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

.secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
