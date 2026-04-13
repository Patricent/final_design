/**
 * 与参考文件 frontend/Chat.vue 中 renderMarkdown 相同的替换顺序与规则，
 * 便于对话区 Markdown 展示一致；流式过程中每次更新都对当前完整文本调用即可（与 Chat.vue 一致）。
 * 渲染前对原文做 HTML 转义，降低 XSS 风险（参考实现未转义）。
 */
function escapeHtml(text) {
  if (!text) return ''
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

/**
 * @param {string} content
 * @param {boolean} _isStreaming 保留参数，与 ChatStream / MarkdownViewer 的 API 一致；逻辑与 Chat.vue 相同，不区分流式与否
 */
export function renderMarkdown(content, _isStreaming = false) {
  if (!content) return ''

  try {
    const text = escapeHtml(String(content))

    return (
      text
        // 代码块
        .replace(/```([\s\S]*?)```/g, '<pre class="code-block"><code>$1</code></pre>')
        // 行内代码
        .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
        // 粗体
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // 斜体
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // 标题
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // 列表
        .replace(/^\* (.*$)/gim, '<li>$1</li>')
        .replace(/^- (.*$)/gim, '<li>$1</li>')
        // 将连续的 li 包在 ul 中
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        // 链接
        .replace(
          /\[([^\]]+)\]\(([^)]+)\)/g,
          '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>',
        )
        // 换行
        .replace(/\n/g, '<br>')
    )
  } catch (error) {
    console.warn('Markdown 渲染失败，使用转义文本:', error)
    return escapeHtml(String(content)).replace(/\n/g, '<br>')
  }
}
