<template>
  <el-dialog
    v-model="visible"
    title="AI内容优化"
    width="800px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    destroy-on-close
    @close="handleClose"
  >
    <!-- 优化配置阶段 -->
    <div v-if="currentStep === 'config'" class="optimize-config">
      <!-- 优化范围显示 -->
      <div class="optimize-scope">
        <div class="scope-info">
          <span class="scope-label">优化范围：</span>
          <span class="scope-value">
            {{ optimizeData?.hasSelection ? '选中内容' : '全部内容' }}
            ({{ optimizeData?.length || 0 }}字)
          </span>
        </div>

        <!-- 内容预览 -->
        <div class="content-preview">
          <div class="preview-label">内容预览：</div>
          <div class="preview-text">
            {{ getContentPreview() }}
          </div>
        </div>
      </div>

      <!-- 优化类型选择 -->
      <div class="optimize-types">
        <div class="types-label">选择优化类型：</div>
        <div class="types-grid">
          <div
            v-for="type in optimizationTypes"
            :key="type.value"
            class="type-card"
            :class="{ active: selectedType === type.value }"
            @click="selectedType = type.value"
          >
            <div class="type-radio">
              <input
                type="radio"
                :value="type.value"
                v-model="selectedType"
                :id="type.value"
              />
              <label :for="type.value" class="radio-label"></label>
            </div>
            <div class="type-info">
              <div class="type-title">{{ type.label }}</div>
              <div class="type-desc">{{ type.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 优化进行中阶段 -->
    <div v-else-if="currentStep === 'processing'" class="optimize-processing">
      <div class="processing-content">
        <el-icon class="processing-icon is-loading"><Loading /></el-icon>
        <div class="processing-text">
          <div class="processing-title">AI正在优化您的内容...</div>
          <div class="processing-desc">这可能需要几秒钟，请稍候</div>
        </div>
      </div>
    </div>

    <!-- 优化结果阶段 -->
    <div v-else-if="currentStep === 'result'" class="optimize-result">
      <!-- 结果对比 -->
      <div class="result-comparison">
        <div class="comparison-panel">
          <div class="panel-header">
            <span class="panel-title">原始内容</span>
            <span class="content-length">({{ originalContent.length }}字)</span>
          </div>
          <div class="panel-content original-content">
            {{ originalContent }}
          </div>
        </div>

        <div class="comparison-divider">
          <el-icon><Right /></el-icon>
        </div>

        <div class="comparison-panel">
          <div class="panel-header">
            <span class="panel-title">优化后内容</span>
            <span class="content-length">({{ optimizedContent.length }}字)</span>
            <!-- 添加复制按钮 -->
            <el-button
              size="small"
              type="primary"
              @click="copyOptimizedContent"
              style="margin-left: 8px;"
            >
              <el-icon><DocumentCopy /></el-icon>
              复制
            </el-button>
          </div>
          <div class="panel-content optimized-content">
            {{ optimizedContent }}
          </div>
        </div>
      </div>

      <!-- 优化说明 -->
      <div v-if="optimizationNote" class="optimization-note">
        <div class="note-header">
          <el-icon><InfoFilled /></el-icon>
          <span>优化说明</span>
        </div>
        <div class="note-content">{{ optimizationNote }}</div>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="currentStep === 'error'" class="optimize-error">
      <div class="error-content">
        <el-icon class="error-icon"><WarningFilled /></el-icon>
        <div class="error-text">
          <div class="error-title">优化失败</div>
          <div class="error-desc">{{ errorMessage }}</div>
        </div>
      </div>
    </div>

    <!-- 对话框底部按钮 -->
    <template #footer>
      <div class="dialog-footer">
        <!-- 配置阶段按钮 -->
        <template v-if="currentStep === 'config'">
          <el-button @click="handleClose">取消</el-button>
          <el-button
            type="primary"
            :disabled="!selectedType || !optimizeData?.content"
            @click="startOptimization"
          >
            开始优化
          </el-button>
        </template>

        <!-- 处理中阶段按钮 -->
        <template v-else-if="currentStep === 'processing'">
          <el-button disabled>处理中...</el-button>
        </template>

        <!-- 结果阶段按钮 -->
        <template v-else-if="currentStep === 'result'">
          <el-button @click="handleClose">取消</el-button>
          <el-button @click="restartOptimization">重新优化</el-button>
        </template>

        <!-- 错误阶段按钮 -->
        <template v-else-if="currentStep === 'error'">
          <el-button @click="handleClose">关闭</el-button>
          <el-button type="primary" @click="restartOptimization">重试</el-button>
        </template>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Loading,
  Right,
  InfoFilled,
  WarningFilled,
  DocumentCopy  // 新增
} from '@element-plus/icons-vue'
import {
  optimizeContent,
  getEditorConfig
} from '@/api/v2/md_editor/index'

// 复制优化后的内容
const copyOptimizedContent = async () => {
  try {
    // 使用传统的 document.execCommand 方法（兼容HTTP协议）
    const textArea = document.createElement('textarea')
    textArea.value = optimizedContent.value
    textArea.style.position = 'fixed'
    textArea.style.left = '-999999px'
    textArea.style.top = '-999999px'
    textArea.style.opacity = '0'
    document.body.appendChild(textArea)
    textArea.focus()
    textArea.select()

    try {
      const successful = document.execCommand('copy')
      if (successful) {
        ElMessage.success('内容已复制到剪贴板')
      } else {
        throw new Error('复制命令执行失败')
      }
    } finally {
      document.body.removeChild(textArea)
    }
  } catch (error) {
    console.error('复制失败:', error)
    // 降级方案：选中文本让用户手动复制
    try {
      const range = document.createRange()
      const selection = window.getSelection()
      const optimizedPanel = document.querySelector('.optimized-content')

      if (optimizedPanel) {
        range.selectNodeContents(optimizedPanel)
        selection.removeAllRanges()
        selection.addRange(range)
        ElMessage({
          message: '已选中优化后的内容，请按 Ctrl+C 复制',
          type: 'info',
          duration: 4000
        })
      } else {
        ElMessage.error('复制失败，请手动选择文本复制')
      }
    } catch (selectError) {
      ElMessage.error('复制失败，请手动选择文本复制')
    }
  }
}

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  sessionId: {
    type: Number,
    default: null
  },
  optimizeData: {
    type: Object,
    default: null
    // {
    //   hasSelection: true/false,
    //   content: "要优化的内容",
    //   length: 45
    // }
  }
})

