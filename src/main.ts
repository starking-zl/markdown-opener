import './style.css'
import { marked } from 'marked'
import hljs from 'highlight.js'
import katex from 'katex'
import mermaid from 'mermaid'
import { open, save } from '@tauri-apps/plugin-dialog'
import { readTextFile, writeFile, readDir } from '@tauri-apps/plugin-fs'
import { basename, join } from '@tauri-apps/api/path'
import { getArgs } from '@tauri-apps/api/cli'

marked.setOptions({
  breaks: true,
  gfm: true
})

mermaid.initialize({
  startOnLoad: false,
  theme: 'default'
})

interface FileItem {
  name: string
  path: string
  isDirectory: boolean
  children?: FileItem[]
}

interface AppState {
  currentFile: string | null
  currentContent: string
  files: FileItem[]
  isDark: boolean
  hasChanges: boolean
  layoutMode: 'split' | 'edit' | 'preview'
  sidebarCollapsed: boolean
}

const state: AppState = {
  currentFile: null,
  currentContent: '',
  files: [],
  isDark: false,
  hasChanges: false,
  layoutMode: 'split',
  sidebarCollapsed: false
}

const app = document.getElementById('app')!

function createHeader() {
  const header = document.createElement('div')
  header.className = 'header'

  const headerLeft = document.createElement('div')
  headerLeft.className = 'header-left'

  const logo = document.createElement('div')
  logo.className = 'logo'
  logo.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" stroke-width="2"/>
    <path d="M8 9L11 12L8 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M13 15H16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
  </svg>`

  const title = document.createElement('h1')
  title.className = 'title'
  title.textContent = 'Markdown Opener'

  const openBtn = createIconButton('folder', '打开文件', true)
  openBtn.addEventListener('click', openFile)

  const saveBtn = createIconButton('save', '保存', false)
  saveBtn.addEventListener('click', saveFile)

  headerLeft.appendChild(logo)
  headerLeft.appendChild(title)
  headerLeft.appendChild(openBtn)
  headerLeft.appendChild(saveBtn)

  const headerCenter = document.createElement('div')
  headerCenter.className = 'header-center'

  const layoutGroup = document.createElement('div')
  layoutGroup.className = 'layout-group'

  const layoutButtons = [
    { id: 'edit', icon: 'edit', label: '编辑' },
    { id: 'split', icon: 'split', label: '拆分' },
    { id: 'preview', icon: 'preview', label: '预览' }
  ]

  layoutButtons.forEach(btn => {
    const button = createLayoutButton(btn.id, btn.icon, btn.label, state.layoutMode === btn.id)
    button.addEventListener('click', () => setLayoutMode(btn.id as 'edit' | 'split' | 'preview'))
    layoutGroup.appendChild(button)
  })

  headerCenter.appendChild(layoutGroup)

  const headerRight = document.createElement('div')
  headerRight.className = 'header-right'

  const sidebarToggle = createIconButton('sidebar', '切换侧边栏', false)
  sidebarToggle.addEventListener('click', toggleSidebar)

  const themeToggle = document.createElement('div')
  themeToggle.className = 'theme-toggle'
  themeToggle.innerHTML = `<svg class="theme-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 3V5M12 19V21M4.22 4.22L5.64 5.64M18.36 18.36L19.78 19.78M3 12H5M19 12H21M4.22 19.78L5.64 18.36M18.36 5.64L19.78 4.22M16 12C16 14.2091 14.2091 16 12 16C9.79086 16 8 14.2091 8 12C8 9.79086 9.79086 8 12 8C14.2091 8 16 9.79086 16 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`
  themeToggle.addEventListener('click', toggleTheme)

  headerRight.appendChild(sidebarToggle)
  headerRight.appendChild(themeToggle)

  header.appendChild(headerLeft)
  header.appendChild(headerCenter)
  header.appendChild(headerRight)

  return header
}

