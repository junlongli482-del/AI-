<template>
  <div class="emoji-picker">
    <el-popover
      placement="bottom-start"
      :width="300"
      trigger="click"
      popper-class="emoji-popover"
      :offset="8"
      :show-arrow="true"
    >
      <template #reference>
        <button class="emoji-trigger">
          <span class="emoji-icon">😀</span>
          <span class="emoji-text">表情</span>
        </button>
      </template>

      <div class="emoji-panel">
        <!-- 表情分类标签 -->
        <div class="emoji-tabs">
          <button
            v-for="category in emojiCategories"
            :key="category.name"
            :class="['emoji-tab', { active: activeCategory === category.name }]"
            @click="switchCategory(category.name)"
          >
            {{ category.icon }}
          </button>
        </div>

        <!-- 表情网格 -->
        <div class="emoji-grid">
          <button
            v-for="emoji in currentEmojis"
            :key="emoji"
            class="emoji-item"
            @click="selectEmoji(emoji)"
            :title="emoji"
          >
            {{ emoji }}
          </button>
        </div>

        <!-- 最近使用 -->
        <div v-if="recentEmojis.length > 0" class="recent-section">
          <div class="recent-title">最近使用</div>
          <div class="recent-emojis">
            <button
              v-for="emoji in recentEmojis"
              :key="emoji"
              class="emoji-item recent-emoji"
              @click="selectEmoji(emoji)"
              :title="emoji"
            >
              {{ emoji }}
            </button>
          </div>
        </div>
      </div>
    </el-popover>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

// ==================== Emits ====================
const emit = defineEmits(['emoji-select'])

// ==================== 响应式数据 ====================
const activeCategory = ref('smileys')
const recentEmojis = ref([])

// 表情分类数据
const emojiCategories = [
  {
    name: 'smileys',
    icon: '😀',
    emojis: [
      '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃',
      '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙',
      '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔'
    ]
  },
  {
    name: 'gestures',
    icon: '👍',
    emojis: [
      '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉',
      '👆', '🖕', '👇', '☝️', '👋', '🤚', '🖐️', '✋', '🖖', '👏'
    ]
  },
  {
    name: 'objects',
    icon: '📱',
    emojis: [
      '📱', '💻', '🖥️', '🖨️', '⌨️', '🖱️', '🖲️', '💽', '💾', '💿',
      '📀', '📼', '📷', '📸', '📹', '🎥', '📞', '☎️', '📟', '📠'
    ]
  },
  {
    name: 'symbols',
    icon: '❤️',
    emojis: [
      '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔',
      '❣️', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟', '☮️'
    ]
  }
]

// ==================== 计算属性 ====================
const currentEmojis = computed(() => {
  const category = emojiCategories.find(cat => cat.name === activeCategory.value)
  return category ? category.emojis : []
})

// ==================== 生命周期 ====================
onMounted(() => {
  loadRecentEmojis()
})

// ==================== 方法 ====================

/**
 * 切换表情分类
 */
const switchCategory = (categoryName) => {
  activeCategory.value = categoryName
}

/**
 * 选择表情
 */
const selectEmoji = (emoji) => {
  // 发送选择事件
  emit('emoji-select', emoji)

  // 添加到最近使用
  addToRecent(emoji)
}

/**
 * 添加到最近使用
 */
const addToRecent = (emoji) => {
  // 移除已存在的
  const index = recentEmojis.value.indexOf(emoji)
  if (index !== -1) {
    recentEmojis.value.splice(index, 1)
  }

  // 添加到开头
  recentEmojis.value.unshift(emoji)

  // 限制数量
  if (recentEmojis.value.length > 15) {
    recentEmojis.value = recentEmojis.value.slice(0, 15)
  }

  // 保存到本地存储
  saveRecentEmojis()
}

/**
 * 加载最近使用的表情
 */
const loadRecentEmojis = () => {
  try {
    const saved = localStorage.getItem('recent-emojis')
    if (saved) {
      recentEmojis.value = JSON.parse(saved)
    }
  } catch (error) {
    console.warn('加载最近表情失败:', error)
  }
}

/**
 * 保存最近使用的表情
 */
const saveRecentEmojis = () => {
  try {
    localStorage.setItem('recent-emojis', JSON.stringify(recentEmojis.value))
  } catch (error) {
    console.warn('保存最近表情失败:', error)
  }
}
</script>

<style scoped>
.emoji-picker {
  display: inline-block;
}

.emoji-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 14px;
  color: #6b7280;
  border-radius: 12px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(255, 154, 158, 0.2);
  cursor: pointer;
  font-weight: 500;
}

.emoji-trigger:hover {
  background: rgba(255, 154, 158, 0.1);
  border-color: rgba(255, 154, 158, 0.4);
  color: #ff9a9e;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 154, 158, 0.2);
}

.emoji-icon {
  font-size: 16px;
}

.emoji-text {
  font-size: 14px;
}

.emoji-panel {
  padding: 16px;
  max-height: 320px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
}

/* 表情分类标签 */
.emoji-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid rgba(255, 154, 158, 0.1);
}

.emoji-tab {
  padding: 8px 10px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.3s ease;
  opacity: 0.6;
  background: rgba(255, 255, 255, 0.5);
  border: 2px solid transparent;
}

.emoji-tab:hover {
  background: rgba(255, 154, 158, 0.1);
  opacity: 1;
  transform: translateY(-1px);
}

.emoji-tab.active {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  color: white;
  opacity: 1;
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(255, 154, 158, 0.4);
}

/* 表情网格 */
.emoji-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 4px;
  max-height: 180px;
  overflow-y: auto;
  padding: 4px;
}

.emoji-item {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.5);
  border: 2px solid transparent;
}

.emoji-item:hover {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  transform: scale(1.2);
  border-color: rgba(168, 237, 234, 0.3);
  box-shadow: 0 4px 12px rgba(168, 237, 234, 0.3);
}

/* 最近使用 */
.recent-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 2px solid rgba(255, 154, 158, 0.1);
}

.recent-title {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 8px;
  font-weight: 600;
  text-align: center;
}

.recent-emojis {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  justify-content: center;
}

.recent-emoji {
  width: 28px;
  height: 28px;
  font-size: 16px;
}

/* 滚动条样式 */
.emoji-grid::-webkit-scrollbar {
  width: 6px;
}

.emoji-grid::-webkit-scrollbar-track {
  background: rgba(255, 154, 158, 0.1);
  border-radius: 3px;
}

.emoji-grid::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  border-radius: 3px;
}

.emoji-grid::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #ff8a8e 0%, #fac0b4 100%);
}
</style>

<style>
/* 全局样式：表情弹窗 */
.emoji-popover {
  padding: 0 !important;
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px) !important;
  border: 2px solid rgba(255, 154, 158, 0.2) !important;
  border-radius: 16px !important;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
  /* 修复：设置更高的z-index，确保在输入框下方显示 */
  z-index: 2000 !important;
}

.emoji-popover .el-popover__content {
  padding: 0 !important;
}

/* 修复：确保弹窗箭头样式 */
.el-popper.is-light .el-popper__arrow::before {
  border-bottom-color: rgba(255, 154, 158, 0.2) !important;
}
</style>
