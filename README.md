# AI Interview Assistant

AI Interview Assistant 是一个基于人工智能的面试准备工具，旨在帮助用户更好地准备技术面试。

## 技术栈

- 后端: FastAPI + LangChain
- AI模型: 阿里云通义千问(Qwen)
- 前端: HTML, CSS, JavaScript + Express.js
- 简历解析: PyPDF2, python-docx

## 功能特性

- 简历解析 (PDF/DOCX)
- AI 面试对话
- 个性化面试问题生成
- 技能评估和建议

## 安装与设置

### 后端设置

1. 创建并激活conda环境:
   ```bash
   conda create -n interview python=3.10
   conda activate interview
   ```

2. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量:
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，添加您的阿里云API密钥
   ```

4. 运行后端服务:
   ```bash
   npm run backend
   # 或者
   cd backend/app
   uvicorn main:app --reload
   ```

### 前端设置

1. 安装前端依赖:
   ```bash
   npm install
   ```

2. 运行前端服务:
   ```bash
   npm start
   # 或者
   npm run frontend
   ```

3. 访问 `http://localhost:3000` 查看应用

### 同时运行前后端

```bash
npm run dev
```

这将同时启动后端服务(端口8000)和前端服务(端口3000)

## API 文档

启动后端服务后，访问 `http://127.0.0.1:8000/docs` 查看自动生成的API文档。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。