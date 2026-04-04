@echo off
color 0A
echo ===================================================
echo   DANG KHOI DONG TAXLENS-AI ENTERPRISE (GEMINI)
echo ===================================================
echo [1/3] Dang sinh du lieu ke toan mau (Mock Data)...
python scripts\generate_test_data.py

echo [2/3] Khoi dong FastAPI Backend Engine...
start cmd /k "uvicorn taxlens.api.main:app --host 127.0.0.1 --port 8000"

echo [3/3] Doi Backend nap LangGraph (4 giay)...
timeout /t 4 /nobreak >nul

echo Mo trinh duyet vao giao dien chinh...
start http://127.0.0.1:8000/
echo Done!
exit
