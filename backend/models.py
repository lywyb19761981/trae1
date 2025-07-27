from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# 用户注册请求模型
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

# 用户登录请求模型
class UserLogin(BaseModel):
    username: str
    password: str

# 用户响应模型
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token响应模型
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# 通用响应模型
class MessageResponse(BaseModel):
    message: str

# 错误响应模型
class ErrorResponse(BaseModel):
    error: str