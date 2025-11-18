import { EventSourcePolyfill } from 'event-source-polyfill'

const STREAM_BASE_URL =
  import.meta.env.VITE_STREAM_BASE_URL ?? `${import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api'}`

export function openConversationStream(identifier, { onChunk, onError, onComplete }) {
  const url = `${STREAM_BASE_URL}/conversations/${identifier}/stream/`
  const source = new EventSourcePolyfill(url, {
    withCredentials: false,
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


