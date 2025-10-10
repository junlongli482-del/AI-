<template>
  <div class="register-container">
    <div class="register-card">
      <h2 class="title">用户注册</h2>

      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        label-width="80px"
        class="register-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="3-20个字符，仅限字母和数字"
            @blur="handleUsernameBlur"
          >
            <template #suffix>
              <span v-if="usernameChecking" class="checking-icon">⏳</span>
              <span v-else-if="usernameAvailable === true" class="success-icon">✓</span>
              <span v-else-if="usernameAvailable === false" class="error-icon">✗</span>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入有效的邮箱地址"
            @blur="handleEmailBlur"
          >
            <template #suffix>
              <span v-if="emailChecking" class="checking-icon">⏳</span>
              <span v-else-if="emailAvailable === true" class="success-icon">✓</span>
              <span v-else-if="emailAvailable === false" class="error-icon">✗</span>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="至少8位，包含字母和数字"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleRegister"
            :loading="loading"
            class="register-button"
          >
            注册
          </el-button>
        </el-form-item>

        <div class="footer-links">
          <span>已有账号？</span>
          <router-link to="/login" class="link">立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { register, checkUsername, checkEmail } from '@/api/v1/user_register'

const router = useRouter()
const registerFormRef = ref(null)
const loading = ref(false)

const usernameChecking = ref(false)
const usernameAvailable = ref(null)
const emailChecking = ref(false)
const emailAvailable = ref(null)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validateUsername = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入用户名'))
  } else if (!/^[a-zA-Z0-9]{3,20}$/.test(value)) {
    callback(new Error('用户名必须是3-20个字符，仅限字母和数字'))
  } else if (usernameAvailable.value === false) {
    callback(new Error('该用户名已被使用'))
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入邮箱'))
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    callback(new Error('请输入有效的邮箱地址'))
  } else if (emailAvailable.value === false) {
    callback(new Error('该邮箱已被注册'))
  } else {
    callback()
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 8) {
    callback(new Error('密码至少8位'))
  } else if (!/(?=.*[A-Za-z])(?=.*\d)/.test(value)) {
    callback(new Error('密码必须包含字母和数字'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ validator: validateUsername, trigger: 'blur' }],
  email: [{ validator: validateEmail, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleUsernameBlur = async () => {
  if (!registerForm.username || !/^[a-zA-Z0-9]{3,20}$/.test(registerForm.username)) {
    usernameAvailable.value = null
    return
  }

  usernameChecking.value = true
  try {
    const response = await checkUsername(registerForm.username)
    usernameAvailable.value = response.available
  } catch (error) {
    usernameAvailable.value = null
  } finally {
    usernameChecking.value = false
  }
}

const handleEmailBlur = async () => {
  if (!registerForm.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.email)) {
    emailAvailable.value = null
    return
  }

  emailChecking.value = true
  try {
    const response = await checkEmail(registerForm.email)
    emailAvailable.value = response.available
  } catch (error) {
    emailAvailable.value = null
  } finally {
    emailChecking.value = false
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await register({
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password
      })

      ElMessage.success('注册成功，即将跳转到登录页面')
      setTimeout(() => {
        router.push('/login')
      }, 1500)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,242,245,0.95) 100%);
  backdrop-filter: blur(20px);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  padding: 48px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(255, 255, 255, 0.5) inset;
}

.title {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  text-align: center;
  margin-bottom: 40px;
  letter-spacing: -0.5px;
}

.register-form {
  width: 100%;
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

.register-button {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: linear-gradient(135deg, #007AFF 0%, #0051D5 100%);
  border: none;
  margin-top: 8px;
  transition: all 0.3s ease;
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 122, 255, 0.3);
}

.footer-links {
  text-align: center;
  margin-top: 24px;
  color: #86868b;
  font-size: 14px;
}

.link {
  color: #007AFF;
  text-decoration: none;
  margin-left: 8px;
  font-weight: 500;
  transition: color 0.2s;
}

.link:hover {
  color: #0051D5;
  text-decoration: underline;
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
</style>
