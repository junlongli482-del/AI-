<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Logo区域 -->
      <div class="logo-section" @click="$router.push('/home')">
        <div class="logo-icon">🚀</div>
        <h1 class="logo-text">智能开发平台</h1>
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <router-link to="/home" class="nav-item">
          <span class="nav-icon">🏠</span>
          <span class="nav-text">首页</span>
        </router-link>
        <router-link to="/document-manager" class="nav-item">
          <span class="nav-icon">📚</span>
          <span class="nav-text">文档管理</span>
        </router-link>
        <router-link to="/ai-platform" class="nav-item">
          <span class="nav-icon">🤖</span>
          <span class="nav-text">AI平台</span>
        </router-link>
        <router-link to="/tech-square" class="nav-item">
          <span class="nav-icon">🌟</span>
          <span class="nav-text">技术广场</span>
        </router-link>
      </nav>

      <!-- 用户菜单 -->
      <div class="user-section">
        <el-dropdown @command="handleCommand" trigger="click">
          <div class="user-info">
            <div class="user-avatar">
              <span class="avatar-text">{{ getAvatarText() }}</span>
            </div>
            <div class="user-details">
              <span class="username">{{ displayName }}</span>
              <span class="user-role">开发者</span>
            </div>
            <span class="dropdown-arrow">▼</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="user-dropdown">
              <el-dropdown-item command="profile" class="dropdown-item">
                <span class="item-icon">👤</span>
                <span class="item-text">用户中心</span>
              </el-dropdown-item>
              <el-dropdown-item command="settings" class="dropdown-item">
                <span class="item-icon">⚙️</span>
                <span class="item-text">设置</span>
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided class="dropdown-item logout">
                <span class="item-icon">🚪</span>
                <span class="item-text">退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <!-- 移动端菜单按钮 -->
      <div class="mobile-menu-btn" @click="toggleMobileMenu">
        <span class="menu-icon">☰</span>
      </div>
    </div>

    <!-- 移动端导航菜单 -->
    <div class="mobile-nav" :class="{ 'mobile-nav-open': mobileMenuOpen }">
      <router-link to="/home" class="mobile-nav-item" @click="closeMobileMenu">
        <span class="nav-icon">🏠</span>
        <span class="nav-text">首页</span>
      </router-link>
      <router-link to="/document-manager" class="mobile-nav-item" @click="closeMobileMenu">
        <span class="nav-icon">📚</span>
        <span class="nav-text">文档管理</span>
      </router-link>
      <router-link to="/ai-platform" class="mobile-nav-item" @click="closeMobileMenu">
        <span class="nav-icon">🤖</span>
        <span class="nav-text">AI平台</span>
      </router-link>
      <router-link to="/tech-square" class="mobile-nav-item" @click="closeMobileMenu">
        <span class="nav-icon">🌟</span>
        <span class="nav-text">技术广场</span>
      </router-link>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const mobileMenuOpen = ref(false)

const displayName = computed(() => userStore.userInfo?.username || '用户')

const getAvatarText = () => {
  const name = displayName.value
  return name.charAt(0).toUpperCase()
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/user-center')
  } else if (command === 'settings') {
    router.push('/settings')
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
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 72px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Logo区域 */
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logo-section:hover {
  transform: translateY(-1px);
}

.logo-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.5px;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 导航菜单 */
.nav-menu {
  display: flex;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 16px;
  text-decoration: none;
  color: #86868b;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.nav-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 16px;
}

.nav-item:hover {
  color: #1d1d1f;
  background: rgba(0, 122, 255, 0.08);
  transform: translateY(-2px);
}

.nav-item.router-link-active {
  color: white;
  background: linear-gradient(135deg, #007AFF 0%, #5856D6 100%);
  box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
}

.nav-icon {
  font-size: 16px;
  position: relative;
  z-index: 1;
}

.nav-text {
  position: relative;
  z-index: 1;
}

/* 用户区域 */
.user-section {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.06);
}

.user-info:hover {
  background: rgba(0, 122, 255, 0.08);
  border-color: rgba(0, 122, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: white;
  font-size: 14px;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.username {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: #86868b;
  line-height: 1.2;
}

.dropdown-arrow {
  font-size: 10px;
  color: #86868b;
  transition: transform 0.3s ease;
}

.user-info:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* 移动端菜单按钮 */
.mobile-menu-btn {
  display: none;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.04);
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mobile-menu-btn:hover {
  background: rgba(0, 122, 255, 0.1);
}

.menu-icon {
  font-size: 18px;
  color: #1d1d1f;
}

/* 移动端导航 */
.mobile-nav {
  display: none;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  padding: 16px 24px;
  transform: translateY(-100%);
  opacity: 0;
  transition: all 0.3s ease;
}

.mobile-nav-open {
  transform: translateY(0);
  opacity: 1;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
  text-decoration: none;
  color: #86868b;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.mobile-nav-item:last-child {
  border-bottom: none;
}

.mobile-nav-item:hover,
.mobile-nav-item.router-link-active {
  color: #007AFF;
}

/* 下拉菜单样式 */
:deep(.user-dropdown) {
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  padding: 8px;
}

:deep(.dropdown-item) {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  margin: 2px 0;
  transition: all 0.3s ease;
}

:deep(.dropdown-item:hover) {
  background: rgba(0, 122, 255, 0.08);
}

:deep(.dropdown-item.logout:hover) {
  background: rgba(255, 59, 48, 0.08);
  color: #FF3B30;
}

.item-icon {
  font-size: 16px;
}

.item-text {
  font-size: 14px;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .nav-menu {
    gap: 4px;
  }

  .nav-item {
    padding: 10px 16px;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
    height: 64px;
  }

  .nav-menu {
    display: none;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .mobile-nav {
    display: block;
  }

  .user-details {
    display: none;
  }

  .logo-text {
    font-size: 18px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 12px;
  }

  .logo-icon {
    font-size: 24px;
  }

  .logo-text {
    font-size: 16px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }
}
</style>