const emit = defineEmits(['update:modelValue'])

// 响应式数据
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const currentStep = ref('config') // 'config' | 'processing' | 'result' | 'error'
const selectedType = ref('general')
const optimizationTypes = ref([])
const originalContent = ref('')
const optimizedContent = ref('')
const optimizationId = ref(null)
const optimizationNote = ref('')
const errorMessage = ref('')

// 监听对话框打开
watch(visible, async (newVisible) => {
  if (newVisible) {
    await initializeDialog()
  } else {
    resetDialog()
  }
})

// 初始化对话框
const initializeDialog = async () => {
  try {
    // 获取优化类型配置
    const config = await getEditorConfig()
    optimizationTypes.value = config.optimization_types || [
      {
        value: 'general',
        label: '通用优化',
        description: '提升表达质量和可读性'
      },
      {
        value: 'grammar',
        label: '语法检查',
        description: '修正语法和拼写错误'
      },
      {
        value: 'structure',
        label: '结构优化',
        description: '改善文档结构和逻辑'
      },
      {
        value: 'expand',
        label: '内容扩展',
        description: '丰富内容细节和深度'
      }
    ]

    // 重置状态
    currentStep.value = 'config'
    selectedType.value = 'general'
    originalContent.value = props.optimizeData?.content || ''
  } catch (error) {
    console.error('初始化对话框失败:', error)
    ElMessage.error('初始化失败')
  }
}

// 重置对话框
const resetDialog = () => {
  currentStep.value = 'config'
  selectedType.value = 'general'
  originalContent.value = ''
  optimizedContent.value = ''
  optimizationId.value = null
  optimizationNote.value = ''
  errorMessage.value = ''
}

// 获取内容预览
const getContentPreview = () => {
  const content = props.optimizeData?.content || ''
  if (content.length <= 100) {
    return content
  }
  return content.substring(0, 97) + '...'
}

// 开始优化
const startOptimization = async () => {
  if (!props.sessionId || !props.optimizeData?.content) {
    ElMessage.error('缺少必要参数')
    return
  }

  currentStep.value = 'processing'

  try {
    const response = await optimizeContent(props.sessionId, {
      content: props.optimizeData.content,
      optimization_type: selectedType.value
    })

    if (response.success) {
      originalContent.value = response.original_content
      optimizedContent.value = response.optimized_content
      optimizationId.value = response.optimization_id
      optimizationNote.value = response.note || ''
      currentStep.value = 'result'
    } else {
      throw new Error(response.message || '优化失败')
    }
  } catch (error) {
    console.error('优化失败:', error)
    errorMessage.value = error.message || '优化过程中发生错误'
    currentStep.value = 'error'
  }
}

// 重新优化
const restartOptimization = () => {
  currentStep.value = 'config'
  optimizedContent.value = ''
  optimizationId.value = null
  optimizationNote.value = ''
  errorMessage.value = ''
}

// 关闭对话框
const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
/* 优化配置 */
.optimize-config {
  padding: 8px 0;
}

.optimize-scope {
  margin-bottom: 24px;
  padding: 16px;
  background: #f6f8fa;
  border-radius: 8px;
}

