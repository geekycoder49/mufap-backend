import pandas as pd
import sqlite3
from datetime import datetime
import sys

DB_PATH = "navs.db"

# ✅ File name handling
FILE = sys.argv[1] if len(sys.argv) > 1 else "navs.xlsx"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

df = pd.read_excel(FILE, skiprows=1)

print("Columns found:", df.columns.tolist())


def get_or_create_fund(name):
    cursor.execute("SELECT id FROM funds WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute("INSERT INTO funds (name) VALUES (?)", (name,))
    return cursor.lastrowid


inserted = 0
skipped = 0

for _, row in df.iterrows():
    try:
        fund_name = str(row["Fund"]).strip()
        nav = float(row["NAV"])

        # Skip bad NAV
        if nav == 0:
            skipped += 1
            continue

        # Convert date → ISO
        date = datetime.strptime(str(row["Validity Date"]), "%b %d, %Y").strftime("%Y-%m-%d")

        fund_id = get_or_create_fund(fund_name)

        cursor.execute("""
        INSERT OR IGNORE INTO nav_history (fund_id, nav, nav_date)
        VALUES (?, ?, ?)
        """, (fund_id, nav, date))

        if cursor.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    except Exception as e:
        skipped += 1
        continue

conn.commit()
conn.close()

print(f"Inserted: {inserted}, Skipped (duplicates/errors): {skipped}")