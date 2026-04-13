<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { apiClient } from '../services/api'
import { authState } from '../store/authStore'

const router = useRouter()
const route = useRoute()

const loadError = ref('')
const loadReady = ref(false)

const loadProfile = async () => {
  loadError.value = ''
  try {
    const { data } = await apiClient.get('/auth/me/')
    authState.user = data
  } catch {
    loadError.value = '加载资料失败'
  } finally {
    loadReady.value = true
  }
}

onMounted(loadProfile)

const navItems = computed(() => [
  { name: 'profile-home', label: '个人主页', path: '/profile/home' },
  { name: 'profile-api-keys', label: '添加 API Key', path: '/profile/api-keys' },
  { name: 'profile-password', label: '修改密码', path: '/profile/password' },
])

const pageTitle = computed(() => {
  const m = {
    'profile-home': '个人主页',
    'profile-api-keys': '添加 API Key',
    'profile-password': '修改密码',
  }
  return m[route.name] || '账号设置'
})

const pageSubtitle = computed(() => {
  const m = {
    'profile-home': '管理头像、昵称、邮箱与个人介绍',
    'profile-api-keys': '为 Qwen、DeepSeek、GPT 配置自有 Key，未填写则使用系统默认',
    'profile-password': '定期更新密码以保护账号安全',
  }
  return m[route.name] || ''
})
</script>

<template>
  <div class="profile-shell">
    <aside class="profile-shell__aside" aria-label="资料功能">
      <div class="profile-shell__brand">
        <span class="profile-shell__brand-title">账号设置</span>
      </div>
      <nav class="profile-shell__nav">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="{ name: item.name }"
          class="profile-shell__link"
          active-class="profile-shell__link--active"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </aside>

    <main class="profile-shell__main">
      <header class="profile-shell__header">
        <div>
          <h1>{{ pageTitle }}</h1>
          <p>{{ pageSubtitle }}</p>
        </div>
        <button type="button" class="profile-shell__back" @click="router.push({ name: 'agent-home' })">
          返回
        </button>
      </header>

      <p v-if="loadError" class="profile-shell__banner profile-shell__banner--error">{{ loadError }}</p>
      <div v-else-if="loadReady" class="profile-shell__outlet">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<style scoped>
.profile-shell {
  min-height: 100vh;
  display: flex;
  align-items: stretch;
  background: var(--app-bg);
  color: var(--color-text);
}

.profile-shell__aside {
  width: 240px;
  flex-shrink: 0;
  padding: 1.75rem 0;
  background: var(--panel-bg);
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.06);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.profile-shell__brand {
  padding: 0 1.25rem;
}

.profile-shell__brand-title {
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--color-heading);
}

.profile-shell__nav {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0 0.75rem;
}

.profile-shell__link {
  display: block;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  color: var(--color-text-muted);
  font-weight: 600;
  font-size: 0.95rem;
  text-decoration: none;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.profile-shell__link:hover {
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

.profile-shell__link--active {
  background: rgba(var(--accent-rgb), 0.18);
  color: rgba(15, 23, 42, 0.88);
  box-shadow: inset 3px 0 0 rgba(var(--accent-rgb), 0.85);
}

.profile-shell__main {
  flex: 1;
  min-width: 0;
  padding: 2rem 2.5rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.profile-shell__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.profile-shell__header h1 {
  margin: 0;
  font-size: 1.65rem;
}

.profile-shell__header p {
  margin: 0.35rem 0 0;
  color: var(--color-text-muted);
  font-size: 0.95rem;
  max-width: 36rem;
}

.profile-shell__back {
  flex-shrink: 0;
  border: 1px solid var(--border-color);
  background: var(--panel-bg-muted);
  color: var(--color-text);
  border-radius: 10px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.95rem;
}

.profile-shell__banner {
  margin: 0;
  padding: 0.85rem 1rem;
  border-radius: 12px;
  font-size: 0.9rem;
}

.profile-shell__banner--error {
  background: rgba(254, 226, 226, 0.7);
  color: #b91c1c;
}

.profile-shell__outlet {
  max-width: 560px;
}

@media (max-width: 768px) {
  .profile-shell {
    flex-direction: column;
  }

  .profile-shell__aside {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    padding: 1rem;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .profile-shell__nav {
    flex-direction: row;
    flex-wrap: wrap;
    width: 100%;
    padding: 0;
  }

  .profile-shell__link {
    flex: 1;
    min-width: 7rem;
    text-align: center;
  }

  .profile-shell__link--active {
    box-shadow: inset 0 -3px 0 rgba(var(--accent-rgb), 0.85);
  }

  .profile-shell__main {
    padding: 1.25rem 1rem 2rem;
  }
}
</style>
