import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  linkify: true,
  breaks: true,
  html: true,
  typographer: true,
})

/**
 * 修复流式更新时的不完整Markdown语法
 * 例如：**text 被截断时，临时处理为 **text**（临时闭合）
 */
function fixIncompleteMarkdown(content) {
  if (!content) return ''
  
  let fixed = content
  
  // 修复不完整的加粗标记 **text 或 text**
  // 统计未配对的 ** 数量
  const boldMatches = fixed.match(/\*\*/g)
  if (boldMatches && boldMatches.length % 2 !== 0) {
    // 有奇数个 **，说明有未闭合的标记
    // 在末尾添加 ** 临时闭合（如果最后一个字符不是 *）
    if (!fixed.endsWith('*')) {
      fixed = fixed + '**'
    } else if (!fixed.endsWith('**')) {
      fixed = fixed + '*'
    }
  }
  
  // 修复不完整的斜体标记 *text 或 text*（但不在 ** 内部）
  // 这个比较复杂，暂时不处理，因为可能误判
  
  // 修复不完整的代码块标记 ```code
  const codeBlockMatches = fixed.match(/```/g)
  if (codeBlockMatches && codeBlockMatches.length % 2 !== 0) {
    // 有奇数个 ```，说明代码块未闭合
    // 在末尾添加 ```
    if (!fixed.endsWith('`')) {
      fixed = fixed + '\n```'
    } else if (!fixed.endsWith('``')) {
      fixed = fixed + '`'
    } else if (!fixed.endsWith('```')) {
      fixed = fixed + '`'
    }
  }
  
  // 修复不完整的行内代码标记 `code
  // 统计未配对的 ` 数量（排除 ```）
  // 先移除所有 ```，然后统计剩余的 `
  const withoutCodeBlocks = fixed.replace(/```[\s\S]*?```/g, '')
  const inlineCodeMatches = withoutCodeBlocks.match(/`/g)
  if (inlineCodeMatches && inlineCodeMatches.length % 2 !== 0) {
    // 有奇数个 `，说明行内代码未闭合
    if (!fixed.endsWith('`')) {
      fixed = fixed + '`'
    }
  }
  
  return fixed
}

export function renderMarkdown(content, isStreaming = false) {
  if (!content) return ''
  
  try {
    // 如果是流式更新，先修复不完整的Markdown语法
    const fixedContent = isStreaming ? fixIncompleteMarkdown(content) : content
    return md.render(fixedContent)
  } catch (error) {
    console.warn('Markdown渲染失败，使用原始内容:', error)
    // 如果渲染失败，至少转义HTML特殊字符并保留换行
    return content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
      .replace(/\n/g, '<br>')
  }
}


