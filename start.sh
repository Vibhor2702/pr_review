#!/bin/bash
# Railway Start Script for PR Review Agent

echo "Starting PR Review Agent Backend..."
echo "Python version: $(python --version)"
echo "Gunicorn version: $(gunicorn --version)"
echo "Port: $PORT"

# Start the Flask application with Gunicorn
exec gunicorn \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  main:app
