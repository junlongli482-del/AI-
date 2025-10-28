<template>
  <div class="markdown-editor-container">
    <div ref="editorRef" class="editor-wrapper"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import '@toast-ui/editor/dist/toastui-editor.css'
import { Editor } from '@toast-ui/editor'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  sessionId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['content-change', 'ready', 'update:content'])

// 响应式数据
const editorRef = ref(null)
const editorInstance = ref(null)
const isReady = ref(false)

// 编辑器初始化
onMounted(async () => {
  await nextTick()
  initializeEditor()
})

onUnmounted(() => {
  if (editorInstance.value) {
    editorInstance.value.destroy()
  }
})

const initializeEditor = () => {
  if (!editorRef.value) return

  try {
    editorInstance.value = new Editor({
      el: editorRef.value,
      height: '100%',
      initialEditType: 'markdown',
      previewStyle: 'tab',
      hideModeSwitch: true,
      initialValue: props.content || '',
      placeholder: '开始编写您的文档...',
      autofocus: true,
      toolbarItems: [
        ['heading', 'bold', 'italic', 'strike'],
        ['hr', 'quote'],
        ['ul', 'ol', 'task', 'indent', 'outdent'],
        ['table', 'link'],
        ['code', 'codeblock'],
        ['scrollSync']
      ],
      events: {
        change: handleEditorChange
      }
    })

    isReady.value = true

    // 详细查看所有方法
    const methods = []
    let obj = editorInstance.value
    while (obj) {
      methods.push(...Object.getOwnPropertyNames(obj))
      obj = Object.getPrototypeOf(obj)
      if (obj === Object.prototype) break
    }
    const uniqueMethods = [...new Set(methods)].sort()

    console.log('=== 所有66个方法 ===')
    uniqueMethods.forEach((method, index) => {
      console.log(`${index + 1}. ${method}`)
    })

    // 特别检查可能的撤销重做方法
    const possibleUndoRedo = uniqueMethods.filter(method =>
      method.includes('undo') ||
      method.includes('redo') ||
      method.includes('history') ||
      method.includes('History') ||
      method.includes('command') ||
      method.includes('Command') ||
      method.includes('exec')
    )
    console.log('可能的撤销重做方法:', possibleUndoRedo)

    emit('ready')
  } catch (error) {
    console.error('编辑器初始化失败:', error)
  }
}

// 内容变化处理
const handleEditorChange = () => {
  if (!editorInstance.value || !isReady.value) return

  const newContent = editorInstance.value.getMarkdown()
  emit('content-change', newContent)
  emit('update:content', newContent)
}

// 监听外部内容变化
watch(() => props.content, (newContent) => {
  if (!editorInstance.value || !isReady.value) return

  const currentContent = editorInstance.value.getMarkdown()
  if (newContent !== currentContent) {
    editorInstance.value.setMarkdown(newContent || '', false)
  }
})

// 获取选中文本或全部内容
const getSelectedText = () => {
  if (!editorInstance.value || !isReady.value) {
    return {
      hasSelection: false,
      content: props.content || '',
      length: (props.content || '').length
    }
  }

  try {
    const selectedText = editorInstance.value.getSelectedText()

    if (selectedText && selectedText.trim()) {
      return {
        hasSelection: true,
        content: selectedText,
        length: selectedText.length
      }
    } else {
      const fullContent = editorInstance.value.getMarkdown()
      return {
        hasSelection: false,
        content: fullContent,
        length: fullContent.length
      }
    }
  } catch (error) {
    console.error('获取选中文本失败:', error)
    const fullContent = props.content || ''
    return {
      hasSelection: false,
      content: fullContent,
      length: fullContent.length
    }
  }
}

// 应用优化结果
const applyOptimization = (optimizedContent, hasSelection) => {
  if (!editorInstance.value || !isReady.value) return

  try {
    if (hasSelection) {
      // 替换选中的内容
      editorInstance.value.replaceSelection(optimizedContent)
    } else {
      // 替换全部内容
      editorInstance.value.setMarkdown(optimizedContent, false)
    }

    // 立即获取新内容并触发更新
    nextTick(() => {
      const newContent = editorInstance.value.getMarkdown()
      emit('content-change', newContent)
      emit('update:content', newContent)
    })
  } catch (error) {
    console.error('应用优化失败:', error)
  }
}

// 获取编辑器实例（用于外部调用）
const getInstance = () => {
  return editorInstance.value
}

// 设置内容
const setContent = (content) => {
  if (!editorInstance.value || !isReady.value) return

  try {
    editorInstance.value.setMarkdown(content || '', false)
  } catch (error) {
    console.error('设置内容失败:', error)
  }
}

// 获取内容
const getContent = () => {
  if (!editorInstance.value || !isReady.value) return ''

  try {
    return editorInstance.value.getMarkdown()
  } catch (error) {
    console.error('获取内容失败:', error)
    return ''
  }
}

