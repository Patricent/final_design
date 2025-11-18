import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  linkify: true,
  breaks: true,
})

export function renderMarkdown(content) {
  return md.render(content ?? '')
}


