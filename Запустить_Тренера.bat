@echo off
title osu! Personal Coach AI - CyberHUD Pro
chcp 65001 > nul
cls
echo ===================================================================
echo               osu! Personal Coach AI • CyberHUD Pro
echo ===================================================================
echo [1/2] Запуск сервера аналитики и ИИ-тренера...
echo [2/2] Открытие CyberHUD в браузере (http://127.0.0.1:8765)...
echo.
echo Для остановки тренера закройте это окно или нажмите Ctrl+C.
echo ===================================================================
echo.
cd /d "%~dp0osu-trainer"
python app.py
pause
