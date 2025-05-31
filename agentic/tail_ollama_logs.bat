@echo off
title Ollama Logs - 1748282273.7865736
echo Tailing Ollama API logs...
echo Press Ctrl+C to stop
echo.
:loop
powershell -command "try { Invoke-RestMethod -Uri http://localhost:11434/api/version } catch { \"Ollama API Error: $_\" }" >> "c:\Users\todd\OneDrive\Documents\GitHub\python\agentic\logs\ollama_logs.txt"
powershell -command "try { Invoke-RestMethod -Uri http://localhost:11434/api/tags } catch { \"Ollama Tags Error: $_\" }" >> "c:\Users\todd\OneDrive\Documents\GitHub\python\agentic\logs\ollama_logs.txt"
type "c:\Users\todd\OneDrive\Documents\GitHub\python\agentic\logs\ollama_logs.txt"
timeout /t 5 /nobreak > nul
cls
goto loop
