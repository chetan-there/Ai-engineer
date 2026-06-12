#!/bin/bash
# run.sh — One-command startup for HybridSeek AI
# Usage: ./run.sh

set -e  # Exit on any error

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║        HybridSeek AI — Starting Up       ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "⚡ Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create .env if missing
if [ ! -f ".env" ]; then
    echo "⚠️  No .env found — copying from .env.example"
    cp .env.example .env
    echo "   Edit .env and add your OPENAI_API_KEY before making /ask requests."
fi

echo ""
echo "🚀 Starting FastAPI server..."
echo "   API:     http://localhost:8000"
echo "   Swagger: http://localhost:8000/docs"
echo "   ReDoc:   http://localhost:8000/redoc"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
