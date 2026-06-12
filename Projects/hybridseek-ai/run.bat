@echo off
REM run.bat — Windows startup for HybridSeek AI
REM Usage: run.bat

echo.
echo ====================================
echo   HybridSeek AI - Starting Up
echo ====================================
echo.

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -q -r requirements.txt

IF NOT EXIST .env (
    echo No .env found - copying from .env.example
    copy .env.example .env
    echo Edit .env and add your OPENAI_API_KEY before using /ask
)

echo.
echo Starting FastAPI server...
echo API:     http://localhost:8000
echo Swagger: http://localhost:8000/docs
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
