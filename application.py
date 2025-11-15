"""
AWS Elastic Beanstalk Entry Point
This file is the WSGI entry point for AWS Elastic Beanstalk deployment.
EB looks for 'application' variable by default.
"""

from src.app import create_app
import os

# Create the Flask application instance
application = create_app()

# AWS Elastic Beanstalk expects a variable named 'application'
# This is aliased for compatibility
app = application

if __name__ == '__main__':
    # This won't be used in production (gunicorn will be used instead)
    # But useful for local testing
    port = int(os.environ.get('PORT', 5000))
    application.run(host='0.0.0.0', port=port)
