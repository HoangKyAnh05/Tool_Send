@echo off
title Antigravity Telegram Remote Controller
chcp 65001 > nul
cd /d "%~dp0"

echo ============================================================
echo        🤖 ANTIGRAVITY TELEGRAM REMOTE CONTROLLER 📱
echo ============================================================
echo.

python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Đã xảy ra lỗi khi chạy Bot. Vui lòng kiểm tra file .env hoặc thông báo lỗi ở trên.
    echo.
    pause
)
