<script setup>
import { reactive, watch } from 'vue'
import ModelSelector from './ModelSelector.vue'

const props = defineProps({
  models: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  agent: {
    type: Object,
    default: () => ({
      name: '',
      description: '',
      modelKey: '',
      temperature: 0.7,
    }),
  },
})

const emit = defineEmits(['submit'])

const form = reactive({
  name: '',
  description: '',
  modelKey: '',
  temperature: 0.7,
})

watch(
  () => props.agent,
  (next) => {
    Object.assign(form, next ?? {})
  },
  { immediate: true, deep: true },
)

watch(
  () => props.models,
  (models) => {
    if (!form.modelKey && models?.length) {
      form.modelKey = models[0].key
    }
  },
  { immediate: true },
)

const handleSubmit = () => {
  emit('submit', { ...form })
}
</script>

<template>
  <div class="agent-form">
    <h2>智能体设定</h2>
    <p class="hint">配置角色、描述与模型，保存后即可开启会话</p>

    <label class="field">
      <span>角色名称</span>
      <input v-model="form.name" placeholder="如：财务顾问、AI 助教" />
    </label>

    <label class="field">
      <span>角色描述 / 指令</span>
      <textarea
        v-model="form.description"
        rows="4"
        placeholder="描述智能体的背景、语气、行为规范……"
      />
    </label>

    <ModelSelector v-model:model-key="form.modelKey" :options="models" :disabled="loading" />

    <label class="field slider">
      <div>
        <span>温度（创造力）</span>
        <small>{{ form.temperature.toFixed(1) }}</small>
      </div>
      <input
        v-model.number="form.temperature"
        type="range"
        min="0"
        max="1"
        step="0.1"
      />
    </label>

    <button class="primary" :disabled="loading" @click="handleSubmit">
      {{ loading ? '保存中...' : '保存智能体' }}
    </button>
  </div>
</template>

<style scoped>
.agent-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.hint {
  margin: -0.5rem 0 0;
  color: var(--color-text-muted);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field span {
  font-size: 0.95rem;
  color: var(--color-text);
}

input,
textarea,
select {
  border-radius: 10px;
  border: 1px solid var(--border-color);
  padding: 0.65rem 0.85rem;
  font-size: 0.95rem;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

textarea {
  resize: vertical;
}

.slider {
  gap: 0.15rem;
}

.slider div {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

button.primary {
  border: none;
  background: linear-gradient(135deg, #409cff, #6a5dff);
  color: white;
  border-radius: 12px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  transition: opacity 0.2s ease;
}

button.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>


