@echo off
REM Setup script for University FAQ Assistant (Windows)
REM Automates the initial setup process

echo.
echo ============================================================
echo    UNIVERSITY FAQ ASSISTANT - AUTOMATED SETUP
echo ============================================================
echo.

REM Check Python installation
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8 or higher.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Create virtual environment
echo [2/7] Creating virtual environment...
if exist venv (
    echo [INFO] Virtual environment already exists
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install dependencies
echo [4/7] Installing dependencies (this may take 5-10 minutes)...
echo [INFO] Installing core packages...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Install optional reportlab for sample docs
echo [5/7] Installing optional packages...
pip install reportlab
echo [OK] Optional packages installed
echo.

REM Setup environment file
echo [6/7] Setting up environment configuration...
if exist .env (
    echo [INFO] .env file already exists
) else (
    copy .env.example .env
    echo [OK] Created .env file from template
    echo [INFO] Please edit .env file to add your API keys if using OpenAI
)
echo.

REM Create necessary directories
echo [7/7] Creating directories...
if not exist "data\pdfs" mkdir "data\pdfs"
if not exist "data\vector_db" mkdir "data\vector_db"
echo [OK] Directories created
echo.

echo ============================================================
echo    SETUP COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo.
echo 1. Configure your API keys (if using OpenAI):
echo    - Edit .env file
echo    - Set OPENAI_API_KEY=your-key-here
echo.
echo 2. Add PDF documents:
echo    - Option A: Place your PDFs in data\pdfs\
echo    - Option B: Generate samples: python create_sample_docs.py
echo.
echo 3. Run document ingestion:
echo    python backend\ingest.py
echo.
echo 4. Launch the application:
echo    streamlit run frontend\app.py
echo.
echo Run test_system.py to verify installation:
echo    python test_system.py
echo.
echo ============================================================
echo.
pause
