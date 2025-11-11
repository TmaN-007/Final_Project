#!/bin/bash

echo "=================================="
echo "SCHEMA VERIFICATION SCRIPT"
echo "=================================="
echo ""

echo "1. Checking database file..."
if [ -f "campus_resource_hub.db" ]; then
    echo "   ✅ Database exists"
    SIZE=$(ls -lh campus_resource_hub.db | awk '{print $5}')
    echo "   Size: $SIZE"
else
    echo "   ❌ Database not found!"
    exit 1
fi

echo ""
echo "2. Counting tables..."
TABLE_COUNT=$(sqlite3 campus_resource_hub.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
echo "   Total tables: $TABLE_COUNT"
if [ "$TABLE_COUNT" = "30" ]; then
    echo "   ✅ Correct (expected 30)"
else
    echo "   ❌ Wrong count (expected 30, got $TABLE_COUNT)"
fi

echo ""
echo "3. Checking critical tables..."
CRITICAL_TABLES=("users" "resources" "bookings" "user_sessions" "csrf_tokens" "ai_interactions" "booking_waitlist")
for table in "${CRITICAL_TABLES[@]}"; do
    EXISTS=$(sqlite3 campus_resource_hub.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='$table';")
    if [ "$EXISTS" = "1" ]; then
        echo "   ✅ $table"
    else
        echo "   ❌ $table MISSING"
    fi
done

echo ""
echo "4. Checking seed data..."
CATEGORIES=$(sqlite3 campus_resource_hub.db "SELECT COUNT(*) FROM resource_categories;")
DEPARTMENTS=$(sqlite3 campus_resource_hub.db "SELECT COUNT(*) FROM departments;")
echo "   Resource categories: $CATEGORIES (expected 8)"
echo "   Departments: $DEPARTMENTS (expected 8)"

echo ""
echo "5. Checking capacity constraint..."
sqlite3 campus_resource_hub.db "INSERT INTO resources (owner_type, owner_id, title, capacity, status) VALUES ('user', 1, 'Test Laptop', NULL, 'draft');" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "   ✅ NULL capacity allowed"
    sqlite3 campus_resource_hub.db "DELETE FROM resources WHERE title='Test Laptop';"
else
    echo "   ❌ NULL capacity rejected (constraint too strict)"
fi

echo ""
echo "6. Listing all tables..."
sqlite3 campus_resource_hub.db "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"

echo ""
echo "=================================="
echo "VERIFICATION COMPLETE"
echo "=================================="
