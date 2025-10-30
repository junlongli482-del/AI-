<template>
  <div class="ai-platform-container">
    <!-- 使用公用导航栏组件 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- 平台头部 -->
      <div class="platform-header">
        <div class="header-content">
          <div class="header-text">
            <h1 class="platform-title">AI 智能开发助手</h1>
            <p class="platform-subtitle">专业的多智能体协作平台，为您的开发之旅提供全方位支持</p>
            <div class="platform-stats">
              <div class="stat-item">
                <span class="stat-number">3</span>
                <span class="stat-label">专业智能体</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">24/7</span>
                <span class="stat-label">在线服务</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">∞</span>
                <span class="stat-label">创意可能</span>
              </div>
            </div>
          </div>
          <div class="header-visual">
            <div class="ai-icon-container">
              <div class="ai-icon">🤖</div>
              <div class="pulse-ring"></div>
              <div class="pulse-ring delay-1"></div>
              <div class="pulse-ring delay-2"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 智能体卡片区域 -->
      <div class="agents-section">
        <div class="section-header">
          <h2 class="section-title">选择您的专属助手</h2>
          <p class="section-desc">每个智能体都拥有专业的领域知识，为您提供精准的开发指导</p>
        </div>

        <div class="agents-grid">
          <!-- 产品经理智能体 -->
          <div class="agent-card product-manager" @click="openAgent('product')">
            <div class="card-background"></div>
            <div class="card-content">
              <div class="agent-header">
                <div class="agent-avatar">
                  <span class="avatar-icon">📋</span>
                  <div class="avatar-glow"></div>
                </div>
                <div class="agent-status">
                  <span class="status-dot"></span>
                  <span class="status-text">在线</span>
                </div>
              </div>

              <div class="agent-info">
                <h3 class="agent-name">产品经理智能体</h3>
                <p class="agent-role">Product Manager AI</p>
                <p class="agent-description">
                  专业的需求分析师，帮助您梳理产品思路，制定清晰的开发路线图，确保项目成功落地
                </p>
              </div>

              <div class="agent-capabilities">
                <div class="capability-item">
                  <span class="capability-icon">🎯</span>
                  <span class="capability-text">需求分析</span>
                </div>
                <div class="capability-item">
                  <span class="capability-icon">🎨</span>
                  <span class="capability-text">设计</span>
                </div>
                <div class="capability-item">
                  <span class="capability-icon">📊</span>
                  <span class="capability-text">项目规划</span>
                </div>
              </div>

              <button class="chat-button">
                <span class="button-text">开始协作</span>
                <span class="button-icon">→</span>
              </button>
            </div>
          </div>

          <!-- 后端开发智能体 -->
          <div class="agent-card backend-developer" @click="openAgent('backend')">
            <div class="card-background"></div>
            <div class="card-content">
              <div class="agent-header">
                <div class="agent-avatar">
                  <span class="avatar-icon">⚙️</span>
                  <div class="avatar-glow"></div>
                </div>
                <div class="agent-status">
                  <span class="status-dot"></span>
                  <span class="status-text">在线</span>
                </div>
              </div>

              <div class="agent-info">
                <h3 class="agent-name">后端开发智能体</h3>
                <p class="agent-role">Backend Developer AI</p>
                <p class="agent-description">
                  资深的架构师，精通服务器端开发，为您构建稳定、高效、可扩展的后端系统
                </p>
              </div>

              <div class="agent-capabilities">
                <div class="capability-item">
                  <span class="capability-icon">🔗</span>
                  <span class="capability-text">API设计</span>
                </div>
                <div class="capability-item">
                  <span class="capability-icon">🗄️</span>
                  <span class="capability-text">数据库</span>
                </div>
                <div class="capability-item">
                  <span class="capability-icon">🏗️</span>
                  <span class="capability-text">系统架构</span>
                </div>
              </div>

              <button class="chat-button">
                <span class="button-text">开始协作</span>
                <span class="button-icon">→</span>
              </button>
            </div>
          </div>

          <!-- 前端开发智能体 -->
          <div class="agent-card frontend-developer" @click="openAgent('frontend')">
            <div class="card-background"></div>
            <div class="card-content">
              <div class="agent-header">
                <div class="agent-avatar">
                  <span class="avatar-icon">🎨</span>
                  <div class="avatar-glow"></div>
                </div>
                <div class="agent-status">
                  <span class="status-dot"></span>
                  <span class="status-text">在线</span>
                </div>
              </div>

              <div class="agent-info">
                <h3 class="agent-name">前端开发智能体</h3>
                <p class="agent-role">Frontend Developer AI</p>
                <p class="agent-description">
                  创意设计师，专注用户体验，帮您打造美观易用的界面，提升产品竞争力
                </p>
              </div>

              <div class="agent-capabilities">
                <div class="capability-item">
                  <span class="capability-icon">🎭</span>
                  <span class="capability-text">UI设计</span>
                </div>
                <div class="capability-item">
                  <span class="capability-icon">✨</span>
                  <span class="capability-text">交互体验</span>
                </div>
                <div class="capability-item">
                  <span class="capability-icon">⚡</span>
                  <span class="capability-text">前端框架</span>
                </div>
              </div>

              <button class="chat-button">
                <span class="button-text">开始协作</span>
                <span class="button-icon">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 工作流程指南 -->
      <div class="workflow-section">
        <div class="section-header">
          <h2 class="section-title">协作工作流</h2>
          <p class="section-desc">建议的智能体协作顺序，让您的开发更加高效</p>
        </div>

        <div class="workflow-container">
          <div class="workflow-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <div class="step-icon">📋</div>
              <h4 class="step-title">需求规划</h4>
              <p class="step-desc">与产品经理智能体明确项目目标和功能需求</p>
            </div>
            <div class="step-arrow">→</div>
          </div>

          <div class="workflow-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <div class="step-icon">⚙️</div>
              <h4 class="step-title">架构设计</h4>
              <p class="step-desc">后端智能体帮您设计数据结构和API接口</p>
            </div>
            <div class="step-arrow">→</div>
          </div>

          <div class="workflow-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <div class="step-icon">🎨</div>
              <h4 class="step-title">界面实现</h4>
              <p class="step-desc">前端智能体协助完成用户界面和交互功能</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 快速入门 -->
      <div class="quick-start-section">
        <div class="quick-start-card">
          <div class="quick-start-content">
            <div class="quick-start-icon">💡</div>
            <div class="quick-start-text">
              <h3>首次使用？</h3>
              <p>查看使用指南，快速上手AI协作开发</p>
            </div>
          </div>
          <button class="help-button" @click="showHelp = true">
            <span class="help-icon">📖</span>
            <span class="help-text">使用指南</span>
          </button>
        </div>
      </div>
    </main>

    <!-- 使用说明侧边栏 -->
    <div class="help-overlay" v-if="showHelp" @click="showHelp = false"></div>
    <div class="help-panel" :class="{ show: showHelp }">
      <div class="help-header">
        <h3>使用指南</h3>
        <button class="close-btn" @click="showHelp = false">✕</button>
      </div>
      <div class="help-content">
        <div class="help-section">
          <h4>🤖 智能体介绍</h4>
          <div class="help-item">
            <div class="help-item-header">
              <span class="help-icon">📋</span>
              <strong>产品经理智能体</strong>
            </div>
            <p>负责项目的整体规划和需求分析，帮助您明确项目目标和功能范围，制定可行的开发计划。</p>
          </div>
          <div class="help-item">
            <div class="help-item-header">
              <span class="help-icon">⚙️</span>
              <strong>后端开发智能体</strong>
            </div>
            <p>专注于服务器端开发，包括API设计、数据库架构、系统性能优化和安全性保障。</p>
          </div>
          <div class="help-item">
            <div class="help-item-header">
              <span class="help-icon">🎨</span>
              <strong>前端开发智能体</strong>
            </div>
            <p>专注于用户界面开发，包括页面设计、交互逻辑、用户体验优化和前端性能提升。</p>
          </div>
        </div>

        <div class="help-section">
          <h4>💡 使用技巧</h4>
          <ul class="tips-list">
            <li>💬 详细描述您的需求，智能体会提供更精准的建议</li>
            <li>🔄 可以随时切换不同智能体获取专业意见</li>
            <li>📝 建议保存重要的对话内容，便于后续参考</li>
            <li>🤝 遇到跨领域问题时，可以咨询多个智能体</li>
            <li>⚡ 每个智能体都会根据您的具体情况提供定制化方案</li>
          </ul>
        </div>

        <div class="help-section">
          <h4>🚀 最佳实践</h4>
          <div class="best-practice">
            <div class="practice-step">
              <span class="practice-number">1</span>
              <div class="practice-content">
                <strong>明确目标</strong>
                <p>先与产品经理智能体讨论项目整体规划</p>
              </div>
            </div>
            <div class="practice-step">
              <span class="practice-number">2</span>
              <div class="practice-content">
                <strong>技术选型</strong>
                <p>根据需求选择合适的技术栈和架构方案</p>
              </div>
            </div>
            <div class="practice-step">
              <span class="practice-number">3</span>
              <div class="practice-content">
                <strong>迭代开发</strong>
                <p>按功能模块逐步实现，及时获取反馈</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import AppHeader from '@/components/layout/AppHeader.vue'

