@echo off
REM Quick demo script for University FAQ Assistant
REM Runs the complete demo from start to finish

echo.
echo ============================================================
echo    UNIVERSITY FAQ ASSISTANT - QUICK DEMO
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if PDFs exist
if not exist "data\pdfs\*.pdf" (
    echo [INFO] No PDF files found. Generating sample documents...
    python create_sample_docs.py
    if errorlevel 1 (
        echo [ERROR] Failed to generate sample documents
        pause
        exit /b 1
    )
    echo.
)

REM Check if vector store exists
if not exist "data\vector_db\faiss_index\index.faiss" (
    echo [INFO] Vector store not found. Running document ingestion...
    python backend\ingest.py
    if errorlevel 1 (
        echo [ERROR] Document ingestion failed
        pause
        exit /b 1
    )
    echo.
)

REM Run system test
echo [INFO] Running system test...
python test_system.py
echo.

REM Launch application
echo ============================================================
echo    LAUNCHING APPLICATION
echo ============================================================
echo.
echo The application will open in your browser automatically.
echo.
echo Try these example questions:
echo   - What are the admission requirements?
echo   - When does fall semester start?
echo   - What is the refund policy?
echo   - How do I register for courses?
echo.
echo Press Ctrl+C in this window to stop the application.
echo.
pause

streamlit run frontend\app.py
