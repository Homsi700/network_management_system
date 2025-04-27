@echo off
echo ========================================
echo Starting Network Management System
echo ========================================
echo.

:: تغيير المجلد الحالي إلى مجلد المشروع
cd /d "%~dp0"

:: تفعيل البيئة الافتراضية
if not exist venv\Scripts\activate.bat (
    echo Error: Virtual environment not found. Please run install_dependencies.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate

:: التحقق من وجود ملف .env
if not exist .env (
    echo Error: .env file not found! Please run install_dependencies.bat first.
    pause
    exit /b 1
)

:: تعيين PYTHONPATH
set PYTHONPATH=%CD%

:: فتح المتصفح (بعد 3 ثواني للتأكد من تشغيل السيرفر)
start /b cmd /c "timeout /t 3 /nobreak > nul && start http://localhost:8000"

:: تشغيل السيرفر
echo Starting server at http://localhost:8000
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000