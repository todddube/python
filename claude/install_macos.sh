#!/bin/bash

# Enhanced Filesystem MCP Server Installer for macOS
# Automatically detects system configuration and installs the MCP server

set -e  # Exit on any error

echo "========================================"
echo "Filesystem MCP Server Installer (macOS)"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org or using Homebrew:"
    echo "  brew install python3"
    exit 1
fi

echo "Python detected:"
python3 --version

# Check Python version
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo "❌ ERROR: Python 3.8+ is required"
    echo "Please upgrade your Python installation"
    exit 1
fi

echo "✅ Python version is compatible"
echo

# Make sure we're in the right directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if the main server file exists
if [ ! -f "filesystem_mcp.py" ]; then
    echo "❌ ERROR: filesystem_mcp.py not found in current directory"
    echo "Please run this script from the MCP server directory"
    exit 1
fi

echo "📁 Running from: $SCRIPT_DIR"
echo

# Run the enhanced installer
echo "🚀 Running enhanced installer..."
python3 install_enhanced.py

if [ $? -eq 0 ]; then
    echo
    echo "✅ Installation completed successfully!"
    echo
    echo "🎉 The Filesystem MCP Server is now ready to use with Claude Desktop."
    echo "Please restart Claude Desktop to activate the new server."
    echo
    echo "💡 Troubleshooting tips:"
    echo "- Check Claude Desktop logs if you encounter issues"
    echo "- Verify Claude Desktop is properly installed"
    echo "- Make sure the server has proper permissions"
    echo
else
    echo
    echo "❌ Installation failed! Check the output above for details."
    exit 1
fi
