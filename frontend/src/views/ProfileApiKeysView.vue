<script setup>
import { ref } from 'vue'
import { patchUserApiKeys } from '../services/api'
import { authState } from '../store/authStore'

const keyQwen = ref('')
const keyDeepseek = ref('')
const keyGpt = ref('')
const clearQwen = ref(false)
const clearDeepseek = ref(false)
const clearGpt = ref(false)
const keysLoading = ref(false)
const keysError = ref('')
const keysOk = ref('')

const submitApiKeys = async () => {
  keysError.value = ''
  keysOk.value = ''
  const body = {}
  if (clearQwen.value) body.qwen_clear = true
  else if (keyQwen.value.trim()) body.qwen_api_key = keyQwen.value.trim()

  if (clearDeepseek.value) body.deepseek_clear = true
  else if (keyDeepseek.value.trim()) body.deepseek_api_key = keyDeepseek.value.trim()

  if (clearGpt.value) body.gpt_clear = true
  else if (keyGpt.value.trim()) body.gpt_api_key = keyGpt.value.trim()

  if (Object.keys(body).length === 0) {
    keysError.value = '请填写新的 Key，或勾选「改用系统默认」'
    return
  }

  keysLoading.value = true
  try {
    const data = await patchUserApiKeys(body)
    authState.user = data
    keyQwen.value = ''
    keyDeepseek.value = ''
    keyGpt.value = ''
    clearQwen.value = false
    clearDeepseek.value = false
    clearGpt.value = false
    keysOk.value = 'API Key 已更新'
  } catch (e) {
    const d = e?.response?.data
    keysError.value =
      typeof d === 'object' && d && typeof d.detail === 'string'
        ? d.detail
        : '保存失败，请稍后重试'
  } finally {
    keysLoading.value = false
  }
}
</script>

<template>
  <section class="profile-card">
    <p class="hint intro">
      与「新建智能体」中的三类模型对应：Qwen（阿里云百炼）、DeepSeek、GPT（OpenAI）。填写并保存后，仅当您本人发起对话时使用您的 Key；输入框留空表示该项本次不修改；勾选清除则恢复为系统默认；系统默认来自环境变量（见各条说明）。
    </p>

    <div class="api-key-block">
      <div class="api-key-head">
        <span class="api-key-title">Qwen（通义）</span>
        <span v-if="authState.user?.has_qwen_api_key" class="api-key-badge">已保存个人 Key</span>
      </div>
      <label class="field">
        <span>API Key</span>
        <input v-model="keyQwen" type="password" autocomplete="off" placeholder="输入新 Key 覆盖；不填表示本条不修改" />
      </label>
      <label class="check-row">
        <input v-model="clearQwen" type="checkbox" />
        <span>清除我的 Key，改用系统默认（DASHSCOPE_API_KEY / QWEN_API_KEY）</span>
      </label>
    </div>

    <div class="api-key-block">
      <div class="api-key-head">
        <span class="api-key-title">DeepSeek</span>
        <span v-if="authState.user?.has_deepseek_api_key" class="api-key-badge">已保存个人 Key</span>
      </div>
      <label class="field">
        <span>API Key</span>
        <input
          v-model="keyDeepseek"
          type="password"
          autocomplete="off"
          placeholder="输入新 Key 覆盖；不填表示本条不修改"
        />
      </label>
      <label class="check-row">
        <input v-model="clearDeepseek" type="checkbox" />
        <span>清除我的 Key，改用系统默认（DEEPSEEK_API_KEY）</span>
      </label>
    </div>

    <div class="api-key-block">
      <div class="api-key-head">
        <span class="api-key-title">OpenAI（GPT）</span>
        <span v-if="authState.user?.has_gpt_api_key" class="api-key-badge">已保存个人 Key</span>
      </div>
      <label class="field">
        <span>API Key</span>
        <input v-model="keyGpt" type="password" autocomplete="off" placeholder="输入新 Key 覆盖；不填表示本条不修改" />
      </label>
      <label class="check-row">
        <input v-model="clearGpt" type="checkbox" />
        <span>清除我的 Key，改用系统默认（OPENAI_API_KEY）</span>
      </label>
    </div>

    <p v-if="keysError" class="msg msg--error">{{ keysError }}</p>
    <p v-if="keysOk" class="msg msg--ok">{{ keysOk }}</p>
    <button type="button" class="secondary" :disabled="keysLoading" @click="submitApiKeys">
      {{ keysLoading ? '保存中…' : '保存 API Key 设置' }}
    </button>
  </section>
</template>

<style scoped>
.profile-card {
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--panel-bg);
  box-shadow: var(--panel-shadow);
}

.intro {
  margin: 0 0 1rem;
  font-size: 0.9rem;
  color: var(--color-text-muted);
  line-height: 1.55;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.5rem;
}

.field span {
  font-size: 0.95rem;
}

input:not([type='checkbox']) {
  border-radius: 10px;
  border: 1px solid var(--border-color);
  padding: 0.65rem 0.85rem;
  font-size: 0.95rem;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

.api-key-block {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.api-key-block:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.api-key-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.35rem;
}

.api-key-title {
  font-weight: 600;
  font-size: 0.95rem;
}

.api-key-badge {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.18);
  color: rgba(15, 23, 42, 0.8);
}

.check-row {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin: 0.5rem 0 0;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  cursor: pointer;
}

.check-row input {
  margin-top: 0.2rem;
}

.msg {
  margin: 1rem 0 0;
  font-size: 0.9rem;
}

.msg--error {
  color: #dc2626;
}

.msg--ok {
  color: #15803d;
}

.secondary {
  margin-top: 1rem;
  width: 100%;
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  background: var(--panel-bg-muted);
  color: var(--color-text);
}

.secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
