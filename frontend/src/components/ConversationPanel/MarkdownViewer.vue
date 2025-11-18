<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '../../utils/markdown'

const props = defineProps({
  content: {
    type: String,
    default: '',
  },
})

const compiled = computed(() => renderMarkdown(props.content))
</script>

<template>
  <div class="markdown" v-html="compiled" />
</template>

<style scoped>
.markdown :deep(pre) {
  background: #0f172a;
  padding: 0.75rem;
  border-radius: 10px;
  overflow-x: auto;
}

.markdown :deep(code) {
  font-family: 'Fira Code', 'JetBrains Mono', Consolas, monospace;
}

.markdown :deep(p) {
  margin: 0.35rem 0;
}

.markdown :deep(ul),
.markdown :deep(ol) {
  margin: 0.35rem 1.25rem;
}
</style>


