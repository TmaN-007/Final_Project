-- ============================================================================
-- Campus Resource Hub - Database Schema
-- ============================================================================
--
-- IMPORTANT: This schema contains only the 20 ACTIVELY USED tables.
-- 11 unused tables have been removed to streamline the database design.
--
-- Database: SQLite 3
-- Total Tables: 20
-- Last Updated: November 15, 2025
--
-- Removed Tables (unused in application code):
--   - admin_logs
--   - ai_interactions
--   - booking_recurrences
--   - calendar_events
--   - csrf_tokens
--   - external_calendar_accounts
--   - group_members
--   - rate_limits
--   - search_queries
--   - uploaded_files
--   - user_sessions
--
-- ============================================================================

-- Drop existing tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS message_thread_participants;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS message_threads;
DROP TABLE IF EXISTS content_reports;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS booking_waitlist;
DROP TABLE IF EXISTS booking_approval_actions;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS resource_analytics;
DROP TABLE IF EXISTS resource_unavailable_slots;
DROP TABLE IF EXISTS resource_availability_rules;
DROP TABLE IF EXISTS resource_equipment;
DROP TABLE IF EXISTS resource_images;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS resource_categories;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS departments;

-- ============================================================================
-- TABLE DEFINITIONS (20 Used Tables)
-- ============================================================================


-- Core Tables
-- ============================================================================

CREATE TABLE users (
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
    updated_at DATETIME
, is_banned INTEGER DEFAULT 0, last_login TIMESTAMP);

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- Resource Management
-- ============================================================================

CREATE TABLE resource_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resources (
    resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_type TEXT NOT NULL CHECK (owner_type IN ('user','group')),
    owner_id INTEGER NOT NULL,  -- Polymorphic FK: user_id when owner_type='user', group_id when owner_type='group'
    title TEXT NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES resource_categories(category_id),
    location TEXT,
    capacity INTEGER CHECK (capacity > 0 OR capacity IS NULL),  -- NULL for resources without capacity limits
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','published','archived')),
    availability_mode TEXT NOT NULL DEFAULT 'rules' CHECK (availability_mode IN ('rules','open','by-request')),
    requires_approval BOOLEAN NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
, images TEXT, availability_rules TEXT);

CREATE TABLE resource_images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    is_primary BOOLEAN NOT NULL DEFAULT 0,
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE resource_equipment (
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    equipment_id INTEGER NOT NULL REFERENCES equipment(equipment_id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1,
    status TEXT DEFAULT 'available' CHECK (status IN ('available','in_use','maintenance','broken')),
    last_checked DATETIME,
    PRIMARY KEY (resource_id, equipment_id)
);

CREATE TABLE resource_availability_rules (
    rule_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    rule_json TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE TABLE resource_unavailable_slots (
    slot_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER NOT NULL REFERENCES resources(resource_id) ON DELETE CASCADE,
    start_datetime DATETIME NOT NULL,
    end_datetime DATETIME NOT NULL,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_datetime > start_datetime)
);

CREATE TABLE resource_analytics (
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

CREATE TABLE equipment (
    equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- Booking System
-- ============================================================================

CREATE TABLE bookings (
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

CREATE TABLE booking_approval_actions (
    approval_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    approver_id INTEGER NOT NULL REFERENCES users(user_id),
    action TEXT NOT NULL CHECK (action IN ('approved','rejected')),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE booking_waitlist (
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


-- Groups & Organizations
-- ============================================================================

CREATE TABLE groups (
    group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- Reviews & Reports
-- ============================================================================

CREATE TABLE reviews (
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

CREATE TABLE content_reports (
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


-- Messaging System
-- ============================================================================

CREATE TABLE message_threads (
    thread_id INTEGER PRIMARY KEY AUTOINCREMENT,
    resource_id INTEGER REFERENCES resources(resource_id) ON DELETE SET NULL,
    booking_id INTEGER REFERENCES bookings(booking_id) ON DELETE SET NULL,
    subject TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME
);

CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL REFERENCES message_threads(thread_id) ON DELETE CASCADE,
    sender_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    receiver_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE message_thread_participants (
    thread_id INTEGER NOT NULL REFERENCES message_threads(thread_id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_read_at DATETIME,
    PRIMARY KEY (thread_id, user_id)
);


-- Notifications
-- ============================================================================

CREATE TABLE notifications (
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

-- ============================================================================
-- INDEXES
-- ============================================================================
-- Note: SQLite automatically creates indexes for PRIMARY KEY and UNIQUE constraints
-- Additional indexes should be created based on query patterns

-- User indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Resource indexes
CREATE INDEX IF NOT EXISTS idx_resources_category ON resources(category_id);
CREATE INDEX IF NOT EXISTS idx_resources_owner ON resources(owner_type, owner_id);
CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(status);

-- Booking indexes
CREATE INDEX IF NOT EXISTS idx_bookings_resource ON bookings(resource_id);
CREATE INDEX IF NOT EXISTS idx_bookings_user ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
CREATE INDEX IF NOT EXISTS idx_bookings_dates ON bookings(start_datetime, end_datetime);

-- Review indexes
CREATE INDEX IF NOT EXISTS idx_reviews_resource ON reviews(resource_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);

-- Message indexes
CREATE INDEX IF NOT EXISTS idx_messages_thread ON messages(thread_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id);

-- Notification indexes
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read);

-- ============================================================================
-- SCHEMA GENERATION COMPLETE
-- ============================================================================
-- Total Tables: 20
-- Total Indexes: 14 (user-defined)
-- Schema Version: 2.0 (Optimized - Unused tables removed)
-- Generated: November 15, 2025
-- ============================================================================
