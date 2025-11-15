#!/usr/bin/env python3
"""
Script to fix test files to match actual DAL API signatures
"""

import re
import os

def fix_create_resource_calls(content):
    """
    Fix resource_dal.create_resource() calls to match actual signature:
    create_resource(owner_type, owner_id, title, description, category_id, location, ...)
    """
    # Pattern to match create_resource calls with old signature
    pattern = r'resource_dal\.create_resource\(\s*title="([^"]+)",\s*description="([^"]+)",\s*category_id=(\d+),\s*owner_id=([^,\)]+),?\s*(?:status="([^"]+)")?\s*\)'

    def replacement(match):
        title, desc, cat_id, owner_id, status = match.groups()
        status = status if status else '"draft"'
        # New signature: owner_type, owner_id, title, description, category_id, location, status
        return f'resource_dal.create_resource(\n            owner_type="user",\n            owner_id={owner_id},\n            title="{title}",\n            description="{desc}",\n            category_id={cat_id},\n            location="Test Location",\n            status={status}\n        )'

    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Also fix simpler positional argument calls like: create_resource("Room", "Desc", 1, owner_id, "published")
    pattern2 = r'resource_dal\.create_resource\("([^"]+)",\s*"([^"]+)",\s*(\d+),\s*([^,\)]+),?\s*"([^"]+)"\)'

    def replacement2(match):
        title, desc, cat_id, owner_id, status = match.groups()
        return f'resource_dal.create_resource(\n            owner_type="user",\n            owner_id={owner_id},\n            title="{title}",\n            description="{desc}",\n            category_id={cat_id},\n            location="Test Location",\n            status="{status}"\n        )'

    content = re.sub(pattern2, replacement2, content)

    # Fix dal.create_resource (not resource_dal prefix)
    pattern3 = r'dal\.create_resource\(\s*title="([^"]+)",\s*description="([^"]+)",\s*category_id=(\d+),\s*owner_id=([^,\)]+),?\s*(?:status="([^"]+)")?\s*\)'

    def replacement3(match):
        title, desc, cat_id, owner_id, status = match.groups()
        status = status if status else '"draft"'
        return f'dal.create_resource(\n            owner_type="user",\n            owner_id={owner_id},\n            title="{title}",\n            description="{desc}",\n            category_id={cat_id},\n            location="Test Location",\n            status={status}\n        )'

    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE)

    return content

def fix_test_file(filepath):
    """Fix a single test file"""
    print(f"Processing {filepath}...")

    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content

    # Apply fixes
    content = fix_create_resource_calls(content)

    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ Fixed {filepath}")
        return True
    else:
        print(f"  - No changes needed for {filepath}")
        return False

def main():
    """Main function to fix all test files"""
    tests_dir = "/Users/hii/Desktop/AiDD Final Project/Final_Project/tests"

    test_files = [
        os.path.join(tests_dir, "test_dal_unit.py"),
        os.path.join(tests_dir, "test_booking_logic.py"),
        os.path.join(tests_dir, "test_e2e_booking.py"),
        os.path.join(tests_dir, "test_security.py"),
    ]

    fixed_count = 0
    for filepath in test_files:
        if os.path.exists(filepath):
            if fix_test_file(filepath):
                fixed_count += 1
        else:
            print(f"  ✗ File not found: {filepath}")

    print(f"\n✅ Fixed {fixed_count} test file(s)")

if __name__ == "__main__":
    main()
