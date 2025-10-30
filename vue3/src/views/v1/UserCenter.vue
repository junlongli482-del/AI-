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
      <div class="content-wrapper">
        <!-- 个人信息主卡片 -->
        <div class="profile-main-card">
          <div class="profile-header">
            <div class="avatar-section">
              <div class="avatar-circle">
                <span class="avatar-text">{{ getAvatarText() }}</span>
              </div>
              <div class="profile-info">
                <h2 class="display-name">{{ userInfo?.display_name || userInfo?.username }}</h2>
                <p class="username-text">@{{ userInfo?.username }}</p>
                <div class="user-badges">
                  <span class="badge verified">已验证</span>
                  <span class="badge member-since">{{ getMemberDuration() }}</span>
                </div>
              </div>
            </div>
            <div class="profile-stats">
              <div class="stat-item">
                <span class="stat-number">{{ userStats.documentsCount || 0 }}</span>
                <span class="stat-label">文档</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ userStats.favoritesCount || 0 }}</span>
                <span class="stat-label">收藏</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ userStats.likesCount || 0 }}</span>
                <span class="stat-label">点赞</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 功能入口网格 -->
        <div class="features-grid">
          <div class="feature-card primary" @click="$router.push('/my-favorites')">
            <div class="feature-icon">📚</div>
            <div class="feature-content">
              <h3 class="feature-title">我的收藏</h3>
              <p class="feature-desc">查看收藏的文档</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>

          <div class="feature-card secondary" @click="$router.push('/document-manager')">
            <div class="feature-icon">📝</div>
            <div class="feature-content">
              <h3 class="feature-title">文档管理</h3>
              <p class="feature-desc">管理我的文档</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>

          <div class="feature-card tertiary" @click="$router.push('/tech-square')">
            <div class="feature-icon">🌟</div>
            <div class="feature-content">
              <h3 class="feature-title">技术广场</h3>
              <p class="feature-desc">发现优质内容</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>

          <div class="feature-card quaternary" @click="$router.push('/ai-platform')">
            <div class="feature-icon">🤖</div>
            <div class="feature-content">
              <h3 class="feature-title">AI平台</h3>
              <p class="feature-desc">智能助手工具</p>
            </div>
            <div class="feature-arrow">→</div>
          </div>
        </div>

        <!-- 详细信息卡片 -->
        <div class="details-card">
          <h3 class="card-title">账户信息</h3>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-label">
                <span class="label-icon">👤</span>
                <span class="label-text">用户名</span>
              </div>
              <span class="info-value">{{ userInfo?.username }}</span>
            </div>

            <div class="info-item">
              <div class="info-label">
                <span class="label-icon">📧</span>
                <span class="label-text">邮箱</span>
              </div>
              <span class="info-value">{{ userInfo?.email }}</span>
            </div>

            <div class="info-item">
              <div class="info-label">
                <span class="label-icon">✨</span>
                <span class="label-text">昵称</span>
              </div>
              <div class="nickname-section">
                <span v-if="!isEditingNickname" class="info-value">
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
                  class="edit-btn"
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
              <div class="info-label">
                <span class="label-icon">📅</span>
                <span class="label-text">注册时间</span>
              </div>
              <span class="info-value">{{ formatDate(userInfo?.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮区域 -->
        <div class="actions-card">
          <div class="actions-grid">
            <el-button
              type="primary"
              @click="$router.push('/change-password')"
              class="action-button primary-action"
            >
              <span class="action-icon">🔒</span>
              <span class="action-text">修改密码</span>
            </el-button>

            <el-button
              @click="handleLogout"
              class="action-button secondary-action"
            >
              <span class="action-icon">🚪</span>
              <span class="action-text">退出登录</span>
            </el-button>
          </div>
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
import { getMyStats } from '@/api/v2/interaction'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const userInfo = ref(null)
const userStats = ref({})
const isEditingNickname = ref(false)
const editNickname = ref('')
const savingNickname = ref(false)
const nicknameChecking = ref(false)
const nicknameAvailable = ref(null)

onMounted(async () => {
  await loadUserProfile()
  await loadUserStats()
})

const loadUserProfile = async () => {
  try {
    userInfo.value = await getUserProfile()
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  }
}

const loadUserStats = async () => {
  try {
    const stats = await getMyStats()
    userStats.value = {
      documentsCount: stats.total_documents || 0,
      favoritesCount: stats.total_favorites || 0,
      likesCount: stats.total_likes_received || 0
    }
  } catch (error) {
    console.warn('获取用户统计失败:', error)
  }
}

const getAvatarText = () => {
  const name = userInfo.value?.display_name || userInfo.value?.username || '用户'
  return name.charAt(0).toUpperCase()
}

const getMemberDuration = () => {
  if (!userInfo.value?.created_at) return '新成员'

  const createDate = new Date(userInfo.value.created_at)
  const now = new Date()
  const diffTime = Math.abs(now - createDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays < 30) {
    return '新成员'
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    return `${months}个月`
  } else {
    const years = Math.floor(diffDays / 365)
    return `${years}年`
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
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}
</script>

<style scoped>
.user-center-container {
  min-height: 100vh;
  background: linear-gradient(135deg,
  rgba(255, 154, 158, 0.1) 0%,
  rgba(250, 208, 196, 0.1) 25%,
  rgba(168, 237, 234, 0.1) 50%,
  rgba(254, 214, 227, 0.1) 75%,
  rgba(255, 234, 167, 0.1) 100%
  );
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 48px 24px;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 个人信息主卡片 */
.profile-main-card {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  border-radius: 24px;
  padding: 40px;
  color: white;
  box-shadow: 0 20px 40px rgba(255, 154, 158, 0.3);
  position: relative;
  overflow: hidden;
}

.profile-main-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, transparent 100%);
  pointer-events: none;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  position: relative;
  z-index: 1;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
}

.avatar-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.avatar-text {
  font-size: 32px;
  font-weight: 600;
  color: white;
}

.profile-info {
  flex: 1;
}

.display-name {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: white;
}

.username-text {
  font-size: 16px;
  margin: 0 0 16px 0;
  color: rgba(255, 255, 255, 0.8);
}

.user-badges {
  display: flex;
  gap: 12px;
}

.badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.profile-stats {
  display: flex;
  gap: 32px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: white;
}

.stat-label {
  display: block;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4px;
}

/* 功能入口网格 */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.5);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.feature-card.primary::before {
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
}

.feature-card.secondary::before {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.feature-card.tertiary::before {
  background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
}

.feature-card.quaternary::before {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.feature-card:hover::before {
  opacity: 0.1;
}

.feature-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.feature-content {
  flex: 1;
}

.feature-title {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 4px 0;
}

.feature-desc {
  font-size: 14px;
  color: #86868b;
  margin: 0;
}

.feature-arrow {
  font-size: 18px;
  color: #86868b;
  transition: all 0.3s ease;
}

.feature-card:hover .feature-arrow {
  color: #007AFF;
  transform: translateX(4px);
}

/* 详细信息卡片 */
.details-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 24px 0;
}

.info-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 12px;
}

.label-icon {
  font-size: 18px;
}

.label-text {
  font-size: 15px;
  font-weight: 500;
  color: #86868b;
}

.info-value {
  font-size: 15px;
  color: #1d1d1f;
  font-weight: 500;
}

.nickname-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.nickname-input {
  max-width: 200px;
}

.edit-btn {
  font-size: 14px;
}

.edit-buttons {
  display: flex;
  gap: 8px;
}

/* 操作按钮区域 */
.actions-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-button {
  height: 56px;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.primary-action {
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  border: none;
  color: white;
}

.primary-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 122, 255, 0.4);
}

.secondary-action {
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #86868b;
}

.secondary-action:hover {
  background: rgba(255, 59, 48, 0.1);
  border-color: rgba(255, 59, 48, 0.3);
  color: #FF3B30;
  transform: translateY(-2px);
}

.action-icon {
  font-size: 18px;
}

.action-text {
  font-size: 15px;
}

/* 状态图标 */
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

/* Element Plus 样式覆盖 */
:deep(.el-dropdown-menu__item) {
  padding: 12px 20px;
}

:deep(.el-input__wrapper) {
  border-radius: 12px;
}

:deep(.el-button) {
  border-radius: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    padding: 24px 16px;
  }

  .profile-main-card {
    padding: 24px;
  }

  .profile-header {
    flex-direction: column;
    gap: 24px;
  }

  .avatar-section {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .profile-stats {
    justify-content: center;
    gap: 24px;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .nickname-section {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .avatar-circle {
    width: 60px;
    height: 60px;
  }

  .avatar-text {
    font-size: 24px;
  }

  .display-name {
    font-size: 24px;
  }

  .details-card,
  .actions-card {
    padding: 20px;
  }
}
</style>
