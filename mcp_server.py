"""
MCP Server for Campus Resource Hub
===================================
Model Context Protocol integration for AI-assisted development.

This server provides:
1. Project structure and metadata
2. Read-only database queries for AI context
3. Schema introspection
4. Safe data summaries for intelligent search

Security: All database operations are READ-ONLY.
"""

import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional


class MCPDatabaseServer:
    """
    MCP Server with safe, read-only database access.

    Enables AI agents to query database content for:
    - Intelligent search suggestions
    - Data summaries
    - Schema exploration
    - Context-aware responses
    """

    def __init__(self, db_path: str = "campus_resource_hub.db"):
        """
        Initialize MCP server.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.project_root = Path(__file__).parent

    def get_connection(self) -> sqlite3.Connection:
        """
        Get read-only database connection.

        Returns:
            SQLite connection in read-only mode
        """
        # Open in read-only mode (URI format)
        db_uri = f"file:{self.db_path}?mode=ro"
        conn = sqlite3.connect(db_uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            List of column definitions
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            conn.close()

            return [
                {
                    "name": col["name"],
                    "type": col["type"],
                    "nullable": not col["notnull"],
                    "primary_key": bool(col["pk"])
                }
                for col in columns
            ]
        except Exception as e:
            return []

    def get_all_tables(self) -> List[str]:
        """
        Get list of all tables in database.

        Returns:
            List of table names
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table'
                ORDER BY name
            """)
            tables = [row["name"] for row in cursor.fetchall()]
            conn.close()
            return tables
        except Exception as e:
            return []

    def get_table_count(self, table_name: str) -> int:
        """
        Get row count for a table.

        Args:
            table_name: Name of the table

        Returns:
            Number of rows
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()["count"]
            conn.close()
            return count
        except Exception as e:
            return 0

    def query_safe(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a safe, read-only query.

        Args:
            query: SQL SELECT query
            params: Query parameters

        Returns:
            Query results as list of dicts

        Security:
            - Only SELECT queries allowed
            - Parameterized queries only
            - Read-only connection
        """
        # Security check: only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")

        # Block dangerous SQL keywords
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Keyword '{keyword}' not allowed in MCP queries")

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()

            # Convert to list of dicts
            return [dict(row) for row in results]
        except Exception as e:
            return []

    def get_resource_summary(self) -> Dict[str, Any]:
        """
        Get summary of resources for AI context.

        Returns:
            Dict with resource statistics
        """
        return {
            "total_resources": self.get_table_count("resources"),
            "published_resources": self.query_safe(
                "SELECT COUNT(*) as count FROM resources WHERE status = 'published'",
                ()
            )[0]["count"] if self.query_safe("SELECT COUNT(*) as count FROM resources WHERE status = 'published'") else 0,
            "categories": self.query_safe(
                "SELECT category_id, name FROM categories ORDER BY name",
                ()
            ),
            "total_bookings": self.get_table_count("bookings"),
            "total_users": self.get_table_count("users")
        }

    def get_project_context(self) -> Dict[str, Any]:
        """
        Get comprehensive project context for AI assistants.

        Returns:
            Dict with project metadata, structure, and database info
        """
        context = {
            "project_name": "Campus Resource Hub",
            "architecture": "Flask MVC with Data Access Layer (DAL)",
            "mcp_version": "1.0.0",
            "mcp_features": [
                "Read-only database queries",
                "Schema introspection",
                "Data summaries",
                "Project structure metadata"
            ],
            "structure": {
                "controllers": self._list_python_files(self.project_root / "src" / "controllers"),
                "models": self._list_python_files(self.project_root / "src" / "models"),
                "dal": self._list_python_files(self.project_root / "src" / "data_access"),
                "templates": self._list_template_files(self.project_root / "src" / "templates"),
                "forms": self._list_python_files(self.project_root / "src" / "forms"),
                "utils": self._list_python_files(self.project_root / "src" / "utils"),
                "static": {
                    "css": self._list_files(self.project_root / "src" / "static" / "css", "*.css"),
                    "js": self._list_files(self.project_root / "src" / "static" / "js", "*.js")
                }
            },
            "database": {
                "type": "SQLite3",
                "location": self.db_path,
                "mode": "read-only (MCP)",
                "tables": self.get_all_tables(),
                "table_count": len(self.get_all_tables()),
                "summary": self.get_resource_summary()
            },
            "security_features": [
                "CSRF Protection (Flask-WTF)",
                "Password Hashing (Werkzeug bcrypt)",
                "Session Management (Flask-Login)",
                "XSS Protection (Bleach + Jinja2 escaping)",
                "SQL Injection Prevention (Parameterized queries)",
                "File Upload Validation",
                "Input Sanitization (validators.py)",
                "Path Traversal Prevention"
            ],
            "development_status": {
                "completed": [
                    "Database schema (30 tables)",
                    "User authentication & authorization",
                    "Resource management (CRUD)",
                    "Booking system with calendar",
                    "Messaging system",
                    "Review & rating system",
                    "Admin panel",
                    "Dark/Light theme toggle",
                    "System notifications",
                    "Security hardening"
                ],
                "in_progress": [],
                "planned": [
                    "AI concierge feature",
                    "Advanced analytics"
                ]
            }
        }

        return context

    def _list_python_files(self, directory: Path) -> List[str]:
        """List all Python files in a directory."""
        if not directory.exists():
            return []
        return [str(f.relative_to(directory.parent))
                for f in directory.glob("*.py")
                if f.name != "__init__.py"]

    def _list_template_files(self, directory: Path) -> Dict[str, List[str]]:
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

    def _list_files(self, directory: Path, pattern: str) -> List[str]:
        """List files matching a pattern."""
        if not directory.exists():
            return []
        return [str(f.relative_to(directory.parent)) for f in directory.glob(pattern)]


def main():
    """
    Main entry point for MCP server.

    Provides JSON output for AI tool integration.
    """
    server = MCPDatabaseServer()

    # Get full context
    context = server.get_project_context()

    # Pretty print for debugging
    print(json.dumps(context, indent=2))

    # Example queries (for testing)
    if os.getenv("MCP_DEBUG"):
        print("\n=== MCP Database Queries ===")

        # Example: Get categories
        categories = server.query_safe("SELECT * FROM categories LIMIT 5")
        print(f"\nCategories: {json.dumps(categories, indent=2)}")

        # Example: Get schema
        schema = server.get_table_schema("resources")
        print(f"\nResources schema: {json.dumps(schema, indent=2)}")


if __name__ == "__main__":
    main()
