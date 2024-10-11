@echo off
call venv\Scripts\activate.bat
fastapi run api.py --port 8888 --host 0.0.0.0
pause