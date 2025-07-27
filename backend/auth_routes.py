from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db, User
from models import UserRegister, UserLogin, UserResponse, TokenResponse, ErrorResponse
from auth_utils import hash_password, verify_password, create_access_token, get_current_user
from datetime import timedelta

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    用户注册
    """
    # 验证密码长度
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为6位"
        )
    
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )
    
    # 创建新用户
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名或邮箱已存在"
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"user_id": new_user.id, "username": new_user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(new_user)
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    """
    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    if not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 创建访问令牌
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息
    """
    return UserResponse.from_orm(current_user)