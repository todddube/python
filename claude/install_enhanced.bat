@echo off
REM Enhanced Filesystem MCP Server Installer for Windows
REM Automatically detects system configuration and installs the MCP server

echo ========================================
echo Filesystem MCP Server Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python detected:
python --version

REM Check Python version (basic check)
python -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8+ is required
    echo Please upgrade your Python installation
    pause
    exit /b 1
)

echo ✓ Python version is compatible
echo.

REM Run the enhanced installer
echo Running enhanced installer...
python install_enhanced.py

if errorlevel 1 (
    echo.
    echo Installation failed! Check the output above for details.
    pause
    exit /b 1
) else (
    echo.
    echo Installation completed successfully!
    echo.
    echo The Filesystem MCP Server is now ready to use with Claude Desktop.
    echo Please restart Claude Desktop to activate the new server.
    echo.
)

pause
