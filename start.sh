#!/bin/bash
cd "$(dirname "$0")"

# 清理旧进程
lsof -ti :8000 | xargs kill 2>/dev/null
lsof -ti :3000 | xargs kill 2>/dev/null
sleep 1

# 启动后端（静默 yfinance 增量更新的无害警告）
uv run python backend.py 2>&1 &
BACKEND_PID=$!

# 等后端就绪
sleep 3

# 启动前端
cd frontend && npm run dev &
FRONTEND_PID=$!

# Ctrl+C 同时杀两个
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
echo ""
echo "  ORACLE 已启动"
echo "  前端: http://localhost:3000"
echo "  后端: http://localhost:8000"
echo "  Ctrl+C 停止"
echo ""
wait
