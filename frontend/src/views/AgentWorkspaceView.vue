<script setup>
import { computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AgentForm from '../components/AgentForm/AgentForm.vue'
import ConversationPanel from '../components/ConversationPanel/ConversationPanel.vue'
import ImageGenPanel from '../components/ImageGenPanel/ImageGenPanel.vue'
import { useChatStore } from '../store/chatStore'
import { authState } from '../store/authStore'

const props = defineProps({
  id: {
    type: Number,
    default: null,
  },
  isNew: {
    type: Boolean,
    default: false,
  },
  showEditor: {
    type: Boolean,
    default: false,
  },
  agentKind: {
    type: String,
    default: 'chat',
  },
})

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

const isNewAgent = computed(() => props.isNew || !props.id)

const isOwner = computed(() => {
  if (isNewAgent.value) return true
  const oid = chatStore.state.agentConfig.ownerId
  if (oid == null) return true
  return Number(authState.user?.id) === Number(oid)
})

const shouldShowEditor = computed(() => {
  if (!isOwner.value) return false
  return props.showEditor || props.isNew || !props.id
})

const isImageAgent = computed(() => chatStore.state.agentConfig.kind === 'image')

const shouldShowConversation = computed(() => {
  if (props.isNew || !props.id) return false
  if (props.showEditor) return false
  if (chatStore.state.agentConfig.kind === 'image') return false
  return true
})

const shouldShowImagePanel = computed(() => {
  if (props.isNew || !props.id || props.showEditor) return false
  return chatStore.state.agentConfig.kind === 'image'
})

const workspaceBodyClass = computed(() => {
  const dual =
    shouldShowEditor.value && (shouldShowConversation.value || shouldShowImagePanel.value)
  return { 'single-column': !dual }
})

const bootstrapWorkspace = async () => {
  await chatStore.bootstrap()
  if (isNewAgent.value) {
    chatStore.prepareNewAgent()
    if (props.agentKind === 'image') {
      Object.assign(chatStore.state.agentConfig, {
        kind: 'image',
        modelKey: 'high_aes_general_v30l_zt2i',
        name: '我的文生图',
        imageWidth: 1328,
        imageHeight: 1328,
      })
    }
    return
  }
  if (props.id) {
    await chatStore.loadAgent(props.id)
  }
}

const handleAgentSubmit = async (payload) => {
  const agent = await chatStore.upsertAgent({
    ...payload,
    id: chatStore.state.agentConfig.id,
  })
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
  if (route.query.from === 'square') {
    router.push({ name: 'agent-square' })
    return
  }
  router.push({ name: 'agent-home' })
}

const handleEnterEdit = () => {
  if (!props.id || !isOwner.value) return
  router.push({
    name: 'agent-workspace',
    params: { id: props.id },
    query: { ...route.query, edit: '1' },
  })
}

const handleViewConversation = () => {
  if (!props.id) return
  const q = { ...route.query }
  delete q.edit
  router.push({
    name: 'agent-workspace',
    params: { id: props.id },
    query: q,
  })
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
      if (props.agentKind === 'image') {
        Object.assign(chatStore.state.agentConfig, {
          kind: 'image',
          modelKey: 'high_aes_general_v30l_zt2i',
          name: '我的文生图',
          imageWidth: 1328,
          imageHeight: 1328,
        })
      }
    }
  },
)
</script>

<template>
  <div class="workspace">
    <header class="workspace__header">
      <div class="workspace__meta">
        <button class="ghost-btn" type="button" @click="handleBack">
          ← {{ route.query.from === 'square' ? '返回智能体广场' : '返回我的智能体' }}
        </button>
        <h1>{{ chatStore.state.agentConfig.name || (isNewAgent ? '新的智能体' : `智能体 #${id}`) }}</h1>
        <p v-if="!isOwner && !isNewAgent" class="workspace__banner">
          公开智能体 · 创建者：{{ chatStore.state.agentConfig.ownerUsername || '未知' }}（{{
            isImageAgent ? '仅可生成图片' : '仅可对话'
          }}，不可修改配置）
        </p>
        <p v-else-if="isImageAgent">配置名称与出图尺寸，保存后在右侧输入提示词生成图片</p>
        <p v-else>设定角色、选择模型，立即开启对话</p>
      </div>
      <div class="workspace__actions">
        <div class="status">
          <span class="dot" :class="{ online: chatStore.state.isBackendReachable }" />
          <span>{{ chatStore.state.isBackendReachable ? '后端在线' : '等待后端' }}</span>
        </div>
        <button
          v-if="!isNewAgent && isOwner && !shouldShowEditor"
          class="ghost-btn"
          type="button"
          @click="handleEnterEdit"
        >
          编辑智能体
        </button>
        <button
          v-else-if="!isNewAgent && isOwner && shouldShowEditor"
          class="ghost-btn"
          type="button"
          @click="handleViewConversation"
        >
          {{ isImageAgent ? '返回生成' : '返回对话' }}
        </button>
      </div>
    </header>

    <main class="workspace__body" :class="workspaceBodyClass">
      <section v-if="shouldShowEditor" class="panel agent-panel">
        <AgentForm
          :models="chatStore.state.models"
          :loading="chatStore.state.isLoading"
          :agent="chatStore.state.agentConfig"
          @submit="handleAgentSubmit"
        />
      </section>

      <section v-if="shouldShowConversation" class="panel conversation-panel">
        <ConversationPanel
          :messages="chatStore.state.messages"
          :is-streaming="chatStore.state.isStreaming"
          :input-disabled="!chatStore.state.agentConfig.modelKey || chatStore.state.isStreaming"
          @send="handleSendMessage"
          @abort="handleAbort"
        />
      </section>

      <section v-if="shouldShowImagePanel" class="panel image-gen-panel">
        <ImageGenPanel :agent-id="id" />
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
  height: 100vh;
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

.workspace__meta {
  max-width: 60%;
}

.workspace__header h1 {
  margin: 0.5rem 0 0;
  font-size: 1.5rem;
}

.workspace__header p {
  margin: 0.25rem 0 0;
  color: var(--color-text-muted);
}

.workspace__banner {
  margin: 0.35rem 0 0;
  color: var(--color-text-muted);
  font-size: 0.9rem;
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

.workspace__actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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
  flex: 1;
  min-height: 0;
}

.workspace__body.single-column {
  grid-template-columns: 1fr;
}

.panel {
  background: var(--panel-bg);
  border-radius: 16px;
  padding: 1.25rem;
  box-shadow: var(--panel-shadow);
  min-height: 0;
  height: 100%;
  overflow: hidden;
}

.conversation-panel,
.image-gen-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.image-gen-panel {
  overflow: auto;
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


