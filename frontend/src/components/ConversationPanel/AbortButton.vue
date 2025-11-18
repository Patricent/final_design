<script setup>
defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <button class="abort" :disabled="disabled">
    <span class="dot" />
    中止对话
  </button>
</template>

<style scoped>
.abort {
  border: none;
  border-radius: 999px;
  padding: 0.5rem 0.9rem;
  background: rgba(255, 77, 79, 0.15);
  color: #ff4d4f;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.abort:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  display: inline-block;
}
</style>


