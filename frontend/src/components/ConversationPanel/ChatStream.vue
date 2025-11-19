<script setup>
import { nextTick, watch, ref, computed } from 'vue'
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

// 计算所有消息内容的字符串，用于监听内容变化
const messagesContent = computed(() => {
  return props.messages.map((m) => m.content).join('|')
})

const scrollToBottom = () => {
  nextTick(() => {
    if (!containerRef.value) return
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  })
}

// 监听消息数组长度变化
watch(
  () => props.messages.length,
  () => scrollToBottom(),
)

// 监听消息内容变化（流式更新时）
watch(
  messagesContent,
  () => {
    // 流式更新时始终滚动到底部
    scrollToBottom()
  },
  { flush: 'post', immediate: false } // 在DOM更新后执行
)

// 额外监听最后一条消息的内容变化（流式更新时）
watch(
  () => {
    const lastMsg = props.messages[props.messages.length - 1]
    return lastMsg?.content || ''
  },
  () => {
    if (props.isStreaming) {
      scrollToBottom()
    }
  },
  { flush: 'post' }
)

// 监听流式状态变化
watch(
  () => props.isStreaming,
  () => scrollToBottom(),
)
</script>

<template>
  <div ref="containerRef" class="chat-stream">
    <template v-if="messages.length">
      <div
        v-for="(message, index) in messages"
        :key="index"
        class="message-wrapper"
        :class="message.role"
      >
        <div class="message-bubble" :class="message.role">
          <MarkdownViewer 
            :content="message.content || ''" 
            :is-streaming="isStreaming && index === messages.length - 1 && message.role === 'assistant'"
          />
        </div>
      </div>
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
  gap: 0.5rem;
}

.message-wrapper {
  display: flex;
  width: 100%;
  margin-bottom: 0.25rem;
}

/* 只在消息首次出现时播放动画，避免流式更新时闪动 */
.message-wrapper:first-child {
  animation: fadeIn 0.2s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 用户消息：右对齐 */
.message-wrapper.user {
  justify-content: flex-end;
}

/* 智能体消息：左对齐 */
.message-wrapper.assistant {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 75%;
  min-width: 60px;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  word-wrap: break-word;
  overflow-wrap: break-word;
  position: relative;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.message-bubble:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

/* 用户消息气泡：右侧，蓝色系 */
.message-bubble.user {
  background: linear-gradient(135deg, #409cff, #6a5dff);
  color: #ffffff;
  border-bottom-right-radius: 4px; /* 右下角小圆角，像微信/iMessage */
}

/* 确保用户消息中的文字是白色 */
.message-bubble.user * {
  color: #ffffff !important;
}

/* 智能体消息气泡：左侧，灰色系 */
.message-bubble.assistant {
  background: rgba(255, 255, 255, 0.15);
  color: var(--color-text);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-bottom-left-radius: 4px; /* 左下角小圆角 */
}

/* 在暗色模式下优化智能体消息 */
@media (prefers-color-scheme: dark) {
  .message-bubble.assistant {
    background: rgba(40, 40, 40, 0.9);
    border-color: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.9);
  }
}

/* 在亮色模式下优化智能体消息 */
@media (prefers-color-scheme: light) {
  .message-bubble.assistant {
    background: rgba(240, 240, 240, 0.9);
    border-color: rgba(0, 0, 0, 0.1);
    color: rgba(0, 0, 0, 0.85);
  }
}

.placeholder {
  text-align: center;
  color: var(--color-text-muted);
  margin-top: 2rem;
  line-height: 1.6;
}
</style>


