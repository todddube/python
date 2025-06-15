#!/usr/bin/env python3
"""
Universal Executable Installer for Filesystem MCP Server

This is the main installer that can be run directly on any platform:
- Windows: python install.py
- macOS: ./install.py
- Linux: ./install.py

This installer will:
1. Detect your operating system (Windows, macOS, Linux)
2. Find all available drives/volumes on your system
3. Install the Filesystem MCP Server with proper Claude Desktop integration
4. Configure Claude Desktop to include detected drives in the MCP environment
5. Create platform-specific launch scripts

Simply run this script and it will automatically detect your system
and install the Filesystem MCP Server for Claude Desktop.
"""

import sys
import os
import platform
from pathlib import Path

def check_requirements():
    """Check if the system meets requirements."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check OS
    system = platform.system()
    if system not in ['Windows', 'Darwin', 'Linux']:
        print(f"⚠️  Unsupported OS: {system}")
        print("   Supported: Windows, macOS (Darwin), Linux")
    else:
        print(f"✅ Operating System: {system}")
    
    return True

def find_claude_desktop():
    """Check if Claude Desktop is installed."""
    system = platform.system()
    home = Path.home()
    
    print("🔍 Checking for Claude Desktop installation...")
    
    if system == "Windows":
        config_path = Path(os.environ.get('APPDATA', '')) / "Claude" / "claude_desktop_config.json"
        claude_paths = [
            Path(os.environ.get('LOCALAPPDATA', '')) / "Claude" / "Claude.exe",
            Path(os.environ.get('PROGRAMFILES', '')) / "Claude" / "Claude.exe",
            Path(os.environ.get('PROGRAMFILES(X86)', '')) / "Claude" / "Claude.exe"
        ]
    elif system == "Darwin":  # macOS
        config_path = home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        claude_paths = [
            Path("/Applications/Claude.app"),
            home / "Applications" / "Claude.app"
        ]
    else:  # Linux
        config_path = home / ".config" / "claude" / "claude_desktop_config.json"
        claude_paths = [
            Path("/usr/bin/claude"),
            Path("/usr/local/bin/claude"),
            home / ".local" / "bin" / "claude"
        ]
    
    # Check for Claude Desktop installation
    claude_found = False
    for path in claude_paths:
        if path.exists():
            print(f"✅ Found Claude Desktop at: {path}")
            claude_found = True
            break
    
    if not claude_found:
        print("⚠️  Claude Desktop not found in common locations")
        print("   You may need to install Claude Desktop first")
        print("   Download from: https://claude.ai/download")
    
    # Check config directory
    if config_path.parent.exists():
        print(f"✅ Claude config directory exists: {config_path.parent}")
    else:
        print(f"📁 Claude config directory will be created: {config_path.parent}")
    
    return config_path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main installer
try:
    from install_for_claude import main
except ImportError as e:
    print(f"❌ Error importing installer: {e}")
    print("Please ensure install_for_claude.py is in the same directory")
    sys.exit(1)

if __name__ == "__main__":
    # Print universal installer header
    print("🚀 Universal Filesystem MCP Server Installer")
    print("🌍 Cross-platform installer for Claude Desktop")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ System requirements not met")
        sys.exit(1)
    
    # Check Claude Desktop
    config_path = find_claude_desktop()
    
    print("\n" + "=" * 60)
    print("🚀 Starting MCP Server Installation...")
    print("=" * 60)
    
    # Run the main installer
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
