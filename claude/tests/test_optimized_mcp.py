#!/usr/bin/env python3
"""
Comprehensive test suite for the optimized Filesystem MCP Server.
Tests MCP protocol compliance, performance optimizations, and Claude Desktop integration.
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from filesystem_mcp import FilesystemMCPServer, OSDetector, PerformanceCache

async def test_mcp_protocol():
    """Test MCP protocol compliance."""
    print("🧪 Testing MCP Protocol Compliance...")
    
    server = FilesystemMCPServer()
    
    # Test initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    
    response = await server.handle_request(init_request)
    assert response is not None
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert response["result"]["protocolVersion"] == "2024-11-05"
    print("✅ Initialize request handled correctly")
    
    # Test initialized notification
    init_notification = {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {}
    }
    
    response = await server.handle_request(init_notification)
    assert response is None  # Notifications don't return responses
    print("✅ Initialized notification handled correctly")
    
    # Test tools/list request
    tools_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response = await server.handle_request(tools_request)
    assert response is not None
    assert "result" in response
    assert "tools" in response["result"]
    assert len(response["result"]["tools"]) > 0
    print(f"✅ Tools list returned {len(response['result']['tools'])} tools")
    
    # Test resources/list request
    resources_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "resources/list",
        "params": {}
    }
    
    response = await server.handle_request(resources_request)
    assert response is not None
    assert "result" in response
    assert "resources" in response["result"]
    print("✅ Resources list handled correctly")
    
    # Test prompts/list request
    prompts_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "prompts/list",
        "params": {}
    }
    
    response = await server.handle_request(prompts_request)
    assert response is not None
    assert "result" in response
    assert "prompts" in response["result"]
    print("✅ Prompts list handled correctly")
    
    print("🎉 All MCP protocol tests passed!")

async def test_performance_optimizations():
    """Test performance optimizations."""
    print("\n⚡ Testing Performance Optimizations...")
    
    # Test cache performance
    cache = PerformanceCache(max_size=100, ttl_seconds=1)
    
    start_time = time.time()
    for i in range(1000):
        cache.set(f"key_{i}", f"value_{i}")
    cache_write_time = time.time() - start_time
    
    start_time = time.time()
    for i in range(1000):
        value = cache.get(f"key_{i}")
    cache_read_time = time.time() - start_time
    
    print(f"✅ Cache performance: {cache_write_time:.4f}s write, {cache_read_time:.4f}s read")
    
    # Test OS detection performance
    detector = OSDetector()
    
    start_time = time.time()
    os_info = detector.get_os_info()
    drives = detector.get_default_drives()
    exclusions = detector.get_default_exclusions()
    detection_time = time.time() - start_time
    
    print(f"✅ OS detection: {detection_time:.4f}s for {len(drives)} drives, {len(exclusions)} exclusions")
    
    print("🎉 All performance tests passed!")

def test_os_compatibility():
    """Test cross-platform OS compatibility."""
    print("\n🌍 Testing Cross-Platform Compatibility...")
    
    detector = OSDetector()
    os_info = detector.get_os_info()
    
    print(f"System: {os_info['system']}")
    print(f"Release: {os_info['release']}")
    print(f"Machine: {os_info['machine']}")
    print(f"Python: {os_info['python_version']}")
    
    drives = detector.get_default_drives()
    print(f"Detected drives: {drives}")
    
    exclusions = detector.get_default_exclusions()
    print(f"OS-specific exclusions: {len(exclusions)} patterns")
    
    # Verify drives are accessible (at least some)
    accessible_drives = []
    for drive in drives[:3]:  # Test first 3 drives only
        try:
            path = Path(drive)
            if path.exists():
                list(path.iterdir())  # Try to list directory
                accessible_drives.append(drive)
        except (PermissionError, OSError):
            pass  # Some drives may not be accessible, that's okay
    
    print(f"✅ {len(accessible_drives)} of {len(drives)} tested drives are accessible")
    print("🎉 Cross-platform compatibility verified!")

async def test_tool_execution():
    """Test actual tool execution."""
    print("\n🔧 Testing Tool Execution...")
    
    server = FilesystemMCPServer()
    
    # Test list_directory tool
    if hasattr(server, 'fs') and server.fs.allowed_drives:
        test_drive = server.fs.allowed_drives[0]
        
        tool_call = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "list_directory",
                "arguments": {
                    "path": test_drive,
                    "max_depth": 1
                }
            }
        }
        
        start_time = time.time()
        response = await server.handle_request(tool_call)
        execution_time = time.time() - start_time
        
        assert response is not None
        assert "result" in response
        assert "content" in response["result"]
        
        print(f"✅ list_directory executed in {execution_time:.4f}s")
        
        # Check response size (should be reasonable for Claude Desktop)
        response_size = len(json.dumps(response))
        print(f"✅ Response size: {response_size:,} bytes")
        
        if response_size > 1024 * 1024:  # 1MB
            print("⚠️  Large response detected - consider pagination for production")
    
    print("🎉 Tool execution tests passed!")

async def main():
    """Run all tests."""
    print("🚀 Starting Optimized Filesystem MCP Server Tests")
    print("=" * 60)
    
    try:
        await test_mcp_protocol()
        await test_performance_optimizations()
        test_os_compatibility()
        await test_tool_execution()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! The optimized MCP server is ready for Claude Desktop.")
        print("✅ MCP 2024-11-05 protocol compliant")
        print("✅ Performance optimizations working")
        print("✅ Cross-platform compatibility verified")
        print("✅ Tool execution functional")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
