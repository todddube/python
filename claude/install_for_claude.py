#!/usr/bin/env python3

import subprocess
import sys
import os
import json
from pathlib import Path

def install_dependencies():
    """Install required Python dependencies."""
    print("Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Python dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def get_claude_desktop_config_path():
    """Get the Claude Desktop configuration path."""
    if sys.platform == "win32":
        # Windows
        config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
    elif sys.platform == "darwin":
        # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "Claude"
    else:
        # Linux
        config_dir = Path.home() / ".config" / "claude"
    
    return config_dir / "claude_desktop_config.json"

def update_claude_config():
    """Update Claude Desktop configuration to include the filesystem MCP."""
    config_path = get_claude_desktop_config_path()
    
    # Get the current script directory
    script_dir = Path(__file__).parent.absolute()
    filesystem_mcp_path = script_dir / "filesystem_mcp.py"
    
    # Create the MCP server configuration
    mcp_config = {
        "mcpServers": {
            "filesystem": {
                "command": str(sys.executable),
                "args": [str(filesystem_mcp_path)],
                "env": {
                    "PYTHONPATH": str(script_dir)
                }
            }
        }
    }
    
    # Read existing config or create new one
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
        except json.JSONDecodeError:
            existing_config = {}
    else:
        existing_config = {}
    
    # Merge configurations
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["filesystem"] = mcp_config["mcpServers"]["filesystem"]
    
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write updated config
    try:
        with open(config_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        print(f"✅ Updated Claude Desktop config at: {config_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to update Claude Desktop config: {e}")
        return False

def main():
    """Main installation script."""
    print("🚀 Installing Filesystem MCP for Claude Desktop...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("filesystem_mcp.py").exists():
        print("❌ filesystem_mcp.py not found in current directory")
        print("Please run this script from the directory containing filesystem_mcp.py")
        return False
    
    # Install Python dependencies
    if not install_dependencies():
        return False
    
    # Update Claude Desktop configuration
    if not update_claude_config():
        return False
    
    print("\n🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Restart Claude Desktop application")
    print("2. You should now see 'filesystem' tools available in Claude")
    print("3. Try asking Claude to 'list my C: drive' or 'search for *.py files'")
    print("\nConfiguration files:")
    print(f"- Exclusions: {Path('config/exclusions.json').absolute()}")
    print(f"- Settings: {Path('config/settings.json').absolute()}")
    print("\nYou can modify these files to customize the filesystem access.")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
