<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

/** 眼球在眼白内的最大偏移（SVG 用户单位） */
const MAX_PUPIL = 3.2

const EYE_CENTERS = [
  { cx: 44, cy: 48 },
  { cx: 76, cy: 48 },
]

const mouse = ref({ x: 0, y: 0 })
const leftSvg = ref(null)
const rightSvg = ref(null)
const leftPupils = ref([
  { x: 0, y: 0 },
  { x: 0, y: 0 },
])
const rightPupils = ref([
  { x: 0, y: 0 },
  { x: 0, y: 0 },
])

let raf = 0

function offsetForEye(clientCx, clientCy, mx, my) {
  const dx = mx - clientCx
  const dy = my - clientCy
  const dist = Math.hypot(dx, dy) || 1
  const pull = Math.min(MAX_PUPIL, dist * 0.04)
  return {
    x: (dx / dist) * pull,
    y: (dy / dist) * pull,
  }
}

function computePupils(svgEl, centers) {
  if (!svgEl) {
    return [
      { x: 0, y: 0 },
      { x: 0, y: 0 },
    ]
  }
  const rect = svgEl.getBoundingClientRect()
  const vb = svgEl.viewBox.baseVal
  const scaleX = rect.width / vb.width
  const scaleY = rect.height / vb.height
  const { x: mx, y: my } = mouse.value
  return centers.map((c) => {
    const clientCx = rect.left + c.cx * scaleX
    const clientCy = rect.top + c.cy * scaleY
    return offsetForEye(clientCx, clientCy, mx, my)
  })
}

function updateEyes() {
  leftPupils.value = computePupils(leftSvg.value, EYE_CENTERS)
  rightPupils.value = computePupils(rightSvg.value, EYE_CENTERS)
}

function onMove(e) {
  mouse.value = { x: e.clientX, y: e.clientY }
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(updateEyes)
}

onMounted(() => {
  window.addEventListener('mousemove', onMove, { passive: true })
  mouse.value = { x: window.innerWidth / 2, y: window.innerHeight / 2 }
  requestAnimationFrame(updateEyes)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', onMove)
  cancelAnimationFrame(raf)
})
</script>

<template>
  <div class="auth-ambient" aria-hidden="true">
    <div class="auth-ambient__glow auth-ambient__glow--a" />
    <div class="auth-ambient__glow auth-ambient__glow--b" />
    <div class="auth-ambient__glow auth-ambient__glow--c" />

    <div class="auth-robot auth-robot--left">
      <svg
        ref="leftSvg"
        class="auth-robot-svg auth-robot-svg--left"
        viewBox="0 0 120 168"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="authBotMetalL" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#e2e8f0" />
            <stop offset="100%" stop-color="#94a3b8" />
          </linearGradient>
          <linearGradient id="authBotFaceL" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#f8fafc" />
            <stop offset="100%" stop-color="#e2e8f0" />
          </linearGradient>
        </defs>
        <rect x="38" y="8" width="8" height="22" rx="3" fill="#64748b" opacity="0.85" />
        <circle cx="42" cy="6" r="5" fill="#38bdf8" class="auth-robot__blink" />
        <rect
          x="18"
          y="28"
          width="84"
          height="68"
          rx="18"
          fill="url(#authBotFaceL)"
          stroke="#cbd5e1"
          stroke-width="2"
        />
        <!-- 左眼白 + 眼珠 -->
        <circle cx="44" cy="48" r="11" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" />
        <g :transform="`translate(${leftPupils[0].x}, ${leftPupils[0].y})`">
          <circle cx="44" cy="48" r="5.5" fill="#0f172a" />
          <circle cx="46" cy="46" r="1.8" fill="#ffffff" opacity="0.85" />
        </g>
        <!-- 右眼 -->
        <circle cx="76" cy="48" r="11" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" />
        <g :transform="`translate(${leftPupils[1].x}, ${leftPupils[1].y})`">
          <circle cx="76" cy="48" r="5.5" fill="#0f172a" />
          <circle cx="78" cy="46" r="1.8" fill="#ffffff" opacity="0.85" />
        </g>
        <path
          d="M 48 72 Q 60 82 72 72"
          fill="none"
          stroke="#94a3b8"
          stroke-width="3"
          stroke-linecap="round"
        />
        <rect x="22" y="102" width="76" height="58" rx="14" fill="url(#authBotMetalL)" stroke="#94a3b8" stroke-width="2" />
        <circle cx="42" cy="128" r="6" fill="#38bdf8" opacity="0.35" />
        <circle cx="78" cy="128" r="6" fill="#c4b5fd" opacity="0.35" />
        <rect x="52" y="118" width="16" height="22" rx="4" fill="#334155" opacity="0.9" />
      </svg>
    </div>

    <div class="auth-robot auth-robot--right">
      <svg
        ref="rightSvg"
        class="auth-robot-svg auth-robot-svg--right"
        viewBox="0 0 120 168"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="authBotMetalR" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#e2e8f0" />
            <stop offset="100%" stop-color="#94a3b8" />
          </linearGradient>
          <linearGradient id="authBotFaceR" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#f8fafc" />
            <stop offset="100%" stop-color="#e2e8f0" />
          </linearGradient>
        </defs>
        <rect x="74" y="8" width="8" height="22" rx="3" fill="#64748b" opacity="0.85" />
        <circle cx="78" cy="6" r="5" fill="#c4b5fd" class="auth-robot__blink" />
        <rect
          x="18"
          y="28"
          width="84"
          height="68"
          rx="18"
          fill="url(#authBotFaceR)"
          stroke="#cbd5e1"
          stroke-width="2"
        />
        <circle cx="44" cy="48" r="11" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" />
        <g :transform="`translate(${rightPupils[0].x}, ${rightPupils[0].y})`">
          <circle cx="44" cy="48" r="5.5" fill="#0f172a" />
          <circle cx="46" cy="46" r="1.8" fill="#ffffff" opacity="0.85" />
        </g>
        <circle cx="76" cy="48" r="11" fill="#ffffff" stroke="#cbd5e1" stroke-width="1" />
        <g :transform="`translate(${rightPupils[1].x}, ${rightPupils[1].y})`">
          <circle cx="76" cy="48" r="5.5" fill="#0f172a" />
          <circle cx="78" cy="46" r="1.8" fill="#ffffff" opacity="0.85" />
        </g>
        <path
          d="M 48 72 Q 60 80 72 72"
          fill="none"
          stroke="#94a3b8"
          stroke-width="3"
          stroke-linecap="round"
        />
        <rect x="22" y="102" width="76" height="58" rx="14" fill="url(#authBotMetalR)" stroke="#94a3b8" stroke-width="2" />
        <circle cx="42" cy="128" r="6" fill="#c4b5fd" opacity="0.35" />
        <circle cx="78" cy="128" r="6" fill="#38bdf8" opacity="0.35" />
        <rect x="52" y="118" width="16" height="22" rx="4" fill="#334155" opacity="0.9" />
      </svg>
    </div>
  </div>
