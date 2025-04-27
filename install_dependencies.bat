@echo off
echo ========================================
echo Installing Network Management System Dependencies
echo ========================================
echo.

:: تغيير المجلد الحالي إلى مجلد المشروع
cd /d "%~dp0"

:: تحقق من وجود Python 3.11
python --version 2>&1 | findstr /r "^Python 3.11" >nul
if errorlevel 1 (
    echo Error: This project requires Python 3.11.x
    echo Please install Python 3.11 from: https://www.python.org/downloads/release/python-3119/
    echo Current Python version:
    python --version
    pause
    exit /b 1
)

:: مسح البيئة الافتراضية القديمة إذا كانت موجودة
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

:: إنشاء البيئة الافتراضية
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

:: تحديث pip
echo Updating pip...
python -m pip install --upgrade pip

:: تثبيت wheel أولاً
echo Installing wheel...
pip install wheel

:: تثبيت المكتبات الأساسية
echo Installing core dependencies...
pip install fastapi==0.95.2
pip install "uvicorn[standard]>=0.15.0,<0.16.0"
pip install python-jose[cryptography]==3.3.0
pip install "passlib[bcrypt]>=1.7.4,<1.8.0"
pip install "sqlalchemy>=1.4.23,<1.5.0"
pip install "python-dotenv>=0.19.0,<0.20.0"
pip install "python-multipart>=0.0.5,<0.1.0"
pip install "paramiko>=2.8.1,<2.9.0"
pip install "routeros-api>=0.17.0,<0.18.0"
pip install "requests>=2.26.0,<2.27.0"
pip install "pydantic>=1.10.13,<2.0.0"
pip install "aiofiles>=0.7.0,<0.8.0"
pip install "websockets>=10.0,<11.0"
pip install "email-validator>=2.1.0.post1,<3.0.0"
pip install "email-validator==2.1.0.post1"
pip install "uvicorn[standard]>=0.15.0,<0.16.0"
pip install "uvicorn==0.15.0"

:: إنشاء ملف .env إذا لم يكن موجوداً
if not exist .env (
    echo Creating .env file...
    echo SECRET_KEY=%RANDOM%%RANDOM%%RANDOM%%RANDOM% > .env
    echo DATABASE_URL=sqlite:///./network_management.db >> .env
    echo DEBUG=True >> .env
)

:: إنشاء المجلدات المطلوبة إذا لم تكن موجودة
mkdir frontend\assets\css 2>nul
mkdir frontend\assets\js 2>nul
mkdir frontend\assets\icons\svg 2>nul

:: تعيين PYTHONPATH
set PYTHONPATH=%CD%

echo.
echo ========================================
echo Setting up admin account...
echo ========================================
python backend\utils\create_admin.py

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To start the application:
echo 1. Run run_project.bat
echo 2. Open http://localhost:8000 in your browser
echo.
pause