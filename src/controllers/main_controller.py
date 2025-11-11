"""
Campus Resource Hub - Main Controller
=====================================
MVC Role: Controller for homepage and general routes
MCP Role: Entry point for user interactions

Handles:
- Homepage (/)
- About page
- Search functionality
- General navigation
"""

import sys
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user

# Create blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Homepage route.

    Displays:
    - If logged in: Home page with search, stats, categories
    - If not logged in: Redirect to login page

    Returns:
        HTML: Rendered homepage template or redirect to login
    """
    # Check if user is authenticated
    print(f"DEBUG: current_user.is_authenticated = {current_user.is_authenticated}", file=sys.stderr, flush=True)
    if current_user.is_authenticated:
        print(f"DEBUG: Rendering home/home.html for user {current_user.email}", file=sys.stderr, flush=True)
        return render_template('home/home.html',
                              title='Home',
                              page='home')
    else:
        # Redirect unauthenticated users to login page
        print("DEBUG: Redirecting anonymous user to login", file=sys.stderr, flush=True)
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))


@main_bp.route('/about')
def about():
    """
    About page route.

    Returns:
        HTML: Rendered about page
    """
    return render_template('about.html',
                          title='About',
                          page='about')


@main_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        JSON: Application health status
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Campus Resource Hub',
        'version': '1.0.0'
    })


@main_bp.route('/search')
def search():
    """
    Search functionality.

    Query Parameters:
        q (str): Search query
        category (str): Filter by category
        location (str): Filter by location
        date (str): Filter by availability date

    Returns:
        HTML: Search results page

    TODO: Implement actual search logic with ResourceDAL
    """
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    date = request.args.get('date', '')

    # TODO: Implement search with ResourceDAL
    # from src.data_access.resource_dal import ResourceDAL
    # results = ResourceDAL.search_resources(query, category, location, date)

    return render_template('search_results.html',
                          title='Search Results',
                          query=query,
                          results=[])  # Placeholder
