<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { authState, isLoggedIn } from '../store/authStore'

const greeting = computed(() => {
  if (!isLoggedIn()) return ''
  const u = authState.user?.nickname || authState.user?.username
  return u ? `${u}` : ''
})

const pillars = [
  {
    icon: '◐',
    title: '双流合一',
    text: '对话与画质在同一张工作台 coexist：会话像河流，画布像星云，各司其职却共享同一扇门。',
  },
  {
    icon: '⚡',
    title: '流式抵达',
    text: '字句不必等整封信送达才拆封；思潮一边生成，屏幕一边亮起，像在黑暗里摸到第一缕温度。',
  },
  {
    icon: '◆',
    title: '可被分享的智能',
    text: '把提示、模型与口吻封进一粒「公开」的露珠，广场上的路人也能拾起来照见自己的倒影。',
  },
  {
    icon: '◇',
    title: '密钥停在后场',
    text: 'API 与云服务签名留在服务器的帷幕之后，浏览器只认得一段短暂的星光——JWT，足够亮，也够谨慎。',
  },
]

const moods = [
  { tag: '用「代码审查员」智能体逐行挑刺', hue: '#7dd3fc' },
  { tag: '把工作流写进助手设定，每天少问一遍怎么开头', hue: '#c4b5fd' },
  { tag: '文生图：赛博朋克灯牌 + 16:9 城市雨夜', hue: '#fbbf24' },
  { tag: '在广场捡一个智能体开启畅聊之旅', hue: '#34d399' },
]
</script>

<template>
  <div class="landing">
    <div class="ambient" aria-hidden="true">
      <span class="orb orb-a" />
      <span class="orb orb-b" />
      <span class="grain" />
    </div>

    <header class="nav">
      <RouterLink class="brand" :to="{ name: 'landing' }">
        <span class="brand__mark">⊹</span>
        <span class="brand__name">个性化智能体平台</span>
        <span class="brand__tag"></span>
      </RouterLink>

      <nav class="nav__actions">
        <template v-if="isLoggedIn()">
          <span class="nav__hello">已进入 · {{ greeting }}</span>
          <RouterLink class="btn btn--ghost" :to="{ name: 'agent-square' }">广场</RouterLink>
          <RouterLink class="btn btn--solid" :to="{ name: 'agent-home' }">我的智能体</RouterLink>
        </template>
        <template v-else>
          <RouterLink class="btn btn--ghost" :to="{ name: 'login' }">登录</RouterLink>
          <RouterLink class="btn btn--solid" :to="{ name: 'register' }">注册</RouterLink>
        </template>
      </nav>
    </header>

    <main class="main">
      <section class="hero">
        <p class="eyebrow">语言与像素，从此共用一个落款</p>
        <h1 class="hero__title">
          让每一次提问都带上<br >
          <span class="hero__accent">可被收藏的形状</span>
        </h1>
        <p class="hero__lead">
          这里不是冰冷的 API 控制台，而是一座停泊在浏览器里的微型星座港：你为「智能体」命名、设色、指明模型，
          随后在对话里推演思想，或是在画布上召唤光景。它不承诺预言未来，只愿成为你愿意反复回来的那一扇窗。
        </p>

        <div class="hero__cta">
          <RouterLink v-if="!isLoggedIn()" class="btn btn--solid btn--lg" :to="{ name: 'register' }">
            免费创建账号，点亮工作台
          </RouterLink>
          <RouterLink v-else class="btn btn--solid btn--lg" :to="{ name: 'agent-home' }">
            前往我的世界
          </RouterLink>
          <RouterLink v-if="!isLoggedIn()" class="btn btn--ghost btn--lg" :to="{ name: 'login' }">
            我已在此寄放星光
          </RouterLink>
        </div>

        <ul class="moods" aria-label="灵感速写">
          <li v-for="(m, i) in moods" :key="i" class="mood" :style="{ '--m-hue': m.hue }">
            <span class="mood__dot" />
            {{ m.tag }}
          </li>
        </ul>
      </section>

      <section class="bridge">
        <div class="bridge__panel">
          <h2 class="bridge__title"></h2>
          <p class="bridge__text">
            当模型的名字越来越多，控制台与文档却各自漂流，创造者真正缺少的往往不是算力，
            而是一张能把<strong>人设、偏好、出镜范围</strong>钉在同一块玻璃板上的工作台。
            本系统把那些碎片收拢为可命名、可复制、可被广场借阅的<strong>智能体</strong>——
            像给每段提示词签发一张暂住证，却从未收缴你的想象力护照。
          </p>
        </div>
      </section>

      <section class="grid-section">
        <h2 class="section-title">四座锚点 · 托起你的日常实验</h2>
        <ul class="pillar-grid">
          <li v-for="(p, i) in pillars" :key="i" class="pillar">
            <span class="pillar__icon">{{ p.icon }}</span>
            <h3>{{ p.title }}</h3>
            <p>{{ p.text }}</p>
          </li>
        </ul>
      </section>

      <section class="outro">
        <p class="outro__poem">
          若神经网络是海面，我们便做码头上的灯<br >
          不替你航行，却只在你返航时，仍认得你的轮廓。
        </p>
        <p class="outro__note">
          本页为产品介绍与启程之地；核心技术栈含 Django、Vue、MySQL，以及面向大模型与视觉 API 的工程化接线。
          创意文案独立于此，可随时按课程要求替换为你的学术表述。
        </p>
      </section>
    </main>

    <footer class="foot">
      <span>© 毕业设计演示 · 个性化智能体平台</span>
      <RouterLink class="foot__link" :to="{ name: 'landing' }">返回顶部</RouterLink>
    </footer>
  </div>
