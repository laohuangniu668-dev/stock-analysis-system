#!/bin/bash

# 安装所有依赖

echo "📦 安装依赖..."

pip install -r requirements.txt
pip install streamlit>=1.28.0

echo "✅ 依赖安装完成！"
echo ""
echo "🚀 启动 Web 应用:"
echo "   sh run_web.sh  (Linux/Mac)"
echo "   run_web.bat    (Windows)"
echo ""
echo "📊 启动命令行版本:"
echo "   python main.py --watchlist config/watchlist.csv"