const userStore = useUserStore()
const showHelp = ref(false)

// 智能体链接配置
const agentLinks = {
  product: 'http://erp.miraclink.com:5200/chat/LLUIQ4m06aZt0dck',
  backend: 'http://erp.miraclink.com:5200/chat/LtBUUEORn88YH5h1',
  frontend: 'http://erp.miraclink.com:5200/chat/LtBUUEORn88YH5h1'
}

onMounted(async () => {
  try {
    await userStore.getUserInfo()
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
})

const openAgent = (agentType) => {
  const url = agentLinks[agentType]
  if (url) {
    window.open(url, '_blank')
  }
}
</script>

<style scoped>
.ai-platform-container {
  min-height: 100vh;
  background: linear-gradient(135deg,
  rgba(74, 144, 226, 0.05) 0%,
  rgba(80, 200, 120, 0.05) 25%,
  rgba(255, 159, 67, 0.05) 50%,
  rgba(238, 82, 83, 0.05) 75%,
  rgba(162, 155, 254, 0.05) 100%
  );
}

.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px 80px;
}

/* 平台头部 */
.platform-header {
  padding: 80px 0;
  margin-bottom: 80px;
}

.header-content {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 60px;
  align-items: center;
}

.header-text {
  max-width: 600px;
}

.platform-title {
  font-size: 48px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0 0 24px 0;
  line-height: 1.1;
  background: linear-gradient(135deg, #4A90E2 0%, #50C878 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.platform-subtitle {
  font-size: 20px;
  color: #86868b;
  margin: 0 0 40px 0;
  line-height: 1.5;
}

.platform-stats {
  display: flex;
  gap: 40px;
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

.header-visual {
  display: flex;
  justify-content: center;
  align-items: center;
}

.ai-icon-container {
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-icon {
  font-size: 80px;
  z-index: 2;
  position: relative;
  filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.15));
}

.pulse-ring {
  position: absolute;
  border: 3px solid rgba(74, 144, 226, 0.3);
  border-radius: 50%;
  animation: pulse 2s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
}

.pulse-ring.delay-1 {
  animation-delay: 0.5s;
}

.pulse-ring.delay-2 {
  animation-delay: 1s;
}

@keyframes pulse {
  0% {
    width: 100px;
    height: 100px;
    opacity: 1;
  }
  100% {
    width: 200px;
    height: 200px;
    opacity: 0;
  }
}

/* 智能体区域 */
.agents-section {
  margin-bottom: 100px;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-size: 36px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 16px 0;
}

.section-desc {
  font-size: 18px;
  color: #86868b;
  margin: 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 32px;
}

.agent-card {
  position: relative;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  border: 1px solid rgba(255, 255, 255, 0.5);
  overflow: hidden;
}

.card-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.4s ease;
  border-radius: 24px;
}