</template>

<style scoped>
.landing {
  width: 100%;
  --landing-gutter: clamp(1rem, 4vw, 2.25rem);
  min-height: 100vh;
  position: relative;
  overflow-x: clip;
  color: var(--color-text);
  background: var(--app-bg);
}

.ambient {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(88px);
  opacity: 0.38;
}

.orb-a {
  width: 42vw;
  height: 42vw;
  max-width: 520px;
  max-height: 520px;
  top: -8%;
  right: -5%;
  background: radial-gradient(circle, rgba(125, 211, 252, 0.55), transparent 70%);
}

.orb-b {
  width: 50vw;
  height: 50vw;
  max-width: 600px;
  max-height: 600px;
  bottom: -18%;
  left: -15%;
  background: radial-gradient(circle, rgba(196, 181, 253, 0.48), transparent 70%);
}

.grain {
  position: absolute;
  inset: 0;
  opacity: 0.035;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

.nav {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem max(var(--landing-gutter), env(safe-area-inset-right)) 1rem
    max(var(--landing-gutter), env(safe-area-inset-left));
  backdrop-filter: blur(14px);
  background: rgba(255, 255, 255, 0.82);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.9) inset;
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 0.65rem;
  text-decoration: none;
  color: var(--color-heading);
  flex-wrap: wrap;
}

.brand__mark {
  font-size: 1.5rem;
  color: #38bdf8;
}

.brand__name {
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: 0.04em;
}

.brand__tag {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.nav__actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  flex-wrap: wrap;
}

.nav__hello {
  font-size: 0.82rem;
  color: var(--color-text-muted);
  margin-right: 0.35rem;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.1rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 600;
  text-decoration: none;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    background 0.18s ease;
}

.btn--ghost {
  border: 1px solid var(--border-color);
  color: var(--color-text);
  background: var(--panel-bg-muted);
}

.btn--ghost:hover {
  transform: translateY(-1px);
  border-color: rgba(var(--accent-rgb), 0.45);
  box-shadow: 0 6px 16px rgba(15, 23, 42, 0.06);
}

.btn--solid {
  border: none;
  color: #0f172a;
  background: linear-gradient(135deg, #7dd3fc 0%, #c4b5fd 100%);
  box-shadow: 0 8px 22px rgba(125, 211, 252, 0.28);
}

.btn--solid:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(196, 181, 253, 0.3);
}

.btn--lg {
  padding: 0.72rem 1.6rem;
  font-size: 0.95rem;
}

