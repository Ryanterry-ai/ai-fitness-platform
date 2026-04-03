#!/bin/bash
# Website Cloner AI System - Run Script for Linux/Mac

echo "Starting Website Cloner AI System..."
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start server
echo ""
echo "Starting server on http://localhost:10000"
echo ""
echo "Access the application:"
echo "  - Main App: http://localhost:10000"
echo "  - Admin Panel: http://localhost:10000/admin"
echo "  - API Docs: http://localhost:10000/docs"
echo ""
echo "Default login: admin@admin.com / admin123"
echo ""

python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 10000
