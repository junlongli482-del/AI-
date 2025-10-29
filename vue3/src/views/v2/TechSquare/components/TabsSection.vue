<template>
  <div class="tabs-section">
    <div class="tabs-container">
      <div class="tabs-wrapper">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{
            active: activeTab === tab.key,
            disabled: tab.disabled
          }"
          @click="handleTabClick(tab)"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-text">{{ tab.label }}</span>
          <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
        </div>
      </div>

      <!-- 移动端下拉选择 -->
      <div class="mobile-select">
        <el-select
          :model-value="activeTab"
          @change="handleTabChange"
          size="large"
        >
          <el-option
            v-for="tab in tabs"
            :key="tab.key"
            :label="`${tab.icon} ${tab.label}`"
            :value="tab.key"
            :disabled="tab.disabled"
          />
        </el-select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  activeTab: {
    type: String,
    default: 'hot'
  },
  stats: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['tab-change'])

// 标签配置
const tabs = computed(() => [
  {
    key: 'hot',
    label: '最热',
    icon: '🔥',
    count: undefined, // 热门文档不显示数量
    disabled: false
  },
  {
    key: 'latest',
    label: '最新',
    icon: '🆕',
    count: props.stats.today_published || undefined,
    disabled: false
  },
  {
    key: 'all',
    label: '全部',
    icon: '📄',
    count: props.stats.total_documents || undefined,
    disabled: false
  }
])

// 方法
const handleTabClick = (tab) => {
  if (tab.disabled || props.loading) return
  if (tab.key === props.activeTab) return

  emit('tab-change', tab.key)
}

const handleTabChange = (tabKey) => {
  if (props.loading) return
  emit('tab-change', tabKey)
}
</script>

<style scoped>
.tabs-section {
  margin-bottom: 32px;
}

.tabs-container {
  display: flex;
  justify-content: center;
}

/* 桌面端标签 */
.tabs-wrapper {
  display: flex;
  background: white;
  border-radius: 12px;
  padding: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  border: 1px solid #e1e4e8;
  gap: 4px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  cursor: pointer;
  border-radius: 8px;
  font-weight: 500;
  color: #656d76;
  transition: all 0.2s ease;
  user-select: none;
  position: relative;
  min-width: 100px;
  justify-content: center;
}

.tab-item:hover:not(.disabled):not(.active) {
  color: #24292f;
  background: #f6f8fa;
}

.tab-item.active {
  color: #007AFF;
  background: #e3f2fd;
  box-shadow: 0 2px 4px rgba(0, 122, 255, 0.2);
}

.tab-item.disabled {
  color: #d0d7de;
  cursor: not-allowed;
}

.tab-icon {
  font-size: 16px;
}

.tab-text {
  font-size: 14px;
  font-weight: 600;
}

.tab-count {
  background: rgba(0, 122, 255, 0.1);
  color: #007AFF;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  min-width: 18px;
  text-align: center;
}

.tab-item.active .tab-count {
  background: rgba(255, 255, 255, 0.8);
  color: #007AFF;
}

/* 移动端下拉选择 */
.mobile-select {
  display: none;
  width: 100%;
  max-width: 300px;
}

/* 响应式 */
@media (max-width: 768px) {
  .tabs-wrapper {
    display: none;
  }

  .mobile-select {
    display: block;
  }
}

@media (max-width: 480px) {
  .tabs-container {
    padding: 0 16px;
  }

  .mobile-select {
    max-width: 100%;
  }
}

/* 加载状态 */
.tabs-wrapper.loading .tab-item {
  pointer-events: none;
  opacity: 0.6;
}

/* 动画效果 */
.tab-item::before {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 2px;
  background: #007AFF;
  border-radius: 1px;
  transition: width 0.2s ease;
}

.tab-item.active::before {
  width: 60%;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .tabs-wrapper {
    background: #1c1c1e;
    border-color: #38383a;
  }

  .tab-item {
    color: #8e8e93;
  }

  .tab-item:hover:not(.disabled):not(.active) {
    color: #ffffff;
    background: #2c2c2e;
  }

  .tab-item.active {
    color: #007AFF;
    background: rgba(0, 122, 255, 0.15);
  }
}
</style>
