@echo off
echo Starting Agentic Conversation Simulator with Ollama optimization...
echo.

:: Check if Ollama is running
powershell -Command "try { $null = Invoke-RestMethod -Uri 'http://localhost:11434/api/version' -Method Get; Write-Host 'Ollama service is running.' -ForegroundColor Green } catch { Write-Host 'Ollama is not running! Please start Ollama first.' -ForegroundColor Red; exit 1 }"
if %ERRORLEVEL% NEQ 0 (
    echo Please start Ollama and try again.
    pause
    exit /b 1
)

:: Start performance monitoring in a separate window
start "Ollama Performance Monitor" cmd /c "python utils\monitor_ollama.py"

:: Start the main application
echo Starting Streamlit application...
echo.
echo If browser doesn't open automatically, visit http://localhost:8501
echo.
streamlit run agent_demo.py

:: Exit when streamlit closes
echo Application terminated.
pause
