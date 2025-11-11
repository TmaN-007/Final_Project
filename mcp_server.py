"""
MCP Server for Campus Resource Hub
===================================
Provides AI context for the Flask application.

This server exposes project structure, patterns, and metadata
to AI assistants for better code understanding and generation.
"""

import json
import os
from pathlib import Path


def get_project_context():
    """
    Return comprehensive project context for AI assistants.
    """
    project_root = Path(__file__).parent

    context = {
        "project_name": "Campus Resource Hub",
        "architecture": "Flask MVC with Data Access Layer",
        "structure": {
            "controllers": list_python_files(project_root / "src" / "controllers"),
            "models": list_python_files(project_root / "src" / "models"),
            "dal": list_python_files(project_root / "src" / "data_access"),
            "templates": list_template_files(project_root / "src" / "templates"),
            "static": {
                "css": list_files(project_root / "src" / "static" / "css", "*.css"),
                "js": list_files(project_root / "src" / "static" / "js", "*.js")
            }
        },
        "database": {
            "type": "SQLite3",
            "location": "database/campus_hub.db",
            "schema": "database/schema.sql"
        },
        "security_features": [
            "CSRF Protection",
            "Password Hashing (bcrypt)",
            "Session Management",
            "XSS Protection",
            "Parameterized SQL Queries"
        ],
        "development_status": {
            "completed": [
                "Database schema and initialization",
                "User authentication (login, register)",
                "Password validation and hashing",
                "Dark/Light theme toggle",
                "Responsive authentication UI"
            ],
            "in_progress": [
                "Resource management",
                "Booking system"
            ],
            "planned": [
                "Message system",
                "Review system",
                "Admin dashboard",
                "Payment integration"
            ]
        }
    }

    return context


def list_python_files(directory):
    """List all Python files in a directory."""
    if not directory.exists():
        return []
    return [str(f.relative_to(directory.parent))
            for f in directory.glob("*.py")
            if f.name != "__init__.py"]


def list_template_files(directory):
    """List all template files organized by subdirectory."""
    if not directory.exists():
        return {}

    templates = {}
    for subdir in directory.iterdir():
        if subdir.is_dir():
            templates[subdir.name] = [
                str(f.relative_to(directory))
                for f in subdir.glob("*.html")
            ]
    return templates


def list_files(directory, pattern):
    """List files matching a pattern."""
    if not directory.exists():
        return []
    return [str(f.relative_to(directory.parent)) for f in directory.glob(pattern)]


if __name__ == "__main__":
    # Print project context in JSON format for MCP
    context = get_project_context()
    print(json.dumps(context, indent=2))