.main {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: none;
  margin: 0;
  padding: clamp(2rem, 6vw, 4rem) max(var(--landing-gutter), env(safe-area-inset-right)) 4rem
    max(var(--landing-gutter), env(safe-area-inset-left));
}

.hero {
  padding-bottom: clamp(2.5rem, 8vw, 4rem);
}

.eyebrow {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  letter-spacing: 0.35em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.hero__title {
  margin: 0;
  font-size: clamp(2rem, 5vw, 3rem);
  line-height: 1.18;
  font-weight: 800;
  color: var(--color-heading);
  letter-spacing: -0.02em;
}

.hero__accent {
  background: linear-gradient(90deg, #0ea5e9, #8b5cf6, #a78bfa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero__lead {
  margin: 1.25rem 0 0;
  max-width: none;
  font-size: clamp(1rem, 2.2vw, 1.1rem);
  line-height: 1.85;
  color: var(--color-text-muted);
}

.hero__cta {
  margin-top: 2rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.moods {
  list-style: none;
  margin: 2.75rem 0 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
}

.mood {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.42rem 0.85rem;
  border-radius: 999px;
  font-size: 0.78rem;
  color: var(--color-text);
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid var(--border-color);
}

.mood__dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--m-hue, #38bdf8);
}

.bridge {
  margin: 1rem 0 3rem;
  width: 100%;
}

.bridge__panel {
  padding: clamp(1.5rem, 4vw, 2.25rem) 0;
  border-radius: 0;
  background: var(--panel-bg);
  border-width: 1px 0;
  border-style: solid;
  border-color: var(--border-color);
  box-shadow: none;
}

.bridge__title {
  margin: 0 0 0.85rem;
  font-size: 1.35rem;
  color: var(--color-heading);
}

.bridge__text {
  margin: 0;
  line-height: 1.82;
  color: var(--color-text-muted);
}

.bridge__text strong {
  color: var(--color-text);
  font-weight: 600;
}

.grid-section {
  margin-bottom: 3rem;
}

.grid-section .section-title {
  text-align: center;
}

.section-title {
  margin: 0 0 1.5rem;
  font-size: 1.35rem;
  color: var(--color-heading);
  font-weight: 700;
}

.pillar-grid {
  list-style: none;
  margin: 0 auto;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 280px));
  justify-content: center;
  gap: 1.1rem;
}

.pillar {
  padding: 1.35rem 1.25rem;
  border-radius: 18px;
  background: var(--panel-bg);
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
  transition:
    border-color 0.2s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.pillar:hover {
  border-color: rgba(var(--accent-rgb), 0.35);
  transform: translateY(-3px);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.09);
}

.pillar__icon {
  font-size: 1.35rem;
  display: block;
  margin-bottom: 0.5rem;
  filter: saturate(1.3);
}

.pillar h3 {
  margin: 0 0 0.5rem;
  font-size: 1.05rem;
  color: var(--color-heading);
}

.pillar p {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.72;
  color: var(--color-text-muted);
}

.outro {
  margin-top: 1rem;
  padding: 2rem 0 0;
  border-top: 1px solid var(--border-color);
  text-align: center;
}

.outro__poem {
  margin: 0 auto;
  max-width: 36rem;
  font-size: 1.05rem;
  line-height: 1.92;
  color: var(--color-text-muted);
  font-style: italic;
}

.outro__note {
  margin: 1.5rem auto 0;
  max-width: 42rem;
  font-size: 0.76rem;
  line-height: 1.65;
  color: var(--color-text-muted);
  opacity: 0.92;
}

.foot {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem max(var(--landing-gutter), env(safe-area-inset-right)) 1.5rem
    max(var(--landing-gutter), env(safe-area-inset-left));
  padding-bottom: max(1.5rem, env(safe-area-inset-bottom));
  border-top: 1px solid var(--border-color);
  font-size: 0.82rem;
  color: var(--color-text-muted);
  background: rgba(255, 255, 255, 0.45);
}

.foot__link {
  color: #0284c7;
  text-decoration: none;
  font-weight: 600;
}

.foot__link:hover {
  text-decoration: underline;
}
</style>
