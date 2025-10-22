from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

# MySQL数据库配置示例:
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()