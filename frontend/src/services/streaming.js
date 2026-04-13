import { EventSourcePolyfill } from 'event-source-polyfill'
import { getAccessToken } from '../store/authStore'

const STREAM_BASE_URL =
  import.meta.env.VITE_STREAM_BASE_URL ?? `${import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'}`

export function openConversationStream(identifier, { onChunk, onError, onComplete }) {
  const token = getAccessToken()
  let url = `${STREAM_BASE_URL}/conversations/${identifier}/stream/`
  if (token) {
    const sep = url.includes('?') ? '&' : '?'
    url = `${url}${sep}token=${encodeURIComponent(token)}`
  }

  const source = new EventSourcePolyfill(url, {
    withCredentials: false,
    heartbeatTimeout: 120000,
    connectionTimeout: 30000,
  })

  source.onmessage = (event) => {
    if (event.data === '[END]') {
      source.close()
      onComplete?.()
      return
    }
    onChunk?.(event.data ?? '')
  }

  source.onerror = (error) => {
    source.close()
    onError?.(error)
  }

  return () => source.close()
}
