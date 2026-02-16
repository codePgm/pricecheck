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

REM Update config for Scania
echo import re > temp_update_config.py
echo content = open('config.py', 'r', encoding='utf-8').read() >> temp_update_config.py
echo content = re.sub(r'SERVER\s*=\s*"[^^"]*"', 'SERVER = "scania"', content) >> temp_update_config.py
echo open('config.py', 'w', encoding='utf-8').write(content) >> temp_update_config.py

python temp_update_config.py
if exist temp_update_config.py del temp_update_config.py

python main.py

echo.
echo.
echo ========================================
echo [2/2] Validating Cllrin Server...
echo ========================================

REM Update config for Cllrin
echo import re > temp_update_config.py
echo content = open('config.py', 'r', encoding='utf-8').read() >> temp_update_config.py
echo content = re.sub(r'SERVER\s*=\s*"[^^"]*"', 'SERVER = "cllrin"', content) >> temp_update_config.py
echo open('config.py', 'w', encoding='utf-8').write(content) >> temp_update_config.py

python temp_update_config.py
if exist temp_update_config.py del temp_update_config.py

python main.py

echo.
echo.
echo ========================================
echo All Servers Validated!
echo ========================================
echo Check the output folder for results.
echo ========================================

pause
