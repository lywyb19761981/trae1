# Trae Todo App

一个基于 Flask 的全栈 Web 应用，提供用户认证和待办事项管理功能。

## 🚀 项目特性

### 用户认证系统
- 🔐 用户注册和登录
- 🔒 JWT 身份验证
- 🛡️ 密码加密存储
- 👤 用户会话管理

### 待办事项管理
- ✅ 创建、编辑、删除待办事项
- 📝 任务描述和优先级设置
- 📅 截止日期管理
- 🏷️ 分类标签系统
- 📊 任务统计和进度跟踪

### 技术特性
- 🎨 响应式前端界面
- 📱 移动端友好设计
- 💾 SQLite 数据库存储
- 🔄 RESTful API 设计
- 🚦 完整的错误处理

## 🛠️ 技术栈

### 后端
- **Flask** - Python Web 框架
- **SQLite** - 轻量级数据库
- **JWT** - 身份验证
- **Werkzeug** - 密码加密
- **Flask-CORS** - 跨域支持

### 前端
- **HTML5** - 页面结构
- **CSS3** - 样式设计
- **JavaScript** - 交互逻辑
- **Fetch API** - HTTP 请求

## 📁 项目结构

```
trae/
├── backend/                 # 后端代码
│   ├── flask_app.py        # Flask 主应用
│   ├── auth_routes.py      # 认证路由
│   ├── todo_routes.py      # Todo 路由
│   ├── auth_decorators.py  # 认证装饰器
│   ├── models.py           # 用户数据模型
│   ├── todo_models.py      # Todo 数据模型
│   ├── database.py         # 数据库配置
│   ├── auth_utils.py       # 认证工具
│   └── requirements.txt    # Python 依赖
├── frontend/               # 前端代码
│   ├── index.html         # 主页面
│   ├── script.js          # JavaScript 逻辑
│   └── styles.css         # 样式文件
├── .gitignore             # Git 忽略文件
└── README.md              # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.7+
- pip (Python 包管理器)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/lywyb19761981/trae1.git
   cd trae1
   ```

2. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **启动服务器**
   ```bash
   python flask_app.py
   ```

4. **访问应用**
   打开浏览器访问：`http://127.0.0.1:8000`

## 📖 API 文档

### 认证接口

#### 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "用户名",
  "password": "密码"
}
```

#### 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "用户名",
  "password": "密码"
}
```

### Todo 接口

#### 获取待办事项列表
```http
GET /api/todo/todos
Authorization: Bearer <JWT_TOKEN>
```

#### 创建待办事项
```http
POST /api/todo/todos
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "title": "任务标题",
  "description": "任务描述",
  "priority": "high",
  "due_date": "2024-12-31"
}
```

#### 更新待办事项
```http
PUT /api/todo/todos/<todo_id>
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "title": "更新的标题",
  "completed": true
}
```

#### 删除待办事项
```http
DELETE /api/todo/todos/<todo_id>
Authorization: Bearer <JWT_TOKEN>
```

## 🎯 使用说明

1. **注册账户**：首次使用需要创建账户
2. **登录系统**：使用用户名和密码登录
3. **创建任务**：点击"添加任务"按钮创建新的待办事项
4. **管理任务**：可以编辑、完成或删除任务
5. **分类管理**：为任务添加分类标签
6. **查看统计**：查看任务完成情况和统计信息

## 🔧 开发说明

### 数据库初始化
应用首次启动时会自动创建数据库表：
- `users` - 用户信息表
- `todos` - 待办事项表
- `categories` - 分类表
- `todo_categories` - 任务分类关联表

### 环境配置
- 开发环境：`DEBUG=True`
- 生产环境：建议使用 WSGI 服务器（如 Gunicorn）

### 安全特性
- JWT Token 过期时间：24小时
- 密码使用 Werkzeug 加密
- 用户数据隔离
- API 路由保护

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- 项目链接：[https://github.com/lywyb19761981/trae1](https://github.com/lywyb19761981/trae1)
- 问题反馈：[Issues](https://github.com/lywyb19761981/trae1/issues)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者！

---

⭐ 如果这个项目对你有帮助，请给它一个星标！