"""
Main entry point for Railway deployment.
This file is required for Railway to properly detect and start the Flask application.
"""

import os
from src.server import create_app

# Create the Flask app
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get("PORT", 8080))
    
    # Run the Flask app
    # Note: In production, Gunicorn will be used instead (see Procfile)
    app.run(host="0.0.0.0", port=port, debug=False)
