#!/usr/bin/env python3
"""
Production Database Initialization Script for AWS Elastic Beanstalk
This script ensures the database is initialized on deployment.
"""

import os

def init_database():
    """
    Initialize database on first deployment.

    The Flask application will automatically create the database
    when it starts if it doesn't exist, so this script simply
    triggers the app initialization.
    """
    db_path = os.environ.get('DATABASE_PATH', 'campus_resource_hub.db')

    if os.path.exists(db_path):
        print(f"✓ Database already exists at {db_path}")
        return

    print(f"Database not found at {db_path}")
    print("The Flask app will create it automatically on first request.")
    print("To pre-initialize, run: python3 -c 'from src.app import create_app; app = create_app(); app.app_context().push()'")

if __name__ == '__main__':
    init_database()