// 聚焦编辑器
const focus = () => {
  if (!editorInstance.value || !isReady.value) return

  try {
    editorInstance.value.focus()
  } catch (error) {
    console.error('聚焦失败:', error)
  }
}


// 撤销
const undo = () => {
  if (!editorInstance.value || !isReady.value) return

  try {
    // 使用新版本的命令系统
    editorInstance.value.exec('undo')
    console.log('撤销执行成功')
  } catch (error) {
    console.error('撤销失败:', error)
  }
}

// 重做
const redo = () => {
  if (!editorInstance.value || !isReady.value) return

  try {
    // 使用新版本的命令系统
    editorInstance.value.exec('redo')
    console.log('重做执行成功')
  } catch (error) {
    console.error('重做失败:', error)
  }
}

// 检查是否可以撤销
const canUndo = () => {
  if (!editorInstance.value || !isReady.value) return false

  try {
    // 检查命令管理器是否有撤销历史
    const commandManager = editorInstance.value.commandManager
    if (commandManager && commandManager.undoStack) {
      return commandManager.undoStack.length > 0
    }
    return false
  } catch (error) {
    return false
  }
}

// 检查是否可以重做
const canRedo = () => {
  if (!editorInstance.value || !isReady.value) return false

  try {
    // 检查命令管理器是否有重做历史
    const commandManager = editorInstance.value.commandManager
    if (commandManager && commandManager.redoStack) {
      return commandManager.redoStack.length > 0
    }
    return false
  } catch (error) {
    return false
  }
}



// 暴露方法给父组件
defineExpose({
  getSelectedText,
  applyOptimization,
  getInstance,
  setContent,
  getContent,
  focus,
  undo,
  redo,
  canUndo,
  canRedo
})

</script>

<style scoped>
.markdown-editor-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-wrapper {
  flex: 1;
  overflow: hidden;
}

/* Toast UI Editor 样式定制 */
:deep(.toastui-editor-defaultUI) {
  height: 100%;
  border: none;
}

:deep(.toastui-editor-main-container) {
  height: 100%;
}

:deep(.toastui-editor-toolbar) {
  border-bottom: 1px solid #d0d7de;
  background: #f6f8fa;
  padding: 8px 16px;
}

:deep(.toastui-editor-toolbar-group) {
  margin-right: 16px;
}

:deep(.toastui-editor-toolbar-item) {
  margin-right: 4px;
}

:deep(.toastui-editor-toolbar-item button) {
  border: none;
  background: transparent;
  color: #656d76;
  border-radius: 4px;
  padding: 6px 8px;
  transition: all 0.2s ease;
}

:deep(.toastui-editor-toolbar-item button:hover) {
  background: #ffffff;
  color: #24292f;
}

:deep(.toastui-editor-toolbar-item button.active) {
  background: #007AFF;
  color: white;
}

:deep(.toastui-editor-md-container) {
  background: #ffffff;
}

:deep(.toastui-editor-md-container .CodeMirror) {
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', 'Source Code Pro', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #24292f;
}

:deep(.toastui-editor-md-container .CodeMirror-lines) {
  padding: 16px;
}

:deep(.toastui-editor-md-container .CodeMirror-placeholder) {
  color: #656d76;
  font-style: italic;
}

/* 代码块样式 */
:deep(.toastui-editor-md-container .cm-header-1) {
  font-size: 24px;
  font-weight: 600;
  color: #24292f;
}

:deep(.toastui-editor-md-container .cm-header-2) {
  font-size: 20px;
  font-weight: 600;
  color: #24292f;
}

:deep(.toastui-editor-md-container .cm-header-3) {
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
}

:deep(.toastui-editor-md-container .cm-strong) {
  font-weight: 600;
  color: #24292f;
}

:deep(.toastui-editor-md-container .cm-em) {
  font-style: italic;
  color: #24292f;
}

:deep(.toastui-editor-md-container .cm-strikethrough) {
  text-decoration: line-through;
  color: #656d76;
}

:deep(.toastui-editor-md-container .cm-code) {
  background: #f6f8fa;
  color: #d73a49;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
}

:deep(.toastui-editor-md-container .cm-link) {
  color: #007AFF;
  text-decoration: underline;
}

:deep(.toastui-editor-md-container .cm-quote) {
  color: #656d76;
  font-style: italic;
}

/* 滚动条样式 */
:deep(.CodeMirror-scroll::-webkit-scrollbar) {
  width: 6px;
}

:deep(.CodeMirror-scroll::-webkit-scrollbar-thumb) {
  background: #d0d7de;
  border-radius: 3px;
}

:deep(.CodeMirror-scroll::-webkit-scrollbar-thumb:hover) {
  background: #656d76;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.toastui-editor-toolbar) {
    padding: 4px 8px;
  }

  :deep(.toastui-editor-toolbar-group) {
    margin-right: 8px;
  }

  :deep(.toastui-editor-md-container .CodeMirror-lines) {
    padding: 12px;
  }

  :deep(.toastui-editor-md-container .CodeMirror) {
    font-size: 13px;
  }
}
</style>
