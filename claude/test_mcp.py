#!/usr/bin/env python3
"""
Test script for the Filesystem MCP Server
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def test_mcp_server():
    """Test the MCP server basic functionality."""
    print("Testing Filesystem MCP Server...")
    print("=" * 40)
    
    # Check if filesystem_mcp.py exists
    mcp_script = Path("filesystem_mcp.py")
    if not mcp_script.exists():
        print("❌ filesystem_mcp.py not found")
        return False
    
    # Test basic import
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("filesystem_mcp", mcp_script)
        if spec is None:
            print("❌ Could not load filesystem_mcp.py")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ filesystem_mcp.py imports successfully")
        
        # Test FilesystemMCP class
        fs = module.FilesystemMCP()
        print("✅ FilesystemMCP class instantiated")
        
        # Test configuration loading
        config_dir = Path("config")
        if config_dir.exists():
            print("✅ Config directory found")
            
            exclusions_file = config_dir / "exclusions.json"
            settings_file = config_dir / "settings.json"
            
            if exclusions_file.exists():
                print("✅ Exclusions config found")
            else:
                print("⚠️ Exclusions config not found")
            
            if settings_file.exists():
                print("✅ Settings config found")
            else:
                print("⚠️ Settings config not found")
        else:
            print("⚠️ Config directory not found")
        
        # Test path validation
        test_paths = [
            "C:\\",
            "C:\\Windows",
            "C:\\Users",
            "D:\\",
        ]
        
        print("\nTesting path validation:")
        for path in test_paths:
            is_allowed = fs.is_path_allowed(path)
            status = "✅ Allowed" if is_allowed else "❌ Blocked"
            print(f"  {path}: {status}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure to install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error testing MCP server: {e}")
        return False

def test_claude_config():
    """Test Claude Desktop configuration."""
    print("\nTesting Claude Desktop Configuration...")
    print("=" * 40)
    
    # Get Claude config path
    config_paths = []
    if sys.platform == "win32":
        config_paths.append(Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json")
    elif sys.platform == "darwin":
        config_paths.append(Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")
    else:
        config_paths.append(Path.home() / ".config" / "claude" / "claude_desktop_config.json")
    
    found_config = False
    for config_path in config_paths:
        if config_path.exists():
            found_config = True
            print(f"✅ Found Claude config at: {config_path}")
            
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                if "mcpServers" in config:
                    if "filesystem" in config["mcpServers"]:
                        print("✅ Filesystem MCP server found in config")
                        fs_config = config["mcpServers"]["filesystem"]
                        print(f"   Command: {fs_config.get('command', 'Not specified')}")
                        print(f"   Args: {fs_config.get('args', 'Not specified')}")
                    else:
                        print("⚠️ Filesystem MCP server not configured")
                else:
                    print("⚠️ No MCP servers configured")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON in config file: {e}")
            except Exception as e:
                print(f"❌ Error reading config: {e}")
            break
    
    if not found_config:
        print("⚠️ Claude Desktop config not found")
        print("This is normal if Claude Desktop hasn't been run yet")
    
    return found_config

def main():
    """Main test function."""
    print("🧪 Filesystem MCP Server Test Suite")
    print("=" * 50)
    
    # Test the MCP server
    server_ok = test_mcp_server()
    
    # Test Claude configuration
    config_ok = test_claude_config()
    
    print(f"\n📊 Test Results:")
    print(f"MCP Server: {'✅ Pass' if server_ok else '❌ Fail'}")
    print(f"Claude Config: {'✅ Found' if config_ok else '⚠️ Not Found'}")
    
    if server_ok:
        print("\n🎉 MCP server is ready!")
        if not config_ok:
            print("💡 Run 'install_for_claude.py' to configure Claude Desktop")
    else:
        print("\n❌ MCP server has issues - check the errors above")
    
    return server_ok

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
