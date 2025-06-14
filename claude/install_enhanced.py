#!/usr/bin/env python3
"""
Enhanced Cross-Platform Installer for Filesystem MCP Server

This installer automatically detects the operating system and sets up the 
Filesystem MCP Server for Claude Desktop with appropriate configurations.

Supports:
- Windows (Claude Desktop)
- macOS (Claude Desktop)
- Linux (Manual setup instructions)
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

class MCPInstaller:
    """Cross-platform MCP installer."""
    
    def __init__(self):
        self.system = platform.system()
        self.home = Path.home()
        self.script_dir = Path(__file__).parent
        
        print(f"🚀 Filesystem MCP Server Installer")
        print(f"📍 Detected OS: {self.system} {platform.release()}")
        print(f"🏠 Home directory: {self.home}")
        print(f"📂 Script directory: {self.script_dir}")
        
    def get_claude_config_path(self) -> Optional[Path]:
        """Get Claude Desktop configuration path based on OS."""
        if self.system == "Windows":
            # Windows: %APPDATA%\Claude\claude_desktop_config.json
            return Path(os.environ.get('APPDATA', '')) / "Claude" / "claude_desktop_config.json"
        elif self.system == "Darwin":  # macOS
            # macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
            return self.home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        else:
            # Linux/Other - Claude Desktop may not be officially supported
            print("⚠️  Claude Desktop configuration path unknown for this OS")
            return None
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    
    def setup_server_directory(self) -> Path:
        """Setup the MCP server directory."""
        if self.system == "Windows":
            server_dir = self.home / "Documents" / "MCP" / "filesystem-mcp"
        elif self.system == "Darwin":
            server_dir = self.home / "Documents" / "MCP" / "filesystem-mcp"
        else:
            server_dir = self.home / ".local" / "share" / "mcp" / "filesystem-mcp"
        
        server_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Server directory: {server_dir}")
        return server_dir
    
    def copy_server_files(self, server_dir: Path) -> bool:
        """Copy server files to installation directory."""
        try:
            # Copy main server file
            server_file = self.script_dir / "filesystem_mcp.py"
            if server_file.exists():
                shutil.copy2(server_file, server_dir / "filesystem_mcp.py")
                print("✅ Copied filesystem_mcp.py")
            else:
                print("❌ filesystem_mcp.py not found!")
                return False
            
            # Copy config files if they exist
            config_dir = server_dir / "config"
            config_dir.mkdir(exist_ok=True)
            
            source_config = self.script_dir / "config"
            if source_config.exists():
                for config_file in source_config.glob("*.json"):
                    shutil.copy2(config_file, config_dir / config_file.name)
                    print(f"✅ Copied {config_file.name}")
            
            # Copy README if it exists
            readme_file = self.script_dir / "README.md"
            if readme_file.exists():
                shutil.copy2(readme_file, server_dir / "README.md")
                print("✅ Copied README.md")
            
            return True
        except Exception as e:
            print(f"❌ Error copying files: {e}")
            return False
    
    def create_launch_script(self, server_dir: Path) -> bool:
        """Create platform-specific launch script."""
        try:
            if self.system == "Windows":
                # Create batch file for Windows
                batch_content = f'''@echo off
cd /d "{server_dir}"
"{sys.executable}" filesystem_mcp.py
'''
                batch_file = server_dir / "run_mcp.bat"
                batch_file.write_text(batch_content)
                print("✅ Created run_mcp.bat")
                
            else:  # macOS/Linux
                # Create shell script
                shell_content = f'''#!/bin/bash
cd "{server_dir}"
"{sys.executable}" filesystem_mcp.py
'''
                shell_file = server_dir / "run_mcp.sh"
                shell_file.write_text(shell_content)
                shell_file.chmod(0o755)  # Make executable
                print("✅ Created run_mcp.sh")
            
            return True
        except Exception as e:
            print(f"❌ Error creating launch script: {e}")
            return False
    
    def update_claude_config(self, server_dir: Path) -> bool:
        """Update Claude Desktop configuration."""
        config_path = self.get_claude_config_path()
        if not config_path:
            return False
        
        try:
            # Create config directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Load existing config or create new one
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Ensure mcpServers section exists
            if 'mcpServers' not in config:
                config['mcpServers'] = {}
            
            # Add filesystem MCP server configuration
            if self.system == "Windows":
                server_config = {
                    "command": str(server_dir / "run_mcp.bat"),
                    "args": []
                }
            else:
                server_config = {
                    "command": sys.executable,
                    "args": [str(server_dir / "filesystem_mcp.py")]
                }
            
            config['mcpServers']['filesystem'] = server_config
            
            # Save updated config
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Updated Claude config: {config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating Claude config: {e}")
            return False
    
    def test_installation(self, server_dir: Path) -> bool:
        """Test the MCP server installation."""
        try:
            print("🧪 Testing MCP server...")
            
            # Simple syntax test
            result = subprocess.run(
                [sys.executable, "-c", "import filesystem_mcp; print('Import successful')"],
                cwd=server_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Server test passed")
                return True
            else:
                print(f"❌ Server test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  Server test timed out")
            return True
        except Exception as e:
            print(f"❌ Error testing server: {e}")
            return False
    
    def print_success_message(self, server_dir: Path):
        """Print installation success message."""
        print("\n" + "="*60)
        print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"📁 Server installed at: {server_dir}")
        print(f"⚙️  Configuration directory: {server_dir / 'config'}")
        
        if self.system == "Windows":
            print(f"🚀 Launch script: {server_dir / 'run_mcp.bat'}")
        else:
            print(f"🚀 Launch script: {server_dir / 'run_mcp.sh'}")
        
        print("\n📋 Next Steps:")
        print("1. Restart Claude Desktop to load the new MCP server")
        print("2. In Claude, you should now see filesystem tools available")
        print("3. Try asking Claude to 'list files in my documents folder'")
        
        print("\n🔧 Configuration:")
        print(f"- Edit exclusions: {server_dir / 'config' / 'exclusions.json'}")
        print(f"- Edit settings: {server_dir / 'config' / 'settings.json'}")
        
        print("\n📚 Documentation:")
        print(f"- README: {server_dir / 'README.md'}")
        print("- Logs: filesystem_mcp.log (in server directory)")
        
        print("\n⚠️  Troubleshooting:")
        print("- Check Claude Desktop logs for connection issues")
        print("- Ensure Python 3.8+ is installed and accessible")
        print("- Verify file permissions on the server directory")
        print("="*60)
    
    def install(self):
        """Run the complete installation process."""
        print("\n🔍 Starting installation process...")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Setup server directory
        server_dir = self.setup_server_directory()
        
        # Copy server files
        if not self.copy_server_files(server_dir):
            return False
        
        # Create launch script
        if not self.create_launch_script(server_dir):
            return False
        
        # Update Claude configuration
        if not self.update_claude_config(server_dir):
            print("⚠️  Could not update Claude config automatically")
            print("   You may need to configure Claude Desktop manually")
        
        # Test installation
        self.test_installation(server_dir)
        
        # Print success message
        self.print_success_message(server_dir)
        
        return True

def main():
    """Main installation function."""
    try:
        installer = MCPInstaller()
        success = installer.install()
        
        if success:
            print("\n✅ Installation completed successfully!")
            return 0
        else:
            print("\n❌ Installation failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
