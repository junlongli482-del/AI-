<template>
  <header class="app-header">
    <div class="header-content">
      <h1 class="logo">多智能体开发平台</h1>
      <nav class="nav-menu">
        <router-link to="/home" class="nav-item">
          首页
        </router-link>
        <router-link to="/ai-platform" class="nav-item">
          AI开发平台
        </router-link>
        <router-link to="/document-manager" class="nav-item">
          文档管理
        </router-link>
        <router-link to="/tech-square" class="nav-item">
          技术广场
        </router-link>
      </nav>
      <div class="user-menu">
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <span class="username">{{ displayName }}</span>
            <span class="arrow">▼</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">👤 用户中心</el-dropdown-item>
              <el-dropdown-item command="logout" divided>🚪 退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const displayName = computed(() => userStore.userInfo?.username || '用户')

const handleCommand = async (command) => {
  if (command === 'profile') {
    router.push('/user-center')
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
  background: #ffffff;
  border-bottom: 1px solid #e1e4e8;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 20px;
  font-weight: 600;
  color: #24292f;
  margin: 0;
  cursor: pointer;
}

.nav-menu {
  display: flex;
  gap: 32px;
}

.nav-item {
  color: #656d76;
  text-decoration: none;
  font-size: 16px;
  font-weight: 500;
  padding: 8px 0;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: #24292f;
}

.nav-item.router-link-active {
  color: #24292f;
  border-bottom-color: #007AFF;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.user-info:hover {
  background: #f6f8fa;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #24292f;
}

.arrow {
  font-size: 12px;
  color: #656d76;
}

/* 响应式 */
@media (max-width: 768px) {
  .nav-menu {
    display: none;
  }
}

:deep(.el-dropdown-menu__item) {
  padding: 12px 20px;
}
</style>
