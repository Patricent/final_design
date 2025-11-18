<script setup>
const props = defineProps({
  options: {
    type: Array,
    default: () => [],
  },
  modelKey: {
    type: String,
    default: '',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelKey'])

const handleChange = (event) => {
  emit('update:modelKey', event.target.value)
}
</script>

<template>
  <label class="field">
    <span>选择模型</span>
    <select :value="props.modelKey" :disabled="disabled" @change="handleChange">
      <option v-if="!options.length" disabled>暂无模型</option>
      <option v-for="model in options" :key="model.key" :value="model.key">
        {{ model.label }} · {{ model.provider }}
      </option>
    </select>
    <small v-if="options.length" class="desc">
      {{ options.find((item) => item.key === props.modelKey)?.description ?? '可自定义模型描述' }}
    </small>
  </label>
</template>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field span {
  font-size: 0.95rem;
}

.desc {
  color: var(--color-text-muted);
}
</style>


