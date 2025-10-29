<template>
  <div class="ai-platform-container">
    <!-- 使用公用导航栏组件 -->
    <AppHeader />

    <!-- 主要内容区域 -->
    <main class="main-content">
      <div class="platform-header">
        <h2 class="platform-title">选择您的AI开发助手</h2>
        <p class="platform-subtitle">每个智能体都有专业的领域知识，可以为您提供针对性的开发指导</p>
      </div>

      <!-- 智能体卡片区域 -->
      <div class="agents-grid">
        <!-- 产品经理智能体 -->
        <div class="agent-card" @click="openAgent('product')">
          <div class="agent-header">
            <div class="agent-avatar">📋</div>
            <div class="agent-info">
              <h3 class="agent-name">产品经理智能体</h3>
              <p class="agent-role">Product Manager AI</p>
            </div>
          </div>
          <p class="agent-description">
            帮助您进行需求分析、产品设计和项目规划，制定清晰的开发路线图
          </p>
          <div class="agent-skills">
            <span class="skill-tag">需求分析</span>
            <span class="skill-tag">产品设计</span>
            <span class="skill-tag">项目规划</span>
          </div>
          <button class="start-chat-btn">
            开始对话
            <span class="btn-arrow">→</span>
          </button>
        </div>

        <!-- 后端开发智能体 -->
        <div class="agent-card" @click="openAgent('backend')">
          <div class="agent-header">
            <div class="agent-avatar">⚙️</div>
            <div class="agent-info">
              <h3 class="agent-name">后端开发智能体</h3>
              <p class="agent-role">Backend Developer AI</p>
            </div>
          </div>
          <p class="agent-description">
            专业的后端架构设计、API开发和数据库设计指导，助您构建稳定的后端系统
          </p>
          <div class="agent-skills">
            <span class="skill-tag">API设计</span>
            <span class="skill-tag">数据库</span>
            <span class="skill-tag">系统架构</span>
          </div>
          <button class="start-chat-btn">
            开始对话
            <span class="btn-arrow">→</span>
          </button>
        </div>

        <!-- 前端开发智能体 -->
        <div class="agent-card" @click="openAgent('frontend')">
          <div class="agent-header">
            <div class="agent-avatar">🎨</div>
            <div class="agent-info">
              <h3 class="agent-name">前端开发智能体</h3>
              <p class="agent-role">Frontend Developer AI</p>
            </div>
          </div>
          <p class="agent-description">
            提供UI/UX设计建议、前端技术选型和代码实现指导，打造优秀的用户体验
          </p>
          <div class="agent-skills">
            <span class="skill-tag">UI设计</span>
            <span class="skill-tag">交互体验</span>
            <span class="skill-tag">前端框架</span>
          </div>
          <button class="start-chat-btn">
            开始对话
            <span class="btn-arrow">→</span>
          </button>
        </div>
      </div>

      <!-- 使用说明按钮 -->
      <div class="help-section">
        <button class="help-button" @click="showHelp = true">
          📖 使用说明
        </button>
      </div>
    </main>

    <!-- 使用说明侧边栏 -->
    <div class="help-overlay" v-if="showHelp" @click="showHelp = false"></div>
    <div class="help-panel" :class="{ show: showHelp }">
      <div class="help-header">
        <h3>使用说明</h3>
        <button class="close-btn" @click="showHelp = false">✕</button>
      </div>
      <div class="help-content">
        <div class="help-section">
          <h4>🤖 智能体介绍</h4>
          <div class="help-item">
            <strong>产品经理智能体</strong>
            <p>负责项目的整体规划和需求分析，帮助您明确项目目标和功能范围。</p>
          </div>
          <div class="help-item">
            <strong>后端开发智能体</strong>
            <p>专注于服务器端开发，包括API设计、数据库架构和系统性能优化。</p>
          </div>
          <div class="help-item">
            <strong>前端开发智能体</strong>
            <p>专注于用户界面开发，包括页面设计、交互逻辑和用户体验优化。</p>
          </div>
        </div>

        <div class="help-section">
          <h4>📋 建议使用顺序</h4>
          <div class="workflow-steps">
            <div class="workflow-step">
              <span class="step-number">1</span>
              <div class="step-content">
                <strong>产品经理智能体</strong>
                <p>首先明确项目需求和功能规划</p>
              </div>
            </div>
            <div class="workflow-step">
              <span class="step-number">2</span>
              <div class="step-content">
                <strong>后端开发智能体</strong>
                <p>设计数据结构和API接口</p>
              </div>
            </div>
            <div class="workflow-step">
              <span class="step-number">3</span>
              <div class="step-content">
                <strong>前端开发智能体</strong>
                <p>实现用户界面和交互功能</p>
              </div>
            </div>
          </div>
        </div>

        <div class="help-section">
          <h4>💡 使用技巧</h4>
          <ul class="tips-list">
            <li>可以随时切换不同的智能体获取专业建议</li>
            <li>建议将对话内容保存下来，便于后续参考</li>
            <li>遇到跨领域问题时，可以咨询多个智能体</li>
            <li>每个智能体都会根据您的具体需求提供定制化建议</li>
          </ul>
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
  background: #ffffff;
}

