好的！我来更新两个文档：

---

# 📘 Vue3 文档管理系统前端 — 技术文档 v4.0

> **版本**: v4.0  
> **更新日期**: 2024-12-20  
> **端口**: 5173  
> **后端**: http://localhost:8100/api

---

## 📋 目录

- [一、项目结构](#一项目结构)
- [二、核心模块说明](#二核心模块说明)
- [三、已完成功能详细清单](#三已完成功能详细清单)
- [四、开发规范](#四开发规范)
- [五、下一步开发方向](#五下一步开发方向)

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
│   │       ├── document_manager/  # 文档管理API
│   │       │   ├── folder.js      # 文件夹管理
│   │       │   └── index.js       # 文档管理
│   │       ├── file_upload/       # ✅ 文件上传API
│   │       │   └── index.js       # 文件上传、验证、创建文档
│   │       └── md_editor/         # ✅ 新增：MD编辑器API
│   │           └── index.js       # 编辑器会话、AI优化
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
│   │       ├── DocumentManager/   # 文档管理模块
│   │       │   ├── index.vue      # 主页面
│   │       │   └── components/
│   │       │       ├── FolderTree.vue
│   │       │       ├── FolderNode.vue
│   │       │       ├── CreateFolder.vue
│   │       │       ├── DocumentList.vue      # 已修改：PDF查看功能
│   │       │       ├── DocumentDetail.vue    # 已修改：PDF查看/下载
│   │       │       ├── UploadArea.vue        # 上传区域
│   │       │       ├── UploadProgress.vue    # 进度显示
│   │       │       ├── UploadDialog.vue      # 上传对话框
│   │       │       ├── CreateDocumentForm.vue # 创建文档表单
│   │       │       └── UploadHistory.vue     # 上传历史
│   │       └── DocumentEditor/    # ✅ 新增：文档编辑器
│   │           ├── index.vue      # 编辑器主页面
│   │           └── components/
│   │               ├── EditorToolbar.vue     # 工具栏（三种视图+撤销重做）
│   │               ├── MarkdownEditor.vue    # Toast UI Editor集成
│   │               ├── PreviewPanel.vue      # Markdown预览面板
│   │               ├── AIOptimizeDialog.vue  # AI优化对话框
│   │               └── SaveDocumentDialog.vue # 保存文档对话框
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
timeout: 10000 (普通接口) / 60000 (AI优化接口)

// 自动功能
- 请求自动携带Token (Authorization: Bearer xxx)
- 响应统一错误处理 (401跳转登录、显示错误提示)
- 支持文件上传（FormData自动处理）
- AI优化接口单独设置60秒超时
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
/document-manager    → 文档管理 (需登录)
/document-editor     → 文档编辑器 (需登录) ✅ 已完成
```

---

### 4. API接口层

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

#### v2 文档管理接口（已实现）

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

#### v2 文件上传接口（已实现）

**文件上传 (`api/v2/file_upload/index.js`)**：
```javascript
// 核心接口
getUploadConfig()                    // 获取上传配置
validateFile(file)                   // 验证文件（不保存）
uploadFile(file, onProgress)         // 上传文件（带进度回调）
getUploadHistory(params)             // 获取上传历史（分页）
getUploadDetail(uploadId)            // 获取上传详情
createDocumentFromUpload(data)       // 从上传文件创建文档
deleteUploadRecord(uploadId)         // 删除上传记录
getUploadStats()                     // 获取上传统计

// 工具函数
formatFileSize(bytes)                // 格式化文件大小
extractTitleFromFilename(filename)   // 从文件名提取标题
validateFileType(file)               // 验证文件类型
validateFileSize(file)               // 验证文件大小

// 枚举常量
UploadStatus                         // 上传状态
UploadStatusText                     // 状态显示文本
FileType                             // 文件类型
FileTypeText                         // 类型显示文本
```

#### v2 MD编辑器接口（✅ 新增）

**MD编辑器 (`api/v2/md_editor/index.js`)**：
```javascript
// 会话管理
createSession(data)                  // 创建编辑会话
getSessions(params)                  // 获取会话列表
getSessionDetail(sessionId)          // 获取会话详情
updateSession(sessionId, data)       // 更新会话内容
deleteSession(sessionId)             // 删除会话
saveAsDocument(sessionId, data)      // 保存为正式文档

// AI优化功能
optimizeContent(sessionId, data)     // AI内容优化（60秒超时）
applyOptimization(sessionId, optimizationId) // 应用优化结果
getOptimizationHistory(sessionId)    // 获取优化历史

// 配置统计
getEditorConfig()                    // 获取编辑器配置
getEditorStats()                     // 获取编辑器统计

// 工具函数
validateSessionTitle(title)          // 验证会话标题
validateContentLength(content)       // 验证内容长度
getContentStats(content)             // 获取内容统计
generateDefaultTitle(content)        // 生成默认标题
debounce(func, delay)               // 防抖函数

// 枚举常量
OptimizationTypes                    // 优化类型
SessionTypes                         // 会话类型
```

---

## 三、已完成功能详细清单

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

### v2 文档管理系统

#### 第一阶段：文档管理基础功能 ✅

**文件夹管理**：
- ✅ 三层文件夹结构（根目录 → 一级 → 二级 → 三级）
- ✅ 创建文件夹（带层级限制提示）
- ✅ 文件夹树形展示（递归渲染）
- ✅ 删除空文件夹
- ✅ 文件夹选择筛选

**文档管理**：
- ✅ 文档列表展示（分页）
- ✅ 文档详情查看
- ✅ 文档删除功能
- ✅ 统计信息显示
- ✅ 文件夹筛选
- ✅ 状态标签显示（草稿/已发布/审核失败）
- ✅ 时间智能格式化（刚刚/X分钟前/X天前）
- ✅ PDF文档查看功能（区分MD/PDF操作）

**界面特性**：
- ✅ 全屏自适应布局（无固定宽度限制）
- ✅ 响应式设计（支持平板、手机）
- ✅ 左侧文件夹树 + 右侧文档列表
- ✅ 加载状态显示
- ✅ 空状态提示

---

#### 第二阶段：文件上传功能 ✅

**文件上传**：
- ✅ 拖拽上传（支持拖拽文件到上传区域）
- ✅ 点击选择（支持多文件选择）
- ✅ 文件类型验证（MD/PDF）
- ✅ 文件大小验证（MD≤20MB，PDF≤100MB）
- ✅ 实时验证反馈（验证通过/失败提示）

**上传流程**：
- ✅ 选择文件 → 自动验证
- ✅ 验证通过 → 显示"开始上传"按钮
- ✅ 循环上传多个文件（一个一个上传）
- ✅ 实时显示上传进度（进度条）
- ✅ 上传成功 → 弹出创建文档表单

**创建文档（从上传文件）**：
- ✅ 标题默认使用文件名（去掉扩展名）
- ✅ 标题可修改
- ✅ 摘要可选（不填也可以）
- ✅ 文件夹选择（默认根目录）
- ✅ 文件夹树形选择器
- ✅ 表单验证

**上传历史**：
- ✅ Tab切换（我的文档 | 上传历史）
- ✅ 历史记录列表展示
- ✅ 状态筛选（全部/已验证/失败）
- ✅ 从历史记录创建文档
- ✅ 删除上传记录
- ✅ 上传统计信息（总上传数、总大小）
- ✅ 分页功能

**界面交互**：
- ✅ 上传对话框（弹窗形式）
- ✅ 响应式设计
- ✅ 加载状态显示
- ✅ 错误提示
- ✅ 成功反馈
- ✅ 上传统计（成功X个/失败X个）

---

#### 第三阶段：MD编辑器功能 ✅ **（本次完成）**

**编辑器核心功能**：
- ✅ Toast UI Editor 集成
- ✅ 三种视图模式（编辑全屏/分屏/预览全屏）
- ✅ 实时Markdown预览（marked.js渲染）
- ✅ 工具栏定制（标题、加粗、斜体、列表、表格等）
- ✅ 编辑器会话管理（新建/编辑文档模式）

**视图模式切换**：
- ✅ 编辑全屏：纯编辑模式
- ✅ 分屏模式：左编辑右预览，实时同步
- ✅ 预览全屏：纯预览模式，GitHub风格样式

**撤销/重做功能**：
- ✅ Ctrl+Z 撤销（基于Toast UI Editor命令系统）
- ✅ Ctrl+Y 重做（基于Toast UI Editor命令系统）
- ✅ 工具栏撤销/重做按钮（实时状态更新）
- ✅ 撤销/重做状态检测（按钮禁用/启用）

**AI优化功能**：
- ✅ 选中内容优化 + 全文优化
- ✅ 四种优化类型（通用/语法/结构/扩展）
- ✅ 优化结果对比展示（原始 vs 优化后）
- ✅ 一键复制优化结果（用户手动粘贴）
- ✅ AI接口60秒超时设置
- ✅ 优化历史记录

**文档保存功能**：
- ✅ 统一保存逻辑（新建和编辑都用保存对话框）
- ✅ 智能默认设置：
    - 新建文档：默认根目录，生成标题
    - 编辑文档：默认原文件夹，保持原标题
- ✅ 文件夹树形选择器
- ✅ 表单验证（标题必填，摘要可选）
- ✅ 保存成功后询问是否查看文档

**PDF文档处理**：
- ✅ PDF文档显示"查看"按钮（不是"编辑"）
- ✅ 点击查看：使用stream接口在新标签页预览
- ✅ 文档详情中：PDF显示"查看PDF"和"下载PDF"按钮
- ✅ 手动Token认证（fetch + Authorization头）

**用户体验优化**：
- ✅ 响应式设计（支持移动端）
- ✅ 加载状态显示
- ✅ 错误处理和友好提示
- ✅ 页面离开提示（有未保存内容时）
- ✅ 内容变化检测（显示未保存状态）

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
- ❌ `utils/request.js` - 除非需要修改baseURL或超时设置
- ❌ `utils/auth.js` - Token管理逻辑
- ❌ `stores/user.js` - 核心用户状态
- ❌ `api/v1/` - 已完成的接口封装
- ❌ `components/layout/AppHeader.vue` - 除非新增导航项

---

## 五、下一步开发方向

### 🎯 开发优先级（按产品需求文档）

```
✅ 第一阶段：个人文档管理（已完成）
   ├── ✅ 文件夹管理（三层结构）
   ├── ✅ 文档列表展示
   └── ✅ 文档基础操作

✅ 第二阶段：文件上传功能（已完成）
   ├── ✅ 文件上传组件
   ├── ✅ 格式验证（MD/PDF）
   ├── ✅ 上传历史
   └── ✅ 从上传文件创建文档

✅ 第三阶段：MD编辑器（已完成）
   ├── ✅ 在线编辑器（Toast UI Editor）
   ├── ✅ 预览功能（三种视图模式）
   ├── ✅ AI优化集成（四种优化类型）
   └── ✅ 撤销/重做功能

🔜 第四阶段：AI审核系统和发布功能（下一步开发）
   ├── 文档发布到技术广场
   ├── AI审核机制
   └── 发布状态管理

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

### 🚀 第四阶段开发准备

#### 需要的接口文档
- 📋 `08-AI审核模块.md`
- 📋 `09-文档发布模块.md`

#### 需要开发的文件
```
src/
├── api/v2/
│   ├── ai_review/
│   │   └── index.js              # AI审核API
│   └── document_publish/
│       └── index.js              # 文档发布API
│
└── views/v2/
    ├── DocumentManager/
    │   └── components/
    │       ├── PublishDialog.vue     # 发布对话框
    │       └── ReviewStatus.vue      # 审核状态组件
    └── DocumentEditor/
        └── components/
            └── PublishButton.vue     # 发布按钮组件
```

---

## 六、开发命令

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

## 七、版本更新日志

### v4.0 (2024-12-20)
- ✅ 新增MD编辑器功能（第三阶段）
- ✅ 新增Toast UI Editor集成
- ✅ 新增三种视图模式切换
- ✅ 新增AI优化功能（四种优化类型）
- ✅ 新增撤销/重做功能（Ctrl+Z/Y）
- ✅ 新增PDF文档查看/下载功能
- ✅ 优化保存逻辑（统一保存对话框）
- ✅ 修复AI优化接口超时问题（60秒）
- ✅ 修复Toast UI Editor撤销/重做API调用
- ✅ 删除Ctrl+S功能（避免浏览器冲突）

### v3.1 (2024-12-20)
- ✅ 新增文件上传功能（第二阶段）
- ✅ 新增上传对话框组件
- ✅ 新增上传历史管理
- ✅ 新增从上传文件创建文档功能
- ✅ 修复响应式更新问题（使用 reactive 包装对象）
- ✅ 修复 Element Plus 组件警告
- ✅ 优化文档列表样式（Tab切换）

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
2. 修改核心文件前，先查看"禁止修改区域"
3. 遇到问题时，参考《Vue3文档管理系统 - 常见问题和解决方案》文档

---
