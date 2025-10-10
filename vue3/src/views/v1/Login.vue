<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title">用户登录</h2>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-width="100px"
        class="login-form"
      >
        <el-form-item label="用户名/邮箱" prop="username_or_email">
          <el-input
            v-model="loginForm.username_or_email"
            placeholder="请输入用户名或邮箱"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-checkbox v-model="loginForm.remember_me">
            记住登录状态（7天）
          </el-checkbox>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleLogin"
            :loading="loading"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="footer-links">
          <span>还没有账号？</span>
          <router-link to="/register" class="link">立即注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username_or_email: '',
  password: '',
  remember_me: false
})

const rules = {
  username_or_email: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码至少8位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.login(loginForm)
      ElMessage.success('登录成功')
      router.push('/home')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,242,245,0.95) 100%);
  backdrop-filter: blur(20px);
  padding: 20px;
}

.login-card {
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

.login-form {
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

.login-button {
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

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 122, 255, 0.3);
}

:deep(.el-checkbox__label) {
  color: #86868b;
  font-size: 14px;
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
</style>