/* 主要内容区域 */
.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 48px 24px;
}

.platform-header {
  text-align: center;
  margin-bottom: 48px;
}

.platform-title {
  font-size: 32px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 16px 0;
  line-height: 1.2;
}

.platform-subtitle {
  font-size: 18px;
  color: #656d76;
  margin: 0;
  line-height: 1.5;
}

/* 智能体卡片网格 */
.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 32px;
  margin-bottom: 48px;
}

.agent-card {
  background: #ffffff;
  border: 1px solid #d0d7de;
  border-radius: 12px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.agent-card:hover {
  border-color: #007AFF;
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.12);
  transform: translateY(-4px);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.agent-avatar {
  font-size: 48px;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f6f8fa;
  border-radius: 12px;
}

.agent-name {
  font-size: 20px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 4px 0;
}

.agent-role {
  font-size: 14px;
  color: #656d76;
  margin: 0;
}

.agent-description {
  font-size: 16px;
  color: #656d76;
  line-height: 1.6;
  margin: 0 0 24px 0;
}

.agent-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.skill-tag {
  background: #f6f8fa;
  color: #24292f;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.start-chat-btn {
  width: 100%;
  background: #007AFF;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.agent-card:hover .start-chat-btn {
  background: #0056CC;
}

.btn-arrow {
  transition: transform 0.2s ease;
}

.agent-card:hover .btn-arrow {
  transform: translateX(4px);
}

/* 使用说明按钮区域 */
.help-section {
  text-align: center;
}

.help-button {
  background: #f6f8fa;
  border: 1px solid #d0d7de;
  color: #24292f;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.help-button:hover {
  background: #f3f4f6;
  border-color: #007AFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 使用说明面板 */
.help-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.help-panel {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  height: 100vh;
  background: #ffffff;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.15);
  transition: right 0.3s ease;
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
  padding: 24px;
  border-bottom: 1px solid #e1e4e8;
}

.help-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #24292f;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #656d76;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: #f6f8fa;
  color: #24292f;
}

.help-content {
  padding: 24px;
}

.help-content .help-section {
  margin-bottom: 32px;
}

.help-content .help-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #24292f;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.help-item {
  margin-bottom: 16px;
  padding: 16px;
  background: #f6f8fa;
  border-radius: 8px;
}

.help-item strong {
  display: block;
  color: #24292f;
  margin-bottom: 4px;
}

.help-item p {
  color: #656d76;
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.workflow-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.workflow-step {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.step-number {
  background: #007AFF;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content strong {
  display: block;
  color: #24292f;
  margin-bottom: 4px;
  font-size: 14px;
}

.step-content p {
  color: #656d76;
  margin: 0;
  font-size: 13px;
  line-height: 1.4;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
}

.tips-list li {
  color: #656d76;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 32px 16px;
  }

  .platform-title {
    font-size: 28px;
  }

  .platform-subtitle {
    font-size: 16px;
  }

  .agents-grid {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .agent-card {
    padding: 24px;
  }

  .help-panel {
    width: 100%;
    right: -100%;
  }
}
</style>
