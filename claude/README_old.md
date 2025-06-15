# Filesystem MCP Server for Claude Desktop

A comprehensive Model Context Protocol (MCP) server that provides Claude Desktop with safe access to your local file system across all detected drives on Windows, macOS, and Linux.

## Features

- 🗂️ **Safe File System Access**: Browse all detected drives with intelligent exclusions
- 🔍 **Advanced Search**: Find files by name patterns, size, and type
- 📖 **File Reading**: Read text files with encoding support and size limits
- 📊 **Drive Information**: Get disk usage and drive statistics for all detected drives
- 🛡️ **Security Controls**: Built-in exclusions for system and sensitive directories
- ⚙️ **Self-Contained**: No external configuration files needed - everything embedded
- 🌍 **Cross-Platform**: Automatic OS detection and drive discovery (Windows, macOS, Linux)
- 🚀 **Easy Installation**: One-click installation with automatic Claude Desktop integration

## Tools Available

1. **list_directory** - List directory contents with detailed information
2. **read_file** - Read text files safely with encoding support
3. **search_files** - Search for files using wildcard patterns
4. **get_file_info** - Get detailed information about files/directories
5. **find_large_files** - Find files above a specified size threshold
6. **get_drive_info** - View drive usage and statistics

## Quick Installation

1. **Run the installer**:
   ```bash
   # Double-click install.bat or run in PowerShell:
   .\install.bat
   ```

2. **Restart Claude Desktop**

3. **Start using filesystem tools**:
   - "List my C: drive contents"
   - "Search for *.py files in my Documents"
   - "Find large files over 100MB"

## Manual Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Add to Claude Desktop config**:
   
   Edit your Claude Desktop configuration file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/claude/claude_desktop_config.json`

   Add this configuration:
   ```json
   {
     "mcpServers": {
       "filesystem": {
         "command": "python",
         "args": ["C:\\path\\to\\your\\filesystem_mcp.py"]
       }
     }
   }
   ```

## Configuration

### Exclusions (`config/exclusions.json`)

Controls which directories and files are blocked from access:

```json
{
  "patterns": [
    "C:\\Windows\\*",
    "C:\\Program Files\\*",
    "*\\AppData\\*",
    "*\\.git\\*",
    "*\\node_modules\\*"
  ]
}
```

### Settings (`config/settings.json`)

Controls server behavior:

```json
{
  "allowed_drives": ["C:", "D:"],
  "max_file_size_mb": 10,
  "max_search_results": 1000
}
```

## Usage Examples

Once installed, you can ask Claude:

- **"List the contents of my Documents folder"**
- **"Search for all Python files in my projects directory"**
- **"Find files larger than 100MB on my C: drive"**
- **"Read the contents of my README.md file"**
- **"Show me information about my D: drive"**
- **"Find all .txt files containing 'todo' in the name"**

## Security Features

- **Path Validation**: All paths are validated and resolved safely
- **Drive Restrictions**: Only allows access to specified drives (C:, D: by default)
- **Exclusion Patterns**: System directories and sensitive areas are blocked
- **File Size Limits**: Large files are rejected to prevent memory issues
- **Permission Handling**: Gracefully handles permission denied errors
- **Path Traversal Protection**: Prevents access outside allowed areas

## Default Exclusions

The server blocks access to:
- Windows system directories (`C:\Windows\*`, `C:\Program Files\*`)
- User AppData directories (`*\AppData\*`)
- Hidden files and directories (`*\.*`)
- Development artifacts (`*\node_modules\*`, `*\.git\*`, `*\__pycache__\*`)
- Temporary directories (`*\Temp\*`, `*\tmp\*`)
- System recovery and boot files

## Troubleshooting

### MCP Server Not Found
- Ensure Python is in your PATH
- Check that `requirements.txt` dependencies are installed
- Verify the path in your Claude Desktop config is correct

### Permission Denied Errors
- Some system directories are intentionally blocked for security
- Check if the path is in your exclusions list
- Run as administrator if needed (not recommended)

### File Too Large Errors
- Adjust `max_file_size_mb` in `config/settings.json`
- Default limit is 10MB to prevent memory issues

## Development

### File Structure
```
claude/
├── filesystem_mcp.py      # Main MCP server
├── install_for_claude.py  # Installation script
├── install.bat           # Windows installer
├── requirements.txt      # Python dependencies
├── package.json         # Node.js package info
├── README.md           # This file
└── config/
    ├── exclusions.json  # Directory exclusions
    └── settings.json   # Server settings
```

### Adding New Tools

1. Add the tool definition to `list_tools()`
2. Add a handler function following the pattern `handle_[tool_name]`
3. Add the handler to the `call_tool()` function

### Testing

Test the MCP server directly:
```bash
python filesystem_mcp.py
```

The server communicates via stdin/stdout using the MCP protocol.

## License

MIT License - feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the configuration files
3. Check the logs in `filesystem_mcp.log`
4. Ensure all dependencies are installed correctly
