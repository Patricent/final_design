<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AdminAgentAPI } from '../services/api'
import { authState, clearTokens } from '../store/authStore'

const router = useRouter()

const displayName = computed(
  () => authState.user?.nickname || authState.user?.username || '用户',
)

const logout = () => {
  clearTokens()
  router.push({ name: 'login' })
}

const tab = ref('all')
const agents = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const actingId = ref(null)
const searchTerm = ref('')

const formatTime = (iso) => {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString('zh-CN', { hour12: false })
}

const load = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    agents.value =
      tab.value === 'recycle' ? await AdminAgentAPI.listRecycle() : await AdminAgentAPI.listAll()
  } catch (e) {
    console.error(e)
    errorMessage.value = '加载失败，请确认已使用管理员账号登录'
  } finally {
    isLoading.value = false
  }
}

const switchTab = async (next) => {
  tab.value = next
  await load()
}

const filtered = computed(() => {
  if (!searchTerm.value?.trim()) return agents.value
  const k = searchTerm.value.trim().toLowerCase()
  return agents.value.filter((a) => {
    const hay = [String(a.id), a.name, a.description, a.modelKey, a.ownerUsername]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return hay.includes(k)
  })
})

const doUnpublish = async (id) => {
  if (!window.confirm('确定将该智能体从广场下架？（不会删除数据）')) return
  actingId.value = id
  errorMessage.value = ''
  try {
    await AdminAgentAPI.unpublish(id)
    await load()
  } catch (e) {
    errorMessage.value = '下架失败'
  } finally {
    actingId.value = null
  }
}

const doSoftDelete = async (id) => {
  if (!window.confirm('确定删除？用户与广场将不再展示，可在回收站恢复。')) return
  actingId.value = id
  errorMessage.value = ''
  try {
    await AdminAgentAPI.softDelete(id)
    await load()
  } catch (e) {
    errorMessage.value = '删除失败'
  } finally {
    actingId.value = null
  }
}

const doRestore = async (id) => {
  actingId.value = id
  errorMessage.value = ''
  try {
    await AdminAgentAPI.restore(id)
    await load()
  } catch (e) {
    errorMessage.value = '恢复失败'
  } finally {
    actingId.value = null
  }
}

onMounted(load)
</script>

<template>
  <div class="page">
    <header class="page__header">
      <div>
        <h1>管理员 · 智能体</h1>
        <p>查看全站智能体；可下架广场展示或删除（回收站可恢复）</p>
      </div>
      <div class="page__header-actions">
        <div class="user-bar">
          <img v-if="authState.user?.avatar" :src="authState.user.avatar" alt="" class="user-bar__avatar" />
          <span class="user-bar__name">{{ displayName }}</span>
          <RouterLink class="nav-action-btn" :to="{ name: 'agent-home' }">我的智能体</RouterLink>
          <RouterLink class="nav-action-btn" :to="{ name: 'profile-home' }">编辑资料</RouterLink>
          <button type="button" class="nav-action-btn nav-action-btn--danger" @click="logout">
            退出
          </button>
        </div>
      </div>
    </header>

    <section class="page__content">
      <div class="tabs">
        <button
          type="button"
          class="tab"
          :class="{ 'tab--active': tab === 'all' }"
          @click="switchTab('all')"
        >
          全部智能体
        </button>
        <button
          type="button"
          class="tab"
          :class="{ 'tab--active': tab === 'recycle' }"
          @click="switchTab('recycle')"
        >
          回收站
        </button>
      </div>

      <div class="toolbar">
        <input
          v-model.trim="searchTerm"
          class="search-input"
          type="search"
          placeholder="搜索 ID / 名称 / 描述 / 模型 / 创建者..."
        />
      </div>

      <div v-if="errorMessage" class="state state--error">{{ errorMessage }}</div>
      <div v-else-if="isLoading" class="state">加载中...</div>
      <div v-else-if="filtered.length === 0" class="state">
        {{ tab === 'recycle' ? '回收站为空' : '暂无数据' }}
      </div>
      <div v-else class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>名称</th>
              <th>创建者</th>
              <th>广场</th>
              <th>模型</th>
              <th>更新</th>
              <th v-if="tab === 'recycle'">删除时间</th>
              <th class="col-actions">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="a in filtered" :key="a.id">
              <td>{{ a.id }}</td>
              <td class="cell-name">{{ a.name || `智能体 #${a.id}` }}</td>
              <td>{{ a.ownerUsername || '—' }}</td>
              <td>
                <span v-if="a.isPublic" class="badge badge--ok">公开</span>
                <span v-else class="badge">未公开</span>
              </td>
              <td class="cell-mono">{{ a.modelKey || '—' }}</td>
              <td class="cell-time">{{ formatTime(a.updatedAt) }}</td>
              <td v-if="tab === 'recycle'" class="cell-time">{{ formatTime(a.deletedAt) }}</td>
              <td class="col-actions">
                <template v-if="tab === 'all'">
                  <button
                    v-if="a.isPublic"
                    type="button"
                    class="mini-btn"
                    :disabled="actingId === a.id"
                    @click="doUnpublish(a.id)"
                  >
                    下架
                  </button>
                  <button
                    type="button"
                    class="mini-btn mini-btn--danger"
                    :disabled="actingId === a.id"
                    @click="doSoftDelete(a.id)"
                  >
                    删除
                  </button>
                </template>
                <template v-else>
                  <button
                    type="button"
                    class="mini-btn mini-btn--primary"
                    :disabled="actingId === a.id"
                    @click="doRestore(a.id)"
                  >
                    恢复
                  </button>
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 2rem;
  background: var(--app-bg);
  color: var(--color-text);
}

