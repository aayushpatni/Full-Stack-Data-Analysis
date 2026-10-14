@echo off
title Datalyze Server
color 0B
echo ========================================================
echo           DATALYZE - INTELLIGENT DATA ANALYSIS
echo ========================================================
echo.
echo Starting Flask backend server...
cd /d "D:\documents\MCA Projects\datalyze\backend"
start http://127.0.0.1:5000
echo.
echo Server is running at: http://127.0.0.1:5000
echo Opening your browser now...
echo.
echo (Keep this window open while using Datalyze)
echo ========================================================
echo.
python app.py
pause