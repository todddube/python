# Enhanced Filesystem MCP Server

A high-performance, cross-platform filesystem Model Context Protocol (MCP) server for Claude Desktop that provides safe access to local file systems with advanced features and optimizations.

## 🚀 Features

### Core Functionality
- **Cross-platform support**: Windows, macOS, and Linux
- **Safe filesystem access** with configurable exclusions
- **Advanced file operations**: list, read, search, and analyze
- **Intelligent caching** for improved performance
- **Parallel processing** for faster operations
- **Content-based search** with regex support
- **MIME type detection** and file analysis

### Security & Safety
- **Smart exclusions** based on operating system
- **Path validation** and sanitization
- **Configurable access controls**
- **Protected system directories**
- **Size limits** and operation timeouts

### Performance Optimizations
- **Multi-threaded operations** for directory listing and search
- **LRU caching** for frequently accessed file information
- **Parallel file processing** with configurable worker pools
- **Efficient pattern matching** and filtering

## 📋 System Requirements

- **Python 3.8+** (3.9+ recommended)
- **Claude Desktop** (Windows/macOS)
- **Operating System**: Windows 10+, macOS 10.15+, or Linux

## 🔧 Installation

### Automatic Installation (Recommended)

#### Windows
1. **Download** or clone this repository
2. **Open Command Prompt** or PowerShell as Administrator
3. **Navigate** to the project directory
4. **Run the installer**:
   ```cmd
   install_enhanced.bat
   ```

#### macOS
1. **Download** or clone this repository
2. **Open Terminal**
3. **Navigate** to the project directory
4. **Make the installer executable** and run:
   ```bash
   chmod +x install_macos.sh
   ./install_macos.sh
   ```

#### Linux
1. **Download** or clone this repository
2. **Open Terminal**
3. **Navigate** to the project directory
4. **Run the Python installer**:
   ```bash
   python3 install_enhanced.py
   ```

### Manual Installation

1. **Copy Files**:
   - Copy `filesystem_mcp.py` to your desired location
   - Copy the `config/` directory with configuration files

2. **Configure Claude Desktop**:
   
   **Windows**: Edit `%APPDATA%\Claude\claude_desktop_config.json`
   **macOS**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
   
   Add this configuration:
   ```json
   {
     "mcpServers": {
       "filesystem": {
         "command": "python",
         "args": ["path/to/filesystem_mcp.py"]
       }
     }
   }
   ```

3. **Restart Claude Desktop**

## ⚙️ Configuration

### Exclusion Patterns (`config/exclusions.json`)
```json
{
  "description": "Filesystem exclusion patterns",
  "patterns": [
    "C:\\Windows\\*",
    "*/.*",
    "*/__pycache__/*",
    "*/node_modules/*"
  ]
}
```

### Server Settings (`config/settings.json`)
```json
{
  "description": "Filesystem MCP Server Settings",
  "allowed_drives": ["C:", "D:", "/", "/home"],
  "max_file_size_mb": 10,
  "max_search_results": 1000
}
```

## 🛠️ Available Tools

### `list_directory`
List contents of a directory with detailed information
- **Parameters**: `path`, `show_hidden`, `recursive`, `max_depth`
- **Example**: "List files in my Documents folder"

### `read_file`
Read the contents of a text file
- **Parameters**: `path`, `encoding`, `max_lines`
- **Example**: "Read the contents of config.txt"

### `search_files`
Search for files by name pattern with advanced filtering
- **Parameters**: `pattern`, `root_path`, `file_types`, `max_results`
- **Example**: "Find all Python files containing 'database'"

### `get_file_info`
Get detailed information about a file or directory
- **Parameters**: `path`
- **Example**: "Show information about this file"

### `find_large_files`
Find large files above a specified size threshold
- **Parameters**: `root_path`, `min_size_mb`, `max_results`
- **Example**: "Find files larger than 100MB in Downloads"

### `get_drive_info`
Get information about available drives and disk usage
- **Parameters**: None
- **Example**: "Show disk space information"

## 🔍 Usage Examples

### Basic File Operations
```
"List the contents of my Desktop folder"
"Read the README file in my project directory"
"Show me information about the large.zip file"
```

### Advanced Search
```
"Find all .py files in my projects folder"
"Search for files containing 'configuration' in their name"
"Find all images larger than 5MB in my Pictures folder"
```

### System Information
```
"Show me disk space information for all drives"
"List hidden files in the current directory"
"Find the largest files in my Downloads folder"
```

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**
   - Check Python version (3.8+ required)
   - Verify file permissions
   - Check the log file: `filesystem_mcp.log`

2. **Access denied errors**
   - Review exclusion patterns in `config/exclusions.json`
   - Check system permissions
   - Verify paths are accessible

3. **Claude Desktop connection issues**
   - Restart Claude Desktop
   - Check Claude Desktop logs
   - Verify configuration file syntax

### Log Files
- **Server logs**: `filesystem_mcp.log` (in server directory)
- **Claude Desktop logs**:
  - Windows: `%APPDATA%\Claude\logs\`
  - macOS: `~/Library/Logs/Claude/`

### Performance Tuning

1. **Adjust cache settings** in the code:
   ```python
   self.cache = PerformanceCache(max_size=2000, ttl_seconds=600)
   ```

2. **Modify thread pool size**:
   ```python
   self.executor = ThreadPoolExecutor(max_workers=8)
   ```

3. **Update exclusion patterns** to skip large directories

## 🔐 Security Considerations

- The server respects OS-specific exclusion patterns
- System directories are protected by default
- File size limits prevent memory issues
- Path validation prevents directory traversal
- Configurable access controls

## 📚 Development

### Project Structure
```
filesystem-mcp/
├── filesystem_mcp.py          # Main server implementation
├── install_enhanced.py        # Cross-platform installer
├── install_enhanced.bat       # Windows installer
├── install_macos.sh          # macOS installer
├── config/
│   ├── exclusions.json       # Path exclusion patterns
│   └── settings.json         # Server configuration
├── README.md                 # This file
└── requirements.txt          # Python dependencies (empty - stdlib only)
```

### Dependencies
This server uses **only Python standard library** modules for maximum compatibility and minimal setup requirements.

## 📄 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Made with ❤️ for the Claude Desktop community**
