from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
# 从 database.py 导入 Base
from ..database import Base
from passlib.context import CryptContext

# 创建密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")
    
    def set_password(self, password: str):
        """设置用户密码"""
        self.hashed_password = pwd_context.hash(password)
    
    def check_password(self, password: str) -> bool:
        """检查用户密码"""
        return pwd_context.verify(password, self.hashed_password)