<script setup>
import { nextTick, watch, ref } from 'vue'
import MarkdownViewer from './MarkdownViewer.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
})

const containerRef = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (!containerRef.value) return
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  })
}

watch(
  () => props.messages.length,
  () => scrollToBottom(),
)

watch(
  () => props.isStreaming,
  () => scrollToBottom(),
)
</script>

<template>
  <div ref="containerRef" class="chat-stream">
    <template v-if="messages.length">
      <article
        v-for="(message, index) in messages"
        :key="index"
        class="bubble"
        :class="message.role"
      >
        <span class="role">{{ message.role === 'user' ? '用户' : '智能体' }}</span>
        <MarkdownViewer :content="message.content" />
      </article>
    </template>
    <div v-else class="placeholder">
      <p>还没有消息，先在左侧配置智能体，然后开始对话吧。</p>
      <p>支持多轮上下文、中止对话、Markdown 代码块等特性。</p>
    </div>
  </div>
</template>

<style scoped>
.chat-stream {
  flex: 1;
  overflow-y: auto;
  border-radius: 12px;
  padding: 1rem;
  background: var(--panel-bg-muted);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.bubble {
  padding: 0.85rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid transparent;
}

.bubble.user {
  border-color: rgba(64, 156, 255, 0.35);
}

.bubble.assistant {
  border-color: rgba(106, 93, 255, 0.35);
  background: rgba(106, 93, 255, 0.08);
}

.role {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.placeholder {
  text-align: center;
  color: var(--color-text-muted);
  margin-top: 2rem;
  line-height: 1.6;
}
</style>


