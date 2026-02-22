@echo off
chcp 65001 > nul
echo ========================================
echo All Servers Price Validation
echo ========================================
echo.
echo This will validate both Scania and Cllrin servers.
echo.

echo.
echo ========================================
echo [1/2] Validating Scania Server...
echo ========================================
set SERVER_NAME=scania
cd /d E:\code\pricecheck
python E:\code\pricecheck\main.py

echo.
echo.
echo ========================================
echo [2/2] Validating Cllrin Server...
echo ========================================
set SERVER_NAME=cllrin
cd /d E:\code\pricecheck
python E:\code\pricecheck\main.py

echo.
echo.
echo ========================================
echo All Servers Validated!
echo ========================================
echo Check the output folder for results.
echo ========================================
