#!/bin/bash
# Start the Pinterest Style Matcher backend server

export PYTHONPATH=/workspaces/shopper

echo "🚀 Starting Pinterest Style Matcher API..."
echo "📍 Server: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python -m backend.main
