<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient, patchUserApiKeys } from '../services/api'
import { authState, clearTokens } from '../store/authStore'

const router = useRouter()

const nickname = ref('')
const email = ref('')
const bio = ref('')
const avatarFile = ref(null)
const avatarPreview = ref('')
const loading = ref(false)
const loadError = ref('')
const saveError = ref('')
const fileInputRef = ref(null)

const oldPassword = ref('')
const newPassword = ref('')
const newPasswordConfirm = ref('')
const pwdLoading = ref(false)
const pwdError = ref('')
const pwdOk = ref('')

const keyQwen = ref('')
const keyDeepseek = ref('')
const keyGpt = ref('')
const clearQwen = ref(false)
const clearDeepseek = ref(false)
const clearGpt = ref(false)
const keysLoading = ref(false)
const keysError = ref('')
const keysOk = ref('')

const loadProfile = async () => {
  loadError.value = ''
  try {
    const { data } = await apiClient.get('/auth/me/')
    nickname.value = data.nickname || ''
    email.value = data.email || ''
    bio.value = data.bio || ''
    avatarPreview.value = data.avatar || ''
    authState.user = data
  } catch (e) {
    loadError.value = '加载资料失败'
  }
}

const onAvatarChange = (e) => {
  const file = e.target.files?.[0]
  avatarFile.value = file || null
  if (file) {
    avatarPreview.value = URL.createObjectURL(file)
  }
}

const submit = async () => {
  saveError.value = ''
  loading.value = true
  try {
    const fd = new FormData()
    fd.append('nickname', nickname.value.trim())
    fd.append('email', email.value.trim())
    fd.append('bio', bio.value)
    if (avatarFile.value) {
      fd.append('avatar', avatarFile.value)
    }
    const { data } = await apiClient.patch('/auth/me/', fd)
    authState.user = data
    avatarFile.value = null
    if (fileInputRef.value) fileInputRef.value.value = ''
    router.push({ name: 'agent-home' })
  } catch (e) {
    const d = e?.response?.data
    if (typeof d === 'object' && d) {
      const first = Object.entries(d).find(([, v]) => v)
      saveError.value = first ? String(Array.isArray(first[1]) ? first[1][0] : first[1]) : '保存失败'
    } else {
      saveError.value = '保存失败'
    }
  } finally {
    loading.value = false
  }
}

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

const submitApiKeys = async () => {
  keysError.value = ''
  keysOk.value = ''
  const body = {}
  if (clearQwen.value) body.qwen_clear = true
  else if (keyQwen.value.trim()) body.qwen_api_key = keyQwen.value.trim()

  if (clearDeepseek.value) body.deepseek_clear = true
  else if (keyDeepseek.value.trim()) body.deepseek_api_key = keyDeepseek.value.trim()

  if (clearGpt.value) body.gpt_clear = true
  else if (keyGpt.value.trim()) body.gpt_api_key = keyGpt.value.trim()

  if (Object.keys(body).length === 0) {
    keysError.value = '请填写新的 Key，或勾选「改用系统默认」'
    return
  }

  keysLoading.value = true
  try {
    const data = await patchUserApiKeys(body)
    authState.user = data
    keyQwen.value = ''
    keyDeepseek.value = ''
    keyGpt.value = ''
    clearQwen.value = false
    clearDeepseek.value = false
    clearGpt.value = false
    keysOk.value = 'API Key 已更新'
  } catch (e) {
    const d = e?.response?.data
    keysError.value =
      typeof d === 'object' && d && typeof d.detail === 'string'
        ? d.detail
        : '保存失败，请稍后重试'
  } finally {
    keysLoading.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div class="page">
    <header class="page__header">
      <div>
        <h1>编辑资料</h1>
        <p>可修改昵称、头像、邮箱、个人介绍、大模型 API Key 与登录密码</p>
      </div>
      <button type="button" class="ghost" @click="router.push({ name: 'agent-home' })">返回</button>
    </header>

    <section class="card">
      <p v-if="loadError" class="msg msg--error">{{ loadError }}</p>
      <form v-else @submit.prevent="submit">
        <div class="avatar-row">
          <div class="avatar-wrap">
            <img v-if="avatarPreview" :src="avatarPreview" alt="" class="avatar" />
            <div v-else class="avatar avatar--placeholder">无头像</div>
          </div>
          <div>
            <label class="file-label">
              <input
                ref="fileInputRef"
                type="file"
                accept="image/*"
                class="sr-only"
                @change="onAvatarChange"
              />
              <span class="file-btn">选择图片</span>
            </label>
            <p class="hint">支持常见图片格式，留空则保留当前头像</p>
          </div>
        </div>

        <label class="field">
          <span>用户名</span>
          <input :value="authState.user?.username" type="text" disabled />
        </label>

        <label class="field">
          <span>昵称</span>
          <input v-model.trim="nickname" type="text" maxlength="50" placeholder="显示名称" />
        </label>

        <label class="field">
          <span>邮箱</span>
          <input v-model.trim="email" type="email" autocomplete="email" placeholder="选填" />
        </label>

        <label class="field">
          <span>个人介绍</span>
          <textarea v-model="bio" rows="5" maxlength="2000" placeholder="简单介绍一下自己…" />
        </label>

        <p v-if="saveError" class="msg msg--error">{{ saveError }}</p>

        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? '保存中…' : '保存资料' }}
        </button>
      </form>
    </section>

    <section v-if="!loadError" class="card card--secondary">
      <h2 class="card-title">大模型 API Key（可选）</h2>
      <p class="hint">
        与「新建智能体」中的三类模型对应：Qwen（阿里云百炼）、DeepSeek、GPT（OpenAI）。填写并保存后，仅当您本人发起对话时使用您的 Key；输入框留空表示该项本次不修改；勾选清除则恢复为系统默认；系统默认来自环境变量（见各条说明）。
      </p>

      <div class="api-key-block">
        <div class="api-key-head">
          <span class="api-key-title">Qwen（通义）</span>
          <span v-if="authState.user?.has_qwen_api_key" class="api-key-badge">已保存个人 Key</span>
        </div>
        <label class="field">
          <span>API Key</span>
          <input v-model="keyQwen" type="password" autocomplete="off" placeholder="输入新 Key 覆盖；不填表示本条不修改" />
        </label>
        <label class="check-row">
          <input v-model="clearQwen" type="checkbox" />
          <span>清除我的 Key，改用系统默认（DASHSCOPE_API_KEY / QWEN_API_KEY）</span>
        </label>
      </div>

      <div class="api-key-block">
        <div class="api-key-head">
          <span class="api-key-title">DeepSeek</span>
          <span v-if="authState.user?.has_deepseek_api_key" class="api-key-badge">已保存个人 Key</span>
        </div>
        <label class="field">
          <span>API Key</span>
          <input
            v-model="keyDeepseek"
            type="password"
            autocomplete="off"
            placeholder="输入新 Key 覆盖；不填表示本条不修改"
          />
        </label>
        <label class="check-row">
          <input v-model="clearDeepseek" type="checkbox" />
          <span>清除我的 Key，改用系统默认（DEEPSEEK_API_KEY）</span>
        </label>
      </div>

      <div class="api-key-block">
        <div class="api-key-head">
          <span class="api-key-title">OpenAI（GPT）</span>
          <span v-if="authState.user?.has_gpt_api_key" class="api-key-badge">已保存个人 Key</span>
        </div>
        <label class="field">
          <span>API Key</span>
          <input v-model="keyGpt" type="password" autocomplete="off" placeholder="输入新 Key 覆盖；不填表示本条不修改" />
        </label>
        <label class="check-row">
          <input v-model="clearGpt" type="checkbox" />
          <span>清除我的 Key，改用系统默认（OPENAI_API_KEY）</span>
        </label>
      </div>

      <p v-if="keysError" class="msg msg--error">{{ keysError }}</p>
      <p v-if="keysOk" class="msg msg--ok">{{ keysOk }}</p>
      <button type="button" class="secondary" :disabled="keysLoading" @click="submitApiKeys">
        {{ keysLoading ? '保存中…' : '保存 API Key 设置' }}
      </button>
    </section>

    <section v-if="!loadError" class="card card--secondary">
      <h2 class="card-title">修改密码</h2>
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
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  padding: 2rem;
  background: var(--app-bg);
  color: var(--color-text);
}

