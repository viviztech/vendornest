#!/bin/bash
# VendorNest deployment script for AWS EC2 (ap-south-1)
# Usage: ./deploy.sh
set -e

EC2_HOST="ubuntu@13.205.180.69"
EC2_KEY="~/.ssh/copytrade-key.pem"
REMOTE_DIR="/home/ubuntu/vendornest"
REPO="git@github.com:viviztech/vendornest.git"

echo "=== VendorNest Deploy ==="

# Push to GitHub first
git add -A && git commit -m "Deploy $(date '+%Y-%m-%d %H:%M')" || true
git push origin main

# SSH and deploy
ssh -i $EC2_KEY $EC2_HOST << 'REMOTE'
set -e
cd /home/ubuntu/vendornest

echo "-- Pulling latest code..."
git pull origin main

echo "-- Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt -q

echo "-- Running migrations..."
alembic upgrade head

echo "-- Restarting services..."
sudo supervisorctl restart vendornest-api vendornest-worker vendornest-beat

echo "-- Reloading nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo "=== Deploy complete ==="
REMOTE
