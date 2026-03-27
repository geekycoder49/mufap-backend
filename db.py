import sqlite3

conn = sqlite3.connect("navs.db")
cursor = conn.cursor()

# 1. Funds table (unique funds)
cursor.execute("""
CREATE TABLE IF NOT EXISTS funds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

# 2. NAV history
cursor.execute("""
CREATE TABLE IF NOT EXISTS nav_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_id INTEGER,
    nav REAL,
    nav_date TEXT,
    fetched_at TEXT,
    UNIQUE(fund_id, nav_date),
    FOREIGN KEY(fund_id) REFERENCES funds(id)
)
""")

conn.commit()
conn.close()

print("DB rebuilt successfully")
