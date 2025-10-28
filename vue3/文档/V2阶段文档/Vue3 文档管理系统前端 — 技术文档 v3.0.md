# 📘 Vue3 文档管理系统前端 — 技术文档 v3.0

> **版本**: v3.0  
> **端口**: 5173  
> **后端**: http://localhost:8100/api

---

## 📋 目录

- [一、项目结构](#一项目结构)
- [二、核心模块说明](#二核心模块说明)
- [三、已完成功能](#三已完成功能)
- [四、开发规范](#四开发规范)
- [五、常用文件速查](#五常用文件速查)
- [六、下一步开发方向](#六下一步开发方向)

---

## 一、项目结构

```bash
vue3/
├── src/
│   ├── api/
│   │   ├── v1/                    # 用户系统接口
│   │   │   ├── user_register/
│   │   │   ├── user_auth/
│   │   │   ├── user_profile/
│   │   │   └── password_manager/
│   │   └── v2/                    # 文档系统接口
│   │       └── document_manager/  # ✅ 新增：文档管理API
│   │           ├── folder.js      # 文件夹管理
│   │           └── index.js       # 文档管理
│   │
│   ├── views/
│   │   ├── v1/                    # 用户系统页面
│   │   │   ├── Register.vue
│   │   │   ├── Login.vue
│   │   │   ├── Home.vue
│   │   │   ├── UserCenter.vue
│   │   │   └── ChangePassword.vue
│   │   └── v2/                    # AI平台与文档系统
│   │       ├── AIPlatform.vue
│   │       ├── DocumentManager/   # ✅ 新增：文档管理模块
│   │       │   ├── index.vue      # 主页面
│   │       │   └── components/
│   │       │       ├── FolderTree.vue
│   │       │       ├── FolderNode.vue
│   │       │       ├── CreateFolder.vue
│   │       │       ├── DocumentList.vue
│   │       │       └── DocumentDetail.vue
│   │       └── DocumentEditor/    # 🔜 待开发：文档编辑器
│   │           └── index.vue      # 占位页面
│   │
│   ├── components/layout/
│   │   └── AppHeader.vue          # 全局导航栏
│   │
│   ├── stores/user.js             # Pinia用户状态
│   ├── router/index.js            # 路由+守卫
│   └── utils/
│       ├── request.js             # Axios封装
│       └── auth.js                # Token管理
│
├── package.json
└── vite.config.js
```

---

## 二、核心模块说明

### 1. 工具函数 (`utils/`)

#### `request.js` - HTTP请求封装
```javascript
// 基础配置
baseURL: 'http://localhost:8100/api'
timeout: 10000

// 自动功能
- 请求自动携带Token (Authorization: Bearer xxx)
- 响应统一错误处理 (401跳转登录、显示错误提示)
```

#### `auth.js` - Token管理
```javascript
getToken()    // 获取localStorage中的token
setToken()    // 保存token
removeToken() // 清除token
```

---

### 2. 状态管理 (`stores/user.js`)

```javascript
// 状态
state: {
  token: '',
  userInfo: null
}

// 方法
login()        // 登录并保存token
getUserInfo()  // 获取用户信息
logout()       // 清除状态和token
```

---

### 3. 路由配置 (`router/index.js`)

#### 路由表
```javascript
// v1 用户系统
/                    → 重定向到 /home
/login               → 登录页
/register            → 注册页
/home                → 主页 (需登录)
/user-center         → 用户中心 (需登录)
/change-password     → 修改密码 (需登录)

// v2 AI与文档系统
/ai-platform         → AI开发平台 (需登录)
/document-manager    → 文档管理 (需登录) ✅ 新增
/document-editor     → 文档编辑器 (需登录) 🔜 待开发
```

#### 路由守卫
```javascript
// 未登录访问受保护页面 → 跳转登录
// 已登录访问登录/注册页 → 跳转主页
```

---

### 4. 全局导航栏 (`components/layout/AppHeader.vue`)

#### 功能特性
- ✅ 统一的顶部导航栏，所有主要页面共用
- ✅ 包含：Logo、导航菜单、用户下拉菜单
- ✅ 自动高亮当前页面（`router-link-active` 类）
- ✅ 自动获取用户信息（从 `useUserStore`）

#### 导航菜单结构
```vue
<nav class="nav-menu">
  <router-link to="/home">首页</router-link>
  <router-link to="/ai-platform">AI开发平台</router-link>
  <router-link to="/document-manager">文档管理</router-link> <!-- ✅ 新增 -->
</nav>
```

#### 使用方法
```vue
<template>
  <div class="page-wrapper">
    <AppHeader />  <!-- 直接引入 -->
    <div class="page-content">
      <!-- 你的页面内容 -->
    </div>
  </div>
</template>

<script setup>
import AppHeader from '@/components/layout/AppHeader.vue'
</script>
```

---

### 5. API接口层

#### v1 用户系统接口（已实现）
```javascript
// 注册模块
checkUsername(username)
checkEmail(email)
register(data)

// 认证模块
login(data)
getCurrentUser()

// 用户资料
getUserProfile()
updateNickname(nickname)
checkNickname(nickname)

// 密码管理
changePassword(data)
checkPasswordStrength()
```

#### v2 文档管理接口（✅ 新增）

**文件夹管理 (`api/v2/document_manager/folder.js`)**：
```javascript
createFolder(data)           // 创建文件夹
getFolderTree()              // 获取文件夹树
deleteFolder(folderId)       // 删除文件夹
validateFolderName(name)     // 验证文件夹名称
```

**文档管理 (`api/v2/document_manager/index.js`)**：
```javascript
createDocument(data)         // 创建文档
getDocuments(params)         // 获取文档列表（分页）
getDocumentDetail(docId)     // 获取文档详情
updateDocument(docId, data)  // 更新文档
deleteDocument(docId)        // 删除文档
getStats()                   // 获取统计信息

// 工具函数
formatFileSize(bytes)        // 格式化文件大小
validateDocumentTitle(title) // 验证文档标题
validateDocumentSummary()    // 验证文档摘要

// 枚举常量
DocumentStatus               // 文档状态
DocumentStatusText           // 状态显示文本
FileType                     // 文件类型
FileTypeText                 // 类型显示文本
```

---

## 三、已完成功能

### v1 用户系统 ✅
- ✅ 用户注册（实时验证、可用性检查）
- ✅ 用户登录（支持用户名/邮箱）
- ✅ 用户中心（查看资料、编辑昵称）
- ✅ 修改密码（强度检测、原密码验证）
- ✅ 导航型主页（快捷入口卡片）

### v2 AI开发平台 ✅
- ✅ AI平台页面（3个智能体卡片）
- ✅ 使用说明面板（右侧滑出）
- ✅ 外部链接跳转（新标签页）

### v2 文档管理系统 ✅ **（第一阶段完成）**

#### 文件夹管理
- ✅ 三层文件夹结构（根目录 → 一级 → 二级 → 三级）
- ✅ 创建文件夹（带层级限制提示）
- ✅ 文件夹树形展示（递归渲染）
- ✅ 删除空文件夹
- ✅ 文件夹选择筛选

#### 文档管理
- ✅ 文档列表展示（分页）
- ✅ 文档详情查看
- ✅ 文档删除功能
- ✅ 统计信息显示
- ✅ 文件夹筛选
- ✅ 状态标签显示（草稿/已发布/审核失败）
- ✅ 时间智能格式化（刚刚/X分钟前/X天前）

#### 界面特性
- ✅ 全屏自适应布局（无固定宽度限制）
- ✅ 响应式设计（支持平板、手机）
- ✅ 左侧文件夹树 + 右侧文档列表
- ✅ 加载状态显示
- ✅ 空状态提示

---

## 四、开发规范

### 新功能开发流程
1. **确定版本**: 在 `views/v2/` 或 `views/v3/` 创建
2. **创建API**: 在 `api/v2/` 或 `api/v3/` 创建对应模块
3. **添加路由**: 在 `router/index.js` 添加路由
4. **复用状态**: 优先使用现有 `stores/user.js`
5. **复用导航**: 所有页面使用 `<AppHeader />`

### 文件命名规范
- 组件: PascalCase (`UserCenter.vue`)
- 文件夹: snake_case (`user_profile/`)
- 函数: camelCase (`getUserInfo()`)

### 设计规范（现代极简风格）
- **配色方案**：
    - 背景：纯白 `#ffffff`
    - 主文字：深灰 `#24292f`
    - 次要文字：`#656d76`
    - 边框：`#d0d7de`
    - 主色调：天蓝色 `#007AFF`
    - 辅助色：浅荧绿色（成功状态）
- **布局特点**：
    - 大量留白，宽松的间距
    - 简洁的白色卡片，轻微圆角 `8px`
    - 细微阴影
- **交互细节**：
    - Hover效果：轻微阴影 + 轻微上移
    - 过渡动画：`0.2s ease`

### 禁止修改区域
- ❌ `utils/request.js` - 除非需要修改baseURL
- ❌ `utils/auth.js` - Token管理逻辑
- ❌ `stores/user.js` - 核心用户状态
- ❌ `api/v1/` - 已完成的接口封装
- ❌ `components/layout/AppHeader.vue` - 除非新增导航项

---

## 五、常用文件速查

### 📌 核心配置文件（需要时提供完整内容）

#### 1. `src/router/index.js` - 路由配置
**作用**：路由表 + 路由守卫  
**修改场景**：新增页面路由  
**关键点**：
- 所有需要登录的页面：`meta: { requiresAuth: true }`
- 路由守卫自动处理登录跳转

#### 2. `src/utils/request.js` - API请求封装
**作用**：统一HTTP请求处理  
**修改场景**：更改后端地址  
**关键点**：
```javascript
baseURL: 'http://localhost:8100/api'  // 本地开发
// baseURL: 'http://ljl.api.cpolar.top/api'  // 公网访问
```

#### 3. `src/components/layout/AppHeader.vue` - 全局导航
**作用**：顶部导航栏  
**修改场景**：新增导航菜单项  
**关键点**：
```vue
<!-- 在 <nav class="nav-menu"> 中添加 -->
<router-link to="/new-page" class="nav-item">
  新页面
</router-link>
```

#### 4. `src/views/v1/Home.vue` - 主页卡片样式
**作用**：主页功能入口卡片  
**修改场景**：新增功能入口卡片  
**关键点**：
- 主要功能卡片：`.main-feature-card`（大卡片）
- 次要功能卡片：`.secondary-card`（小卡片）
- 即将上线：添加 `.coming-soon` 类

---

### 📊 文件修改频率统计

| 文件 | 修改频率 | 场景 |
|------|---------|------|
| `router/index.js` | 🔴 高 | 每次新增页面 |
| `AppHeader.vue` | 🟡 中 | 新增导航项 |
| `Home.vue` | 🟡 中 | 新增功能卡片 |
| `request.js` | 🟢 低 | 切换后端地址 |

---

## 六、下一步开发方向

### 🎯 开发优先级（按产品需求文档）

```
✅ 第一阶段：个人文档管理（已完成）
   ├── ✅ 文件夹管理（三层结构）
   ├── ✅ 文档列表展示
   └── ✅ 文档基础操作

🔜 第二阶段：文件上传功能（下一步开发）
   ├── 文件上传组件
   ├── 格式验证（MD/PDF）
   ├── 上传历史
   └── 从上传文件创建文档

📋 第三阶段：MD编辑器
   ├── 在线编辑器
   ├── 预览功能（分屏/全屏）
   └── AI优化集成

📋 第四阶段：发布与审核
   ├── 文档发布
   ├── AI审核
   └── 状态管理

📋 第五阶段：技术广场
   ├── 文档展示
   ├── 搜索排序
   └── 详情页面

📋 第六阶段：互动功能
   ├── 点赞收藏
   ├── 评论系统
   └── 分享功能
```

---

### 🚀 第二阶段开发准备

#### 需要的接口文档
- ✅ `06-文件上传模块.md`（已有）

#### 需要开发的文件
```
src/
├── api/v2/
│   └── file_upload/
│       └── index.js              # 文件上传API
│
└── views/v2/
    └── FileUpload/
        ├── index.vue             # 文件上传主页面
        └── components/
            ├── UploadArea.vue    # 上传区域组件
            ├── UploadHistory.vue # 上传历史列表
            └── FileValidator.vue # 文件验证组件
```

#### 技术选型建议
- **文件上传**：Element Plus `el-upload` 组件
- **拖拽上传**：原生 HTML5 Drag & Drop API
- **进度显示**：`el-progress` 组件
- **文件验证**：前端验证 + 后端验证双重保障

---

### 📋 第二阶段开发检查清单

开始开发前，需要确认：
- [ ] 已提供 `06-文件上传模块.md` 详细接口文档
- [ ] 确认文件上传的具体需求（是否支持拖拽、多文件等）
- [ ] 确认文件验证规则（MD最大20MB，PDF最大100MB，最多20页）
- [ ] 确认上传后的文档创建流程

---

### 🔗 与现有模块的集成点

1. **文档管理 ↔ 文件上传**
    - 上传完成后可直接创建文档
    - 文档列表显示上传的文件信息

2. **文件上传 ↔ MD编辑器**
    - 上传MD文件后可进入编辑器编辑
    - 编辑器可保存为上传记录

3. **全局导航**
    - 可在 `AppHeader.vue` 添加"文件上传"入口
    - 或在文档管理页面内嵌上传功能

---

## 七、常见问题

### 跨域问题
后端已配置CORS，无需前端处理

### Token过期
自动在 `request.js` 中处理，跳转登录页

### 获取用户信息
```javascript
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
await userStore.getUserInfo()
```

### Vue响应式类型转换问题
```javascript
// ❌ 错误：可能导致类型变化
const uploadId = uploadResult.upload_id
const createData = { upload_id: uploadId }

// ✅ 正确：直接构造对象
await createDocumentFromUpload({
  upload_id: uploadResult.upload_id,
  title: fileTitle
})

// ✅ 或使用 toRaw
import { toRaw } from 'vue'
const rawId = toRaw(uploadId)
```

---

## 八、开发命令

```bash
# 安装依赖
npm install

# 启动开发服务器（热更新）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

---

## 九、版本更新日志

### v3.0 (2024-12-19)
- ✅ 新增文档管理模块（第一阶段）
- ✅ 新增文件夹管理功能（三层结构）
- ✅ 新增文档列表展示（分页）
- ✅ 优化页面布局（全屏自适应）
- ✅ 更新路由配置
- ✅ 更新全局导航

### v2.0
- ✅ AI开发平台
- ✅ 全局导航栏组件

### v1.0
- ✅ 用户注册登录
- ✅ 用户中心
- ✅ 密码管理

---

**💡 开发建议**：
1. 每次开发新功能前，先查看本文档的"下一步开发方向"
2. 修改核心文件前，先查看"常用文件速查"
3. 遵循设计规范，保持界面风格一致
4. 新增页面必须添加 `<AppHeader />`

**文档版本**：v3.0 | **最后更新**：2024-12-19 | **下一步**：文件上传功能 🚀
