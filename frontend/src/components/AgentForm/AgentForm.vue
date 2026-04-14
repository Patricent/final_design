<script setup>
import { computed, reactive, watch } from 'vue'
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
      isPublic: false,
    }),
  },
})

const emit = defineEmits(['submit'])

const form = reactive({
  name: '',
  kind: 'chat',
  description: '',
  modelKey: '',
  temperature: 0.7,
  isPublic: false,
  imageWidth: 1328,
  imageHeight: 1328,
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
    if (form.kind !== 'image' && !form.modelKey && models?.length) {
      form.modelKey = models[0].key
    }
  },
  { immediate: true },
)

const isImage = computed(() => form.kind === 'image')

const handleSubmit = () => {
  const payload = { ...form }
  if (payload.kind === 'image') {
    payload.imageWidth = Number(payload.imageWidth) || 1328
    payload.imageHeight = Number(payload.imageHeight) || 1328
  }
  emit('submit', payload)
}
</script>

<template>
  <div class="agent-form">
    <h2>{{ isImage ? '文生图智能体' : '智能体设定' }}</h2>
    <p class="hint">
      {{
        isImage
          ? '使用火山引擎文生图通用 3.0（high_aes_general_v30l_zt2i），保存后在右侧输入画面描述生成图片'
          : '配置角色、描述与模型，保存后即可开启会话'
      }}
    </p>

    <label class="field">
      <span>角色名称</span>
      <input v-model="form.name" placeholder="如：财务顾问、AI 助教" />
    </label>

    <label class="field">
      <span>{{ isImage ? '说明（可选）' : '角色描述 / 指令' }}</span>
      <textarea
        v-model="form.description"
        rows="4"
        :placeholder="
          isImage ? '可填写常用风格、用途等备注（不会自动拼进每次提示词）' : '描述智能体的背景、语气、行为规范……'
        "
      />
    </label>

    <template v-if="isImage">
      <div class="field-row">
        <label class="field">
          <span>宽度（512–2048）</span>
          <input v-model.number="form.imageWidth" type="number" min="512" max="2048" step="8" />
        </label>
        <label class="field">
          <span>高度（512–2048）</span>
          <input v-model.number="form.imageHeight" type="number" min="512" max="2048" step="8" />
        </label>
      </div>
      <p class="hint small">推荐 1:1 为 1328×1328；具体以火山引擎文档为准</p>
    </template>

    <ModelSelector
      v-if="!isImage"
      v-model:model-key="form.modelKey"
      :options="models"
      :disabled="loading"
    />

    <label v-if="!isImage" class="field slider">
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

    <label class="field checkbox-row">
      <input v-model="form.isPublic" type="checkbox" />
      <span>公开到智能体广场（其他登录用户可见并与你一样发起对话）</span>
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

.hint.small {
  margin: 0;
  font-size: 0.82rem;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

@media (max-width: 520px) {
  .field-row {
    grid-template-columns: 1fr;
  }
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

.checkbox-row {
  flex-direction: row;
  align-items: flex-start;
  gap: 0.6rem;
}

.checkbox-row input {
  margin-top: 0.2rem;
  width: auto;
}

.checkbox-row span {
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}

button.primary {
  border: none;
  background: var(--accent-color);
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


