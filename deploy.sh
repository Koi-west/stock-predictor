#!/bin/bash
# ORACLE Stock Predictor — 一键部署脚本
# 用法: ssh ubuntu@你的IP "bash -s" < deploy.sh

set -e

echo "=== 1/5 安装系统依赖 ==="
sudo apt-get update -qq
sudo apt-get install -y -qq curl git

echo "=== 2/5 安装 Node.js 20 ==="
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y -qq nodejs

echo "=== 3/5 安装 uv (Python) ==="
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc

echo "=== 4/5 拉取代码 ==="
sudo rm -rf /opt/stock-predictor
sudo git clone https://github.com/Koi-west/stock-predictor.git /opt/stock-predictor
sudo chown -R ubuntu:ubuntu /opt/stock-predictor
cd /opt/stock-predictor

# Python 依赖
uv sync

# 前端依赖 + 构建
cd frontend
npm install
npm run build
cd ..

echo "=== 5/5 配置系统服务 ==="

# 后端服务
sudo tee /etc/systemd/system/oracle-backend.service > /dev/null << 'EOF'
[Unit]
Description=Oracle Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/stock-predictor
ExecStart=/home/ubuntu/.local/bin/uv run python backend.py
Restart=always
RestartSec=3
Environment=PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

# 前端服务
sudo tee /etc/systemd/system/oracle-frontend.service > /dev/null << 'EOF'
[Unit]
Description=Oracle Frontend (Next.js)
After=oracle-backend.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/stock-predictor/frontend
ExecStart=/usr/bin/npm run start -- -p 3000
Restart=always
RestartSec=3
Environment=NEXT_PUBLIC_API_URL=

[Install]
WantedBy=multi-user.target
EOF

# Next.js 代理 API 到后端
cat > /opt/stock-predictor/frontend/next.config.mjs << 'NEXTEOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
NEXTEOF

# 重新构建（带 rewrite 配置）
cd /opt/stock-predictor/frontend
npm run build

# 启动
sudo systemctl daemon-reload
sudo systemctl enable oracle-backend oracle-frontend
sudo systemctl start oracle-backend
sleep 3
sudo systemctl start oracle-frontend

echo ""
echo "========================================="
echo "  ORACLE 部署完成!"
echo "  访问: http://$(curl -s ifconfig.me):3000"
echo "========================================="
