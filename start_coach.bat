@echo off
title osu! Personal Coach AI
chcp 65001 > nul
cd /d "%~dp0osu-trainer"
python app.py
pause
