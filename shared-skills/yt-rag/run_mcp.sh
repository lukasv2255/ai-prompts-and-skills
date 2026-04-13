#!/bin/bash
# Wrapper pro MCP server — načte .env a spustí server
set -a
source "$(dirname "$0")/.env"
set +a
exec /opt/homebrew/bin/python3 "$(dirname "$0")/mcp_server.py"
