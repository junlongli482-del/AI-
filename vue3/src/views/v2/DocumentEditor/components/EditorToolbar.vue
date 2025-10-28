<template>
  <div class="editor-toolbar">
    <!-- 左侧：视图切换按钮 + 撤销重做 -->
    <div class="toolbar-left">
      <div class="view-controls">
        <el-button
          :type="viewMode === 'edit' ? 'primary' : ''"
          :class="{ active: viewMode === 'edit' }"
          size="small"
          @click="$emit('view-change', 'edit')"
        >
          <el-icon><Edit /></el-icon>
          编辑
        </el-button>
        <el-button
          :type="viewMode === 'split' ? 'primary' : ''"
          :class="{ active: viewMode === 'split' }"
          size="small"
          @click="$emit('view-change', 'split')"
        >
          <el-icon><Operation /></el-icon>
          分屏
        </el-button>
        <el-button
          :type="viewMode === 'preview' ? 'primary' : ''"
          :class="{ active: viewMode === 'preview' }"
          size="small"
          @click="$emit('view-change', 'preview')"
        >
          <el-icon><View /></el-icon>
          预览
        </el-button>
      </div>

      <!-- 撤销/重做按钮 -->
      <div class="undo-redo-controls">
        <el-button
          size="small"
          :disabled="!canUndo"
          @click="$emit('undo')"
          title="撤销 (Ctrl+Z)"
        >
          <el-icon><RefreshLeft /></el-icon>
        </el-button>
        <el-button
          size="small"
          :disabled="!canRedo"
          @click="$emit('redo')"
          title="重做 (Ctrl+Y)"
        >
          <el-icon><RefreshRight /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 中间：文档信息 -->
    <div class="toolbar-center">
      <div class="document-info">
        <span class="doc-title">{{ displayTitle }}</span>
        <div class="doc-status">
          <span v-if="hasUnsavedChanges" class="unsaved-indicator">
            <el-icon><Warning /></el-icon>
            未保存
          </span>
          <span v-else-if="isSaving" class="saving-indicator">
            <el-icon class="is-loading"><Loading /></el-icon>
            保存中...
          </span>
          <span v-else class="saved-indicator">
            <el-icon><CircleCheck /></el-icon>
            已保存
          </span>
        </div>
      </div>
    </div>

    <!-- 右侧：操作按钮 -->
    <!-- 右侧：操作按钮 -->
    <div class="toolbar-right">
      <div class="action-controls">
        <!-- 统一的另存为按钮 -->
        <el-button
          type="primary"
          size="small"
          :loading="isSaving"
          @click="$emit('save-as')"
        >
          <el-icon v-if="!isSaving"><DocumentAdd /></el-icon>
          {{ saveButtonText }}
        </el-button>

        <!-- AI优化按钮 -->
        <el-button
          size="small"
          class="ai-button"
          @click="$emit('ai-optimize')"
        >
          <el-icon><MagicStick /></el-icon>
          AI优化
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Edit,
  Operation,
  View,
  Document,
  DocumentAdd,
  FolderAdd,  // 新增：另存为图标
  MagicStick,
  Warning,
  Loading,
  CircleCheck,
  RefreshLeft,
  RefreshRight
} from '@element-plus/icons-vue'
import { generateDefaultTitle } from '@/api/v2/md_editor/index'

const props = defineProps({
  viewMode: {
    type: String,
    required: true,
    validator: (value) => ['edit', 'split', 'preview'].includes(value)
  },
  sessionData: {
    type: Object,
    default: null
  },
  hasUnsavedChanges: {
    type: Boolean,
    default: false
  },
  isSaving: {
    type: Boolean,
    default: false
  },
  canUndo: {
    type: Boolean,
    default: false
  },
  canRedo: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'view-change',
  'save-as',        // 只保留另存为
  'ai-optimize',
  'undo',
  'redo'
])

// 计算属性
const displayTitle = computed(() => {
  if (!props.sessionData) return '加载中...'

  const title = props.sessionData.title
  if (title && title !== '未命名文档') {
    return title
  }

  // 如果没有标题或是默认标题，尝试从内容生成
  const content = props.sessionData.content
  if (content) {
    return generateDefaultTitle(content)
  }

  return '未命名文档'
})

// 是否为编辑模式
const isEditMode = computed(() => {
  return props.sessionData?.session_type === 'edit_document'
})

const saveButtonText = computed(() => {
  // 统一显示"保存文档"，不管是新建还是编辑
  return '保存文档'
})
</script>

<style scoped>
.editor-toolbar {
  height: 56px;
  border-bottom: 1px solid #d0d7de;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

/* 左侧视图控制 */
.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-controls {
  display: flex;
  gap: 4px;
  background: #f6f8fa;
  border-radius: 6px;
  padding: 4px;
}

.view-controls .el-button {
  margin: 0;
  border: none;
  background: transparent;
  color: #656d76;
  font-weight: 500;
}

.view-controls .el-button:hover {
  background: #ffffff;
  color: #24292f;
}

.view-controls .el-button.active,
.view-controls .el-button--primary {
  background: #ffffff;
  color: #007AFF;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 撤销/重做按钮 */
.undo-redo-controls {
  display: flex;
  gap: 4px;
}

.undo-redo-controls .el-button {
  margin: 0;
  border: 1px solid #d0d7de;
  background: #ffffff;
  color: #656d76;
  font-weight: 500;
  border-radius: 4px;
  padding: 4px 8px;
}

.undo-redo-controls .el-button:hover:not(:disabled) {
  background: #f6f8fa;
  color: #24292f;
  border-color: #007AFF;
}

.undo-redo-controls .el-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f6f8fa;
  border-color: #d0d7de;
  color: #8c959f;
}

/* 中间文档信息 */
.toolbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 0;
}

.document-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 0;
}

.doc-title {
  font-size: 14px;
  font-weight: 600;
  color: #24292f;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-status {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.unsaved-indicator {
  color: #f56c6c;
  display: flex;
  align-items: center;
  gap: 4px;
}

.saving-indicator {
  color: #409eff;
  display: flex;
  align-items: center;
  gap: 4px;
}

.saved-indicator {
  color: #67c23a;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 右侧操作控制 */
.toolbar-right {
  display: flex;
  align-items: center;
}

.action-controls {
  display: flex;
  gap: 8px;
}

.action-controls .el-button {
  font-weight: 500;
}

.ai-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.ai-button:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  color: white;
}

.ai-button:focus {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .editor-toolbar {
    padding: 0 16px;
    height: 48px;
  }

  .toolbar-left {
    gap: 8px;
  }

  .toolbar-center {
    display: none; /* 在小屏幕上隐藏文档信息 */
  }

  .view-controls {
    gap: 2px;
    padding: 2px;
  }

  .view-controls .el-button {
    padding: 4px 8px;
    font-size: 12px;
  }

  .undo-redo-controls .el-button {
    padding: 4px 6px;
  }

  .action-controls {
    gap: 4px;
  }

  .action-controls .el-button {
    padding: 4px 8px;
    font-size: 12px;
  }

  .action-controls .el-button span {
    display: none; /* 隐藏按钮文字，只显示图标 */
  }
}

@media (max-width: 480px) {
  .view-controls .el-button span {
    display: none; /* 超小屏幕只显示图标 */
  }
}
</style>