.page__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;
  max-width: 560px;
  margin-left: auto;
  margin-right: auto;
}

.page__header h1 {
  margin: 0;
  font-size: 1.5rem;
}

.page__header p {
  margin: 0.25rem 0 0;
  color: var(--color-text-muted);
  font-size: 0.95rem;
}

.ghost {
  border: 1px solid var(--border-color);
  background: var(--panel-bg-muted);
  color: var(--color-text);
  border-radius: 10px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.card {
  max-width: 560px;
  margin: 0 auto 1.25rem;
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
}

.card--secondary {
  margin-top: 0;
}

.card-title {
  margin: 0 0 0.5rem;
  font-size: 1.1rem;
}

.pwd-form {
  margin-top: 0.5rem;
}

.avatar-row {
  display: flex;
  gap: 1.25rem;
  align-items: center;
  margin-bottom: 1.25rem;
}

.avatar-wrap {
  flex-shrink: 0;
}

.avatar {
  width: 88px;
  height: 88px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--border-color);
}

.avatar--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--panel-bg-muted);
  color: var(--color-text-muted);
  font-size: 0.8rem;
}

.file-label {
  cursor: pointer;
}

.file-btn {
  display: inline-block;
  padding: 0.45rem 0.9rem;
  border-radius: 10px;
  background: var(--panel-bg-muted);
  border: 1px solid var(--border-color);
  font-size: 0.9rem;
}

.hint {
  margin: 0.5rem 0 0;
  font-size: 0.85rem;
  color: var(--color-text-muted);
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

input:not([type='file']),
textarea {
  border-radius: 10px;
  border: 1px solid var(--border-color);
  padding: 0.65rem 0.85rem;
  font-size: 0.95rem;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

input:disabled {
  opacity: 0.75;
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
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

.primary {
  margin-top: 0.5rem;
  width: 100%;
  border: none;
  border-radius: 12px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  background: var(--accent-color);
  color: #fff;
}

.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.api-key-block {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.api-key-block:first-of-type {
  margin-top: 0.75rem;
  padding-top: 0;
  border-top: none;
}

.api-key-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}

.api-key-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.api-key-badge {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.18);
  color: rgba(15, 23, 42, 0.8);
}

.check-row {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin: 0.5rem 0 0;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  cursor: pointer;
}

.check-row input {
  margin-top: 0.2rem;
}
</style>
