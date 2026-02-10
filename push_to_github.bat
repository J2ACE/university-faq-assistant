@echo off
:: Quick GitHub Push Script
:: Run this after creating your GitHub repository

echo ========================================
echo   University FAQ Assistant
echo   GitHub Push Script
echo ========================================
echo.

:: Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Step 1: Initialize Git repository...
git init

echo.
echo Step 2: Add all files...
git add .

echo.
echo Step 3: Create initial commit...
git commit -m "Initial commit: University FAQ Assistant with RAG"

echo.
echo Step 4: Set main branch...
git branch -M main

echo.
echo ========================================
echo IMPORTANT: Enter your GitHub repository URL
echo Example: https://github.com/yourusername/university-faq-assistant.git
echo ========================================
set /p REPO_URL="Enter your GitHub repository URL: "

echo.
echo Step 5: Adding remote repository...
git remote add origin %REPO_URL%

echo.
echo Step 6: Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo SUCCESS! Your code is now on GitHub!
echo ========================================
echo.
echo Next Steps:
echo 1. Go to https://share.streamlit.io/
echo 2. Deploy your app (see DEPLOYMENT.md)
echo 3. Create LinkedIn post (see SUBMISSION_CHECKLIST.md)
echo.
pause
