import { reactive } from 'vue'
import { AgentAPI } from '../services/api'
import { openConversationStream } from '../services/streaming'

const state = reactive({
  isLoading: false,
  isStreaming: false,
  isBackendReachable: false,
  agentConfig: {
    id: null,
    name: '',
    description: '',
    modelKey: '',
    temperature: 0.7,
  },
  models: [],
  messages: [],
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
  const lastMessage = state.messages.at(-1)
  if (!lastMessage || lastMessage.role !== 'assistant') {
    state.messages.push({
      role: 'assistant',
      content: chunk,
    })
    return
  }
  lastMessage.content += chunk
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
      state.agentConfig = {
        ...state.agentConfig,
        ...payload,
        id: agent.id ?? state.agentConfig.id,
      }
      state.messages = []
      state.conversationId = null
    } catch (error) {
      state.error = error?.response?.data ?? error.message
      console.error('保存智能体失败', error)
      throw error
    } finally {
      state.isLoading = false
    }
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
          state.error = '流式响应异常，请稍后重试'
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
    sendMessage,
    abortActiveStream,
  }
}


