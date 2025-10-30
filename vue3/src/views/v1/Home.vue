<template>
  <div class="home-container">
    <!-- 简化背景 -->
    <div class="simple-background">
      <div class="gradient-overlay"></div>
    </div>

    <!-- 使用全局导航组件 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <div class="welcome-content">
          <h1 class="welcome-title">
            <span class="title-gradient">智能开发平台</span>
          </h1>
          <p class="welcome-subtitle">
            🚀 通过AI智能体协同，让全栈开发变得简单高效
          </p>
          <div class="welcome-stats">
            <div class="stat-item">
              <span class="stat-number">1000+</span>
              <span class="stat-label">开发者</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">500+</span>
              <span class="stat-label">项目</span>
            </div>
            <div class="stat-item">
              <span class="stat-number">24/7</span>
              <span class="stat-label">AI支持</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 主要功能卡片 -->
      <div class="feature-cards">
        <!-- AI开发平台大卡片 -->
        <div class="main-feature-card" @click="$router.push('/ai-platform')">
          <div class="card-content">
            <div class="feature-header">
              <div class="feature-icon">🤖</div>
              <div class="feature-badge">核心功能</div>
            </div>

            <h3 class="feature-title">AI开发平台</h3>
            <p class="feature-description">
              选择专业的AI智能体，获得产品设计、后端开发、前端开发的专业指导，
              让您的项目开发更加高效和专业。
            </p>

            <div class="feature-highlights">
              <div class="highlight-item">
                <span class="highlight-icon">🎯</span>
                <span class="highlight-text">智能代码生成</span>
              </div>
              <div class="highlight-item">
                <span class="highlight-icon">⚡</span>
                <span class="highlight-text">实时协作</span>
              </div>
              <div class="highlight-item">
                <span class="highlight-icon">🔧</span>
                <span class="highlight-text">自动化部署</span>
              </div>
            </div>

            <div class="feature-button">
              <span class="button-text">🚀 进入平台</span>
              <span class="arrow-right">→</span>
            </div>
          </div>
        </div>

        <!-- 其他功能卡片 -->
        <div class="secondary-cards">
          <div class="secondary-card" @click="$router.push('/user-center')">
            <div class="secondary-icon">👤</div>
            <h4>用户中心</h4>
            <p>管理个人信息</p>
            <div class="card-arrow">→</div>
          </div>

          <div class="secondary-card" @click="$router.push('/change-password')">
            <div class="secondary-icon">🔒</div>
            <h4>修改密码</h4>
            <p>更新登录密码</p>
            <div class="card-arrow">→</div>
          </div>

          <div class="secondary-card" @click="$router.push('/document-manager')">
            <div class="secondary-icon">📚</div>
            <h4>文档管理</h4>
            <p>管理技术文档</p>
            <div class="card-arrow">→</div>
          </div>

          <div class="secondary-card" @click="$router.push('/tech-square')">
            <div class="secondary-icon">🌟</div>
            <h4>技术广场</h4>
            <p>发现优质内容</p>
            <div class="card-arrow">→</div>
          </div>

          <div class="secondary-card coming-soon">
            <div class="secondary-icon">📊</div>
            <h4>项目管理</h4>
            <p>即将上线</p>
            <div class="coming-soon-badge">Soon</div>
          </div>

          <div class="secondary-card coming-soon">
            <div class="secondary-icon">🎓</div>
            <h4>学习中心</h4>
            <p>即将上线</p>
            <div class="coming-soon-badge">Soon</div>
          </div>
        </div>
      </div>

      <!-- 底部装饰 -->
      <div class="bottom-decoration">
        <div class="decoration-text">
          ✨ 让AI成为您的开发伙伴 ✨
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'

const userStore = useUserStore()

