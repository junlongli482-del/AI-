<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建文件夹"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="文件夹名称" prop="name">
        <el-input
          v-model="formData.name"
          placeholder="请输入文件夹名称"
          maxlength="100"
          show-word-limit
          @keyup.enter="handleSubmit"
        />
      </el-form-item>

      <el-form-item label="父文件夹">
        <el-input
          :value="parentFolderName"
          disabled
          placeholder="根目录"
        />
      </el-form-item>

      <el-form-item label="层级提示">
        <div class="level-hint">
          <span v-if="currentLevel === 0">将创建一级文件夹</span>
          <span v-else-if="currentLevel === 1">将创建二级文件夹</span>
          <span v-else-if="currentLevel === 2">将创建三级文件夹（最后一层）</span>
          <span v-else class="error-hint">⚠️ 已达到最大层级限制</span>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          确定
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createFolder, validateFolderName } from '@/api/v2/document_manager/folder'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  parentFolder: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

// 响应式数据
const formRef = ref(null)
const submitting = ref(false)
const formData = ref({
  name: '',
  parent_id: null
})

// 对话框显示状态
const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

// 父文件夹名称
const parentFolderName = computed(() => {
  return props.parentFolder ? props.parentFolder.name : '根目录'
})

// 当前层级
const currentLevel = computed(() => {
  return props.parentFolder ? props.parentFolder.level : 0
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入文件夹名称', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        const result = validateFolderName(value)
        if (!result.valid) {
          callback(new Error(result.message))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 监听父文件夹变化
watch(() => props.parentFolder, (newVal) => {
  formData.value.parent_id = newVal ? newVal.id : null
}, { immediate: true })

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()

    // 检查层级限制
    if (currentLevel.value >= 3) {
      ElMessage.error('文件夹层级不能超过3层')
      return
    }

    submitting.value = true

    const data = {
      name: formData.value.name.trim()
    }

    // 如果有父文件夹，添加 parent_id
    if (formData.value.parent_id) {
      data.parent_id = formData.value.parent_id
    }

    await createFolder(data)

    emit('success')
    handleClose()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('创建文件夹失败:', error)
    }
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const handleClose = () => {
  formRef.value?.resetFields()
  formData.value = {
    name: '',
    parent_id: props.parentFolder ? props.parentFolder.id : null
  }
  dialogVisible.value = false
}
</script>

<style scoped>
.level-hint {
  font-size: 13px;
  color: #656d76;
}

.error-hint {
  color: #f56c6c;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
