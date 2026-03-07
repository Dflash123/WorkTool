@echo off
echo Starting web_tool...
echo.
echo Local:  http://localhost:5000
echo LAN:    http://%COMPUTERNAME%:5000
echo.
python app.py
pause
