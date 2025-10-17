<template>
  <div class="home-container">
    <!-- 使用全局导航组件 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 欢迎区域 -->
      <div class="welcome-section">
        <h2 class="welcome-title">欢迎使用多智能体开发平台</h2>
        <p class="welcome-subtitle">通过AI智能体协同，让全栈开发变得简单高效</p>
      </div>

      <!-- 主要功能卡片 -->
      <div class="feature-cards">
        <!-- AI开发平台大卡片 -->
        <div class="main-feature-card" @click="$router.push('/ai-platform')">
          <div class="feature-icon">🤖</div>
          <h3 class="feature-title">AI开发平台</h3>
          <p class="feature-description">
            选择专业的AI智能体，获得产品设计、后端开发、前端开发的专业指导，
            让您的项目开发更加高效和专业。
          </p>
          <div class="feature-button">
            进入平台
            <span class="arrow-right">→</span>
          </div>
        </div>

        <!-- 其他功能卡片 -->
        <div class="secondary-cards">
          <div class="secondary-card" @click="$router.push('/user-center')">
            <div class="secondary-icon">👤</div>
            <h4>用户中心</h4>
            <p>管理个人信息</p>
          </div>

          <div class="secondary-card" @click="$router.push('/change-password')">
            <div class="secondary-icon">🔒</div>
            <h4>修改密码</h4>
            <p>更新登录密码</p>
          </div>

          <div class="secondary-card" @click="$router.push('/document-manager')">
            <div class="secondary-icon">📚</div>
            <h4>文档管理</h4>
            <p>管理技术文档</p>
          </div>

          <div class="secondary-card coming-soon">
            <div class="secondary-icon">📊</div>
            <h4>项目管理</h4>
            <p>即将上线</p>
          </div>

          <div class="secondary-card coming-soon">
            <div class="secondary-icon">📚</div>
            <h4>学习中心</h4>
            <p>即将上线</p>
          </div>
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
  background: #ffffff;
}

/* 删除原来的 .header 相关样式 */

/* 主要内容区域 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 48px;
}

.welcome-title {
  font-size: 36px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 16px 0;
  line-height: 1.2;
}

.welcome-subtitle {
  font-size: 18px;
  color: #656d76;
  margin: 0;
  line-height: 1.5;
}

/* 功能卡片区域 */
.feature-cards {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 32px;
  align-items: start;
}

/* 主要功能卡片 */
.main-feature-card {
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 12px;
  padding: 48px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.main-feature-card:hover {
  border-color: #007AFF;
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.12);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.feature-title {
  font-size: 28px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 16px 0;
}

.feature-description {
  font-size: 16px;
  color: #656d76;
  line-height: 1.6;
  margin: 0 0 32px 0;
}

.feature-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #007AFF;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.main-feature-card:hover .feature-button {
  background: #0056CC;
}

.arrow-right {
  transition: transform 0.2s ease;
}

.main-feature-card:hover .arrow-right {
  transform: translateX(4px);
}

/* 次要功能卡片 */
.secondary-cards {
  display: grid;
  gap: 16px;
}

.secondary-card {
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.secondary-card:hover:not(.coming-soon) {
  border-color: #007AFF;
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.1);
}

.secondary-card.coming-soon {
  opacity: 0.6;
  cursor: not-allowed;
}

.secondary-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.secondary-card h4 {
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 8px 0;
}

.secondary-card p {
  font-size: 14px;
  color: #656d76;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 32px 16px;
  }

  .welcome-title {
    font-size: 28px;
  }

  .welcome-subtitle {
    font-size: 16px;
  }

  .feature-cards {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .main-feature-card {
    padding: 32px 24px;
  }

  .feature-title {
    font-size: 24px;
  }
}
</style>
