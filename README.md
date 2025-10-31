# AI Interview Assistant

AI面试助手是一个基于人工智能的面试辅助工具，帮助求职者准备面试并提高成功率。

## 功能特性

- 简历解析与分析
- AI驱动的面试对话系统
- 基于RAG的知识库问答
- 用户注册登录认证系统

## 技术架构

- 后端：FastAPI + LangChain + Qwen大模型
- 前端：React/Vue + Vite
- 数据库：MySQL (用户数据) + Qdrant (向量数据)
- 部署：Docker容器化部署

## 快速开始

### 环境准备

1. 克隆项目：
   ```bash
   git clone <repository-url>
   cd ai-interview-assistant
   ```

2. 创建Conda环境：
   ```bash
   conda create -n interview python=3.10
   conda activate interview
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加您的配置
   ```

5. 配置MySQL数据库：
   - 创建数据库和用户
   - 在 `.env` 文件中设置正确的 `DATABASE_URL`

### 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload
```

### 启动前端服务

```bash
npm install
npm run dev
```

## API 文档

启动后端服务后，可以通过以下地址访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 认证系统

本系统提供了完整的用户注册登录认证功能：

### 注册用户
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

### 登录获取令牌
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 使用令牌访问受保护的端点
```bash
curl -X GET "http://localhost:8000/auth/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 数据库配置

系统支持 SQLite 和 MySQL 数据库：

1. SQLite（默认）：适用于开发和测试环境
2. MySQL：适用于生产环境

### MySQL 配置步骤：

1. 安装 MySQL 服务器
2. 创建数据库和用户：
   ```sql
   CREATE DATABASE interview_assistant;
   CREATE USER 'interview_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON interview_assistant.* TO 'interview_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
3. 在 `.env` 文件中配置连接信息：
   ```
   DATABASE_URL=mysql+pymysql://interview_user:your_password@localhost:3306/interview_assistant
   ```

## 开发指南

### 项目结构

```
ai-interview-assistant/
├── backend/
│   ├── app/
│   │   ├── api/          # API路由
│   │   ├── core/         # 核心业务逻辑
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # 数据验证模式
│   │   └── utils/        # 工具函数
│   └── main.py           # 应用入口
├── frontend/
├── docs/
└── tests/
```

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情