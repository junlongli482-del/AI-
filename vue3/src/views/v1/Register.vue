<template>
  <div class="register-container">
    <!-- 动态背景 -->
    <div class="animated-bg">
      <!-- 渐变网格 -->
      <div class="grid-overlay"></div>

      <!-- 浮动几何图形 -->
      <div class="floating-shapes">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
        <div class="shape shape-4"></div>
        <div class="shape shape-5"></div>
        <div class="shape shape-6"></div>
      </div>

      <!-- 粒子效果 -->
      <div class="particles">
        <div class="particle" v-for="i in 18" :key="i" :style="getParticleStyle(i)"></div>
      </div>

      <!-- 光束效果 -->
      <div class="light-beams">
        <div class="beam beam-1"></div>
        <div class="beam beam-2"></div>
        <div class="beam beam-3"></div>
        <div class="beam beam-4"></div>
      </div>
    </div>

    <!-- 主注册卡片 -->
    <div class="register-card">
      <!-- 发光边框 -->
      <div class="glow-border"></div>

      <!-- 头部区域 -->
      <div class="header">
        <div class="logo-container">
          <div class="logo-rings">
            <div class="ring ring-1"></div>
            <div class="ring ring-2"></div>
            <div class="ring ring-3"></div>
            <div class="ring ring-4"></div>
          </div>
          <div class="logo">🌟</div>
        </div>
        <h1 class="title">
          <span class="title-gradient">Join</span>
          <span class="title-normal">Us</span>
        </h1>
        <p class="subtitle">创建您的智能文档管理账户</p>
      </div>

      <!-- 表单区域 -->
      <el-form
        ref="registerFormRef"
        :model="registerForm"
        :rules="rules"
        class="register-form"
        :show-message="false"
      >
        <div class="form-group">
          <div class="input-wrapper">
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名 (3-20个字符)"
                size="large"
                class="fancy-input"
                @blur="handleUsernameBlur"
              >
                <template #prefix>
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                  </div>
                </template>
                <template #suffix>
                  <div class="validation-icon">
                    <span v-if="usernameChecking" class="checking-icon">⏳</span>
                    <span v-else-if="usernameAvailable === true" class="success-icon">✨</span>
                    <span v-else-if="usernameAvailable === false" class="error-icon">❌</span>
                  </div>
                </template>
              </el-input>
            </el-form-item>
          </div>
        </div>

        <div class="form-group">
          <div class="input-wrapper">
            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱地址"
                size="large"
                class="fancy-input"
                @blur="handleEmailBlur"
              >
                <template #prefix>
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="currentColor" d="M20,8L12,13L4,8V6L12,11L20,6M20,4H4C2.89,4 2,4.89 2,6V18A2,2 0 0,0 4,20H20A2,2 0 0,0 22,18V6C22,4.89 21.1,4 20,4Z"/>
                    </svg>
                  </div>
                </template>
                <template #suffix>
                  <div class="validation-icon">
                    <span v-if="emailChecking" class="checking-icon">⏳</span>
                    <span v-else-if="emailAvailable === true" class="success-icon">✨</span>
                    <span v-else-if="emailAvailable === false" class="error-icon">❌</span>
                  </div>
                </template>
              </el-input>
            </el-form-item>
          </div>
        </div>

        <div class="form-group">
          <div class="input-wrapper">
            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码 (至少8位，包含字母和数字)"
                size="large"
                class="fancy-input"
                show-password
              >
                <template #prefix>
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="currentColor" d="M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10A2,2 0 0,1 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
                    </svg>
                  </div>
                </template>
              </el-input>
            </el-form-item>
          </div>
        </div>

        <div class="form-group">
          <div class="input-wrapper">
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                class="fancy-input"
                show-password
              >
                <template #prefix>
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="currentColor" d="M12,17A2,2 0 0,0 14,15C14,13.89 13.1,13 12,13A2,2 0 0,0 10,15A2,2 0 0,0 12,17M18,8A2,2 0 0,1 20,10V20A2,2 0 0,1 18,22H6A2,2 0 0,1 4,20V10C4,8.89 4.9,8 6,8H7V6A5,5 0 0,1 12,1A5,5 0 0,1 17,6V8H18M12,3A3,3 0 0,0 9,6V8H15V6A3,3 0 0,0 12,3Z"/>
                    </svg>
                  </div>
                </template>
              </el-input>
            </el-form-item>
          </div>
        </div>

        <div class="form-group">
          <button
            type="button"
            @click="handleRegister"
            :disabled="loading"
            class="fancy-button"
          >
            <div class="button-bg"></div>
            <div class="button-shine"></div>
            <div class="button-content">
              <span v-if="!loading" class="button-text">🚀 创建账户</span>
              <span v-else class="button-text">
                <svg class="loading-spinner" viewBox="0 0 24 24" width="20" height="20">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                    <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                    <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                  </circle>
                </svg>
                创建中...
              </span>
            </div>
          </button>
        </div>
      </el-form>

      <!-- 底部链接 -->
      <div class="footer">
        <div class="divider">
          <span class="divider-text">🎯 或者 🎯</span>
        </div>
        <p class="footer-text">
          已有账号？
          <router-link to="/login" class="footer-link">
            <span class="link-text">🔥 立即登录</span>
            <svg class="link-arrow" viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"/>
            </svg>
          </router-link>
        </p>
      </div>
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

