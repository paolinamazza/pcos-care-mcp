#!/bin/bash

echo "🔍 Testing PCOS Care MCP Server with MCP Inspector..."
echo ""
echo "Questo aprirà MCP Inspector nel browser."
echo "Potrai:"
echo "  - Vedere i tools disponibili"
echo "  - Testare il tool 'hello_pcos'"
echo "  - Vedere i log del server"
echo ""

cd /home/claude/pcos-care-mcp
mcp-inspector python3 server.py
