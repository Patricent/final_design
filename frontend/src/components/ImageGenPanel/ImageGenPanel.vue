<script setup>
import { ref } from 'vue'
import { ImageGenAPI } from '../../services/api'

const props = defineProps({
  agentId: {
    type: Number,
    required: true,
  },
})

const prompt = ref('')
const usePreLlm = ref(false)
const busy = ref(false)
const statusText = ref('')
const errorText = ref('')
const imageUrls = ref([])

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const run = async () => {
  errorText.value = ''
  statusText.value = ''
  imageUrls.value = []
  const p = prompt.value.trim()
  if (!p) {
    errorText.value = '请输入画面描述'
    return
  }
  busy.value = true
  try {
    const { task_id: taskId } = await ImageGenAPI.submit({
      agent_id: props.agentId,
      prompt: p,
      use_pre_llm: usePreLlm.value,
    })
    statusText.value = '任务已提交，生成中…'

    for (let i = 0; i < 90; i++) {
      await sleep(2000)
      const r = await ImageGenAPI.result({ task_id: taskId, agent_id: props.agentId })
      if (r.code !== 10000) {
        errorText.value = r.message || '生成失败'
        return
      }
      const st = r.status
      if (st === 'in_queue') statusText.value = '排队中…'
      else if (st === 'generating') statusText.value = '绘制中…'
      else if (st === 'done') {
        imageUrls.value = r.image_urls || []
        if (!imageUrls.value.length) {
          errorText.value = '已完成但未返回图片链接'
        } else {
          statusText.value = '完成'
        }
        return
      } else if (st === 'not_found' || st === 'expired') {
        errorText.value = '任务已失效，请重试'
        return
      }
    }
    errorText.value = '等待超时，请稍后重试'
  } catch (e) {
    errorText.value = e?.response?.data?.detail || e?.message || '请求失败'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="img-gen">
    <h2>生成图片</h2>
    <p class="hint">基于当前智能体配置的宽高调用火山引擎文生图通用 3.0。链接有效期约 24 小时，请及时保存。</p>

    <label class="field">
      <span>画面描述（提示词）</span>
      <textarea v-model="prompt" rows="4" placeholder="主体 + 场景 + 风格与光影，可用英文写专业词" />
    </label>

    <label class="check">
      <input v-model="usePreLlm" type="checkbox" />
      <span>开启文本扩写（提示词较短时建议开启）</span>
    </label>

    <button type="button" class="primary" :disabled="busy" @click="run">
      {{ busy ? '生成中…' : '生成图片' }}
    </button>

    <p v-if="statusText" class="status">{{ statusText }}</p>
    <p v-if="errorText" class="err">{{ errorText }}</p>

    <div v-if="imageUrls.length" class="gallery">
      <a
        v-for="(u, idx) in imageUrls"
        :key="idx"
        :href="u"
        target="_blank"
        rel="noopener noreferrer"
        class="thumb-wrap"
      >
        <img :src="u" :alt="`生成图 ${idx + 1}`" class="thumb" />
      </a>
    </div>
  </div>
</template>

<style scoped>
.img-gen {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
}

.img-gen h2 {
  margin: 0;
  font-size: 1.2rem;
}

.hint {
  margin: -0.25rem 0 0;
  font-size: 0.88rem;
  color: var(--color-text-muted);
  line-height: 1.5;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field span {
  font-size: 0.95rem;
}

textarea {
  border-radius: 12px;
  border: 1px solid var(--border-color);
  padding: 0.75rem;
  font-size: 0.95rem;
  background: var(--panel-bg-muted);
  color: var(--color-text);
  resize: vertical;
  min-height: 120px;
}

.check {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.check input {
  margin-top: 0.2rem;
}

.primary {
  align-self: flex-start;
  border: none;
  border-radius: 12px;
  padding: 0.65rem 1.25rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  background: var(--accent-color);
  color: #fff;
}

.primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.status {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-muted);
}

.err {
  margin: 0;
  font-size: 0.9rem;
  color: #b91c1c;
}

.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.thumb-wrap {
  display: block;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  background: var(--panel-bg-muted);
}

.thumb {
  width: 100%;
  height: auto;
  vertical-align: middle;
  display: block;
}
</style>
