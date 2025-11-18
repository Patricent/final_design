<script setup>
import { ref } from 'vue'
import ChatStream from './ChatStream.vue'
import AbortButton from './AbortButton.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
  inputDisabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['send', 'abort'])

const input = ref('')

const handleSend = () => {
  if (!input.value.trim()) return
  emit('send', input.value)
  input.value = ''
}

const handleKeydown = (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSend()
  }
}
</script>

<template>
  <div class="conversation-panel">
    <header>
      <div>
        <h2>对话面板</h2>
        <p>支持 Markdown 渲染与实时流式输出</p>
      </div>
      <AbortButton :disabled="!isStreaming" @click="emit('abort')" />
    </header>

    <ChatStream :messages="messages" :is-streaming="isStreaming" />

    <footer>
      <textarea
        v-model="input"
        :disabled="inputDisabled"
        rows="3"
        placeholder="输入问题，Shift + Enter 换行"
        @keydown="handleKeydown"
      />
      <button class="send" :disabled="inputDisabled || !input.trim()" @click="handleSend">
        发送
      </button>
    </footer>
  </div>
</template>

<style scoped>
.conversation-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

header h2 {
  margin: 0;
}

header p {
  margin: 0.15rem 0 0;
  color: var(--color-text-muted);
}

footer {
  display: flex;
  gap: 0.75rem;
}

textarea {
  flex: 1;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  padding: 0.85rem;
  resize: none;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

button.send {
  min-width: 96px;
  border-radius: 12px;
  border: none;
  background: var(--accent-color);
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

button.send:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>


