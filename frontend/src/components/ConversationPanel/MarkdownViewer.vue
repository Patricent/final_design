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

// computed会自动响应props.content的变化，每次content变化都会重新计算
// 在流式更新时，传递isStreaming标志以修复不完整的Markdown语法
const compiled = computed(() => {
  return renderMarkdown(props.content || '', props.isStreaming)
})
</script>

<template>
  <div class="markdown" v-html="compiled" />
</template>

<style scoped>
.markdown {
  line-height: 1.6;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.markdown :deep(h1),
.markdown :deep(h2),
.markdown :deep(h3),
.markdown :deep(h4),
.markdown :deep(h5),
.markdown :deep(h6) {
  margin: 1rem 0 0.5rem;
  font-weight: 600;
  line-height: 1.4;
}

.markdown :deep(h1) {
  font-size: 1.5rem;
  border-bottom: 2px solid var(--border-color);
  padding-bottom: 0.5rem;
}

.markdown :deep(h2) {
  font-size: 1.3rem;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.4rem;
}

.markdown :deep(h3) {
  font-size: 1.15rem;
}

.markdown :deep(h4) {
  font-size: 1.05rem;
}

.markdown :deep(p) {
  margin: 0.5rem 0;
  line-height: 1.7;
}

.markdown :deep(ul),
.markdown :deep(ol) {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.markdown :deep(li) {
  margin: 0.25rem 0;
  line-height: 1.6;
}

.markdown :deep(blockquote) {
  margin: 0.75rem 0;
  padding: 0.5rem 1rem;
  border-left: 4px solid rgba(106, 93, 255, 0.5);
  background: rgba(106, 93, 255, 0.05);
  border-radius: 4px;
}

.markdown :deep(pre) {
  background: #0f172a;
  padding: 1rem;
  border-radius: 10px;
  overflow-x: auto;
  margin: 0.75rem 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.markdown :deep(pre code) {
  background: transparent;
  padding: 0;
  border-radius: 0;
  font-size: 0.9rem;
}

.markdown :deep(code) {
  font-family: 'Fira Code', 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
  background: rgba(106, 93, 255, 0.15);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.9em;
}

.markdown :deep(strong) {
  font-weight: 600;
  color: var(--color-text);
}

.markdown :deep(em) {
  font-style: italic;
}

.markdown :deep(a) {
  color: #409cff;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.markdown :deep(a:hover) {
  color: #6a5dff;
}

.markdown :deep(hr) {
  margin: 1rem 0;
  border: none;
  border-top: 1px solid var(--border-color);
}

.markdown :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0;
}

.markdown :deep(th),
.markdown :deep(td) {
  border: 1px solid var(--border-color);
  padding: 0.5rem;
  text-align: left;
}

.markdown :deep(th) {
  background: rgba(106, 93, 255, 0.1);
  font-weight: 600;
}
</style>


