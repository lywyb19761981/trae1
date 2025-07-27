from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from database import create_tables
import os

# 创建FastAPI应用
app = FastAPI(
    title="用户注册登录系统",
    description="基于FastAPI和SQLite的用户认证系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
create_tables()

# 注册路由
app.include_router(auth_router)

# 静态文件服务（前端）
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# 根路径返回前端页面
@app.get("/")
async def read_root():
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "欢迎使用用户注册登录系统API"}

# 健康检查端点
@app.get("/api/health")
async def health_check():
    return {"status": "OK", "message": "服务器运行正常"}

# 启动信息
@app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI服务器启动成功！")
    print("📖 API文档地址: http://localhost:8000/docs")
    print("🌐 前端页面地址: http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    import asyncio
    import sys
    
    # Windows兼容性设置
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)