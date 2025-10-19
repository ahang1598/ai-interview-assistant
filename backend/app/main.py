from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import resume, chat

app = FastAPI(
    title="AI Interview Assistant API",
    description="An AI-powered interview assistant API",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Interview Assistant API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}