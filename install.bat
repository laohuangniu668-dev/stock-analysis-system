@echo off
REM Windows 批处理脚本：安装依赖

echo 📦 安装依赖...

pip install -r requirements.txt
pip install streamlit>=1.28.0

echo ✅ 依赖安装完成！
echo.
echo 🚀 启动 Web 应用:
echo    run_web.bat (Windows)
echo.
echo 📊 启动命令行版本:
echo    python main.py --watchlist config/watchlist.csv
echo.

pause
