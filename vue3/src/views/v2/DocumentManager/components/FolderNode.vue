<template>
  <div class="folder-node-wrapper">
    <!-- 文件夹节点 -->
    <div
      class="folder-node"
      :class="{
        active: selectedId === folder.id,
        'level-1': folder.level === 1,
        'level-2': folder.level === 2,
        'level-3': folder.level === 3
      }"
      @click.stop="handleSelect"
    >
      <div class="node-content">
        <!-- 展开/收起图标 -->
        <span
          v-if="hasChildren"
          class="expand-icon"
          @click.stop="toggleExpand"
        >
          {{ expanded ? '▼' : '▶' }}
        </span>
        <span v-else class="expand-placeholder"></span>

        <!-- 文件夹图标和名称 -->
        <span class="folder-icon">📁</span>
        <span class="folder-name">{{ folder.name }}</span>
        <span class="doc-count">({{ folder.document_count }})</span>

        <!-- 操作按钮 -->
        <div class="node-actions">
          <el-button
            v-if="folder.level < 3"
            type="text"
            size="small"
            @click.stop="handleCreate"
            title="创建子文件夹"
          >
            ➕
          </el-button>
          <el-button
            type="text"
            size="small"
            @click.stop="handleDelete"
            title="删除文件夹"
          >
            🗑️
          </el-button>
        </div>
      </div>
    </div>

    <!-- 递归渲染子文件夹 -->
    <div v-if="hasChildren && expanded" class="children-nodes">
      <FolderNode
        v-for="child in folder.children"
        :key="child.id"
        :folder="child"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
        @create="$emit('create', $event)"
        @delete="$emit('delete', $event)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  folder: {
    type: Object,
    required: true
  },
  selectedId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['select', 'create', 'delete'])

// 展开状态
const expanded = ref(true)

// 是否有子文件夹
const hasChildren = computed(() => {
  return props.folder.children && props.folder.children.length > 0
})

// 切换展开状态
const toggleExpand = () => {
  expanded.value = !expanded.value
}

// 选择文件夹
const handleSelect = () => {
  emit('select', props.folder.id)
}

// 创建子文件夹
const handleCreate = () => {
  emit('create', props.folder)
}

// 删除文件夹
const handleDelete = () => {
  emit('delete', props.folder)
}
</script>

<style scoped>
.folder-node-wrapper {
  margin-left: 0;
}

.folder-node {
  padding: 6px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 2px;
}

.folder-node:hover {
  background: #f6f8fa;
}

.folder-node.active {
  background: #e8f4ff;
  color: #007AFF;
}

/* 层级缩进 */
.folder-node.level-1 {
  margin-left: 0;
}

.folder-node.level-2 {
  margin-left: 20px;
}

.folder-node.level-3 {
  margin-left: 40px;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.expand-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: #656d76;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.expand-placeholder {
  width: 16px;
}

.folder-icon {
  font-size: 14px;
}

.folder-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-count {
  font-size: 12px;
  color: #656d76;
}

.node-actions {
  display: none;
  gap: 4px;
}

.folder-node:hover .node-actions {
  display: flex;
}

.node-actions .el-button {
  padding: 2px 4px;
  font-size: 12px;
}

.children-nodes {
  margin-top: 2px;
}
</style>
