import uvicorn
import asyncio
import sys
from main import app

def run_server():
    """启动服务器的简化版本"""
    try:
        # 设置Windows兼容的事件循环
        if sys.platform == "win32":
            # 使用SelectorEventLoop而不是ProactorEventLoop
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        # 使用基础配置启动服务器
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            reload=False,
            workers=1
        )
        
        server = uvicorn.Server(config)
        print("🚀 正在启动FastAPI服务器...")
        print("📖 API文档地址: http://127.0.0.1:8000/docs")
        print("🌐 前端页面地址: http://127.0.0.1:8000")
        
        # 运行服务器
        asyncio.run(server.serve())
        
    except Exception as e:
        print(f"启动服务器时出错: {e}")
        print("尝试使用备用方法启动...")
        
        # 备用方法：直接使用uvicorn.run
        uvicorn.run(
            "main:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            workers=1,
            log_level="info"
        )

if __name__ == "__main__":
    run_server()