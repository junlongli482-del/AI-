<template>
  <div class="user-center-container">
    <header class="header">
      <div class="header-content">
        <h1 class="logo" @click="$router.push('/home')">用户系统</h1>
        <div class="user-menu">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <span class="username">{{ userInfo?.username || '用户' }}</span>
              <span class="arrow">▼</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="home">🏠 返回主页</el-dropdown-item>
                <el-dropdown-item command="logout" divided>🚪 退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="profile-card">
        <h2 class="card-title">个人资料</h2>

        <div class="info-section">
          <div class="info-item">
            <span class="label">用户名</span>
            <span class="value">{{ userInfo?.username }}</span>
          </div>

          <div class="info-item">
            <span class="label">邮箱</span>
            <span class="value">{{ userInfo?.email }}</span>
          </div>

          <div class="info-item">
            <span class="label">昵称</span>
            <div class="nickname-edit">
              <span v-if="!isEditingNickname" class="value">
                {{ userInfo?.nickname || '未设置' }}
              </span>
              <el-input
                v-else
                v-model="editNickname"
                placeholder="请输入昵称（2-20个字符）"
                class="nickname-input"
                @keyup.enter="handleSaveNickname"
              >
                <template #suffix>
                  <span v-if="nicknameChecking" class="checking-icon">⏳</span>
                  <span v-else-if="nicknameAvailable === true" class="success-icon">✓</span>
                  <span v-else-if="nicknameAvailable === false" class="error-icon">✗</span>
                </template>
              </el-input>
              <el-button
                v-if="!isEditingNickname"
                type="primary"
                text
                @click="handleEditNickname"
              >
                编辑
              </el-button>
              <div v-else class="edit-buttons">
                <el-button
                  type="primary"
                  size="small"
                  @click="handleSaveNickname"
                  :loading="savingNickname"
                >
                  保存
                </el-button>
                <el-button
                  size="small"
                  @click="handleCancelEdit"
                >
                  取消
                </el-button>
              </div>
            </div>
          </div>

          <div class="info-item">
            <span class="label">显示名称</span>
            <span class="value">{{ userInfo?.display_name || userInfo?.username }}</span>
          </div>

          <div class="info-item">
            <span class="label">注册时间</span>
            <span class="value">{{ formatDate(userInfo?.created_at) }}</span>
          </div>
        </div>

        <div class="action-buttons">
          <el-button
            type="primary"
            @click="$router.push('/change-password')"
            class="action-button"
          >
            🔒 修改密码
          </el-button>
          <el-button
            @click="handleLogout"
            class="action-button"
          >
            🚪 退出登录
          </el-button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserProfile, updateNickname, checkNickname } from '@/api/v1/user_profile'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const userInfo = ref(null)
const isEditingNickname = ref(false)
const editNickname = ref('')
const savingNickname = ref(false)
const nicknameChecking = ref(false)
const nicknameAvailable = ref(null)

onMounted(async () => {
  await loadUserProfile()
})

const loadUserProfile = async () => {
  try {
    userInfo.value = await getUserProfile()
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

const handleEditNickname = () => {
  isEditingNickname.value = true
  editNickname.value = userInfo.value?.nickname || ''
}

const handleCancelEdit = () => {
  isEditingNickname.value = false
  editNickname.value = ''
  nicknameAvailable.value = null
}

const checkNicknameAvailability = async () => {
  if (!editNickname.value || editNickname.value === userInfo.value?.nickname) {
    nicknameAvailable.value = null
    return
  }

  if (!/^[\u4e00-\u9fa5a-zA-Z0-9]{2,20}$/.test(editNickname.value)) {
    nicknameAvailable.value = null
    return
  }

  nicknameChecking.value = true
  try {
    const response = await checkNickname(editNickname.value)
    nicknameAvailable.value = response.available
  } catch (error) {
    nicknameAvailable.value = null
  } finally {
    nicknameChecking.value = false
  }
}

const handleSaveNickname = async () => {
  if (!editNickname.value) {
    ElMessage.warning('请输入昵称')
    return
  }

  if (!/^[一-龥a-zA-Z0-9]{2,20}$/.test(editNickname.value)) {
    ElMessage.warning('昵称必须是2-20个字符，支持中英文和数字')
    return
  }

  if (editNickname.value === userInfo.value?.nickname) {
    handleCancelEdit()
    return
  }

  await checkNicknameAvailability()

  if (nicknameAvailable.value === false) {
    ElMessage.error('该昵称已被使用')
    return
  }

  savingNickname.value = true
  try {
    await updateNickname(editNickname.value)
    ElMessage.success('昵称修改成功')
    await loadUserProfile()
    isEditingNickname.value = false
    nicknameAvailable.value = null
  } catch (error) {
    // 错误已在拦截器处理
  } finally {
    savingNickname.value = false
  }
}

const handleCommand = async (command) => {
  if (command === 'home') {
    router.push('/home')
  } else if (command === 'logout') {
    await handleLogout()
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch {
    // 用户取消
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.user-center-container {
  min-height: 100vh;
  background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,242,245,0.95) 100%);
  backdrop-filter: blur(20px);
}

.header {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.5px;
  cursor: pointer;
  transition: color 0.2s;
}

.logo:hover {
  color: #007AFF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.user-info:hover {
  background: rgba(0, 0, 0, 0.04);
}

.username {
  font-size: 15px;
  font-weight: 500;
  color: #1d1d1f;
}

.arrow {
  font-size: 12px;
  color: #86868b;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  padding: 48px 24px;
}

.profile-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  padding: 48px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

.card-title {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 32px 0;
  letter-spacing: -0.5px;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 40px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.label {
  font-size: 15px;
  font-weight: 500;
  color: #86868b;
  min-width: 100px;
}

.value {
  font-size: 15px;
  color: #1d1d1f;
  flex: 1;
  text-align: right;
}

.nickname-edit {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  justify-content: flex-end;
}

.nickname-input {
  max-width: 300px;
}

.edit-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.action-button {
  min-width: 140px;
  height: 44px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
}

.checking-icon {
  color: #909399;
  font-size: 16px;
}

.success-icon {
  color: #67C23A;
  font-size: 18px;
  font-weight: bold;
}

.error-icon {
  color: #F56C6C;
  font-size: 18px;
  font-weight: bold;
}

:deep(.el-dropdown-menu__item) {
  padding: 12px 20px;
}
</style>
