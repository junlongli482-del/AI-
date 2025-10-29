<template>
  <div class="login-container">
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
      </div>

      <!-- 粒子效果 -->
      <div class="particles">
        <div class="particle" v-for="i in 15" :key="i" :style="getParticleStyle(i)"></div>
      </div>

      <!-- 光束效果 -->
      <div class="light-beams">
        <div class="beam beam-1"></div>
        <div class="beam beam-2"></div>
        <div class="beam beam-3"></div>
      </div>
    </div>

    <!-- 主登录卡片 -->
    <div class="login-card">
      <!-- 发光边框 -->
      <div class="glow-border"></div>

      <!-- 头部区域 -->
      <div class="header">
        <div class="logo-container">
          <div class="logo-rings">
            <div class="ring ring-1"></div>
            <div class="ring ring-2"></div>
            <div class="ring ring-3"></div>
          </div>
          <div class="logo">🚀</div>
        </div>
        <h1 class="title">
          <span class="title-gradient">Smart</span>
          <span class="title-normal">Login</span>
        </h1>
        <p class="subtitle">进入您的智能文档管理世界</p>
      </div>

      <!-- 表单区域 -->
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        :show-message="false"
      >
        <div class="form-group">
          <div class="input-wrapper">
            <el-form-item prop="username_or_email">
              <el-input
                v-model="loginForm.username_or_email"
                placeholder="用户名或邮箱"
                size="large"
                class="fancy-input"
              >
                <template #prefix>
                  <div class="input-icon">
                    <svg viewBox="0 0 24 24" width="20" height="20">
                      <path fill="currentColor" d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
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
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                class="fancy-input"
                show-password
                @keyup.enter="handleLogin"
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

        <div class="form-group checkbox-group">
          <el-checkbox v-model="loginForm.remember_me" class="fancy-checkbox">
            <span class="checkbox-text">记住登录状态（7天）</span>
          </el-checkbox>
        </div>

        <div class="form-group">
          <button
            type="button"
            @click="handleLogin"
            :disabled="loading"
            class="fancy-button"
          >
            <div class="button-bg"></div>
            <div class="button-shine"></div>
            <div class="button-content">
              <span v-if="!loading" class="button-text">🔥 登录系统</span>
              <span v-else class="button-text">
                <svg class="loading-spinner" viewBox="0 0 24 24" width="20" height="20">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                    <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                    <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                  </circle>
                </svg>
                登录中...
              </span>
            </div>
          </button>
        </div>
      </el-form>

      <!-- 底部链接 -->
      <div class="footer">
        <div class="divider">
          <span class="divider-text">✨ 或者 ✨</span>
        </div>
        <p class="footer-text">
          还没有账号？
          <router-link to="/register" class="footer-link">
            <span class="link-text">🎯 立即注册</span>
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

// 粒子样式生成
const getParticleStyle = (index) => {
  const delay = Math.random() * 5
  const duration = 4 + Math.random() * 3
  const size = 3 + Math.random() * 5
  const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#fd79a8']
  return {
    left: Math.random() * 100 + '%',
    animationDelay: delay + 's',
    animationDuration: duration + 's',
    width: size + 'px',
    height: size + 'px',
    background: colors[Math.floor(Math.random() * colors.length)]
  }
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
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 25%, #fecfef 50%, #fad0c4 75%, #ffd1ff 100%);
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
    linear-gradient(rgba(255,255,255,0.15) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.15) 1px, transparent 1px);
  background-size: 60px 60px;
  animation: gridMove 25s linear infinite;
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(60px, 60px); }
}

/* 光束效果 */
.light-beams {
  position: absolute;
  width: 100%;
  height: 100%;
}

.beam {
  position: absolute;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  animation: beamMove 8s ease-in-out infinite;
}

.beam-1 {
  width: 2px;
  height: 100%;
  left: 20%;
  animation-delay: 0s;
}

.beam-2 {
  width: 100%;
  height: 2px;
  top: 30%;
  animation-delay: 2s;
  background: linear-gradient(0deg, transparent, rgba(255,255,255,0.3), transparent);
}

