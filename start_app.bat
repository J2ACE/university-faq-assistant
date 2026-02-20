@echo off
echo Starting University FAQ Assistant...
cd /d "d:\Intell Unnati\university_faq_assistant"
call .\venv\Scripts\activate.bat
streamlit run frontend\app.py
pause