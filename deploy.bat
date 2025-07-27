@echo off
REM 部署脚本 - Trae Todo App (Windows版本)
REM 支持多种部署方式

setlocal enabledelayedexpansion

echo 🚀 开始部署 Trae Todo App...

REM 检查部署类型
set DEPLOY_TYPE=%1
if "%DEPLOY_TYPE%"=="" set DEPLOY_TYPE=local

if "%DEPLOY_TYPE%"=="local" goto local
if "%DEPLOY_TYPE%"=="docker" goto docker
if "%DEPLOY_TYPE%"=="docker-compose" goto docker-compose
if "%DEPLOY_TYPE%"=="vercel" goto vercel
goto usage

:local
echo 📦 本地部署模式
echo 安装Python依赖...
cd backend
pip install -r requirements.txt
cd ..
echo 启动Flask服务器...
python backend\flask_app.py
goto end

:docker
echo 🐳 Docker部署模式
echo 构建Docker镜像...
docker build -t trae-todo-app .
echo 启动Docker容器...
docker run -d -p 8000:8000 --name trae-todo trae-todo-app
echo ✅ Docker容器已启动，访问 http://localhost:8000
goto end

:docker-compose
echo 🐳 Docker Compose部署模式
echo 启动服务...
docker-compose up -d
echo ✅ 服务已启动，访问 http://localhost:8000
goto end

:vercel
echo ☁️ Vercel部署模式
echo 检查Vercel CLI...
vercel --version >nul 2>&1
if errorlevel 1 (
    echo 请先安装Vercel CLI: npm install -g vercel
    exit /b 1
)
echo 部署到Vercel...
vercel --prod
goto end

:usage
echo ❌ 未知的部署类型: %DEPLOY_TYPE%
echo 支持的部署类型:
echo   local          - 本地开发服务器
echo   docker         - Docker容器
echo   docker-compose - Docker Compose
echo   vercel         - Vercel云平台
echo.
echo 使用方法: deploy.bat [部署类型]
exit /b 1

:end
echo 🎉 部署完成！
endlocal