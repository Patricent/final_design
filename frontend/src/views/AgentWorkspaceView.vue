<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import AgentForm from '../components/AgentForm/AgentForm.vue'
import ConversationPanel from '../components/ConversationPanel/ConversationPanel.vue'
import { useChatStore } from '../store/chatStore'

const props = defineProps({
  id: {
    type: Number,
    default: null,
  },
  isNew: {
    type: Boolean,
    default: false,
  },
})

const router = useRouter()
const chatStore = useChatStore()

const isNewAgent = computed(() => props.isNew || !props.id)

const bootstrapWorkspace = async () => {
  await chatStore.bootstrap()
  if (isNewAgent.value) {
    chatStore.prepareNewAgent()
    return
  }
  if (props.id) {
    await chatStore.loadAgent(props.id)
  }
}

const handleAgentSubmit = async (payload) => {
  const agent = await chatStore.upsertAgent(payload)
  if (agent?.id) {
    router.replace({ name: 'agent-workspace', params: { id: agent.id } })
  }
}

const handleSendMessage = async (content) => {
  await chatStore.sendMessage(content)
}

const handleAbort = () => {
  chatStore.abortActiveStream()
}

const handleBack = () => {
  router.push({ name: 'agent-home' })
}

onMounted(bootstrapWorkspace)

watch(
  () => props.id,
  async (newId, oldId) => {
    if (newId && newId !== oldId) {
      await chatStore.loadAgent(newId)
    }
  },
)

watch(
  () => props.isNew,
  (flag) => {
    if (flag) {
      chatStore.prepareNewAgent()
    }
  },
)
</script>

<template>
  <div class="workspace">
    <header class="workspace__header">
      <div>
        <button class="ghost-btn" type="button" @click="handleBack">
          ← 返回智能体广场
        </button>
        <h1>{{ chatStore.state.agentConfig.name || (isNewAgent ? '新的智能体' : `智能体 #${id}`) }}</h1>
        <p>设定角色、选择模型，立即开启对话</p>
      </div>
      <div class="status">
        <span class="dot" :class="{ online: chatStore.state.isBackendReachable }" />
        <span>{{ chatStore.state.isBackendReachable ? '后端在线' : '等待后端' }}</span>
      </div>
    </header>

    <main class="workspace__body">
      <section class="panel agent-panel">
        <AgentForm
          :models="chatStore.state.models"
          :loading="chatStore.state.isLoading"
          :agent="chatStore.state.agentConfig"
          @submit="handleAgentSubmit"
        />
      </section>

      <section class="panel conversation-panel">
        <ConversationPanel
          :messages="chatStore.state.messages"
          :is-streaming="chatStore.state.isStreaming"
          :input-disabled="!chatStore.state.agentConfig.modelKey || chatStore.state.isStreaming"
          @send="handleSendMessage"
          @abort="handleAbort"
        />
      </section>
    </main>

    <transition name="fade">
      <div v-if="chatStore.state.error" class="error-banner">
        <span>{{ chatStore.state.error }}</span>
        <button type="button" @click="chatStore.state.error = null">关闭</button>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.workspace {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
  background: var(--app-bg);
  color: var(--color-text);
}

.workspace__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
  gap: 1.25rem;
}

.workspace__header h1 {
  margin: 0.5rem 0 0;
  font-size: 1.5rem;
}

.workspace__header p {
  margin: 0.25rem 0 0;
  color: var(--color-text-muted);
}

.ghost-btn {
  border: none;
  background: transparent;
  padding: 0;
  margin: 0;
  color: #a5b4fc;
  font-size: 0.95rem;
  cursor: pointer;
}

.status {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.95rem;
  color: var(--color-text-muted);
}

.status .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #b1b1b1;
  display: inline-block;
}

.status .dot.online {
  background: #3de57f;
  box-shadow: 0 0 6px rgba(61, 229, 127, 0.6);
}

.workspace__body {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 1.5rem;
}

.panel {
  background: var(--panel-bg);
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: var(--panel-shadow);
  min-height: 0;
}

.conversation-panel {
  display: flex;
  flex-direction: column;
}

.error-banner {
  position: fixed;
  left: 50%;
  bottom: 24px;
  transform: translateX(-50%);
  padding: 0.75rem 1rem;
  border-radius: 999px;
  background: rgba(239, 68, 68, 0.92);
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
  font-size: 0.95rem;
}

.error-banner button {
  border: none;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  border-radius: 999px;
  padding: 0.2rem 0.6rem;
  cursor: pointer;
  font-size: 0.85rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 1024px) {
  .workspace__body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .workspace {
    padding: 1rem;
  }
}
</style>