.beam-3 {
  width: 2px;
  height: 100%;
  right: 25%;
  animation-delay: 4s;
}

@keyframes beamMove {
  0%, 100% { opacity: 0; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

/* 浮动几何图形 */
.floating-shapes {
  position: absolute;
  width: 100%;
  height: 100%;
}

.shape {
  position: absolute;
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255,255,255,0.3);
}

.shape-1 {
  width: 120px;
  height: 120px;
  top: 15%;
  left: 8%;
  background: linear-gradient(45deg, rgba(255,107,107,0.2), rgba(255,107,107,0.05));
  border-radius: 30px;
  animation: float1 7s ease-in-out infinite;
}

.shape-2 {
  width: 80px;
  height: 80px;
  top: 25%;
  right: 12%;
  background: linear-gradient(45deg, rgba(78,205,196,0.2), rgba(78,205,196,0.05));
  border-radius: 50%;
  animation: float2 9s ease-in-out infinite;
}

.shape-3 {
  width: 100px;
  height: 100px;
  bottom: 25%;
  left: 15%;
  background: linear-gradient(45deg, rgba(255,234,167,0.2), rgba(255,234,167,0.05));
  transform: rotate(45deg);
  animation: float3 8s ease-in-out infinite;
}

.shape-4 {
  width: 140px;
  height: 50px;
  top: 65%;
  right: 8%;
  background: linear-gradient(45deg, rgba(253,121,168,0.2), rgba(253,121,168,0.05));
  border-radius: 25px;
  animation: float4 10s ease-in-out infinite;
}

.shape-5 {
  width: 60px;
  height: 60px;
  bottom: 15%;
  right: 35%;
  background: linear-gradient(45deg, rgba(150,206,180,0.2), rgba(150,206,180,0.05));
  border-radius: 50%;
  animation: float5 6s ease-in-out infinite;
}

@keyframes float1 {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-40px) rotate(180deg); }
}

@keyframes float2 {
  0%, 100% { transform: translateY(0px) translateX(0px); }
  50% { transform: translateY(-25px) translateX(25px); }
}

@keyframes float3 {
  0%, 100% { transform: rotate(45deg) translateY(0px); }
  50% { transform: rotate(225deg) translateY(-30px); }
}

@keyframes float4 {
  0%, 100% { transform: translateY(0px) scale(1); }
  50% { transform: translateY(-20px) scale(1.15); }
}

@keyframes float5 {
  0%, 100% { transform: translateY(0px) translateX(0px); }
  33% { transform: translateY(-15px) translateX(-15px); }
  66% { transform: translateY(-8px) translateX(15px); }
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
  animation: particleFloat 7s ease-in-out infinite;
  box-shadow: 0 0 10px currentColor;
}

@keyframes particleFloat {
  0% { transform: translateY(100vh) opacity(0); }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-100px) opacity(0); }
}

/* 登录卡片 */
.login-card {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(25px);
  border-radius: 28px;
  padding: 50px 42px;
  position: relative;
  z-index: 1;
  box-shadow:
    0 30px 60px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(255, 255, 255, 0.7) inset;
  transition: all 0.4s ease;
}

.login-card:hover {
  transform: translateY(-10px) scale(1.02);
  box-shadow:
    0 40px 80px rgba(0, 0, 0, 0.18),
    0 0 0 1px rgba(255, 255, 255, 0.7) inset;
}