function createIconButton(iconName: string, tooltip: string, primary: boolean) {
  const btn = document.createElement('button')
  btn.className = `icon-btn ${primary ? 'primary' : 'secondary'}`
  btn.setAttribute('title', tooltip)
  btn.innerHTML = getIconSVG(iconName)
  return btn
}

function getIconSVG(name: string): string {
  const icons: Record<string, string> = {
    folder: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M3 7V5C3 3.89543 3.89543 3 5 3H9L11 5H19C20.1046 5 21 5.89543 21 7V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    save: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M17 3H5C3.89543 3 3 3.89543 3 5V19C3 20.1046 3.89543 21 5 21H19C20.1046 21 21 20.1046 21 19V7L17 3Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M7 21V13H17V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M7 3V7H15V3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    sidebar: `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M2 4C2 3.44772 2.44772 3 3 3H21C21.5523 3 22 3.44772 22 4V20C22 20.5523 21.5523 21 21 21H3C2.44772 21 2 20.5523 2 20V4Z" stroke="currentColor" stroke-width="2"/>
      <path d="M8 3V21" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    edit: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M11 4H4C3.44772 4 3 4.44772 3 5V20C3 20.5523 3.44772 21 4 21H20C20.5523 21 21 20.5523 21 20V14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M18.5 2.5C18.8978 2.10218 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10218 21.5 2.5C21.8978 2.89782 22.1213 3.43743 22.1213 4C22.1213 4.56257 21.8978 5.10218 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`,
    split: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="3" width="18" height="18" rx="2" stroke="currentColor" stroke-width="2"/>
      <path d="M12 3V21" stroke="currentColor" stroke-width="2"/>
    </svg>`,
    preview: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
    </svg>`
  }
  return icons[name] || ''
}

function createLayoutButton(id: string, icon: string, label: string, isActive: boolean) {
  const btn = document.createElement('button')
  btn.className = `layout-btn ${isActive ? 'active' : ''}`
  btn.setAttribute('data-mode', id)
  btn.innerHTML = `${getIconSVG(icon)}<span>${label}</span>`
  return btn
}

function setLayoutMode(mode: 'edit' | 'split' | 'preview') {
  state.layoutMode = mode

  document.querySelectorAll('.layout-btn').forEach(btn => {
    btn.classList.remove('active')
  })
  document.querySelector(`.layout-btn[data-mode="${mode}"]`)?.classList.add('active')

  const editorPanel = document.querySelector('.editor-panel') as HTMLElement
  const previewPanel = document.querySelector('.preview-panel') as HTMLElement

  if (mode === 'edit') {
    editorPanel.style.display = 'flex'
    previewPanel.style.display = 'none'
  } else if (mode === 'preview') {
    editorPanel.style.display = 'none'
    previewPanel.style.display = 'flex'
  } else {
    editorPanel.style.display = 'flex'
    previewPanel.style.display = 'flex'
  }
}

function toggleSidebar() {
  state.sidebarCollapsed = !state.sidebarCollapsed

  const sidebar = document.querySelector('.sidebar') as HTMLElement
  const editorContainer = document.querySelector('.editor-container') as HTMLElement

  if (state.sidebarCollapsed) {
    sidebar.style.width = '0'
    sidebar.style.minWidth = '0'
    sidebar.style.padding = '0'
  } else {
    sidebar.style.width = '260px'
    sidebar.style.minWidth = '260px'
    sidebar.style.padding = ''
  }
}