onMounted(async () => {
  try {
    if (!userStore.userInfo) {
      await userStore.getUserInfo()
    }
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  position: relative;
}

/* 简化背景 */
.simple-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background: linear-gradient(135deg,
  rgba(255, 154, 158, 0.1) 0%,
  rgba(250, 208, 196, 0.1) 25%,
  rgba(168, 237, 234, 0.1) 50%,
  rgba(254, 214, 227, 0.1) 75%,
  rgba(255, 234, 167, 0.1) 100%
  );
}

.gradient-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
  radial-gradient(circle at 70% 80%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
}

/* 主要内容区域 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 24px;
  position: relative;
  z-index: 1;
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 60px;
}

.welcome-content {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  padding: 60px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.welcome-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 24px 0;
  letter-spacing: -1px;
  line-height: 1.1;
}

.title-gradient {
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 20px;
  color: #86868b;
  margin: 0 0 40px 0;
  line-height: 1.6;
  font-weight: 500;
}

.welcome-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 60px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #86868b;
  font-weight: 500;
}

/* 功能卡片区域 */
.feature-cards {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 40px;
  align-items: start;
}

/* 主要功能卡片 */
.main-feature-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.main-feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border-color: rgba(0, 122, 255, 0.3);
}

.card-content {
  padding: 40px;
}

.feature-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.feature-icon {
  font-size: 64px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

.feature-badge {
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.feature-title {
  font-size: 32px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 20px 0;
  letter-spacing: -1px;
}

.feature-description {
  font-size: 16px;
  color: #86868b;
  line-height: 1.7;
  margin: 0 0 32px 0;
}

.feature-highlights {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.highlight-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.8);
  padding: 12px 16px;
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.highlight-icon {
  font-size: 16px;
}

.highlight-text {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
}

.feature-button {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  color: white;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: none;
}

.main-feature-card:hover .feature-button {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.4);
}

.arrow-right {
  transition: transform 0.3s ease;
}

.main-feature-card:hover .arrow-right {
  transform: translateX(4px);
}

/* 次要功能卡片 */
.secondary-cards {
  display: grid;
  gap: 20px;
}

.secondary-card {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 20px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
  text-align: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.secondary-card:hover:not(.coming-soon) {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  border-color: rgba(0, 122, 255, 0.3);
}

.secondary-card.coming-soon {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary-icon {
  font-size: 32px;
  margin-bottom: 16px;
  display: block;
}

.secondary-card h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
}

.secondary-card p {
  font-size: 14px;
  color: #86868b;
  margin: 0 0 16px 0;
}

.card-arrow {
  font-size: 16px;
  color: #86868b;
  transition: all 0.3s ease;
}

.secondary-card:hover:not(.coming-soon) .card-arrow {
  color: #007AFF;
  transform: translateX(4px);
}

.coming-soon-badge {
  display: inline-block;
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
  color: #856404;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

/* 底部装饰 */
.bottom-decoration {
  text-align: center;
  margin-top: 80px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(30px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

.decoration-text {
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #007AFF 0%, #4A90E2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .feature-cards {
    grid-template-columns: 1fr;
    gap: 32px;
  }

  .welcome-stats {
    gap: 40px;
  }

  .feature-highlights {
    flex-direction: column;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 40px 16px;
  }

  .welcome-content {
    padding: 40px 24px;
    border-radius: 20px;
  }

  .welcome-title {
    font-size: 36px;
  }

  .welcome-subtitle {
    font-size: 18px;
  }

  .welcome-stats {
    flex-direction: column;
    gap: 24px;
  }

  .card-content {
    padding: 32px 24px;
  }

  .feature-title {
    font-size: 28px;
  }

  .feature-description {
    font-size: 15px;
  }

  .feature-icon {
    font-size: 48px;
  }

  .secondary-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .feature-header {
    flex-direction: column;
    gap: 20px;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 28px;
  }

  .secondary-cards {
    grid-template-columns: 1fr;
  }

  .bottom-decoration {
    margin-top: 60px;
    padding: 24px;
  }

  .decoration-text {
    font-size: 16px;
  }
}
</style>
