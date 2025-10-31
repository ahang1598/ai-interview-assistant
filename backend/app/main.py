import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置以确保环境变量被加载
from app.core.config import settings

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import resume, chat, knowledge, auth, multi_knowledge
from app.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时的代码
    yield
    # 关闭时的代码

app = FastAPI(lifespan=lifespan, title="AI Interview Assistant API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(multi_knowledge.router, tags=["multi_knowledge"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Interview Assistant API"}