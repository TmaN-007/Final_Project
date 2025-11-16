#!/usr/bin/env python3
"""
Database Initialization Script for Campus Resource Hub
This script creates the SQLite database with all necessary tables and indexes.
It should be run once during deployment or when setting up a new environment.
"""

import sqlite3
import os
import sys
from pathlib import Path

# Database schema SQL
SCHEMA_SQL = """
-- Departments Table
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student','staff','admin')),
    profile_image TEXT,
    department_id INTEGER REFERENCES departments(department_id),
    email_verified BOOLEAN NOT NULL DEFAULT 0,
    verification_token TEXT,
    verification_token_expires DATETIME,
    reset_password_token TEXT,
    reset_password_expires DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    is_banned INTEGER DEFAULT 0,
    last_login TIMESTAMP
);

-- User Sessions Table
CREATE TABLE IF NOT EXISTS user_sessions (
    session_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    ip_address TEXT,
    user_agent TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- CSRF Tokens Table
CREATE TABLE IF NOT EXISTS csrf_tokens (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL
);

-- Groups Table
CREATE TABLE IF NOT EXISTS groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Group Members Table
CREATE TABLE IF NOT EXISTS group_members (
    group_id INTEGER NOT NULL REFERENCES groups(group_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    member_role TEXT NOT NULL DEFAULT 'member' CHECK (member_role IN ('owner','admin','member')),
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (group_id, user_id)
);

-- Resource Categories Table
CREATE TABLE IF NOT EXISTS resource_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Resources Table
CREATE TABLE IF NOT EXISTS resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_type TEXT NOT NULL CHECK (owner_type IN ('user','group')),
    owner_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES resource_categories(category_id),
    location TEXT,
    capacity INTEGER CHECK (capacity > 0 OR capacity IS NULL),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published','archived')),
    availability_mode TEXT NOT NULL DEFAULT 'rules' CHECK (availability_mode IN ('rules','open','by-request')),
    requires_approval BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    images TEXT,
    availability_rules TEXT
);

-- Resource Images Table
CREATE TABLE IF NOT EXISTS resource_images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Equipment Table
CREATE TABLE IF NOT EXISTS equipment (
    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Resource Equipment Table
CREATE TABLE IF NOT EXISTS resource_equipment (
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    equipment_id INTEGER NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    status TEXT DEFAULT 'available' CHECK (status IN ('available','in_use','maintenance','broken')),
    last_checked DATETIME,
    PRIMARY KEY (resource_id, equipment_id)
);

-- Resource Availability Rules Table
CREATE TABLE IF NOT EXISTS resource_availability_rules (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    rule_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Resource Unavailable Slots Table
CREATE TABLE IF NOT EXISTS resource_unavailable_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_datetime > start_datetime)
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE RESTRICT,
    requester_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected','cancelled','completed')),
    approval_required BOOLEAN NOT NULL DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME,
    CHECK (end_datetime > start_datetime)
);

-- Booking Recurrences Table
CREATE TABLE IF NOT EXISTS booking_recurrences (
    recurrence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    recurrence_rule TEXT NOT NULL,
    ends_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Booking Approval Actions Table
CREATE TABLE IF NOT EXISTS booking_approval_actions (
    approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    approver_id INTEGER NOT NULL REFERENCES users(user_id),
    action TEXT NOT NULL CHECK (action IN ('approved','rejected')),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Booking Waitlist Table
CREATE TABLE IF NOT EXISTS booking_waitlist (
    waitlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    desired_start_datetime DATETIME NOT NULL,
    desired_end_datetime DATETIME NOT NULL,
    status TEXT NOT NULL DEFAULT 'waiting' CHECK (status IN ('waiting','notified','converted','cancelled')),
    converted_booking_id INTEGER REFERENCES bookings(booking_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notified_at DATETIME,
    CHECK (desired_end_datetime > desired_start_datetime)
);

-- External Calendar Accounts Table
CREATE TABLE IF NOT EXISTS external_calendar_accounts (
    calendar_account_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    provider TEXT NOT NULL CHECK (provider IN ('google','microsoft','ical_export')),
    auth_data_json TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Calendar Events Table
CREATE TABLE IF NOT EXISTS calendar_events (
    calendar_event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    calendar_account_id INTEGER NOT NULL REFERENCES external_calendar_accounts(calendar_account_id) ON DELETE CASCADE,
    external_event_id TEXT NOT NULL,
    sync_status TEXT NOT NULL DEFAULT 'created' CHECK (sync_status IN ('created','updated','deleted','error')),
    last_sync_at DATETIME,
    error_message TEXT
);

-- Message Threads Table
CREATE TABLE IF NOT EXISTS message_threads (
    thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER REFERENCES resources(resource_id) ON DELETE SET NULL,
    booking_id INTEGER REFERENCES bookings(booking_id) ON DELETE SET NULL,
    subject TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Messages Table
CREATE TABLE IF NOT EXISTS messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL REFERENCES message_threads(thread_id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    receiver_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Message Thread Participants Table
CREATE TABLE IF NOT EXISTS message_thread_participants (
    thread_id INTEGER NOT NULL REFERENCES message_threads(thread_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_read_at DATETIME,
    PRIMARY KEY (thread_id, user_id)
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL CHECK (notification_type IN ('booking_requested','booking_approved','booking_rejected','booking_cancelled','waitlist_notified','message_received','review_posted','resource_available')),
    payload_json TEXT,
    delivery_method TEXT DEFAULT 'in_app' CHECK (delivery_method IN ('in_app','email','sms','push')),
    delivery_status TEXT DEFAULT 'pending' CHECK (delivery_status IN ('pending','sent','failed')),
    is_read BOOLEAN NOT NULL DEFAULT 0,
    sent_at DATETIME,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Reviews Table
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    is_visible BOOLEAN NOT NULL DEFAULT 1,
    flagged_count INTEGER DEFAULT 0,
    host_response TEXT,
    host_responded_at DATETIME,
    helpful_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

-- Content Reports Table
CREATE TABLE IF NOT EXISTS content_reports (
    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reporter_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    target_type TEXT NOT NULL CHECK (target_type IN ('review','message','resource','user')),
    target_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','in_review','resolved','dismissed')),
    resolved_by INTEGER REFERENCES users(user_id),
    resolved_at DATETIME,
    resolution_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Admin Logs Table
CREATE TABLE IF NOT EXISTS admin_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    target_table TEXT,
    target_id INTEGER,
    details TEXT,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Resource Analytics Table
CREATE TABLE IF NOT EXISTS resource_analytics (
    analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_bookings INTEGER DEFAULT 0,
    total_hours_booked REAL DEFAULT 0,
    unique_users INTEGER DEFAULT 0,
    avg_rating REAL,
    utilization_rate REAL,
    revenue REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource_id, date)
);

-- Search Queries Table
CREATE TABLE IF NOT EXISTS search_queries (
    query_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    query_text TEXT NOT NULL,
    filters_json TEXT,
    results_count INTEGER,
    clicked_resource_id INTEGER REFERENCES resources(resource_id) ON DELETE SET NULL,
    session_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Uploaded Files Table
CREATE TABLE IF NOT EXISTS uploaded_files (
    file_id INTEGER PRIMARY KEY AUTOINCREMENT,
    uploader_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT NOT NULL,
    scan_status TEXT DEFAULT 'pending' CHECK (scan_status IN ('pending','clean','infected','error')),
    scan_message TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- AI Interactions Table
CREATE TABLE IF NOT EXISTS ai_interactions (
    ai_interaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    interaction_type TEXT NOT NULL CHECK (interaction_type IN ('booking_help','resource_concierge','doc_summary','scheduler','search_assist')),
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    grounded_sources TEXT,
    context_used TEXT,
    validation_status TEXT DEFAULT 'unverified' CHECK (validation_status IN ('verified','unverified','hallucination_detected')),
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5),
    corrected_by INTEGER REFERENCES users(user_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Rate Limits Table
CREATE TABLE IF NOT EXISTS rate_limits (
    limit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    ip_address TEXT,
    endpoint TEXT NOT NULL,
    request_count INTEGER DEFAULT 1,
    window_start DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_department ON users(department_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);
CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category_id);
CREATE INDEX IF NOT EXISTS idx_resources_owner ON resources(owner_type, owner_id);
CREATE INDEX IF NOT EXISTS idx_bookings_resource_datetime ON bookings(resource_id, start_datetime, end_datetime);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_requester ON bookings(requester_id);
CREATE INDEX IF NOT EXISTS idx_unavailable_resource_datetime ON resource_unavailable_slots(resource_id, start_datetime, end_datetime);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_reviews_resource ON reviews(resource_id);
CREATE INDEX IF NOT EXISTS idx_reviews_visible ON reviews(is_visible);
CREATE INDEX IF NOT EXISTS idx_analytics_resource_date ON resource_analytics(resource_id, date);
CREATE INDEX IF NOT EXISTS idx_search_queries_user ON search_queries(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_target ON admin_logs(target_table, target_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_user ON rate_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_ip ON rate_limits(ip_address);
CREATE INDEX IF NOT EXISTS idx_message_participants_user ON message_thread_participants(user_id);
CREATE INDEX IF NOT EXISTS idx_message_participants_thread ON message_thread_participants(thread_id);
"""


def init_database(db_path=None):
    """
    Initialize the database with all tables and indexes.

    Args:
        db_path: Path to the database file. If None, uses environment variable or default.

    Returns:
        bool: True if successful, False otherwise
    """
    if db_path is None:
        # Try to get from environment variable
        db_path = os.environ.get('DATABASE_PATH')
        if not db_path:
            # Default to current directory
            db_path = 'campus_resource_hub.db'

    try:
        print(f"Initializing database at: {db_path}")

        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")

        # Connect to database (creates file if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Execute schema SQL
        print("Creating tables and indexes...")
        cursor.executescript(SCHEMA_SQL)
        conn.commit()

        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        print(f"\nSuccessfully created {len(tables)} tables:")
        for table in tables:
            if table[0] != 'sqlite_sequence':  # Skip internal table
                print(f"  - {table[0]}")

        conn.close()
        print(f"\nDatabase initialized successfully at: {db_path}")
        return True

    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")
        return False


if __name__ == '__main__':
    # Get database path from command line argument or environment variable
    db_path = sys.argv[1] if len(sys.argv) > 1 else None

    success = init_database(db_path)
    sys.exit(0 if success else 1)
