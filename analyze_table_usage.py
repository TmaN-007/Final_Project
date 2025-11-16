#!/usr/bin/env python3
"""
Database Table Usage Analyzer
==============================
Analyzes all source files to determine which database tables are actually used
in the Campus Resource Hub application.

This script searches through:
- Python source files (src/, tests/)
- SQL schema files
- Template files (templates/)
- Configuration files

Author: Campus Resource Hub Team
Date: November 15, 2025
"""

import os
import re
from collections import defaultdict
from pathlib import Path

# All 30 database tables
TABLES = [
    'admin_logs',
    'ai_interactions',
    'booking_approval_actions',
    'booking_recurrences',
    'booking_waitlist',
    'bookings',
    'calendar_events',
    'content_reports',
    'csrf_tokens',
    'departments',
    'equipment',
    'external_calendar_accounts',
    'group_members',
    'groups',
    'message_thread_participants',
    'message_threads',
    'messages',
    'notifications',
    'rate_limits',
    'resource_analytics',
    'resource_availability_rules',
    'resource_categories',
    'resource_equipment',
    'resource_images',
    'resource_unavailable_slots',
    'resources',
    'reviews',
    'search_queries',
    'uploaded_files',
    'user_sessions',
    'users'
]

def search_in_file(file_path, table_name):
    """
    Search for table name references in a file.
    Returns list of (line_number, line_content) tuples.
    """
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                # Case-insensitive search for table name
                # Look for table name as whole word (with boundaries)
                pattern = r'\b' + re.escape(table_name) + r'\b'
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append((line_num, line.strip()))
    except Exception as e:
        pass  # Skip files that can't be read

    return matches

def analyze_directory(base_path, extensions):
    """
    Recursively search directory for files with given extensions.
    Returns dict: {table_name: [(file_path, line_num, line_content), ...]}
    """
    table_usage = defaultdict(list)

    base_path = Path(base_path)

    # Get all files with matching extensions
    for ext in extensions:
        for file_path in base_path.rglob(f'*{ext}'):
            # Skip virtual environment, cache, etc.
            str_path = str(file_path)
            if any(skip in str_path for skip in ['venv', '__pycache__', '.git', 'node_modules']):
                continue

            # Search for each table in this file
            for table in TABLES:
                matches = search_in_file(file_path, table)
                for line_num, line_content in matches:
                    table_usage[table].append((str(file_path), line_num, line_content))

    return table_usage

def main():
    """Main analysis function."""

    print("="*80)
    print("DATABASE TABLE USAGE ANALYSIS")
    print("="*80)
    print(f"\nAnalyzing {len(TABLES)} database tables across entire codebase...")
    print()

    # Search in different file types
    searches = [
        ("Python Source Files", ["*.py"], "src/"),
        ("Python Test Files", ["*.py"], "tests/"),
        ("SQL Files", ["*.sql"], "."),
        ("HTML Templates", ["*.html"], "templates/"),
    ]

    all_usage = defaultdict(list)

    for search_name, extensions, directory in searches:
        if not os.path.exists(directory):
            continue

        print(f"Searching {search_name} in {directory}...")
        usage = analyze_directory(directory, extensions)

        # Merge results
        for table, matches in usage.items():
            all_usage[table].extend(matches)

    print("\n" + "="*80)
    print("RESULTS: TABLE USAGE BREAKDOWN")
    print("="*80)

    # Categorize tables
    used_tables = {}
    unused_tables = []
    schema_only_tables = []

    for table in TABLES:
        matches = all_usage[table]

        if not matches:
            unused_tables.append(table)
        else:
            # Check if only referenced in schema
            non_schema_matches = [m for m in matches if 'schema' not in m[0].lower()]

            if not non_schema_matches:
                schema_only_tables.append(table)
            else:
                used_tables[table] = matches

    # Print USED TABLES
    print("\n" + "="*80)
    print(f"✅ USED TABLES ({len(used_tables)} tables)")
    print("="*80)

    for table in sorted(used_tables.keys()):
        matches = used_tables[table]

        # Count unique files
        unique_files = set(m[0] for m in matches)

        print(f"\n📊 {table.upper()}")
        print(f"   References: {len(matches)} | Files: {len(unique_files)}")

        # Show first 5 references
        print(f"   Locations:")
        for file_path, line_num, line_content in matches[:5]:
            # Shorten file path for display
            short_path = file_path.replace('/Users/hii/Desktop/AiDD Final Project/Final_Project/', '')
            print(f"      - {short_path}:{line_num}")
            # Show truncated line content
            if len(line_content) > 80:
                line_content = line_content[:77] + "..."
            print(f"        {line_content}")

        if len(matches) > 5:
            print(f"      ... and {len(matches) - 5} more references")

    # Print SCHEMA-ONLY TABLES
    if schema_only_tables:
        print("\n" + "="*80)
        print(f"⚠️  SCHEMA-ONLY TABLES ({len(schema_only_tables)} tables)")
        print("="*80)
        print("\nThese tables exist in database schema but are NOT used in application code:")
        print()
        for table in sorted(schema_only_tables):
            print(f"   - {table}")

    # Print COMPLETELY UNUSED TABLES
    if unused_tables:
        print("\n" + "="*80)
        print(f"❌ COMPLETELY UNUSED TABLES ({len(unused_tables)} tables)")
        print("="*80)
        print("\nThese tables have NO references anywhere (not even in schema):")
        print()
        for table in sorted(unused_tables):
            print(f"   - {table}")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Tables: {len(TABLES)}")
    print(f"✅ Used in Application: {len(used_tables)} ({len(used_tables)/len(TABLES)*100:.1f}%)")
    print(f"⚠️  Schema-Only (not used): {len(schema_only_tables)} ({len(schema_only_tables)/len(TABLES)*100:.1f}%)")
    print(f"❌ Completely Unused: {len(unused_tables)} ({len(unused_tables)/len(TABLES)*100:.1f}%)")
    print("="*80)

    # Calculate total references
    total_refs = sum(len(matches) for matches in used_tables.values())
    print(f"\nTotal References Found: {total_refs}")
    print()

if __name__ == "__main__":
    main()
