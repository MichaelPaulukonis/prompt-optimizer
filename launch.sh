#!/bin/bash

# Prompt Optimizer Launch Script
# This script starts the MLX server and Flask app, then opens the browser

set -e

echo "🚀 Starting Prompt Optimizer..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run 'python -m venv venv' and install requirements first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if MLX is available
if ! python -c "import mlx_lm" 2>/dev/null; then
    echo "❌ MLX not found in virtual environment. Please install requirements: pip install -r requirements.txt"
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo "🧹 Cleaning up..."
    if [ ! -z "$MLX_PID" ]; then
        kill $MLX_PID 2>/dev/null || true
    fi
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Start MLX server in background
echo "🤖 Starting MLX server on port 8080..."
python -m mlx_lm server \
    --model mlx-community/Mistral-7B-Instruct-v0.3-4bit \
    --host 127.0.0.1 \
    --port 8080 &
MLX_PID=$!

# Wait for MLX server to start
echo "⏳ Waiting for MLX server to initialize..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8080/health >/dev/null 2>&1; then
        echo "✅ MLX server ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ MLX server failed to start"
        exit 1
    fi
    sleep 2
done

# Start Flask app in background
echo "🌐 Starting Flask app on port 5001..."
python app.py &
FLASK_PID=$!

# Wait for Flask app to start
echo "⏳ Waiting for Flask app to initialize..."
for i in {1..10}; do
    if curl -s http://127.0.0.1:5001/api/status >/dev/null 2>&1; then
        echo "✅ Flask app ready"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "❌ Flask app failed to start"
        exit 1
    fi
    sleep 1
done

# Open browser
echo "🌐 Opening browser..."
if command -v open >/dev/null 2>&1; then
    # macOS
    open http://127.0.0.1:5001
elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open http://127.0.0.1:5001
elif command -v start >/dev/null 2>&1; then
    # Windows
    start http://127.0.0.1:5001
else
    echo "📝 Please open http://127.0.0.1:5001 in your browser"
fi

echo "🎉 Prompt Optimizer is running!"
echo "📝 Access the app at: http://127.0.0.1:5001"
echo "🛑 Press Ctrl+C to stop all services"

# Wait for user to stop
wait
