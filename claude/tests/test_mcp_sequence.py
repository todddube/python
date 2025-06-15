#!/usr/bin/env python3
"""
Test the MCP server with a complete initialization sequence.
"""

import subprocess
import json
import sys
import time

def test_mcp_server():
    """Test the MCP server with proper initialization sequence."""
      # Start the server process
    process = subprocess.Popen(
        [sys.executable, "../filesystem_mcp.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="."
    )
    
    print("Testing MCP server initialization sequence...")
    
    try:
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("1. Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline().strip()
        if response:
            init_response = json.loads(response)
            print(f"   Initialize response: {init_response}")
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        }
        
        print("2. Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Step 3: List tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("3. Sending tools/list request...")
        process.stdin.write(json.dumps(list_tools_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline().strip()
        if response:
            tools_response = json.loads(response)
            print(f"   Tools list response: Found {len(tools_response.get('result', {}).get('tools', []))} tools")
            for tool in tools_response.get('result', {}).get('tools', []):
                print(f"     - {tool['name']}: {tool['description']}")
        
        # Step 4: Test a simple tool call
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_drive_info",
                "arguments": {}
            }
        }
        
        print("4. Testing get_drive_info tool...")
        process.stdin.write(json.dumps(tool_call_request) + "\n")
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline().strip()
        if response:
            tool_response = json.loads(response)
            print(f"   Tool call response: {tool_response}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {e}")
        # Read any stderr output
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Server stderr: {stderr_output}")
    
    finally:
        # Clean up
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    test_mcp_server()
