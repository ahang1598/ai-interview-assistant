from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, User as UserSchema, Token, PasswordChange
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token
from fastapi.security import OAuth2PasswordBearer
import os
import shutil

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

router = APIRouter(
    prefix="",
    tags=["auth"]
)

@router.post("/register", response_model=UserSchema)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册端点
    """
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    new_user = User(
        username=user.username,
        email=user.email
    )
    new_user.set_password(user.password)
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 为新用户创建专属的知识库目录
        # 注意：Qdrant 是外部数据库，不需要本地目录
        # user_kb_path = f"./chroma_db/user_{new_user.id}"
        # if not os.path.exists(user_kb_path):
        #     os.makedirs(user_kb_path)
        
        # 手动转换 datetime 字段为字符串
        user_dict = {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
            "updated_at": new_user.updated_at.isoformat() if new_user.updated_at else None
        }
        return user_dict
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户注册失败"
        )

@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录端点
    """
    # 根据用户名查找用户
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前用户依赖项
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    获取当前活跃用户依赖项
    """
    # 可以在这里添加检查用户是否被禁用的逻辑
    return current_user

@router.put("/users/me/password", response_model=UserSchema)
def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    修改当前用户密码
    """
    # 验证当前密码是否正确
    if not current_user.check_password(password_change.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 设置新密码
    current_user.set_password(password_change.new_password)
    db.commit()
    db.refresh(current_user)
    
    # 手动转换 datetime 字段为字符串
    user_dict = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }
    return user_dict

@router.delete("/users/me/knowledge", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_knowledge(current_user: User = Depends(get_current_active_user)):
    """
    删除当前用户的知识库
    """
    # Qdrant 不需要手动清理目录，由 UserRAGPipeline 处理
    # user_kb_path = f"./chroma_db/user_{current_user.id}"
    # if os.path.exists(user_kb_path):
    #     shutil.rmtree(user_kb_path)
    return

@router.get("/users/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    """
    # 手动转换 datetime 字段为字符串
    user_dict = {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
    }
    return user_dict