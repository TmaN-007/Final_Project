#!/usr/bin/env python3
"""
Campus Resource Hub - Application Entry Point
=============================================
This is the main entry point for running the Flask application.

Usage:
    python run.py                    # Run with default (development) config
    FLASK_ENV=production python run.py  # Run in production mode

    Or use Flask CLI:
    flask run                        # Development server
    flask run --host=0.0.0.0        # Accessible from network
"""

import os
from src.app import create_app

# Create application instance
# Uses FLASK_ENV environment variable to determine configuration
# Defaults to 'development' if not set
app = create_app(os.environ.get('FLASK_ENV'))

if __name__ == '__main__':
    # Get configuration from environment
    host = os.environ.get('FLASK_RUN_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    debug = app.config.get('DEBUG', True)

    print("=" * 60)
    print("🎓 Campus Resource Hub - Starting...")
    print("=" * 60)
    print(f"Environment: {app.config.get('ENV', 'development')}")
    print(f"Debug Mode: {debug}")
    print(f"Running on: http://{host}:{port}")
    print("=" * 60)
    print("\nPress CTRL+C to stop the server\n")

    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug
    )
