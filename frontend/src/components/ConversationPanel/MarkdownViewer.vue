<script setup>
import { computed } from 'vue'

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
  isStreaming: {
    type: Boolean,
    default: false,
  },
})

// 转义HTML特殊字符，但保留换行符
function escapeHtml(text) {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
    .replace(/\n/g, '<br>')
}

// 使用computed确保响应式更新
const escapedContent = computed(() => escapeHtml(props.content || ''))
</script>

<template>
  <div class="text-content" v-html="escapedContent" />
</template>

<style scoped>
.text-content {
  line-height: 1.8;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word; /* 长单词自动换行 */
  max-width: 100%; /* 确保内容不会溢出 */
  white-space: pre-wrap; /* 保留换行符和空格，但允许自动换行 */
  color: inherit; /* 继承父元素的颜色 */
}
</style>


