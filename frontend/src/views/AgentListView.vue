<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AgentAPI } from '../services/api'

const router = useRouter()
const agents = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const fetchAgents = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    agents.value = await AgentAPI.listAgents()
  } catch (error) {
    console.error('获取智能体失败', error)
    errorMessage.value = '获取智能体列表失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}

const handleCardClick = (agentId) => {
  router.push({ name: 'agent-workspace', params: { id: agentId } })
}

onMounted(fetchAgents)
</script>

<template>
  <div class="page">
    <header class="page__header">
      <div>
        <h1>智能体广场</h1>
        <p>查看并管理已经创建的智能体，点击即可继续对话</p>
      </div>
      <RouterLink class="primary-btn" :to="{ name: 'agent-create' }">
        + 创建新智能体
      </RouterLink>
    </header>

    <section class="page__content">
      <div v-if="errorMessage" class="state state--error">
        {{ errorMessage }}
      </div>
      <div v-else-if="isLoading" class="state">
        正在加载智能体...
      </div>
      <div v-else-if="agents.length === 0" class="state">
        还没有任何智能体，点击右上角按钮开始创建吧。
      </div>
      <div v-else class="agent-grid">
        <article
          v-for="agent in agents"
          :key="agent.id"
          class="agent-card"
          role="button"
          tabindex="0"
          @click="handleCardClick(agent.id)"
          @keypress.enter="handleCardClick(agent.id)"
        >
          <header class="agent-card__header">
            <h2>{{ agent.name || `智能体 #${agent.id}` }}</h2>
            <span class="agent-card__model">{{ agent.modelLabel || agent.modelKey }}</span>
          </header>
          <p class="agent-card__description">
            {{ agent.description || '暂无描述' }}
          </p>
          <footer class="agent-card__footer">
            <span>温度：{{ agent.temperature ?? '--' }}</span>
            <span class="agent-card__link">查看对话 →</span>
          </footer>
        </article>
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
}

.page__header h1 {
  margin: 0;
  font-size: 1.8rem;
}

.page__header p {
  margin: 0.2rem 0 0;
  color: var(--color-text-muted);
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(99, 102, 241, 0.35);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.primary-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 32px rgba(99, 102, 241, 0.45);
}

.page__content {
  flex: 1;
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
}

.state {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted);
}

.state--error {
  color: #ef4444;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}

.agent-card {
  padding: 1.25rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.agent-card:hover,
.agent-card:focus-visible {
  outline: none;
  border-color: rgba(99, 102, 241, 0.6);
  transform: translateY(-2px);
}

.agent-card__header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 0.5rem;
}

.agent-card__header h2 {
  margin: 0;
  font-size: 1.2rem;
}

.agent-card__model {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.15);
  color: #a5b4fc;
  font-size: 0.85rem;
}

.agent-card__description {
  margin: 0;
  min-height: 2.5rem;
  color: var(--color-text-muted);
}

.agent-card__footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.agent-card__link {
  color: #818cf8;
  font-weight: 600;
}

@media (max-width: 768px) {
  .page {
    padding: 1.5rem 1rem;
  }

  .page__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page__content {
    padding: 1rem;
  }
}
</style>