function createSidebar() {
  const sidebar = document.createElement('div')
  sidebar.className = 'sidebar'

  const sidebarHeader = document.createElement('div')
  sidebarHeader.className = 'sidebar-header'

  const title = document.createElement('div')
  title.className = 'sidebar-title'
  title.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 7V5C3 3.89543 3.89543 3 5 3H9L11 5H19C20.1046 5 21 5.89543 21 7V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  文件浏览器`

  const refreshBtn = createIconButton('folder', '选择文件夹', false)
  refreshBtn.addEventListener('click', loadFolder)

  sidebarHeader.appendChild(title)
  sidebarHeader.appendChild(refreshBtn)

  const folderTree = document.createElement('div')
  folderTree.className = 'folder-tree'

  sidebar.appendChild(sidebarHeader)
  sidebar.appendChild(folderTree)

  return sidebar
}

function createEditorContainer() {
  const container = document.createElement('div')
  container.className = 'editor-container'

  const editorPanel = document.createElement('div')
  editorPanel.className = 'editor-panel'

  const editorHeader = document.createElement('div')
  editorHeader.className = 'panel-header'
  editorHeader.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M11 4H4C3.44772 4 3 4.44772 3 5V20C3 20.5523 3.44772 21 4 21H20C20.5523 21 21 20.5523 21 20V14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  编辑`

  const textarea = document.createElement('textarea')
  textarea.className = 'textarea'
  textarea.placeholder = '在这里输入 Markdown 内容...'
  textarea.addEventListener('input', handleTextChange)

  editorPanel.appendChild(editorHeader)
  editorPanel.appendChild(textarea)

  const previewPanel = document.createElement('div')
  previewPanel.className = 'preview-panel'

  const previewHeader = document.createElement('div')
  previewHeader.className = 'panel-header'
  previewHeader.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M1 12C1 12 5 4 12 4C19 4 23 12 23 12C23 12 19 20 12 20C5 20 1 12 1 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
  </svg>
  预览`

  const previewContent = document.createElement('div')
  previewContent.className = 'preview-content'

  previewPanel.appendChild(previewHeader)
  previewPanel.appendChild(previewContent)

  container.appendChild(editorPanel)
  container.appendChild(previewPanel)

  return container
}

function buildTree(files: FileItem[], parentElement: HTMLElement, depth: number = 0) {
  files.forEach(file => {
    const item = document.createElement('div')
    item.className = file.isDirectory ? 'folder-item' : 'file-item'
    item.style.paddingLeft = `${depth * 16 + 12}px`

    const icon = document.createElement('div')
    icon.className = 'file-icon'
    if (file.isDirectory) {
      icon.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 7V5C3 3.89543 3.89543 3 5 3H9L11 5H19C20.1046 5 21 5.89543 21 7V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" fill="currentColor" opacity="0.3"/>
        <path d="M3 7V5C3 3.89543 3.89543 3 5 3H9L11 5H19C20.1046 5 21 5.89543 21 7V17C21 18.1046 20.1046 19 19 19H5C3.89543 19 3 18.1046 3 17V7Z" stroke="currentColor" stroke-width="2"/>
      </svg>`
    } else {
      icon.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" fill="currentColor" opacity="0.2"/>
        <path d="M14 2V8H20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M6 2H14L20 8V20C20 21.1046 19.1046 22 18 22H6C4.89543 22 4 21.1046 4 20V4C4 2.89543 4.89543 2 6 2Z" stroke="currentColor" stroke-width="2"/>
      </svg>`
    }

    const filename = document.createElement('div')
    filename.className = 'filename'
    filename.textContent = file.name

    item.appendChild(icon)
    item.appendChild(filename)

    if (file.isDirectory) {
      item.addEventListener('click', () => toggleFolder(item, file))
    } else if (file.name.endsWith('.md')) {
      item.addEventListener('click', () => openMarkdownFile(file.path))
    }

    parentElement.appendChild(item)

    if (file.isDirectory && file.children) {
      const childrenContainer = document.createElement('div')
      childrenContainer.style.display = 'none'
      buildTree(file.children, childrenContainer, depth + 1)
      parentElement.appendChild(childrenContainer)
    }
  })
}

function toggleFolder(item: HTMLElement, file: FileItem) {
  const nextSibling = item.nextElementSibling as HTMLElement | null
  if (nextSibling && nextSibling.style.display === 'none') {
    nextSibling.style.display = 'block'
  } else if (nextSibling) {
    nextSibling.style.display = 'none'
  }

  if (!file.children) {
    loadFolderContent(file.path).then(children => {
      file.children = children
      if (nextSibling) {
        buildTree(children, nextSibling, (parseInt(item.style.paddingLeft || '12') / 16 - 1))
      }
    })
  }
}

async function loadFolder() {
  try {
    const selected = await open({
      directory: true,
      title: '选择文件夹'
    })

    if (selected) {
      state.files = await loadFolderContent(selected as string)
      const folderTree = document.querySelector('.folder-tree') as HTMLElement
      folderTree.innerHTML = ''
      buildTree(state.files, folderTree)
    }
  } catch (err) {
    console.error('Failed to load folder:', err)
    showToast('加载文件夹失败')
  }
}

async function loadFolderContent(folderPath: string): Promise<FileItem[]> {
  try {
    const entries = await readDir(folderPath)
    const items: FileItem[] = []

    for (const entry of entries) {
      items.push({
        name: entry.name,
        path: await join(folderPath, entry.name),
        isDirectory: entry.isDirectory || false,
        children: entry.isDirectory ? undefined : undefined
      })
    }

    items.sort((a, b) => {
      if (a.isDirectory && !b.isDirectory) return -1
      if (!a.isDirectory && b.isDirectory) return 1
      return a.name.localeCompare(b.name)
    })

    return items
  } catch (err) {
    console.error('Failed to read directory:', err)
    return []
  }
}

async function openFile() {
  try {
    const selected = await open({
      multiple: false,
      filters: [
        { name: 'Markdown Files', extensions: ['md'] },
        { name: 'All Files', extensions: ['*'] }
      ],
      title: '打开 Markdown 文件'
    })

    if (selected) {
      await openMarkdownFile(selected as string)
    }
  } catch (err) {
    console.error('Failed to open file:', err)
    showToast('打开文件失败')
  }
}

async function openMarkdownFile(filePath: string) {
  try {
    const content = await readTextFile(filePath)
    state.currentFile = filePath
    state.currentContent = content
    state.hasChanges = false

    const textarea = document.querySelector('.textarea') as HTMLTextAreaElement
    textarea.value = content

    await updatePreview(content)
    document.title = `${await basename(filePath)} - Markdown Opener`
  } catch (err) {
    console.error('Failed to read file:', err)
    showToast('无法读取文件')
  }
}

async function saveFile() {
  if (!state.currentFile) {
    await saveAsFile()
    return
  }

  try {
    const textarea = document.querySelector('.textarea') as HTMLTextAreaElement
    await writeFile(state.currentFile, textarea.value)
    state.hasChanges = false
    showToast('文件已保存')
  } catch (err) {
    console.error('Failed to save file:', err)
    showToast('保存失败')
  }
}

async function saveAsFile() {
  try {
    const selected = await save({
      filters: [
        { name: 'Markdown Files', extensions: ['md'] },
        { name: 'All Files', extensions: ['*'] }
      ],
      title: '保存文件'
    })

    if (selected) {
      const textarea = document.querySelector('.textarea') as HTMLTextAreaElement
      await writeFile(selected as string, textarea.value)
      state.currentFile = selected as string
      state.hasChanges = false
      showToast('文件已保存')
      document.title = `${await basename(selected as string)} - Markdown Opener`
    }
  } catch (err) {
    console.error('Failed to save file:', err)
    showToast('保存失败')
  }
}

function handleTextChange() {
  state.hasChanges = true
  const textarea = document.querySelector('.textarea') as HTMLTextAreaElement
  updatePreview(textarea.value)
}

async function updatePreview(content: string) {
  const previewContent = document.querySelector('.preview-content') as HTMLElement

  try {
    let html = marked.parse(content) as string

    html = html.replace(/\$\$(.*?)\$\$/gs, (_, formula) => {
      try {
        return katex.renderToString(formula.trim(), {
          throwOnError: false,
          displayMode: true
        })
      } catch {
        return `<span class="math-error">${formula}</span>`
      }
    })

    html = html.replace(/\$(.*?)\$/g, (_, formula) => {
      try {
        return katex.renderToString(formula.trim(), {
          throwOnError: false,
          displayMode: false
        })
      } catch {
        return `<span class="math-error">${formula}</span>`
      }
    })

    previewContent.innerHTML = html

    previewContent.querySelectorAll('pre code').forEach((block) => {
      hljs.highlightElement(block as HTMLElement)
    })

    const mermaidBlocks = previewContent.querySelectorAll('pre code.language-mermaid')
    for (const block of mermaidBlocks) {
      const parentPre = block.parentElement as HTMLElement
      const code = block.textContent || ''
      try {
        const result = await mermaid.render(`mermaid-${Math.random().toString(36)}`, code.trim())
        const mermaidDiv = document.createElement('div')
        mermaidDiv.innerHTML = result.svg
        parentPre.replaceWith(mermaidDiv)
      } catch {
        console.log('Failed to render mermaid')
      }
    }
  } catch (err) {
    previewContent.innerHTML = `<p style="color: red;">渲染错误: ${err}</p>`
  }
}

function showToast(message: string) {
  const toast = document.createElement('div')
  toast.className = 'toast'
  toast.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  ${message}`

  document.body.appendChild(toast)

  setTimeout(() => {
    toast.remove()
  }, 3000)
}

