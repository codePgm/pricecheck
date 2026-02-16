@echo off
chcp 65001 > nul
echo ========================================
echo Cllrin Server Price Validation
echo ========================================
echo.

REM Create temp Python script to update config
echo import re > temp_update_config.py
echo content = open('config.py', 'r', encoding='utf-8').read() >> temp_update_config.py
echo content = re.sub(r'SERVER\s*=\s*"[^^"]*"', 'SERVER = "cllrin"', content) >> temp_update_config.py
echo open('config.py', 'w', encoding='utf-8').write(content) >> temp_update_config.py

REM Run the update script
python temp_update_config.py

REM Delete temp script
if exist temp_update_config.py del temp_update_config.py

REM Run main program
python main.py

pause
