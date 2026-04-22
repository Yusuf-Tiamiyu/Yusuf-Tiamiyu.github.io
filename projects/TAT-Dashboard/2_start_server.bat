@echo off
title TAT Dashboard Server
color 0A
echo.
echo  ============================================
echo   TAT Dashboard Server
echo  ============================================
echo.
echo   Server is starting...
echo.
echo   Once started, open your browser and go to:
echo   --^> http://localhost:5000
echo.
echo   DO NOT close this window while using the
echo   dashboard. To stop the server, press CTRL+C
echo  ============================================
echo.
cd /d "%~dp0"
python app.py
pause
