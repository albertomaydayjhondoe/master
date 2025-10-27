@echo off
echo 🎯 Reiniciando Dashboard Viral con Mejoras...
echo.

REM Matar procesos existentes de Streamlit
taskkill /f /im streamlit.exe 2>nul
timeout /t 2 /nobreak >nul

REM Lanzar dashboard mejorado
echo 🚀 Lanzando Dashboard Viral Mejorado...
echo 📊 URL: http://localhost:8503
echo.
streamlit run dashboard_viral_timeline.py --server.port 8503

pause