// 粒子样式生成
const getParticleStyle = (index) => {
  const delay = Math.random() * 6
  const duration = 5 + Math.random() * 4
  const size = 3 + Math.random() * 6
  const colors = ['#ff6b6b', '#4ecdc4', '#ffeaa7', '#fd79a8', '#a8e6cf', '#ff8a80', '#ffcc02', '#6c5ce7']
  return {
    left: Math.random() * 100 + '%',
    animationDelay: delay + 's',
    animationDuration: duration + 's',
    width: size + 'px',
    height: size + 'px',
    background: colors[Math.floor(Math.random() * colors.length)]
  }
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
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #fef5e7 0%, #fed7d7 30%, #f7fafc 50%, #fbb6ce 70%, #f6ad55 100%);
}

/* 动态背景 */
.animated-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(255,255,255,0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.12) 1px, transparent 1px);
  background-size: 70px 70px;
  animation: gridMove 30s linear infinite;
}

@keyframes gridMove {
  0% { transform: translate(0, 0) rotate(0deg); }
  100% { transform: translate(70px, 70px) rotate(360deg); }
}

/* 光束效果 */
.light-beams {
  position: absolute;
  width: 100%;
  height: 100%;
}

.beam {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  animation: beamMove 10s ease-in-out infinite;
}

.beam-1 {
  width: 3px;
  height: 100%;
  left: 15%;
  animation-delay: 0s;
}

.beam-2 {
  width: 100%;
  height: 3px;
  top: 25%;
  animation-delay: 2.5s;
  background: linear-gradient(0deg, transparent, rgba(255,255,255,0.25), transparent);
}

.beam-3 {
  width: 3px;
  height: 100%;
  right: 20%;
  animation-delay: 5s;
}

.beam-4 {
  width: 100%;
  height: 3px;
  bottom: 30%;
  animation-delay: 7.5s;
  background: linear-gradient(0deg, transparent, rgba(255,255,255,0.25), transparent);
}