</template>

<style scoped>
.auth-ambient {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
}

.auth-ambient__glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(72px);
  opacity: 0.45;
  animation: authGlowDrift 18s ease-in-out infinite;
}

.auth-ambient__glow--a {
  width: min(55vw, 420px);
  height: min(55vw, 420px);
  top: -12%;
  left: -8%;
  background: radial-gradient(circle, rgba(125, 211, 252, 0.55), transparent 68%);
  animation-delay: 0s;
}

.auth-ambient__glow--b {
  width: min(50vw, 380px);
  height: min(50vw, 380px);
  bottom: -18%;
  right: -10%;
  background: radial-gradient(circle, rgba(196, 181, 253, 0.5), transparent 68%);
  animation-delay: -6s;
}

.auth-ambient__glow--c {
  width: min(40vw, 320px);
  height: min(40vw, 320px);
  top: 38%;
  left: 36%;
  background: radial-gradient(circle, rgba(251, 191, 36, 0.12), transparent 70%);
  animation: authGlowPulse 10s ease-in-out infinite;
}

@keyframes authGlowDrift {
  0%,
  100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(3%, 2%) scale(1.05);
  }
  66% {
    transform: translate(-2%, 4%) scale(0.96);
  }
}

@keyframes authGlowPulse {
  0%,
  100% {
    opacity: 0.35;
    transform: scale(1);
  }
  50% {
    opacity: 0.55;
    transform: scale(1.08);
  }
}

.auth-robot {
  position: absolute;
  bottom: clamp(4%, 8vh, 12%);
  width: min(200px, 28vw);
  max-width: 220px;
  animation: authRobotFloat 5.2s ease-in-out infinite;
}

.auth-robot--left {
  left: clamp(0.25rem, 4vw, 2.5rem);
  animation-delay: 0s;
}

.auth-robot--right {
  right: clamp(0.25rem, 4vw, 2.5rem);
  animation-delay: -2.6s;
  animation-duration: 5.8s;
}

@keyframes authRobotFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-14px);
  }
}

.auth-robot svg {
  width: 100%;
  height: auto;
  display: block;
  filter: drop-shadow(0 14px 28px rgba(15, 23, 42, 0.12));
}

.auth-robot__blink {
  animation: authAntennaPulse 2.4s ease-in-out infinite;
}

.auth-robot--right .auth-robot__blink {
  animation-delay: 1.2s;
}

@keyframes authAntennaPulse {
  0%,
  100% {
    opacity: 1;
    filter: brightness(1);
  }
  50% {
    opacity: 0.65;
    filter: brightness(1.35);
  }
}

@media (max-width: 720px) {
  .auth-robot {
    width: min(120px, 22vw);
    bottom: 2%;
    opacity: 0.55;
  }

  .auth-ambient__glow {
    opacity: 0.32;
  }
}

@media (max-width: 480px) {
  .auth-robot {
    display: none;
  }
}
</style>
