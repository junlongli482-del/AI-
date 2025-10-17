# AI开发平台功能文档
开发时用 npm run dev（热更新，修改后自动刷新）
构建后用 npm run build + npm run preview（需要重新构建）
> **版本**: V2.0  
> **状态**: ✅ 已完成  
> **开发时间**: 2024年

## 📋 功能概述

在现有用户系统基础上，新增AI开发平台功能，提供三个专业智能体协助用户进行全栈开发。

## 🗂️ 文件结构

```
src/
├── router/index.js           # ✏️ 已修改 - 新增AI平台路由
├── views/
│   ├── v1/
│   │   └── Home.vue         # ✏️ 已修改 - 改造为导航型主页
│   └── v2/                  # 🆕 新建文件夹
│       └── AIPlatform.vue   # 🆕 AI开发平台页面
└── stores/user.js           # 📖 复用现有用户状态
```

## 🔗 路由配置

```javascript
// 新增路由
{
  path: '/ai-platform',
  name: 'AIPlatform', 
  component: () => import('@/views/v2/AIPlatform.vue'),
  meta: { requiresAuth: true }
}

// 修改重定向
{ path: '/', redirect: '/home' }
```

## 🎨 页面功能

### 1. 主页 (`v1/Home.vue`)
- **顶部导航**: 首页 + AI开发平台 + 用户菜单
- **主要卡片**: AI开发平台入口（大卡片）
- **次要卡片**: 用户中心、修改密码、预留扩展位

### 2. AI开发平台 (`v2/AIPlatform.vue`)
- **智能体展示**: 3个卡片（产品经理、后端、前端）
- **使用说明**: 右侧滑出面板
- **外部链接**: 新标签页打开对话系统

## 🤖 智能体配置

```javascript
const agentLinks = {
  product: 'http://ljl.ai.cpolar.top/chat/1Bm70PgYEomGF58M',   // 产品经理
  backend: 'http://ljl.ai.cpolar.top/chat/8Ca7meeZgcvuRzkq',   // 后端开发  
  frontend: 'http://ljl.ai.cpolar.top/chat/3hJb4QDXQaJtlJan'   // 前端开发
}
```

## 🎯 设计规范

- **配色**: 白色背景 + 深灰文字(#24292f) + 蓝色强调(#007AFF)
- **布局**: GitHub风格，简洁现代
- **交互**: hover效果 + 平滑动画
- **响应式**: 支持桌面/移动端

## 🚀 后续扩展点

### 主页预留位置
- 📊 项目管理（即将上线）
- 📚 学习中心（即将上线）

### 技术扩展
- 使用说明面板可扩展为完整文档系统
- 智能体可增加更多专业角色
- 可添加对话历史记录功能

## 🔧 开发命令

```bash
# 启动开发
npm run dev

# 访问地址
http://localhost:5173

# 测试流程
登录 → 主页 → 进入平台 → 选择智能体 → 查看说明
```

## 📝 核心代码片段

### 智能体跳转
```javascript
const openAgent = (agentType) => {
  const url = agentLinks[agentType]
  if (url) {
    window.open(url, '_blank')
  }
}
```

### 说明面板控制
```javascript
const showHelp = ref(false)
// 点击按钮显示，点击遮罩隐藏
```

---

**💡 这个功能为后续的项目管理、学习中心等模块奠定了基础架构！**


上面两个文档，在保证不影响AI下次开发了解认识这个项目的情况，把一些无用的东西去掉。只要能满足AI开发的内容就行了。AI进行下次新功能开发时知道上一次做了什么，这样子他就知道有些东西弄好了，不用动，有些也不能动。以及需要上个开发阶段的什么文件。