@echo off
REM Windows 批处理脚本：启动 Streamlit Web 应用

echo 🚀 启动个人投研平台 Web 应用...
echo 📍 访问地址: http://localhost:8501
echo.
echo 按 Ctrl+C 停止服务
echo.

streamlit run web_app.py

pause
