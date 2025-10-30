# 🚀 FastAPI 模块化文档管理系统

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.0+-brightgreen.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**一个基于 FastAPI + Vue3 的企业级文档管理平台**

[在线演示](http://your-demo-url.com) · [文档](./docs) · [问题反馈](https://github.com/yourusername/fastapi-document-system/issues)

</div>

## ✨ 特性

- 🏗️ **模块化架构** - 每个功能独立成模块，支持热插拔
- 📦 **版本化管理** - v1用户系统，v2文档系统，支持并行开发
- 🔄 **自动注册** - 新模块零配置自动发现和注册
- 🤖 **AI 集成** - 智能内容优化、自动审核、内容安全检测
- 📝 **在线编辑** - 基于 Toast UI Editor 的 Markdown 编辑器
- 🔍 **智能搜索** - 全文搜索、分类筛选、智能推荐
- 💬 **互动功能** - 点赞、收藏、评论、分享系统
- 📱 **响应式设计** - 完美适配 PC、平板、手机
- 🛡️ **安全可靠** - JWT 认证、权限控制、数据验证

## 🎯 功能模块

### v1 用户系统
- ✅ 用户注册/登录
- ✅ 用户中心管理
- ✅ 密码安全管理
- ✅ JWT 认证体系

### v2 文档系统
- ✅ 文档管理（CRUD、文件夹分层）
- ✅ 文件上传（MD/PDF 支持）
- ✅ 在线编辑器（AI 优化、实时预览）
- ✅ AI 审核系统（内容安全检测）
- ✅ 文档发布（自动化发布流程）
- ✅ 技术广场（公开展示平台）
- ✅ 互动功能（点赞、收藏、评论）
- ✅ 分享系统（公开/私有/密码分享）

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+

### 后端启动

```bash
# 克隆项目
git clone https://github.com/yourusername/fastapi-document-system.git
cd fastapi-document-system

# 安装后端依赖
cd fastapi
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息

# 启动后端服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
```

### 前端启动

```bash
# 安装前端依赖
cd vue3
npm install

# 启动前端开发服务器
npm run dev
```

### 数据库配置

```sql
-- 创建数据库
CREATE DATABASE user_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 导入数据表结构
mysql -u root -p user_system < database/schema.sql
```

### 访问应用

- 前端地址: http://localhost:5173
- 后端 API: http://localhost:8100
- API 文档: http://localhost:8100/docs

## 📁 项目结构

```
fastapi-document-system/
├── fastapi/                    # 后端 FastAPI 项目
│   ├── app/
│   │   ├── core/              # 核心基础设施
│   │   │   ├── config.py      # 配置管理
│   │   │   ├── database.py    # 数据库连接
│   │   │   └── ai_client.py   # AI 客户端
│   │   ├── modules/           # 业务模块
│   │   │   ├── v1/           # 用户系统模块
│   │   │   └── v2/           # 文档系统模块
│   │   └── main.py           # 应用入口
│   ├── uploads/              # 文件上传目录
│   ├── requirements.txt      # Python 依赖
│   └── .env                  # 环境配置
├── vue3/                     # 前端 Vue3 项目
│   ├── src/
│   │   ├── api/              # API 接口封装
│   │   ├── views/            # 页面组件
│   │   ├── components/       # 公共组件
│   │   ├── stores/           # 状态管理
│   │   └── router/           # 路由配置
│   ├── package.json          # Node.js 依赖
│   └── vite.config.js        # Vite 配置
└── docs/                     # 项目文档
```

## 🔧 配置说明

### 环境变量配置

```bash
# .env 文件示例
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/user_system
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BASE_URL=http://localhost:8100
```

### AI 服务配置

```python
# app/core/ai_client.py
AI_CONFIG = {
    "provider": "custom",  # 支持自定义 AI 服务
    "api_key": "your-api-key",
    "base_url": "your-ai-service-url"
}
```

## 📊 API 文档

### 用户系统 API (v1)

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v1/user_auth/login` | POST | 用户登录 |
| `/api/v1/user_auth/register` | POST | 用户注册 |
| `/api/v1/user_profile/me` | GET | 获取用户信息 |

### 文档系统 API (v2)

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/v2/document_manager/documents` | GET | 获取文档列表 |
| `/api/v2/document_manager/documents` | POST | 创建文档 |
| `/api/v2/tech_square/documents` | GET | 技术广场文档列表 |
| `/api/v2/share_system/create` | POST | 创建文档分享 |

完整 API 文档请访问: http://localhost:8100/docs

## 🧪 测试

```bash
# 运行后端测试
cd fastapi/测试脚本/v2测试脚本
python test_document_manager_clean.py

# 运行前端测试
cd vue3
npm run test
```

## 📈 性能特性

- **模块化架构**: 支持独立开发和部署
- **自动注册机制**: 新模块零配置集成
- **数据库优化**: 合理索引设计，支持大数据量
- **缓存策略**: 统计数据缓存，提升查询性能
- **分页加载**: 避免大数据量一次性加载
- **响应式设计**: 完美适配各种设备

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 开发规范

### 后端开发规范

- 遵循 FastAPI 最佳实践
- 使用 Pydantic 进行数据验证
- 统一的错误处理和响应格式
- 完整的类型注解

### 前端开发规范

- 使用 Vue 3 Composition API
- 遵循 ESLint 代码规范
- 组件化开发，单一职责原则
- 响应式设计优先

## 🐛 问题反馈

如果您发现任何问题或有改进建议，请：

1. 查看 [已知问题](https://github.com/yourusername/fastapi-document-system/issues)
2. 创建新的 [Issue](https://github.com/yourusername/fastapi-document-system/issues/new)
3. 提供详细的问题描述和复现步骤

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库
- [Toast UI Editor](https://ui.toast.com/tui-editor) - Markdown 编辑器

## 📞 联系方式

- 作者: Your Name
- 邮箱: your.email@example.com
- 项目主页: https://github.com/yourusername/fastapi-document-system

---

<div align="center">

**如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

</div>