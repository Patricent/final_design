import { reactive } from 'vue'
import { AgentAPI } from '../services/api'
import { openConversationStream } from '../services/streaming'

const createEmptyAgent = () => ({
  id: null,
  name: '',
  description: '',
  modelKey: '',
  temperature: 0.7,
})

const state = reactive({
  isLoading: false,
  isStreaming: false,
  isBackendReachable: false,
  agentConfig: createEmptyAgent(),
  models: [],
  messages: [], // 使用reactive数组，确保响应式
  conversationId: null,
  error: null,
})

let closeStream = null

async function fetchModels() {
  try {
    const data = await AgentAPI.listModels()
    state.models = data
    if (!state.agentConfig.modelKey && data.length > 0) {
      state.agentConfig.modelKey = data[0].key
    }
    state.isBackendReachable = true
  } catch (error) {
    console.warn('模型列表获取失败，等待后端可用', error)
    state.isBackendReachable = false
  }
}

function assignAgentConfig(payload = {}) {
  Object.assign(state.agentConfig, createEmptyAgent(), payload)
  if (!state.agentConfig.modelKey && state.models.length > 0) {
    state.agentConfig.modelKey = state.models[0].key
  }
}

function resetConversationState() {
  state.messages = []
  state.conversationId = null
  resetStreamState()
}

async function ensureConversation(agentId) {
  if (state.conversationId) {
    return state.conversationId
  }
  const payload = {
    agent_id: agentId ?? state.agentConfig.id,
  }
  const conversation = await AgentAPI.startConversation(payload)
  state.conversationId = conversation.id
  state.messages = conversation.history ?? []
  return state.conversationId
}

function appendAssistantMessageChunk(chunk) {
  // 只过滤明确的结束标记和null/undefined，保留所有其他内容（包括空白字符）
  if (chunk === null || chunk === undefined || chunk === '[END]') return
  
  const lastMessage = state.messages.at(-1)
  if (!lastMessage || lastMessage.role !== 'assistant') {
    // 创建新的消息对象，确保响应式
    state.messages.push({
      role: 'assistant',
      content: chunk || '', // 确保是字符串
    })
    return
  }
  // 使用字符串拼接确保内容完整累积
  // 直接修改对象的content属性，Vue的响应式系统会自动检测
  // 使用nextTick确保更新在下一个tick执行，避免频繁更新
  const currentContent = lastMessage.content || ''
  lastMessage.content = currentContent + (chunk || '')
}

function resetStreamState() {
  if (closeStream) {
    closeStream()
    closeStream = null
  }
  state.isStreaming = false
}

export function useChatStore() {
  const bootstrap = async () => {
    await fetchModels()
  }

  const upsertAgent = async (payload) => {
    state.isLoading = true
    try {
      const agent = await AgentAPI.upsertAgent(payload)
      assignAgentConfig(agent)
      resetConversationState()
      return agent
    } catch (error) {
      state.error = error?.response?.data ?? error.message
      console.error('保存智能体失败', error)
      throw error
    } finally {
      state.isLoading = false
    }
  }

  const loadAgent = async (agentId) => {
    if (!agentId) {
      prepareNewAgent()
      return
    }
    state.isLoading = true
    try {
      const agent = await AgentAPI.getAgent(agentId)
      assignAgentConfig(agent)
      resetConversationState()
    } catch (error) {
      state.error = error?.response?.data ?? error.message
      console.error('加载智能体失败', error)
      throw error
    } finally {
      state.isLoading = false
    }
  }

  const prepareNewAgent = () => {
    assignAgentConfig(createEmptyAgent())
    resetConversationState()
  }

  const sendMessage = async (content) => {
    if (!content?.trim()) {
      return
    }
    if (!state.agentConfig.id) {
      await upsertAgent(state.agentConfig)
    }
    const conversationId = await ensureConversation(state.agentConfig.id)

    state.messages.push({
      role: 'user',
      content,
    })

    state.isStreaming = true
    try {
      const response = await AgentAPI.sendMessage({
        conversationId,
        content,
      })
      const streamId = response.stream_id ?? conversationId
      closeStream = openConversationStream(streamId, {
        onChunk: appendAssistantMessageChunk,
        onError: (error) => {
          console.error('流式响应错误', error)
          // 检查是否是超时错误
          const errorMessage = error?.message || error?.toString() || ''
          if (errorMessage.includes('timeout') || errorMessage.includes('No activity')) {
            state.error = '请求超时，可能是模型响应时间较长，请稍后重试或检查网络连接'
          } else {
            state.error = '流式响应异常，请稍后重试'
          }
          resetStreamState()
        },
        onComplete: () => {
          resetStreamState()
        },
      })
    } catch (error) {
      state.error = error?.response?.data ?? error.message
      console.error('发送消息失败', error)
      resetStreamState()
      throw error
    }
  }

  const abortActiveStream = async () => {
    if (!state.conversationId) return
    try {
      await AgentAPI.abortConversation(state.conversationId)
    } catch (error) {
      console.warn('中止请求失败', error)
    } finally {
      resetStreamState()
    }
  }

  return {
    state,
    bootstrap,
    upsertAgent,
    loadAgent,
    prepareNewAgent,
    sendMessage,
    abortActiveStream,
  }
}


