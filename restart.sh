#!/bin/bash
# restart.sh — stop the uvicorn server, wipe the DB, and restart

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Stop any running uvicorn instance
pkill -f "uvicorn main:app" 2>/dev/null && echo "Server stopped." || echo "No running server found."

# Delete the database
rm -f todos.db
echo "todos.db deleted."

# Activate venv and start server
source .venv/bin/activate
echo "Starting server..."
uvicorn main:app --reload --host 127.0.0.1 --port 8000
