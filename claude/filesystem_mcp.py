#!/usr/bin/env python3
"""
Enhanced Filesystem MCP Server for Claude Desktop

A high-performance, cross-platform filesystem Model Context Protocol server 
with advanced features and optimizations.

Features:
- Cross-platform support (Windows, macOS, Linux)
- Optimized file operations with caching
- Advanced search with regex and content matching
- Parallel operations for better performance
- Enhanced security and path validation
- Comprehensive logging and error handling
- Smart exclusions based on OS
"""

import json
import os
import sys
import platform
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Set
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import logging
import fnmatch
import stat
import re
import mimetypes
import hashlib
from functools import lru_cache

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('filesystem_mcp.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class OSDetector:
    """Cross-platform OS detection and configuration."""
    
    @staticmethod
    def get_os_info() -> Dict[str, Any]:
        """Get comprehensive OS information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version()
        }
    
    @staticmethod
    def get_default_drives() -> List[str]:
        """Get default drives/mount points based on OS."""
        system = platform.system()
        if system == "Windows":
            drives = []
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{letter}:"
                if os.path.exists(f"{drive}\\"):
                    drives.append(drive)
            return drives or ['C:', 'D:']  # Fallback
        elif system == "Darwin":  # macOS
            return ["/", "/Users", "/Applications", "/Volumes"]
        else:  # Linux and others
            return ["/", "/home", "/mnt", "/media"]
    
    @staticmethod
    def get_default_exclusions() -> List[str]:
        """Get OS-specific default exclusions."""
        system = platform.system()
        
        base_exclusions = [
            "*/.*",  # Hidden files/folders
            "*/__pycache__/*",
            "*/node_modules/*", 
            "*/.git/*",
            "*/.svn/*",
            "*/temp/*",
            "*/tmp/*",
            "*/cache/*",
            "*/Cache/*"
        ]
        
        if system == "Windows":
            windows_exclusions = [
                "C:\\Windows\\*",
                "C:\\Program Files\\*",
                "C:\\Program Files (x86)\\*",
                "C:\\ProgramData\\*",
                "C:\\System Volume Information\\*",
                "C:\\$Recycle.Bin\\*",
                "C:\\Recovery\\*",
                "*\\AppData\\Local\\Temp\\*",
                "*\\Microsoft\\*",
                "*\\Intel\\*",
                "*\\NVIDIA\\*"
            ]
            return base_exclusions + windows_exclusions
        elif system == "Darwin":  # macOS
            macos_exclusions = [
                "/System/*",
                "/Library/Application Support/*",
                "/private/*",
                "/usr/bin/*",
                "/usr/sbin/*",
                "/Applications/*.app/Contents/*",
                "*/Library/Caches/*",
                "*/Library/Logs/*",
                "*/.Trash/*",
                "/cores/*"
            ]
            return base_exclusions + macos_exclusions
        else:  # Linux
            linux_exclusions = [
                "/proc/*",
                "/sys/*",
                "/dev/*",
                "/boot/*",
                "/usr/bin/*",
                "/usr/sbin/*",
                "/var/log/*",
                "/var/cache/*"
            ]
            return base_exclusions + linux_exclusions

class PerformanceCache:
    """Simple LRU cache for performance optimization."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self.cache = {}
        self.access_times = {}
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self.cache:
                # Check TTL
                if time.time() - self.access_times[key] < self.ttl:
                    self.access_times[key] = time.time()
                    return self.cache[key]
                else:
                    # Expired
                    del self.cache[key]
                    del self.access_times[key]
            return None
    
    def set(self, key: str, value: Any):
        with self._lock:
            # Clean up if at max size
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
            
            self.cache[key] = value
            self.access_times[key] = time.time()
    
    def clear(self):
        with self._lock:
            self.cache.clear()
            self.access_times.clear()

class MCPServer:
    """Enhanced MCP Server implementation with performance optimizations."""
    
    def __init__(self, name: str):
        self.name = name
        self.tools = []
        self.request_id = 0
        self.cache = PerformanceCache()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def add_tool(self, tool_def: Dict[str, Any]):
        """Add a tool definition."""
        self.tools.append(tool_def)
    
    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP requests."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            print(f"Handling request: {method}", file=sys.stderr)
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": self.name,
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "initialized":
                # This is a notification, no response needed
                print("Server initialized successfully", file=sys.stderr)
                return None
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.tools}
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                # Find and call the tool
                result = await self.call_tool(tool_name, arguments)
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {"content": result}
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        except Exception as e:
            print(f"Error in handle_request: {e}", file=sys.stderr)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}            }
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Override this method to handle tool calls."""
        return [{"type": "text", "text": f"Tool {name} not implemented"}]
    
    async def run_stdio(self):
        """Run the MCP server using stdio transport."""
        print("MCP Server starting...", file=sys.stderr)
        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    print("No more input, exiting...", file=sys.stderr)
                    break
                
                request = json.loads(line.strip())
                response = await self.handle_request(request)
                
                # Only send response if it's not None (some methods like 'initialized' don't need responses)
                if response is not None:
                    print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}", file=sys.stderr)
                continue
            except Exception as e:
                print(f"Error handling request: {e}", file=sys.stderr)
                logger.error(f"Error handling request: {e}")
                continue

class FilesystemMCP:
    """Enhanced Filesystem MCP Server implementation with cross-platform support."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.os_detector = OSDetector()
        self.cache = PerformanceCache()
        
        # Get OS-specific defaults
        self.os_info = self.os_detector.get_os_info()
        self.default_exclusions = self.os_detector.get_default_exclusions()
        self.allowed_drives = self.os_detector.get_default_drives()
        
        logger.info(f"Detected OS: {self.os_info['system']} {self.os_info['release']}")
        logger.info(f"Available drives/paths: {self.allowed_drives}")
        
        # Load configuration
        self.load_config()
        
        # Initialize thread pool for parallel operations
        self.executor = ThreadPoolExecutor(max_workers=6)
        
    def load_config(self):
        """Load configuration from config files."""
        exclusions_file = self.config_dir / "exclusions.json"
        settings_file = self.config_dir / "settings.json"
        
        # Load exclusions
        if exclusions_file.exists():
            try:
                with open(exclusions_file, 'r') as f:
                    config_exclusions = json.load(f)
                    self.exclusions = config_exclusions.get('patterns', self.default_exclusions)
                    logger.info(f"Loaded {len(self.exclusions)} exclusion patterns")
            except Exception as e:
                logger.warning(f"Failed to load exclusions config: {e}")
                self.exclusions = self.default_exclusions
        else:
            # Create default exclusions file
            self.exclusions = self.default_exclusions
            self.save_exclusions_config()
        
        # Load settings
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.allowed_drives = settings.get('allowed_drives', self.allowed_drives)
                    self.max_file_size = settings.get('max_file_size_mb', 10) * 1024 * 1024  # Convert to bytes
                    self.max_search_results = settings.get('max_search_results', 1000)
                    logger.info(f"Loaded settings: drives={self.allowed_drives}")
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}")
                self.max_file_size = 10 * 1024 * 1024  # 10MB default
                self.max_search_results = 1000
        else:
            self.max_file_size = 10 * 1024 * 1024  # 10MB default
            self.max_search_results = 1000
            self.save_settings_config()
    
    def save_exclusions_config(self):
        """Save exclusions configuration to file."""
        exclusions_file = self.config_dir / "exclusions.json"
        config = {
            "description": "Filesystem exclusion patterns. Use * for wildcards.",
            "patterns": self.exclusions,
            "examples": [
                "C:\\Windows\\*",
                "*\\AppData\\*",
                "*.tmp",
                "*\\node_modules\\*"
            ]
        }
        try:
            with open(exclusions_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved exclusions config to {exclusions_file}")
        except Exception as e:
            logger.error(f"Failed to save exclusions config: {e}")
    
    def save_settings_config(self):
        """Save settings configuration to file."""
        settings_file = self.config_dir / "settings.json"
        config = {
            "description": "Filesystem MCP Server Settings",
            "allowed_drives": self.allowed_drives,
            "max_file_size_mb": self.max_file_size // (1024 * 1024),
            "max_search_results": self.max_search_results
        }
        try:
            with open(settings_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved settings config to {settings_file}")
        except Exception as e:
            logger.error(f"Failed to save settings config: {e}")
    
    def is_path_allowed(self, path: Union[str, Path]) -> bool:
        """Check if a path is allowed based on exclusion patterns with cross-platform support."""
        path_str = str(Path(path).resolve())
        
        # Normalize path separators for cross-platform compatibility
        if platform.system() == "Windows":
            path_str = path_str.replace('/', '\\')
        else:
            path_str = path_str.replace('\\', '/')
        
        # Check drive/root allowlist
        is_allowed = False
        for allowed_path in self.allowed_drives:
            if path_str.startswith(allowed_path):
                is_allowed = True
                break
        
        if not is_allowed:
            return False
        
        # Check exclusion patterns
        for pattern in self.exclusions:
            if fnmatch.fnmatch(path_str, pattern):
                return False
        
        return True
    
    @lru_cache(maxsize=1000)
    def safe_path_resolve(self, path: str) -> Optional[Path]:
        """Safely resolve a path and validate it with caching."""
        try:
            resolved_path = Path(path).resolve()
            if self.is_path_allowed(resolved_path):
                return resolved_path
            return None
        except Exception as e:
            logger.warning(f"Failed to resolve path {path}: {e}")
            return None
    
    def get_file_info(self, path: Path) -> Dict[str, Any]:
        """Get comprehensive file/directory information with caching."""
        cache_key = f"file_info:{str(path)}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        try:
            stat_info = path.stat()
            
            # Get MIME type for files
            mime_type = None
            if path.is_file():
                mime_type, _ = mimetypes.guess_type(str(path))
            
            info = {
                "path": str(path),
                "name": path.name,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "size": stat_info.st_size if path.is_file() else None,
                "size_human": self.format_size(stat_info.st_size) if path.is_file() else None,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                "extension": path.suffix.lower() if path.is_file() else None,
                "mime_type": mime_type,
                "permissions": stat.filemode(stat_info.st_mode),
                "is_hidden": self._is_hidden(path, stat_info)
            }
            
            self.cache.set(cache_key, info)
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info for {path}: {e}")
            return {
                "path": str(path),
                "name": path.name,
                "error": str(e)
            }
    
    def _is_hidden(self, path: Path, stat_info) -> bool:
        """Detect if file/directory is hidden (cross-platform)."""
        # Unix-style hidden files
        if path.name.startswith('.'):
            return True
        
        # Windows hidden attribute
        if platform.system() == "Windows":
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
                return bool(attrs != -1 and attrs & 2)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
        
        return False
    
    def list_directory_parallel(self, path: Path, show_hidden: bool = False, max_items: int = 1000) -> List[Dict[str, Any]]:
        """List directory contents with parallel processing."""
        try:
            items = []
            count = 0
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                
                for item in path.iterdir():
                    if count >= max_items:
                        break
                    
                    if not show_hidden and self._is_hidden(item, None):
                        continue
                    
                    if not self.is_path_allowed(item):
                        continue
                    
                    future = executor.submit(self.get_file_info, item)
                    futures.append(future)
                    count += 1
                
                # Collect results
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=5)
                        items.append(result)
                    except Exception as e:
                        logger.warning(f"Failed to get info for item: {e}")
            
            # Sort by name
            items.sort(key=lambda x: x.get('name', '').lower())
            return items
            
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return []
    
    @staticmethod
    def format_size(size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

class FilesystemMCPServer(MCPServer):
    """Filesystem MCP Server implementation."""
    
    def __init__(self):
        super().__init__("filesystem-mcp")
        self.fs = FilesystemMCP()
        self.setup_tools()
    
    def setup_tools(self):
        """Setup all available tools."""
        tools = [
            {
                "name": "list_directory",
                "description": "List contents of a directory with detailed file information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path to list (e.g., 'C:\\', 'D:\\Documents')"
                        },
                        "show_hidden": {
                            "type": "boolean",
                            "description": "Include hidden files and directories",
                            "default": False
                        },
                        "recursive": {
                            "type": "boolean", 
                            "description": "List subdirectories recursively",
                            "default": False
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum recursion depth (only used with recursive=true)",
                            "default": 3
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "read_file",
                "description": "Read the contents of a text file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Full path to the file to read"
                        },
                        "encoding": {
                            "type": "string", 
                            "description": "File encoding (default: utf-8)",
                            "default": "utf-8"
                        },
                        "max_lines": {
                            "type": "integer",
                            "description": "Maximum number of lines to read (0 = all)",
                            "default": 0
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "search_files",
                "description": "Search for files and directories by name pattern",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "Search pattern (supports wildcards like *.py, test*, etc.)"
                        },
                        "root_path": {
                            "type": "string",
                            "description": "Root directory to search from (default: C:\\)",
                            "default": "C:\\"
                        },
                        "file_types": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Filter by file extensions (e.g., ['.py', '.txt'])"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 100
                        }
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "get_file_info",
                "description": "Get detailed information about a specific file or directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Full path to the file or directory"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "find_large_files",
                "description": "Find large files above a specified size threshold",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "root_path": {
                            "type": "string",
                            "description": "Root directory to search from",
                            "default": "C:\\"
                        },
                        "min_size_mb": {
                            "type": "number",
                            "description": "Minimum file size in MB",
                            "default": 100
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 50
                        }
                    },
                    "required": ["root_path"]
                }
            },
            {
                "name": "get_drive_info",
                "description": "Get information about available drives and their usage",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]
        
        for tool in tools:
            self.add_tool(tool)
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle tool calls."""
        try:
            if name == "list_directory":
                return await self.handle_list_directory(arguments)
            elif name == "read_file":
                return await self.handle_read_file(arguments)
            elif name == "search_files":
                return await self.handle_search_files(arguments)
            elif name == "get_file_info":
                return await self.handle_get_file_info(arguments)
            elif name == "find_large_files":
                return await self.handle_find_large_files(arguments)
            elif name == "get_drive_info":
                return await self.handle_get_drive_info(arguments)
            else:
                return [{"type": "text", "text": f"Unknown tool: {name}"}]
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return [{"type": "text", "text": f"Error: {str(e)}"}]

    async def handle_list_directory(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle directory listing."""
        path_str = arguments["path"]
        show_hidden = arguments.get("show_hidden", False)
        recursive = arguments.get("recursive", False)
        max_depth = arguments.get("max_depth", 3)
        
        path = self.fs.safe_path_resolve(path_str)
        if not path:
            return [{"type": "text", "text": f"Path not allowed or invalid: {path_str}"}]
        
        if not path.exists():
            return [{"type": "text", "text": f"Path does not exist: {path}"}]
        
        if not path.is_dir():
            return [{"type": "text", "text": f"Path is not a directory: {path}"}]
        
        def list_dir_recursive(current_path: Path, current_depth: int = 0) -> List[Dict[str, Any]]:
            items = []
            if current_depth > max_depth:
                return items
            
            try:
                for item in current_path.iterdir():
                    if not show_hidden and item.name.startswith('.'):
                        continue
                    
                    if not self.fs.is_path_allowed(item):
                        continue
                    
                    file_info = self.fs.get_file_info(item)
                    file_info["depth"] = current_depth
                    items.append(file_info)
                    
                    if recursive and item.is_dir() and current_depth < max_depth:
                        items.extend(list_dir_recursive(item, current_depth + 1))
            except PermissionError:
                items.append({
                    "path": str(current_path),
                    "name": current_path.name,
                    "error": "Permission denied",
                    "depth": current_depth
                })
            except Exception as e:
                items.append({
                    "path": str(current_path),
                    "name": current_path.name,
                    "error": str(e),
                    "depth": current_depth
                })
            
            return items
        
        items = list_dir_recursive(path)
        
        # Format output
        result = f"Directory listing for: {path}\n"
        result += f"Found {len(items)} items\n\n"
        
        for item in items:
            indent = "  " * item.get("depth", 0)
            if "error" in item:
                result += f"{indent}❌ {item['name']} - {item['error']}\n"
            elif item.get("is_dir"):
                result += f"{indent}📁 {item['name']}/\n"
            else:
                size = item.get("size_human", "")
                ext = item.get("extension", "")
                result += f"{indent}📄 {item['name']} {size} {ext}\n"
        
        return [{"type": "text", "text": result}]

    async def handle_read_file(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle file reading."""
        path_str = arguments["path"]
        encoding = arguments.get("encoding", "utf-8")
        max_lines = arguments.get("max_lines", 0)
        
        path = self.fs.safe_path_resolve(path_str)
        if not path:
            return [{"type": "text", "text": f"Path not allowed or invalid: {path_str}"}]
        
        if not path.exists():
            return [{"type": "text", "text": f"File does not exist: {path}"}]
        
        if not path.is_file():
            return [{"type": "text", "text": f"Path is not a file: {path}"}]
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > self.fs.max_file_size:
            size_mb = file_size / (1024 * 1024)
            max_mb = self.fs.max_file_size / (1024 * 1024)
            return [{"type": "text", "text": f"File too large: {size_mb:.1f}MB (max: {max_mb:.1f}MB)"}]
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                if max_lines > 0:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            break
                        lines.append(line.rstrip())
                    content = '\n'.join(lines)
                    if i >= max_lines - 1:
                        content += f"\n\n... (truncated to {max_lines} lines)"
                else:
                    content = f.read()
            
            result = f"File: {path}\n"
            result += f"Size: {self.fs.format_size(file_size)}\n"
            result += f"Encoding: {encoding}\n"
            result += "=" * 50 + "\n"
            result += content
            
            return [{"type": "text", "text": result}]
        
        except UnicodeDecodeError as e:
            return [{"type": "text", "text": f"Encoding error reading file with {encoding}: {e}"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error reading file: {e}"}]

    async def handle_search_files(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle file searching."""
        pattern = arguments["pattern"]
        root_path_str = arguments.get("root_path", "C:\\")
        file_types = arguments.get("file_types", [])
        max_results = min(arguments.get("max_results", 100), self.fs.max_search_results)
        
        root_path = self.fs.safe_path_resolve(root_path_str)
        if not root_path:
            return [{"type": "text", "text": f"Root path not allowed or invalid: {root_path_str}"}]
        
        if not root_path.exists():
            return [{"type": "text", "text": f"Root path does not exist: {root_path}"}]
        
        results = []
        
        def search_recursive(current_path: Path, depth: int = 0):
            if len(results) >= max_results or depth > 10:  # Limit search depth
                return
            
            try:
                for item in current_path.iterdir():
                    if len(results) >= max_results:
                        break
                    
                    if not self.fs.is_path_allowed(item):
                        continue
                    
                    # Check if name matches pattern
                    if fnmatch.fnmatch(item.name.lower(), pattern.lower()):
                        # Check file type filter
                        if file_types and item.is_file():
                            if not any(item.suffix.lower() == ext.lower() for ext in file_types):
                                continue
                        
                        results.append(self.fs.get_file_info(item))
                    
                    # Recurse into directories
                    if item.is_dir():  
                        search_recursive(item, depth + 1)
            
            except PermissionError:
                pass  # Skip directories we can't access
            except Exception as e:
                logger.warning(f"Error searching in {current_path}: {e}")
        
        search_recursive(root_path)
        
        # Format results
        result_text = f"Search results for pattern: {pattern}\n"
        result_text += f"Root path: {root_path}\n"
        if file_types:
            result_text += f"File types: {', '.join(file_types)}\n"
        result_text += f"Found {len(results)} matches\n\n"
        
        for item in results:
            if item.get("is_dir"):
                result_text += f"📁 {item['path']}\n"
            else:
                size = item.get("size_human", "")
                result_text += f"📄 {item['path']} ({size})\n"
        
        if len(results) >= max_results:
            result_text += f"\n... (truncated to {max_results} results)"
        
        return [{"type": "text", "text": result_text}]

    async def handle_get_file_info(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle file info retrieval."""
        path_str = arguments["path"]
        
        path = self.fs.safe_path_resolve(path_str)
        if not path:
            return [{"type": "text", "text": f"Path not allowed or invalid: {path_str}"}]
        
        if not path.exists():
            return [{"type": "text", "text": f"Path does not exist: {path}"}]
        
        info = self.fs.get_file_info(path)
        
        if "error" in info:
            return [{"type": "text", "text": f"Error getting file info: {info['error']}"}]
        
        result = f"File Information for: {info['path']}\n"
        result += "=" * 50 + "\n"
        result += f"Name: {info['name']}\n"
        result += f"Type: {'Directory' if info['is_dir'] else 'File'}\n"
        
        if info.get('size') is not None:
            result += f"Size: {info['size_human']} ({info['size']:,} bytes)\n"
        
        result += f"Modified: {info['modified']}\n"
        result += f"Created: {info['created']}\n"
        result += f"Permissions: {info['permissions']}\n"
        
        if info.get('extension'):
            result += f"Extension: {info['extension']}\n"
        
        return [{"type": "text", "text": result}]

    async def handle_find_large_files(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle finding large files."""
        root_path_str = arguments.get("root_path", "C:\\")
        min_size_mb = arguments.get("min_size_mb", 100)
        max_results = arguments.get("max_results", 50)
        
        min_size_bytes = int(min_size_mb * 1024 * 1024)
        
        root_path = self.fs.safe_path_resolve(root_path_str)
        if not root_path:
            return [{"type": "text", "text": f"Root path not allowed or invalid: {root_path_str}"}]
        
        large_files = []
        
        def find_large_recursive(current_path: Path, depth: int = 0):
            if len(large_files) >= max_results or depth > 8:
                return
            
            try:
                for item in current_path.iterdir():
                    if len(large_files) >= max_results:
                        break
                    
                    if not self.fs.is_path_allowed(item):
                        continue
                    
                    if item.is_file():
                        try:
                            size = item.stat().st_size
                            if size >= min_size_bytes:
                                large_files.append(self.fs.get_file_info(item))
                        except Exception:
                            pass  # Skip files we can't stat
                    elif item.is_dir():
                        find_large_recursive(item, depth + 1)
            
            except PermissionError:
                pass
            except Exception as e:
                logger.warning(f"Error searching for large files in {current_path}: {e}")
        
        find_large_recursive(root_path)
        
        # Sort by size (largest first)
        large_files.sort(key=lambda x: x.get('size', 0), reverse=True)
        
        result_text = f"Large files (>= {min_size_mb}MB) in: {root_path}\n"
        result_text += f"Found {len(large_files)} large files\n\n"
        
        for file_info in large_files:
            result_text += f"📄 {file_info['path']}\n"
            result_text += f"   Size: {file_info['size_human']}\n"
            result_text += f"   Modified: {file_info['modified']}\n\n"
        
        return [{"type": "text", "text": result_text}]

    async def handle_get_drive_info(self, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle drive information retrieval."""
        import shutil
        
        result = "Drive Information\n"
        result += "=" * 30 + "\n\n"
        
        for drive in self.fs.allowed_drives:
            drive_path = f"{drive}\\"
            try:
                if Path(drive_path).exists():
                    total, used, free = shutil.disk_usage(drive_path)
                    
                    result += f"Drive {drive}\n"
                    result += f"  Total: {self.fs.format_size(total)}\n"
                    result += f"  Used:  {self.fs.format_size(used)} ({used/total*100:.1f}%)\n"
                    result += f"  Free:  {self.fs.format_size(free)} ({free/total*100:.1f}%)\n\n"
                else:
                    result += f"Drive {drive}: Not available\n\n"
            except Exception as e:
                result += f"Drive {drive}: Error - {e}\n\n"
        
        return [{"type": "text", "text": result}]

async def main():
    """Main entry point for the MCP server."""
    logger.info("Starting Filesystem MCP Server")
    
    server = FilesystemMCPServer()
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