function toggleTheme() {
  state.isDark = !state.isDark
  document.documentElement.setAttribute('data-theme', state.isDark ? 'dark' : 'light')
  localStorage.setItem('theme', state.isDark ? 'dark' : 'light')

  const themeToggle = document.querySelector('.theme-toggle') as HTMLElement
  themeToggle.innerHTML = state.isDark 
    ? `<svg class="theme-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`
    : `<svg class="theme-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 3V5M12 19V21M4.22 4.22L5.64 5.64M18.36 18.36L19.78 19.78M3 12H5M19 12H21M4.22 19.78L5.64 18.36M18.36 5.64L19.78 4.22M16 12C16 14.2091 14.2091 16 12 16C9.79086 16 8 14.2091 8 12C8 9.79086 9.79086 8 12 8C14.2091 8 16 9.79086 16 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`
}

function handleDrop(e: DragEvent) {
  e.preventDefault()

  const files = e.dataTransfer?.files
  if (!files || files.length === 0) return

  const file = files[0]
  if (file.name.endsWith('.md')) {
    const filePath = (file as unknown as { path?: string }).path || file.name
    openMarkdownFile(filePath)
  }
}

function handleDragOver(e: DragEvent) {
  e.preventDefault()
}

async function init() {
  const header = createHeader()
  const sidebar = createSidebar()
  const editorContainer = createEditorContainer()

  app.appendChild(header)

  const mainContent = document.createElement('div')
  mainContent.className = 'main-content'
  mainContent.appendChild(sidebar)
  mainContent.appendChild(editorContainer)

  app.appendChild(mainContent)

  const editorPanel = document.querySelector('.editor-panel') as HTMLElement
  editorPanel.addEventListener('drop', handleDrop)
  editorPanel.addEventListener('dragover', handleDragOver)

  const previewPanel = document.querySelector('.preview-panel') as HTMLElement
  previewPanel.addEventListener('drop', handleDrop)
  previewPanel.addEventListener('dragover', handleDragOver)

  const theme = localStorage.getItem('theme')
  if (theme === 'dark') {
    state.isDark = true
    document.documentElement.setAttribute('data-theme', 'dark')
    const themeToggle = document.querySelector('.theme-toggle') as HTMLElement
    themeToggle.innerHTML = `<svg class="theme-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`
  }

  try {
    const args = await getArgs()
    if (args && args.length > 0) {
      const filePath = args[0]
      if (filePath && filePath.endsWith('.md')) {
        openMarkdownFile(filePath)
      }
    }
  } catch (e) {
    console.log('No command line arguments')
  }
}

init()
