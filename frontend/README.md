# ERP进销存管理系统 - 前端

基于Vue.js 3 + TypeScript + Element Plus的现代化前端应用。

## 技术栈

- **Vue.js 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - Vue 3 UI组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - 状态管理
- **Axios** - HTTP客户端
- **ECharts** - 数据可视化
- **Vite** - 现代化构建工具

## 功能特性

### ✅ 已实现功能

1. **用户认证系统**
   - 登录页面（支持表单验证）
   - JWT令牌认证
   - 路由守卫保护
   - 自动token刷新

2. **主界面布局**
   - 响应式侧边栏导航
   - 用户信息显示和登出
   - 面包屑导航
   - 页面标题动态显示

3. **仪表板页面**
   - 实时数据统计卡片
   - 库存不足警告列表
   - 系统概览信息
   - 销售趋势图表（ECharts）

4. **供应商管理页面**
   - 完整的CRUD操作
   - 高级搜索功能
   - 分页和排序
   - 表单验证
   - 删除确认对话框

5. **统计分析页面**
   - 销售报表（按日/周/月）
   - 采购报表
   - 热销商品排行
   - 重要客户分析
   - 利润分析

### 🚧 待实现功能

- 客户管理页面
- 商品管理页面
- 库存管理页面
- 采购管理页面
- 销售管理页面

## 快速开始

### 环境要求

- Node.js 16+
- npm 或 yarn

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/              # API服务层
│   │   ├── index.ts      # API配置
│   │   └── types.ts      # 类型定义
│   ├── assets/           # 静态资源
│   ├── components/       # 组件
│   │   ├── Layout/       # 布局组件
│   │   └── Common/       # 通用组件
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # 状态管理
│   │   ├── auth.ts       # 用户认证
│   │   └── suppliers.ts  # 供应商管理
│   ├── views/            # 页面组件
│   │   ├── Auth/         # 认证页面
│   │   ├── Dashboard/    # 仪表板
│   │   ├── Suppliers/    # 供应商管理
│   │   ├── Analytics/    # 统计分析
│   │   └── ...
│   ├── App.vue           # 根组件
│   └── main.ts           # 应用入口
├── index.html            # HTML模板
├── package.json          # 项目配置
├── tsconfig.json         # TypeScript配置
├── vite.config.ts        # Vite配置
└── README.md             # 项目说明
```

## 开发指南

### 组件开发规范

1. **命名规范**
   - 组件文件使用PascalCase命名
   - 组件props使用camelCase
   - 事件处理函数使用handle开头

2. **TypeScript使用**
   - 所有组件都应该使用TypeScript
   - 定义明确的接口和类型
   - 避免使用any类型

3. **样式规范**
   - 使用scoped样式
   - 统一使用Element Plus主题
   - 响应式设计支持

### API调用规范

```typescript
// 使用统一的API服务
import api from '@/services/api'

// GET请求
const data = await api.get('/suppliers')

// POST请求
const result = await api.post('/suppliers', supplierData)

// 错误处理
try {
  const result = await api.post('/suppliers', supplierData)
  ElMessage.success('创建成功')
} catch (error) {
  ElMessage.error('创建失败')
}
```

### 状态管理规范

```typescript
// 使用Pinia进行状态管理
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', () => {
  const state = ref({})

  const action = async () => {
    // 业务逻辑
  }

  return { state, action }
})
```

## 路由配置

系统使用Vue Router进行路由管理，所有需要认证的页面都通过路由守卫进行保护：

```typescript
// 需要认证的路由
{
  path: '/dashboard',
  component: Dashboard,
  meta: { requiresAuth: true }
}

// 公开路由
{
  path: '/login',
  component: Login
}
```

## 样式主题

系统使用Element Plus的默认主题，主要颜色：

- 主色：#409EFF
- 成功：#67C23A
- 警告：#E6A23C
- 危险：#F56C6C
- 信息：#909399

## 部署说明

### 环境变量

创建 `.env.production` 文件：

```env
VITE_API_BASE_URL=https://your-api-domain.com
VITE_APP_TITLE=ERP进销存管理系统
```

### 构建和部署

```bash
# 构建生产版本
npm run build

# dist目录包含构建后的文件
# 可以部署到任何静态文件服务器
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License