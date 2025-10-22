#!/usr/bin/env python3
"""
Test script per verificare che il server MCP funzioni correttamente
"""

import asyncio
import json
from server import app, list_tools, call_tool

async def test_server():
    print("🧪 Testing PCOS Care MCP Server...")
    print("=" * 50)
    
    # Test 1: Lista tools
    print("\n📋 Test 1: Listing available tools...")
    tools = await list_tools()
    print(f"✅ Found {len(tools)} tool(s):")
    for tool in tools:
        print(f"   - {tool.name}: {tool.description}")
    
    # Test 2: Chiama il tool hello_pcos
    print("\n🔧 Test 2: Calling 'hello_pcos' tool...")
    result = await call_tool(
        name="hello_pcos",
        arguments={"name": "Alice"}
    )
    print("✅ Tool response:")
    print(result[0].text)
    
    print("\n" + "=" * 50)
    print("✅ Tutti i test passati! Il server funziona correttamente.")
    print("\nProssimi passi:")
    print("1. Testa con MCP Inspector: ./test_with_inspector.sh")
    print("2. Connetti a Claude Desktop")
    print("3. Implementa il tool track_symptom()")

if __name__ == "__main__":
    asyncio.run(test_server())
