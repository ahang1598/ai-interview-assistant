from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库URL，默认使用MySQL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://ahang:Ahang%40123@172.30.153.10:3306/interview")

# 创建引擎，移除SQLite特有的connect_args参数
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()