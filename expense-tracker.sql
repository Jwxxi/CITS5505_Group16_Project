-- Enable FK enforcement (run this once when opening the DB)
PRAGMA foreign_keys = ON;

-- Users table
-- This table stores user information
-- Each user has a unique ID, first name, last name, email, and password
CREATE TABLE
    users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );

-- Categories table
-- This table stores the categories for income and expenses
-- Each category has a unique ID, name, type (income/expense), and icon
-- The type is enforced to be either 'income' or 'expense'
CREATE TABLE
    categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
        icon TEXT NOT NULL
    );

-- Items table
-- This table stores the actual transactions (income/expense)
-- Each item is linked to a user and a category
CREATE TABLE
    items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
        category_id INTEGER NOT NULL REFERENCES categories (id) ON DELETE CASCADE,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP)
    );

-- (Optional) Indexes to speed up lookups
CREATE INDEX idx_items_user ON items (user_id);

CREATE INDEX idx_items_category ON items (category_id);

CREATE INDEX idx_categories_type ON categories (type);