.scope-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.scope-label {
  font-weight: 600;
  color: #24292f;
}

.scope-value {
  color: #656d76;
  font-size: 14px;
}

.content-preview {
  margin-top: 12px;
}

.preview-label {
  font-size: 13px;
  color: #656d76;
  margin-bottom: 8px;
}

.preview-text {
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
  line-height: 1.5;
  color: #24292f;
  max-height: 120px;
  overflow-y: auto;
  word-break: break-word;
}

.optimize-types {
  margin-bottom: 16px;
}

.types-label {
  font-weight: 600;
  color: #24292f;
  margin-bottom: 16px;
}

.types-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.type-option {
  margin: 0;
  padding: 16px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.type-option:hover {
  border-color: #007AFF;
  background: #f6f8fa;
}

.type-option.is-checked {
  border-color: #007AFF;
  background: #f0f8ff;
}

.type-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-left: 8px;
}

.type-title {
  font-weight: 600;
  color: #24292f;
  font-size: 14px;
}

.type-desc {
  color: #656d76;
  font-size: 13px;
}

/* 处理中状态 */
.optimize-processing {
  padding: 48px 0;
  text-align: center;
}

.processing-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.processing-icon {
  font-size: 32px;
  color: #007AFF;
}

.processing-title {
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
}

.processing-desc {
  font-size: 14px;
  color: #656d76;
}

/* 优化结果 */
.optimize-result {
  padding: 8px 0;
}

.result-comparison {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.comparison-panel {
  flex: 1;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  overflow: hidden;
}

.panel-header {
  background: #f6f8fa;
  padding: 12px 16px;
  border-bottom: 1px solid #d0d7de;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  font-weight: 600;
  color: #24292f;
  font-size: 14px;
}

.content-length {
  font-size: 12px;
  color: #656d76;
}

.panel-content {
  padding: 16px;
  max-height: 200px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
  white-space: pre-wrap;
}

.original-content {
  color: #656d76;
  background: #f8f9fa;
}

.optimized-content {
  color: #24292f;
  background: #ffffff;
}

.comparison-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #007AFF;
  font-size: 20px;
  flex-shrink: 0;
}

.optimization-note {
  background: #f0f8ff;
  border: 1px solid #b3d8ff;
  border-radius: 8px;
  padding: 16px;
}

.note-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #0969da;
}

.note-content {
  color: #24292f;
  font-size: 14px;
  line-height: 1.5;
}

/* 错误状态 */
.optimize-error {
  padding: 48px 0;
  text-align: center;
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.error-icon {
  font-size: 32px;
  color: #f56c6c;
}

.error-title {
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
}

.error-desc {
  font-size: 14px;
  color: #656d76;
}

/* 对话框底部 */
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 滚动条样式 */
.preview-text::-webkit-scrollbar,
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.preview-text::-webkit-scrollbar-thumb,
.panel-content::-webkit-scrollbar-thumb {
  background: #d0d7de;
  border-radius: 3px;
}

.preview-text::-webkit-scrollbar-thumb:hover,
.panel-content::-webkit-scrollbar-thumb:hover {
  background: #656d76;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-comparison {
    flex-direction: column;
  }

  .comparison-divider {
    transform: rotate(90deg);
    margin: 8px 0;
  }

  .panel-content {
    max-height: 150px;
  }
}

.optimize-types {
  margin-bottom: 16px;
}

.types-label {
  font-weight: 600;
  color: #24292f;
  margin-bottom: 16px;
  font-size: 14px;
}

.types-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.type-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border: 2px solid #d0d7de;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #ffffff;
}

.type-card:hover {
  border-color: #007AFF;
  background: #f6f8fa;
}

.type-card.active {
  border-color: #007AFF;
  background: #f0f8ff;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.1);
}

.type-radio {
  flex-shrink: 0;
  margin-top: 2px;
}

.type-radio input[type="radio"] {
  display: none;
}

.radio-label {
  display: block;
  width: 18px;
  height: 18px;
  border: 2px solid #d0d7de;
  border-radius: 50%;
  background: #ffffff;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.type-card.active .radio-label {
  border-color: #007AFF;
  background: #007AFF;
}

.type-card.active .radio-label::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffffff;
}

.type-info {
  flex: 1;
  min-width: 0;
}

.type-title {
  font-weight: 600;
  color: #24292f;
  font-size: 14px;
  margin-bottom: 4px;
  line-height: 1.3;
}

.type-desc {
  color: #656d76;
  font-size: 12px;
  line-height: 1.4;
  word-break: break-word;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .types-grid {
    grid-template-columns: 1fr;
  }

  .type-card {
    padding: 12px;
  }

  .type-title {
    font-size: 13px;
  }

  .type-desc {
    font-size: 11px;
  }
}
</style>
