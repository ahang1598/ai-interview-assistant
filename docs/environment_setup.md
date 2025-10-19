# 环境设置指南

本文档详细说明了如何设置和使用AI Interview Assistant项目的开发环境。

## 使用Conda环境

本项目推荐使用conda环境进行依赖管理。

### 创建Conda环境

```bash
conda create -n interview python=3.12
```

### 激活环境

```bash
conda activate interview
```

### 退出环境

```bash
conda deactivate
```

## 安装依赖

在激活的conda环境中，使用pip安装项目依赖：

```bash
pip install -r requirements.txt
```

## 环境变量配置

创建环境变量配置文件：

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，添加必要的API密钥和其他配置。

## 运行应用

确保环境已激活后运行应用：

```bash
conda activate interview
uvicorn backend.app.main:app --reload
```

## 验证环境

可以通过以下命令验证当前环境：

```bash
conda info --envs
conda list
```