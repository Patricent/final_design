<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { apiClient } from '../services/api'
import { authState } from '../store/authStore'

const router = useRouter()

const nickname = ref('')
const email = ref('')
const bio = ref('')
const avatarFile = ref(null)
const avatarPreview = ref('')
const loading = ref(false)
const saveError = ref('')
const fileInputRef = ref(null)

const syncFromUser = () => {
  const u = authState.user
  if (!u) return
  nickname.value = u.nickname || ''
  email.value = u.email || ''
  bio.value = u.bio || ''
  avatarPreview.value = u.avatar || ''
}

watch(
  () => authState.user,
  () => syncFromUser(),
  { immediate: true, deep: true },
)

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
</script>

<template>
  <section class="profile-card">
    <form @submit.prevent="submit">
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
</template>

<style scoped>
.profile-card {
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
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
</style>
