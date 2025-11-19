import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
})

const normalizeAgent = (agent = {}) => ({
  id: agent.id ?? null,
  name: agent.name ?? '',
  description: agent.description ?? '',
  modelKey: agent.model_key ?? agent.modelKey ?? '',
  temperature: agent.temperature ?? 0.7,
})

export const AgentAPI = {
  async listModels() {
    const { data } = await apiClient.get('/agents/models/')
    return data ?? []
  },
  async listAgents() {
    const { data } = await apiClient.get('/agents/list/')
    return (data ?? []).map(normalizeAgent)
  },
  async getAgent(agentId) {
    const { data } = await apiClient.get(`/agents/${agentId}/`)
    return normalizeAgent(data)
  },
  async upsertAgent(payload) {
    const { data } = await apiClient.post('/agents/', payload)
    return normalizeAgent(data)
  },
  async deleteAgent(agentId) {
    await apiClient.delete(`/agents/${agentId}/`)
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


