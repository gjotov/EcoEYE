@echo off
title EVEE Launcher

echo [1/2] Запускаю Go Streamer (Видео-ядро)...
cd go_streamer

start /min "EVEE Video Core" go run main.go
cd ..

echo [2/2] Жду запуска сервера...
timeout /t 3 /nobreak >nul

echo [3/3] Запускаю Python AI (Мозги)...
python main.py

pause