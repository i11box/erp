# 进销存管理系统

基于FastAPI + Vue.js的进销存管理系统，提供采购管理、销售管理、库存管理和统计分析等核心功能。

## 项目结构

```
erp/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心功能（认证、安全）
│   │   ├── crud/           # 数据库操作
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   ├── services/       # 业务逻辑服务
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # FastAPI应用入口
│   ├── requirements.txt    # Python依赖
│   ├── init_db.py         # 数据库初始化脚本
│   └── create_models.py   # 创建数据库表脚本
├── frontend/              # Vue.js前端
└── docs/                 # 文档
```

## 功能特性

### 已完成功能
- ✅ 数据库模型设计（用户、供应商、客户、商品、库存、采购、销售）
- ✅ 供应商管理API（增删改查、搜索、关联检查）
- ✅ 客户管理API（增删改查、搜索、关联检查）
- ✅ 商品管理API（增删改查、搜索、库存预警）
- ✅ 用户认证和权限管理
- ✅ 数据验证和错误处理

### 待开发功能
- 🔄 采购管理API
- 🔄 销售管理API
- 🔄 库存管理API
- 🔄 统计分析API
- 🔄 Vue.js前端界面
- 🔄 性能测试

## 技术栈

### 后端
- **FastAPI**: 高性能异步Web框架
- **SQLAlchemy**: ORM框架
- **Pydantic**: 数据验证和序列化
- **SQLite**: 轻量级数据库
- **JWT**: 用户认证
- **BCrypt**: 密码加密

### 前端（计划）
- **Vue.js 3**: 渐进式JavaScript框架
- **TypeScript**: 类型安全
- **Element Plus**: UI组件库
- **Axios**: HTTP客户端

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd erp
```

### 2. 后端设置
```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 创建数据库表
python create_models.py

# 初始化示例数据
python init_db.py
```

### 3. 启动后端服务
```bash
# 启动FastAPI开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问API文档
打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API接口

### 供应商管理
- `GET /api/suppliers/` - 获取供应商列表
- `POST /api/suppliers/` - 创建供应商
- `GET /api/suppliers/{id}` - 获取供应商详情
- `PUT /api/suppliers/{id}` - 更新供应商
- `DELETE /api/suppliers/{id}` - 删除供应商

### 客户管理
- `GET /api/customers/` - 获取客户列表
- `POST /api/customers/` - 创建客户
- `GET /api/customers/{id}` - 获取客户详情
- `PUT /api/customers/{id}` - 更新客户
- `DELETE /api/customers/{id}` - 删除客户

### 商品管理
- `GET /api/products/` - 获取商品列表
- `POST /api/products/` - 创建商品
- `GET /api/products/{id}` - 获取商品详情
- `PUT /api/products/{id}` - 更新商品
- `DELETE /api/products/{id}` - 删除商品
- `GET /api/products/low-stock` - 获取库存不足商品

## 示例数据

系统初始化时会创建以下示例数据：

### 用户
- 管理员: admin / admin123
- 普通用户: user / user123

### 供应商
- 科技有限公司（张经理）
- 电子产品批发商（李总）

### 客户
- ABC贸易公司（王经理）
- XYZ零售店（赵老板）

### 商品
- 笔记本电脑（成本价: 3000, 售价: 4500）
- 无线鼠标（成本价: 50, 售价: 80）
- 机械键盘（成本价: 200, 售价: 350）
- 显示器（成本价: 1500, 售价: 2200）

## 开发说明

### 数据库设计
系统采用关系型数据库设计，主要表结构：
- users: 用户表
- suppliers: 供应商表
- customers: 客户表
- products: 商品表
- inventory: 库存表
- inventory_movements: 库存变动记录表
- purchases: 采购订单表
- purchase_items: 采购订单明细表
- sales: 销售订单表
- sale_items: 销售订单明细表

### API设计规范
- 使用RESTful API设计风格
- 统一的错误处理和响应格式
- 数据验证和类型检查
- 关联数据的完整性检查

### 安全特性
- JWT令牌认证
- 密码BCrypt加密
- CORS跨域配置
- 输入数据验证

## 测试

### 运行测试
```bash
cd backend
pytest
```

### 性能测试
```bash
cd backend
locust -f tests/performance_test.py --host=http://localhost:8000
```

## 部署

### Docker部署（待实现）
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱: your-email@example.com
- 项目地址: https://github.com/your-username/erp

## 更新日志

### v0.1.0 (2024-01-XX)
- ✅ 完成项目基础架构搭建
- ✅ 实现供应商管理API
- ✅ 实现客户管理API
- ✅ 实现商品管理API
- ✅ 完成数据库模型设计
- ✅ 添加用户认证功能