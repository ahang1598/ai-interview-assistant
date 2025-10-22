from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib
import secrets

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    salt = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.salt = secrets.token_hex(16)
        # 使用SHA-256和盐值对密码进行哈希
        self.hashed_password = hashlib.sha256((password + self.salt).encode()).hexdigest()
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash"""
        hashed_input = hashlib.sha256((password + self.salt).encode()).hexdigest()
        return hashed_input == self.hashed_password