@keyframes beamMove {
  0%, 100% { opacity: 0; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

/* 浮动几何图形 */
.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  backdrop-filter: blur(15px);
  border: 2px solid rgba(255,255,255,0.25);
}

.shape-1 {
  width: 140px;
  height: 140px;
  top: 10%;
  left: 5%;
  background: linear-gradient(45deg, rgba(255,107,107,0.15), rgba(255,107,107,0.03));
  border-radius: 35px;
  animation: float1 8s ease-in-out infinite;
}

.shape-2 {
  width: 90px;
  height: 90px;
  top: 20%;
  right: 8%;
  background: linear-gradient(45deg, rgba(78,205,196,0.15), rgba(78,205,196,0.03));
  border-radius: 50%;
  animation: float2 10s ease-in-out infinite;
}

.shape-3 {
  width: 110px;
  height: 110px;
  bottom: 20%;
  left: 10%;
  background: linear-gradient(45deg, rgba(255,234,167,0.15), rgba(255,234,167,0.03));
  transform: rotate(45deg);
  animation: float3 9s ease-in-out infinite;
}

.shape-4 {
  width: 160px;
  height: 60px;
  top: 60%;
  right: 5%;
  background: linear-gradient(45deg, rgba(253,121,168,0.15), rgba(253,121,168,0.03));
  border-radius: 30px;
  animation: float4 11s ease-in-out infinite;
}

.shape-5 {
  width: 70px;
  height: 70px;
  bottom: 10%;
  right: 30%;
  background: linear-gradient(45deg, rgba(168,230,207,0.15), rgba(168,230,207,0.03));
  border-radius: 50%;
  animation: float5 7s ease-in-out infinite;
}

.shape-6 {
  width: 100px;
  height: 100px;
  top: 45%;
  left: 3%;
  background: linear-gradient(45deg, rgba(255,138,128,0.15), rgba(255,138,128,0.03));
  border-radius: 20px;
  animation: float6 12s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-50px) rotate(180deg); }
}

@keyframes float2 {
  0%, 100% { transform: translateY(0px) translateX(0px); }
  50% { transform: translateY(-30px) translateX(30px); }
}

@keyframes float3 {
  0%, 100% { transform: rotate(45deg) translateY(0px); }
  50% { transform: rotate(225deg) translateY(-35px); }
}

@keyframes float4 {
  0%, 100% { transform: translateY(0px) scale(1); }
  50% { transform: translateY(-25px) scale(1.2); }
}

@keyframes float5 {
  0%, 100% { transform: translateY(0px) translateX(0px); }
  33% { transform: translateY(-20px) translateX(-20px); }
  66% { transform: translateY(-10px) translateX(20px); }
}

@keyframes float6 {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(90deg); }
}

/* 粒子效果 */
.particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  border-radius: 50%;
  animation: particleFloat 8s ease-in-out infinite;
  box-shadow: 0 0 15px currentColor;
}

@keyframes particleFloat {
  0% { transform: translateY(100vh) rotate(0deg) opacity(0); }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-100px) rotate(360deg) opacity(0); }
}

/* 注册卡片 */
.register-card {
  width: 100%;
  max-width: 480px;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(30px);
  border-radius: 32px;
  padding: 52px 44px;
  position: relative;
  z-index: 1;
  box-shadow:
    0 35px 70px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;
  transition: all 0.4s ease;
}

.register-card:hover {
  transform: translateY(-12px) scale(1.02);
  box-shadow:
    0 45px 90px rgba(0, 0, 0, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.8) inset;
}

