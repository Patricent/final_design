import axios from 'axios'
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
})

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (!original || error.response?.status !== 401 || original._retry) {
      return Promise.reject(error)
    }
    original._retry = true
    const refresh = getRefreshToken()
    if (!refresh) {
      clearTokens()
      return Promise.reject(error)
    }
    try {
      const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, { refresh })
      setTokens(data.access, refresh)
      original.headers.Authorization = `Bearer ${data.access}`
      return apiClient(original)
    } catch {
      clearTokens()
      return Promise.reject(error)
    }
  },
)

const normalizeAgent = (agent = {}) => ({
  id: agent.id ?? null,
  name: agent.name ?? '',
  description: agent.description ?? '',
  modelKey: agent.model_key ?? agent.modelKey ?? '',
  modelLabel: agent.model_label ?? agent.modelLabel,
  temperature: agent.temperature ?? 0.7,
  isPublic: Boolean(agent.is_public ?? agent.isPublic),
  ownerId: agent.owner_id ?? agent.ownerId ?? null,
  ownerUsername: agent.owner_username ?? agent.ownerUsername ?? '',
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
  async listSquareAgents() {
    const { data } = await apiClient.get('/agents/square/')
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
