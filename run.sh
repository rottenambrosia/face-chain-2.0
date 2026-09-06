#!/usr/bin/env bash
# FaceChain 2.0 Startup Script

echo "======================================================"
echo "  FaceChain 2.0 — Biometric Web3 Provenance Pipeline   "
echo "======================================================"

if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

PYTHON_BIN="./.venv/bin/python"
if [ ! -f "$PYTHON_BIN" ]; then
    PYTHON_BIN="python3"
fi

echo "Starting FastAPI Backend on port 8000..."
$PYTHON_BIN -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

sleep 2

echo "Starting Streamlit Frontend on port 8501..."
$PYTHON_BIN -m streamlit run frontend/streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "FaceChain 2.0 is running!"
echo "• Frontend: http://localhost:8501"
echo "• API Docs: http://localhost:8000/docs"
echo "• Health:   http://localhost:8000/api/v1/health"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