/* 发光边框 */
.glow-border {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #ffeaa7, #fd79a8, #a8e6cf, #ff8a80, #ffcc02, #6c5ce7);
  background-size: 400% 400%;
  border-radius: 36px;
  z-index: -1;
  animation: gradientShift 6s ease infinite;
  opacity: 0.9;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 头部样式 */
.header {
  text-align: center;
  margin-bottom: 45px;
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 28px;
}

.logo-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.ring {
  position: absolute;
  border: 3px solid;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.ring-1 {
  width: 90px;
  height: 90px;
  border-color: rgba(255,107,107,0.4);
  animation: ringRotate1 10s linear infinite;
}

.ring-2 {
  width: 110px;
  height: 110px;
  border-color: rgba(78,205,196,0.4);
  animation: ringRotate2 15s linear infinite reverse;
}

.ring-3 {
  width: 130px;
  height: 130px;
  border-color: rgba(255,234,167,0.4);
  animation: ringRotate3 18s linear infinite;
}

.ring-4 {
  width: 150px;
  height: 150px;
  border-color: rgba(253,121,168,0.4);
  animation: ringRotate4 22s linear infinite reverse;
}

@keyframes ringRotate1 {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes ringRotate2 {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes ringRotate3 {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes ringRotate4 {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.logo {
  font-size: 56px;
  display: block;
  filter: drop-shadow(0 8px 16px rgba(0,0,0,0.2));
  position: relative;
  z-index: 1;
  animation: logoFloat 5s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(10deg); }
}

.title {
  font-size: 42px;
  font-weight: 800;
  margin: 0 0 15px 0;
  letter-spacing: -2px;
}

.title-gradient {
  background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 30%, #ffeaa7 60%, #fd79a8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-normal {
  color: #2d3748;
  margin-left: 12px;
}

.subtitle {
  font-size: 18px;
  color: #718096;
  margin: 0;
  font-weight: 500;
}

/* 表单样式 */
.register-form {
  width: 100%;
}

.form-group {
  margin-bottom: 28px;
}

.input-wrapper {
  position: relative;
}

.input-wrapper::before {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  background: linear-gradient(45deg, #ff9a9e, #fad0c4, #a8edea, #fed6e3, #d299c2);
  border-radius: 22px;
  z-index: -1;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.input-wrapper:focus-within::before {
  opacity: 1;
}

:deep(.el-form-item) {
  margin-bottom: 0;
}

:deep(.el-input__wrapper) {
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.96);
  border: 2px solid rgba(0, 0, 0, 0.05);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  padding: 20px 24px;
  transition: all 0.3s ease;
  height: auto;
}

:deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(255,107,107, 0.25);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
}

:deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 1);
  border-color: transparent;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.18);
}

:deep(.el-input__inner) {
  font-size: 17px;
  color: #2d3748;
  font-weight: 500;
}

:deep(.el-input__inner::placeholder) {
  color: #a0aec0;
  font-weight: 400;
}

.input-icon {
  display: flex;
  align-items: center;
  color: #718096;
  margin-right: 16px;
}

.validation-icon {
  display: flex;
  align-items: center;
  margin-left: 12px;
}

.checking-icon {
  font-size: 18px;
  animation: spin 1s linear infinite;
}

.success-icon {
  color: #4ecdc4;
  font-size: 20px;
  animation: bounce 0.6s ease;
}

.error-icon {
  color: #ff6b6b;
  font-size: 18px;
  animation: shake 0.5s ease;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
  60% { transform: translateY(-4px); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

/* 花哨按钮 */
.fancy-button {
  width: 100%;
  height: 62px;
  border: none;
  border-radius: 20px;
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  background: transparent;
  margin-top: 10px;
}

.fancy-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.button-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #2d3748;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.button-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  transition: left 0.7s ease;
}

.fancy-button:hover:not(:disabled) .button-bg {
  background: #1a202c;
  transform: translateY(-4px);
  box-shadow: 0 18px 40px rgba(45, 55, 72, 0.5);
}

.fancy-button:hover:not(:disabled) .button-shine {
  left: 100%;
}

.fancy-button:active:not(:disabled) .button-bg {
  transform: translateY(0);
  box-shadow: 0 10px 25px rgba(45, 55, 72, 0.4);
}

.button-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.loading-spinner {
  margin-right: 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 底部样式 */
.footer {
  margin-top: 38px;
}

.divider {
  text-align: center;
  margin: 32px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);
}

.divider-text {
  background: rgba(255, 255, 255, 0.95);
  padding: 0 20px;
  color: #a0aec0;
  font-size: 16px;
  position: relative;
  z-index: 1;
}

.footer-text {
  text-align: center;
  color: #718096;
  font-size: 17px;
  margin: 0;
}

.footer-link {
  color: #ff6b6b;
  text-decoration: none;
  font-weight: 600;
  margin-left: 8px;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s ease;
}

.footer-link:hover {
  color: #ff5252;
  transform: translateX(4px);
}

.link-arrow {
  margin-left: 8px;
  transition: transform 0.2s ease;
}

.footer-link:hover .link-arrow {
  transform: translateX(4px);
}

/* 响应式 */
@media (max-width: 480px) {
  .register-card {
    margin: 20px;
    padding: 38px 32px;
    border-radius: 28px;
  }

  .title {
    font-size: 36px;
  }

  .subtitle {
    font-size: 16px;
  }

  .logo {
    font-size: 48px;
  }

  .form-group {
    margin-bottom: 24px;
  }
}
</style>