.product-manager .card-background {
  background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
}

.backend-developer .card-background {
  background: linear-gradient(135deg, #50C878 0%, #3A9B5C 100%);
}

.frontend-developer .card-background {
  background: linear-gradient(135deg, #FF9F43 0%, #E67E22 100%);
}

.agent-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.agent-card:hover .card-background {
  opacity: 0.1;
}

.card-content {
  position: relative;
  z-index: 1;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.agent-avatar {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.avatar-icon {
  font-size: 28px;
  z-index: 2;
}

.avatar-glow {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  border-radius: 24px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.product-manager .avatar-glow {
  background: linear-gradient(135deg, #4A90E2, #357ABD);
}

.backend-developer .avatar-glow {
  background: linear-gradient(135deg, #50C878, #3A9B5C);
}

.frontend-developer .avatar-glow {
  background: linear-gradient(135deg, #FF9F43, #E67E22);
}

.agent-card:hover .avatar-glow {
  opacity: 0.3;
}

.agent-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(80, 200, 120, 0.1);
  border-radius: 20px;
  border: 1px solid rgba(80, 200, 120, 0.2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #50C878;
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  color: #50C878;
  font-weight: 500;
}

.agent-info {
  margin-bottom: 24px;
}

.agent-name {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
}

.agent-role {
  font-size: 14px;
  color: #86868b;
  margin: 0 0 16px 0;
  font-weight: 500;
}

.agent-description {
  font-size: 16px;
  color: #86868b;
  line-height: 1.6;
  margin: 0;
}

.agent-capabilities {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 32px;
}

.capability-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.agent-card:hover .capability-item {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
}

.capability-icon {
  font-size: 14px;
}

.capability-text {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.chat-button {
  width: 100%;
  height: 56px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #1d1d1f 0%, #86868b 100%);
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.product-manager:hover .chat-button {
  background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
}

.backend-developer:hover .chat-button {
  background: linear-gradient(135deg, #50C878 0%, #3A9B5C 100%);
}

.frontend-developer:hover .chat-button {
  background: linear-gradient(135deg, #FF9F43 0%, #E67E22 100%);
}

.chat-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.button-icon {
  transition: transform 0.3s ease;
}

.chat-button:hover .button-icon {
  transform: translateX(4px);
}

/* 工作流程 */
.workflow-section {
  margin-bottom: 80px;
}

.workflow-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  flex-wrap: wrap;
}

.workflow-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  max-width: 280px;
}

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A90E2 0%, #50C878 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(74, 144, 226, 0.3);
}

.step-content {
  text-align: center;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  padding: 24px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.step-icon {
  font-size: 32px;
  margin-bottom: 16px;
}

.step-title {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 12px 0;
}

.step-desc {
  font-size: 14px;
  color: #86868b;
  margin: 0;
  line-height: 1.5;
}

.step-arrow {
  position: absolute;
  right: -40px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
  color: #86868b;
}

.workflow-step:last-child .step-arrow {
  display: none;
}

/* 快速入门 */
.quick-start-section {
  margin-bottom: 60px;
}

.quick-start-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.quick-start-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
}

.quick-start-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.quick-start-icon {
  font-size: 48px;
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.1));
}

.quick-start-text h3 {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
}

.quick-start-text p {
  font-size: 16px;
  color: #86868b;
  margin: 0;
}

.help-button {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #4A90E2 0%, #50C878 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.help-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(74, 144, 226, 0.3);
}

/* 帮助面板 */
.help-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 1000;
  opacity: 0;
  animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
  to { opacity: 1; }
}

.help-panel {
  position: fixed;
  top: 0;
  right: -500px;
  width: 500px;
  height: 100vh;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.15);
  transition: right 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
  z-index: 1001;
  overflow-y: auto;
}

.help-panel.show {
  right: 0;
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.help-header h3 {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
}

.close-btn {
  width: 40px;
  height: 40px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  font-size: 18px;
  color: #86868b;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 59, 48, 0.1);
  color: #FF3B30;
}

.help-content {
  padding: 32px;
}

.help-section {
  margin-bottom: 40px;
}

.help-section h4 {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.help-item {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.help-item:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
}

.help-item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.help-item-header strong {
  font-size: 16px;
  color: #1d1d1f;
}

.help-item p {
  color: #86868b;
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
}

.tips-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.tips-list li {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  color: #86868b;
  font-size: 14px;
  line-height: 1.6;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.tips-list li:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateX(4px);
}

.best-practice {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.practice-step {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.practice-step:hover {
  background: rgba(255, 255, 255, 0.9);
  transform: translateY(-2px);
}

.practice-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A90E2 0%, #50C878 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.practice-content strong {
  display: block;
  color: #1d1d1f;
  margin-bottom: 8px;
  font-size: 15px;
}

.practice-content p {
  color: #86868b;
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .header-content {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }

  .agents-grid {
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 0 16px 60px;
  }

  .platform-header {
    padding: 40px 0;
    margin-bottom: 60px;
  }

  .platform-title {
    font-size: 36px;
  }

  .platform-subtitle {
    font-size: 18px;
  }

  .platform-stats {
    justify-content: center;
    gap: 24px;
  }

  .agents-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .agent-card {
    padding: 24px;
  }

  .workflow-container {
    flex-direction: column;
    gap: 24px;
  }

  .step-arrow {
    display: none;
  }

  .quick-start-card {
    flex-direction: column;
    gap: 24px;
    text-align: center;
    padding: 32px 24px;
  }

  .help-panel {
    width: 100%;
    right: -100%;
  }
}

@media (max-width: 480px) {
  .platform-title {
    font-size: 28px;
  }

  .section-title {
    font-size: 28px;
  }

  .agent-card {
    padding: 20px;
  }

  .help-content {
    padding: 24px 20px;
  }
}
</style>
