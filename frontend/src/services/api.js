import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
})

export const AgentAPI = {
  async listModels() {
    const { data } = await apiClient.get('/agents/models/')
    return data ?? []
  },
  async upsertAgent(payload) {
    const { data } = await apiClient.post('/agents/', payload)
    return data
  },
  async startConversation(payload) {
    const { data } = await apiClient.post('/conversations/', payload)
    return data
  },
  async sendMessage({ conversationId, content }) {
    const { data } = await apiClient.post(`/conversations/${conversationId}/messages/`, {
      content,
    })
    return data
  },
  async abortConversation(conversationId) {
    const { data } = await apiClient.post(`/conversations/${conversationId}/abort/`)
    return data
  },
}