/* 发光边框 */
.glow-border {
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #ffeaa7, #fd79a8, #a8e6cf, #ff8a80);
  background-size: 400% 400%;
  border-radius: 31px;
  z-index: -1;
  animation: gradientShift 5s ease infinite;
  opacity: 0.8;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 头部样式 */
.header {
  text-align: center;
  margin-bottom: 42px;
}

.logo-container {
  position: relative;
  display: inline-block;
  margin-bottom: 24px;
}

.logo-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.ring {
  position: absolute;
  border: 2px solid;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.ring-1 {
  width: 80px;
  height: 80px;
  border-color: rgba(255,107,107,0.3);
  animation: ringRotate1 8s linear infinite;
}

.ring-2 {
  width: 100px;
  height: 100px;
  border-color: rgba(78,205,196,0.3);
  animation: ringRotate2 12s linear infinite reverse;
}

.ring-3 {
  width: 120px;
  height: 120px;
  border-color: rgba(255,234,167,0.3);
  animation: ringRotate3 15s linear infinite;
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

.logo {
  font-size: 52px;
  display: block;
  filter: drop-shadow(0 6px 12px rgba(0,0,0,0.15));
  position: relative;
  z-index: 1;
  animation: logoFloat 4s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-8px); }
}

.title {
  font-size: 38px;
  font-weight: 800;
  margin: 0 0 12px 0;
  letter-spacing: -1.5px;
}

.title-gradient {
  background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 50%, #ffeaa7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-normal {
  color: #2d3748;
  margin-left: 10px;
}

.subtitle {
  font-size: 17px;
  color: #718096;
  margin: 0;
  font-weight: 500;
}

/* 表单样式 */
.login-form {
  width: 100%;
}

.form-group {
  margin-bottom: 26px;
}

.input-wrapper {
  position: relative;
}

.input-wrapper::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg, #ff9a9e, #fad0c4, #a8edea, #fed6e3);
  border-radius: 20px;
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
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.08);
  padding: 18px 22px;
  transition: all 0.3s ease;
  height: auto;
}

:deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 1);
  border-color: rgba(255,107,107, 0.3);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

:deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 1);
  border-color: transparent;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
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
  margin-right: 14px;
}

/* 复选框样式 */
.checkbox-group {
  display: flex;
  justify-content: center;
  margin: 35px 0;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
  border-color: #ff6b6b;
}

.checkbox-text {
  color: #718096;
  font-size: 15px;
  font-weight: 500;
}

/* 花哨按钮 */
.fancy-button {
  width: 100%;
  height: 58px;
  border: none;
  border-radius: 18px;
  position: relative;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s ease;
  background: transparent;
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
  border-radius: 18px;
  transition: all 0.3s ease;
}

.button-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
  transition: left 0.6s ease;
}

.fancy-button:hover:not(:disabled) .button-bg {
  background: #1a202c;
  transform: translateY(-3px);
  box-shadow: 0 15px 35px rgba(45, 55, 72, 0.4);
}

.fancy-button:hover:not(:disabled) .button-shine {
  left: 100%;
}

.fancy-button:active:not(:disabled) .button-bg {
  transform: translateY(0);
  box-shadow: 0 8px 20px rgba(45, 55, 72, 0.3);
}

.button-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
  font-size: 19px;
  font-weight: 600;
}

.loading-spinner {
  margin-right: 10px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 底部样式 */
.footer {
  margin-top: 35px;
}

.divider {
  text-align: center;
  margin: 28px 0;
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
  padding: 0 18px;
  color: #a0aec0;
  font-size: 15px;
  position: relative;
  z-index: 1;
}

.footer-text {
  text-align: center;
  color: #718096;
  font-size: 16px;
  margin: 0;
}

.footer-link {
  color: #ff6b6b;
  text-decoration: none;
  font-weight: 600;
  margin-left: 6px;
  display: inline-flex;
  align-items: center;
  transition: all 0.2s ease;
}

.footer-link:hover {
  color: #ff5252;
  transform: translateX(3px);
}

.link-arrow {
  margin-left: 6px;
  transition: transform 0.2s ease;
}

.footer-link:hover .link-arrow {
  transform: translateX(3px);
}

/* 响应式 */
@media (max-width: 480px) {
  .login-card {
    margin: 20px;
    padding: 35px 28px;
    border-radius: 24px;
  }

  .title {
    font-size: 32px;
  }

  .subtitle {
    font-size: 15px;
  }

  .logo {
    font-size: 44px;
  }
}
</style>
