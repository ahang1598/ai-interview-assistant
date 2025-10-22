from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the parent directory to the path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api import resume, chat, knowledge, auth
from app.database import Base, engine

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Assistant API",
    description="An AI-powered interview assistant API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(resume.router, prefix="/resume", tags=["resume"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(knowledge.router, prefix="", tags=["knowledge"])  # Removed /knowledge prefix
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to AI Interview Assistant API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}