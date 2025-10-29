<template>
  <div class="search-section">
    <div class="search-container">
      <el-input
        v-model="searchValue"
        placeholder="搜索文档标题、摘要..."
        size="large"
        clearable
        @input="handleInput"
        @clear="handleClear"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon class="search-prefix-icon">
            <Search />
          </el-icon>
        </template>
        <template #suffix>
          <el-button
            type="primary"
            :icon="Search"
            @click="handleSearch"
            :disabled="!searchValue.trim()"
            class="search-button"
          >
            搜索
          </el-button>
        </template>
      </el-input>

      <!-- 搜索建议 -->
      <div v-if="showSuggestions && suggestions.length > 0" class="search-suggestions">
        <div class="suggestions-header">搜索建议</div>
        <div
          v-for="suggestion in suggestions"
          :key="suggestion"
          class="suggestion-item"
          @click="selectSuggestion(suggestion)"
        >
          <el-icon><Search /></el-icon>
          <span>{{ suggestion }}</span>
        </div>
      </div>

      <!-- 搜索历史 -->
      <div v-if="showHistory && searchHistory.length > 0" class="search-history">
        <div class="history-header">
          <span>最近搜索</span>
          <el-button text @click="clearHistory">清空</el-button>
        </div>
        <div class="history-tags">
          <el-tag
            v-for="item in searchHistory"
            :key="item"
            @click="selectSuggestion(item)"
            @close="removeFromHistory(item)"
            closable
            class="history-tag"
          >
            {{ item }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '搜索文档标题、摘要...'
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'search', 'clear'])

// 响应式数据
const searchValue = ref(props.modelValue)
const showSuggestions = ref(false)
const showHistory = ref(false)
const searchHistory = ref([])

// 搜索建议（可以根据实际需求从API获取）
const suggestions = computed(() => {
  if (!searchValue.value.trim()) return []

  const commonKeywords = [
    'Vue3', 'React', 'JavaScript', 'TypeScript', 'Node.js',
    'Python', 'FastAPI', 'Docker', 'MySQL', 'Redis',
    'Linux', 'Git', 'Webpack', 'Vite', 'Element Plus'
  ]

  return commonKeywords
    .filter(keyword =>
      keyword.toLowerCase().includes(searchValue.value.toLowerCase()) &&
      keyword.toLowerCase() !== searchValue.value.toLowerCase()
    )
    .slice(0, 5)
})

// 监听输入值变化
watch(() => props.modelValue, (newValue) => {
  searchValue.value = newValue
})

watch(searchValue, (newValue) => {
  emit('update:modelValue', newValue)
})

// 生命周期
onMounted(() => {
  loadSearchHistory()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 方法
const handleInput = (value) => {
  searchValue.value = value
  showSuggestions.value = value.trim().length > 0
  showHistory.value = value.trim().length === 0
}

const handleSearch = () => {
  const keyword = searchValue.value.trim()
  if (!keyword) return

  // 添加到搜索历史
  addToHistory(keyword)

  // 隐藏建议和历史
  showSuggestions.value = false
  showHistory.value = false

  // 触发搜索事件
  emit('search', keyword)
}

const handleClear = () => {
  searchValue.value = ''
  showSuggestions.value = false
  showHistory.value = true
  emit('clear')
}

const selectSuggestion = (suggestion) => {
  searchValue.value = suggestion
  showSuggestions.value = false
  showHistory.value = false
  handleSearch()
}

const addToHistory = (keyword) => {
  // 移除重复项
  const filtered = searchHistory.value.filter(item => item !== keyword)
  // 添加到开头
  searchHistory.value = [keyword, ...filtered].slice(0, 10)
  // 保存到本地存储
  saveSearchHistory()
}

const removeFromHistory = (keyword) => {
  searchHistory.value = searchHistory.value.filter(item => item !== keyword)
  saveSearchHistory()
}

const clearHistory = () => {
  searchHistory.value = []
  saveSearchHistory()
}

const loadSearchHistory = () => {
  try {
    const history = localStorage.getItem('tech_square_search_history')
    if (history) {
      searchHistory.value = JSON.parse(history)
    }
  } catch (error) {
    console.error('加载搜索历史失败:', error)
  }
}

const saveSearchHistory = () => {
  try {
    localStorage.setItem('tech_square_search_history', JSON.stringify(searchHistory.value))
  } catch (error) {
    console.error('保存搜索历史失败:', error)
  }
}

// 点击外部隐藏建议
const handleClickOutside = () => {
  showSuggestions.value = false
  showHistory.value = false
}
</script>

<style scoped>
.search-section {
  margin-bottom: 32px;
  position: relative;
}

.search-container {
  max-width: 600px;
  margin: 0 auto;
  position: relative;
}

.search-prefix-icon {
  color: #656d76;
}

.search-button {
  border-radius: 0 6px 6px 0;
  border-left: none;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
}

:deep(.el-input__suffix) {
  padding: 0;
}

/* 搜索建议 */
.search-suggestions,
.search-history {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e1e4e8;
  border-top: none;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.suggestions-header,
.history-header {
  padding: 12px 16px;
  font-size: 12px;
  color: #656d76;
  font-weight: 500;
  border-bottom: 1px solid #f6f8fa;
  background: #fafbfc;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #24292f;
  transition: background-color 0.2s ease;
}

.suggestion-item:hover {
  background: #f6f8fa;
}

.suggestion-item .el-icon {
  color: #656d76;
  font-size: 14px;
}

/* 搜索历史 */
.history-tags {
  padding: 12px 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-tag {
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-tag:hover {
  background: #e3f2fd;
  border-color: #007AFF;
}

/* 响应式 */
@media (max-width: 768px) {
  .search-container {
    max-width: 100%;
  }

  :deep(.el-input--large .el-input__wrapper) {
    font-size: 16px; /* 防止iOS缩放 */
  }

  .search-button {
    font-size: 14px;
    padding: 0 12px;
  }
}
</style>
