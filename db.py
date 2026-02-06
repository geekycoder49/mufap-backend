import sqlite3

conn = sqlite3.connect("navs.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS nav_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund TEXT,
    nav REAL,
    nav_date TEXT,
    fetched_at TEXT
)
""")

conn.commit()
conn.close()
print("DB ready")
