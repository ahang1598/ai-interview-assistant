import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

class Settings:
    # API密钥
    TONGYI_API_KEY: str = os.getenv("TONGYI_API_KEY", "")
    
    # 应用设置
    APP_NAME: str = "AI Interview Assistant"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # 数据库设置（如果需要）
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # CORS设置
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

settings = Settings()