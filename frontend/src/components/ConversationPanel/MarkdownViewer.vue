<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '../../utils/markdown'

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

const rendered = computed(() => renderMarkdown(props.content || '', props.isStreaming))
</script>

<template>
  <div class="markdown-content text-content" v-html="rendered" />
</template>

<style scoped>
/* 对齐参考 frontend/Chat.vue 中 .markdown-content，按当前浅色气泡适配 */
.text-content {
  line-height: 1.6;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-word;
  max-width: 100%;
  color: inherit;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  margin: 10px 0 8px 0;
  font-weight: 600;
  color: inherit;
}

.markdown-content :deep(h1) {
  font-size: 1.4rem;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 5px;
}

.markdown-content :deep(h2) {
  font-size: 1.2rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 3px;
}

.markdown-content :deep(h3) {
  font-size: 1.1rem;
}

.markdown-content :deep(strong) {
  font-weight: 700;
  color: inherit;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: inherit;
}

.markdown-content :deep(.inline-code),
.markdown-content :deep(code.inline-code) {
  background: rgba(15, 23, 42, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', ui-monospace, monospace;
  font-size: 0.9em;
  color: inherit;
}

.markdown-content :deep(.code-block) {
  background: rgba(15, 23, 42, 0.06);
  padding: 15px;
  border-radius: 8px;
  margin: 10px 0;
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-left: 4px solid rgba(var(--accent-rgb), 0.45);
}

.markdown-content :deep(.code-block code) {
  background: none;
  padding: 0;
  color: inherit;
  font-family: 'Courier New', ui-monospace, monospace;
  font-size: 0.9em;
  line-height: 1.4;
}

.markdown-content :deep(ul) {
  margin: 10px 0;
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 5px 0;
  color: inherit;
}

.markdown-content :deep(a) {
  color: inherit;
  text-decoration: underline;
  opacity: 0.95;
}

.markdown-content :deep(a:hover) {
  opacity: 1;
}
</style>
