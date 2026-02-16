@echo off
chcp 65001 > nul
echo ========================================
echo Cllrin Server Price Validation
echo ========================================
echo.

set SERVER_NAME=cllrin
python main.py

pause
