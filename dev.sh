#!/usr/bin/env bash
set -e

# Go to repo root (folder where this script lives)
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Starting CRAI dev environment..."
echo "Repo: $ROOT_DIR"

# ---- Backend ----
echo "Starting backend (FastAPI) on http://127.0.0.1:8000 ..."
cd "$ROOT_DIR/backend"

# Create venv if missing
if [ ! -d "venv" ]; then
  echo "Backend venv not found -> creating venv..."
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip (helps avoid weird install issues)
python -m pip install --upgrade pip

# Install requirements
python -m pip install -r requirements.txt

# Start backend in background (use python -m uvicorn to ensure correct venv)
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# ---- Frontend ----
echo "Starting frontend (Vite) on http://localhost:5173 ..."
cd "$ROOT_DIR/frontend"

# Install node modules if missing
if [ ! -d "node_modules" ]; then
  npm install
fi

# Stop backend when script exits (even if you Ctrl+C)
cleanup() {
  echo ""
  echo "Stopping backend..."
  kill $BACKEND_PID 2>/dev/null || true
}
trap cleanup EXIT

# Start frontend (foreground)
npm run dev