@echo off
chcp 65001 > nul
echo ========================================
echo Scania Server Price Validation
echo ========================================
echo.

set SERVER_NAME=scania
python main.py

pause
