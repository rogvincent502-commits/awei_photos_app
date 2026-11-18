@echo off
setlocal
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
title AWei Photos Server
call "C:\Users\Dong\miniconda3\Scripts\activate.bat"
cd /d "D:\awei_photos_app"
python app.py
endlocal
pause
