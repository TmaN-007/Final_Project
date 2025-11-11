"""
Campus Resource Hub - Base Data Access Layer
============================================
MVC Role: Foundation for all data access operations
MCP Role: Database connection management for AI-assisted queries

This module provides base functionality for all DAL classes including:
- Database connection management
- Common CRUD operations
- Transaction handling
- Error handling
- Query logging

All DAL classes should inherit from BaseDAL.
"""

import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseDAL:
    """
    Base Data Access Layer class.

    Provides common database operations and connection management.
    All specific DAL classes (UserDAL, ResourceDAL, etc.) should inherit from this.

    Attributes:
        db_path (str): Path to SQLite database file
    """

    # Class-level database path (can be overridden for testing)
    _db_path: Optional[str] = None

    @classmethod
    def set_db_path(cls, db_path: str):
        """
        Set the database path for all DAL operations.

        Args:
            db_path (str): Path to SQLite database file

        Note:
            This is typically set in config.py and should be called
            during application initialization.
        """
        cls._db_path = db_path

    @classmethod
    def get_db_path(cls) -> str:
        """
        Get the current database path.

        Returns:
            str: Path to SQLite database file

        Raises:
            ValueError: If database path not set
        """
        if cls._db_path is None:
            # Default to database in project root
            base_dir = Path(__file__).parent.parent.parent
            cls._db_path = str(base_dir / 'campus_resource_hub.db')

        return cls._db_path

    @classmethod
    @contextmanager
    def get_connection(cls, commit: bool = False):
        """
        Context manager for database connections.

        Handles connection lifecycle:
        - Opens connection
        - Executes code block
        - Commits if requested
        - Closes connection
        - Handles errors

        Args:
            commit (bool): Whether to commit transaction on success

        Yields:
            sqlite3.Connection: Database connection

        Example:
            >>> with BaseDAL.get_connection(commit=True) as conn:
            ...     cursor = conn.cursor()
            ...     cursor.execute("INSERT INTO users ...")
        """
        conn = None
        try:
            conn = sqlite3.connect(cls.get_db_path())
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            yield conn

            if commit:
                conn.commit()

        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            if conn:
                conn.rollback()
            raise

        finally:
            if conn:
                conn.close()

    @classmethod
    def execute_query(cls, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results.

        Args:
            query (str): SQL SELECT statement
            params (tuple): Query parameters (use ? placeholders)

        Returns:
            List[Dict]: List of result rows as dictionaries

        Example:
            >>> results = BaseDAL.execute_query(
            ...     "SELECT * FROM users WHERE role = ?",
            ...     ('student',)
            ... )

        Security:
            ALWAYS use parameterized queries to prevent SQL injection.
            Never use string formatting or concatenation for SQL queries.
        """
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Convert sqlite3.Row objects to dictionaries
            return [dict(row) for row in rows]

    @classmethod
    def execute_update(cls, query: str, params: Tuple = ()) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query (str): SQL statement
            params (tuple): Query parameters

        Returns:
            int: Number of rows affected or last inserted row ID

        Example:
            >>> user_id = BaseDAL.execute_update(
            ...     "INSERT INTO users (name, email) VALUES (?, ?)",
            ...     ('John Doe', 'john@example.com')
            ... )
        """
        with cls.get_connection(commit=True) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid if cursor.lastrowid else cursor.rowcount

    @classmethod
    def execute_many(cls, query: str, param_list: List[Tuple]) -> int:
        """
        Execute the same query with multiple parameter sets.

        Useful for bulk inserts or updates.

        Args:
            query (str): SQL statement
            param_list (List[Tuple]): List of parameter tuples

        Returns:
            int: Number of rows affected

        Example:
            >>> BaseDAL.execute_many(
            ...     "INSERT INTO tags (name) VALUES (?)",
            ...     [('study',), ('quiet',), ('group',)]
            ... )
        """
        with cls.get_connection(commit=True) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, param_list)
            return cursor.rowcount

    @classmethod
    def table_exists(cls, table_name: str) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name (str): Name of the table

        Returns:
            bool: True if table exists, False otherwise

        Example:
            >>> if BaseDAL.table_exists('users'):
            ...     print("Users table exists")
        """
        query = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """
        results = cls.execute_query(query, (table_name,))
        return len(results) > 0

    @classmethod
    def get_row_count(cls, table_name: str, where_clause: str = "", params: Tuple = ()) -> int:
        """
        Get count of rows in a table (optionally with WHERE clause).

        Args:
            table_name (str): Name of the table
            where_clause (str): Optional WHERE clause (without 'WHERE' keyword)
            params (tuple): Parameters for WHERE clause

        Returns:
            int: Number of rows

        Example:
            >>> active_users = BaseDAL.get_row_count(
            ...     'users',
            ...     'role = ? AND email_verified = 1',
            ...     ('student',)
            ... )
        """
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        results = cls.execute_query(query, params)
        return results[0]['count'] if results else 0

    @classmethod
    def get_by_id(cls, table_name: str, id_column: str, id_value: int) -> Optional[Dict[str, Any]]:
        """
        Get a single row by ID.

        Args:
            table_name (str): Name of the table
            id_column (str): Name of the ID column
            id_value (int): ID value

        Returns:
            Optional[Dict]: Row as dictionary, or None if not found

        Example:
            >>> user = BaseDAL.get_by_id('users', 'user_id', 123)
        """
        query = f"SELECT * FROM {table_name} WHERE {id_column} = ?"
        results = cls.execute_query(query, (id_value,))
        return results[0] if results else None

    @classmethod
    def delete_by_id(cls, table_name: str, id_column: str, id_value: int) -> bool:
        """
        Delete a row by ID.

        Args:
            table_name (str): Name of the table
            id_column (str): Name of the ID column
            id_value (int): ID value

        Returns:
            bool: True if row was deleted, False otherwise

        Example:
            >>> success = BaseDAL.delete_by_id('bookings', 'booking_id', 456)
        """
        query = f"DELETE FROM {table_name} WHERE {id_column} = ?"
        rows_affected = cls.execute_update(query, (id_value,))
        return rows_affected > 0