.page__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
  gap: 1rem;
  flex-wrap: wrap;
}

.page__header h1 {
  margin: 0;
  font-size: 1.8rem;
}

.page__header p {
  margin: 0.2rem 0 0;
  color: var(--color-text-muted);
}

.page__header-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.75rem;
}

.user-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.user-bar__avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid var(--border-color);
}

.page__content {
  flex: 1;
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
}

.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab {
  padding: 0.5rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--panel-bg-muted);
  color: var(--color-text);
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.9rem;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.tab--active {
  border-color: rgba(var(--accent-rgb), 0.55);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
}

.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1rem;
}

.search-input {
  width: min(360px, 100%);
  border-radius: 999px;
  border: 1px solid var(--border-color);
  padding: 0.6rem 1rem;
  font-size: 0.95rem;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

.search-input:focus {
  outline: none;
  border-color: rgba(var(--accent-rgb), 0.65);
  box-shadow: 0 0 0 3px rgba(var(--accent-rgb), 0.18);
}

.state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted);
}

.state--error {
  color: #b91c1c;
}

.table-wrap {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.data-table th,
.data-table td {
  padding: 0.65rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.data-table th {
  color: var(--color-text-muted);
  font-weight: 600;
  white-space: nowrap;
}

.cell-name {
  max-width: 12rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-mono {
  font-family: ui-monospace, monospace;
  font-size: 0.82rem;
  max-width: 10rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cell-time {
  white-space: nowrap;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.col-actions {
  white-space: nowrap;
}

.badge {
  display: inline-block;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  font-size: 0.75rem;
  background: rgba(15, 23, 42, 0.06);
  color: var(--color-text-muted);
}

.badge--ok {
  background: rgba(34, 197, 94, 0.18);
  color: rgba(15, 23, 42, 0.8);
}

.mini-btn {
  margin-right: 0.35rem;
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: var(--panel-bg-muted);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  color: var(--color-text);
  transition: border-color 0.15s ease;
}

.mini-btn:hover:not(:disabled) {
  border-color: rgba(var(--accent-rgb), 0.45);
}

.mini-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.mini-btn--danger {
  border-color: rgba(239, 68, 68, 0.4);
  color: #b91c1c;
  background: rgba(254, 226, 226, 0.45);
}

.mini-btn--primary {
  background: var(--accent-color);
  color: #fff;
  border: none;
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.12);
}
</style>
