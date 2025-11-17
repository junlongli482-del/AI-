<template>
  <header class="app-header">
    <div class="header-content">
      <!-- Logo区域 -->
      <div class="logo-section" @click="$router.push('/home')">
        <div class="logo-icon">🚀</div>
        <h1 class="logo-text">智能开发平台</h1>
      </div>

      <!-- 桌面端导航菜单 -->
      <nav class="nav-menu desktop-nav">
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
            <div class="user-details desktop-only">
              <span class="username">{{ displayName }}</span>
              <span class="user-role">开发者</span>
            </div>
            <span class="dropdown-arrow desktop-only">▼</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu class="user-dropdown">
              <el-dropdown-item command="profile" class="dropdown-item">
                <span class="item-icon">👤</span>
                <span class="item-text">用户中心</span>
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
      <button
        class="mobile-menu-btn mobile-only"
        @click="toggleMobileMenu"
        :class="{ 'menu-active': mobileMenuOpen }"
      >
        <span class="menu-icon">{{ mobileMenuOpen ? '✕' : '☰' }}</span>
      </button>
    </div>

    <!-- 移动端导航菜单 -->
    <transition name="mobile-nav">
      <div v-if="mobileMenuOpen" class="mobile-nav">
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
    </transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
  console.log('Toggle mobile menu clicked', mobileMenuOpen.value) // 调试日志
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  console.log('Close mobile menu') // 调试日志
  mobileMenuOpen.value = false
}

// 点击外部关闭菜单
const handleClickOutside = (event) => {
  if (mobileMenuOpen.value && !event.target.closest('.app-header')) {
    closeMobileMenu()
  }
}

// 监听路由变化自动关闭菜单
router.afterEach(() => {
  closeMobileMenu()
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/user-center')
  } else if (command === 'logout') {  // 直接连接到 logout 处理
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
  flex-shrink: 0;
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
  flex: 1;
  justify-content: center;
  max-width: 600px;
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
  white-space: nowrap;
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
  flex-shrink: 0;
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
  flex-shrink: 0;
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
  border: none;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.mobile-menu-btn:hover {
  background: rgba(0, 122, 255, 0.1);
}

.mobile-menu-btn.menu-active {
  background: rgba(0, 122, 255, 0.15);
  transform: rotate(90deg);
}

.menu-icon {
  font-size: 18px;
  color: #1d1d1f;
  transition: all 0.3s ease;
}

   /* 移动端导航 */
 .mobile-nav {
   background: rgba(255, 255, 255, 0.98);
   backdrop-filter: blur(20px);
   border-top: 1px solid rgba(0, 0, 0, 0.06);
   padding: 16px 24px;
   box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
 }

.mobile-nav-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 12px;
  text-decoration: none;
  color: #86868b;
  font-size: 16px;
  font-weight: 500;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border-radius: 12px;
  margin-bottom: 4px;
}

.mobile-nav-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.mobile-nav-item:hover,
.mobile-nav-item.router-link-active {
  color: #007AFF;
  background: rgba(0, 122, 255, 0.08);
}

.mobile-nav-item .nav-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.mobile-nav-item .nav-text {
  flex: 1;
  font-size: 16px;
  font-weight: 500;
}

/* 修改响应式设计部分 */
@media (max-width: 1024px) {
  .nav-menu {
    gap: 4px;
  }

  .nav-item {
    padding: 10px 16px;
  }

  /* 只在桌面端导航中隐藏文字 */
  .desktop-nav .nav-text {
    display: none;
  }
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
    height: 64px;
  }

  .desktop-nav {
    display: none;
  }

  .mobile-only {
    display: flex;
  }

  .desktop-only {
    display: none;
  }

  .logo-text {
    font-size: 18px;
  }

  .user-info {
    padding: 8px 12px;
    gap: 8px;
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

  .mobile-nav {
    padding: 12px 16px;
  }

  .mobile-nav-item {
    padding: 14px 12px;
    gap: 14px;
  }

  .mobile-nav-item .nav-text {
    font-size: 15px;
  }
}
</style>
