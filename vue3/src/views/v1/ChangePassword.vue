<template>
  <div class="change-password-container">
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
                <el-dropdown-item command="profile">👤 用户中心</el-dropdown-item>
                <el-dropdown-item command="logout" divided>🚪 退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </header>

    <main class="main-content">
      <div class="password-card">
        <h2 class="card-title">修改密码</h2>

        <div class="user-info-display">
          <div class="info-item">
            <span class="label">当前用户：</span>
            <span class="value">{{ userInfo?.username }}</span>
          </div>
          <div class="info-item">
            <span class="label">邮箱：</span>
            <span class="value">{{ userInfo?.email }}</span>
          </div>
        </div>

        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="rules"
          label-width="100px"
          class="password-form"
        >
          <el-form-item label="原密码" prop="current_password">
            <el-input
              v-model="passwordForm.current_password"
              type="password"
              placeholder="请输入原密码"
              show-password
            />
          </el-form-item>

          <el-form-item label="新密码" prop="new_password">
            <el-input
              v-model="passwordForm.new_password"
              type="password"
              placeholder="至少8位，包含字母和数字"
              show-password
              @input="handlePasswordInput"
            />
            <div v-if="passwordStrength" class="password-strength">
              <div class="strength-bar">
                <div
                  class="strength-fill"
                  :class="strengthClass"
                  :style="{ width: strengthWidth }"
                ></div>
              </div>
              <span class="strength-text" :class="strengthClass">
                {{ strengthText }}
              </span>
            </div>
          </el-form-item>

          <el-form-item label="确认新密码" prop="confirm_password">
            <el-input
              v-model="passwordForm.confirm_password"
              type="password"
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>

          <el-form-item>
            <div class="button-group">
              <el-button
                type="primary"
                @click="handleChangePassword"
                :loading="loading"
                class="submit-button"
              >
                确认修改
              </el-button>
              <el-button
                @click="handleCancel"
                class="cancel-button"
              >
                取消
              </el-button>
            </div>
          </el-form-item>
        </el-form>

        <div class="password-tips">
          <h4>密码要求：</h4>
          <ul>
            <li>长度至少8位</li>
            <li>必须包含字母和数字</li>
            <li>建议使用大小写字母、数字和特殊字符组合</li>
          </ul>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { changePassword, checkPasswordStrength, getUserInfo } from '@/api/v1/password_manager'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const passwordFormRef = ref(null)
const loading = ref(false)

const userInfo = ref(null)
const passwordStrength = ref(null)

const passwordForm = reactive({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

onMounted(async () => {
  try {
    userInfo.value = await getUserInfo()
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
})

const validateCurrentPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入原密码'))
  } else if (value.length < 8) {
    callback(new Error('密码至少8位'))
  } else {
    callback()
  }
}

const validateNewPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'))
  } else if (value.length < 8) {
    callback(new Error('密码至少8位'))
  } else if (!/(?=.*[A-Za-z])(?=.*\d)/.test(value)) {
    callback(new Error('密码必须包含字母和数字'))
  } else if (value === passwordForm.current_password) {
    callback(new Error('新密码不能与原密码相同'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入新密码'))
  } else if (value !== passwordForm.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  current_password: [{ validator: validateCurrentPassword, trigger: 'blur' }],
  new_password: [{ validator: validateNewPassword, trigger: 'blur' }],
  confirm_password: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const handlePasswordInput = async () => {
  if (passwordForm.new_password.length >= 8) {
    try {
      passwordStrength.value = await checkPasswordStrength(passwordForm.new_password)
    } catch (error) {
      passwordStrength.value = null
    }
  } else {
    passwordStrength.value = null
  }
}

const strengthClass = computed(() => {
  if (!passwordStrength.value) return ''
  const score = passwordStrength.value.score
  if (score >= 80) return 'strong'
  if (score >= 60) return 'medium'
  return 'weak'
})

const strengthWidth = computed(() => {
  if (!passwordStrength.value) return '0%'
  return `${passwordStrength.value.score}%`
})

const strengthText = computed(() => {
  if (!passwordStrength.value) return ''
  const score = passwordStrength.value.score
  if (score >= 80) return '强'
  if (score >= 60) return '中'
  return '弱'
})

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password
      })

      ElMessage.success('密码修改成功，请重新登录')

      setTimeout(() => {
        userStore.logout()
        router.push('/login')
      }, 1500)
    } catch (error) {
      // 错误已在拦截器处理
    } finally {
      loading.value = false
    }
  })
}

const handleCancel = () => {
  router.back()
}

const handleCommand = async (command) => {
  if (command === 'home') {
    router.push('/home')
  } else if (command === 'profile') {
    router.push('/user-center')
  } else if (command === 'logout') {
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
}
</script>

<style scoped>
.change-password-container {
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
  max-width: 700px;
  margin: 0 auto;
  padding: 48px 24px;
}

.password-card {
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

.user-info-display {
  background: rgba(0, 122, 255, 0.05);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 32px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  font-size: 14px;
  color: #86868b;
  font-weight: 500;
}

.value {
  font-size: 14px;
  color: #1d1d1f;
  font-weight: 500;
}

.password-form {
  margin-bottom: 32px;
}

:deep(.el-form-item__label) {
  color: #424245;
  font-weight: 500;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.6);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

:deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.2);
}

.password-strength {
  margin-top: 8px;
}

.strength-bar {
  height: 4px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  background: #F56C6C;
}

.strength-fill.medium {
  background: #E6A23C;
}

.strength-fill.strong {
  background: #67C23A;
}

.strength-text {
  font-size: 12px;
  font-weight: 500;
}

.strength-text.weak {
  color: #F56C6C;
}

.strength-text.medium {
  color: #E6A23C;
}

.strength-text.strong {
  color: #67C23A;
}

.button-group {
  display: flex;
  gap: 16px;
  width: 100%;
}

.submit-button,
.cancel-button {
  flex: 1;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
}

.submit-button {
  background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
  border: none;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 122, 255, 0.3);
}

.password-tips {
  background: rgba(0, 122, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border-left: 4px solid #007AFF;
}

.password-tips h4 {
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 12px 0;
}

.password-tips ul {
  margin: 0;
  padding-left: 20px;
}

.password-tips li {
  font-size: 14px;
  color: #86868b;
  margin-bottom: 6px;
  line-height: 1.6;
}

.password-tips li:last-child {
  margin-bottom: 0;
}

:deep(.el-dropdown-menu__item) {
  padding: 12px 20px;
}
</style>
