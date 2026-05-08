@echo off
cd /d D:\edutest
call .venv\Scripts\activate
waitress-serve --host=0.0.0.0 --port=5000 run:app
pause