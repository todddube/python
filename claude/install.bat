@echo off
echo Installing Filesystem MCP for Claude Desktop...
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Run the installation script
python install_for_claude.py

if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo Please restart Claude Desktop to use the filesystem tools.
pause
