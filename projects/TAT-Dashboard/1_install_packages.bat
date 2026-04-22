@echo off
title Installing TAT Dashboard Packages
color 0B
echo.
echo  Installing required Python packages...
echo  This may take 1-2 minutes. Please wait.
echo.
pip install -r requirements.txt
echo.
echo ================================================
echo  Done! All packages installed successfully.
echo  You can close this window.
echo ================================================
pause
