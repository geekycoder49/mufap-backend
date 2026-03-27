import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

DB_PATH = "navs.db"
MUFAP_URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=3"


def scrape_navs():
    res = requests.get(MUFAP_URL, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table tbody tr")
    data = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 9:
            continue

        fund = cols[2]
        nav = cols[7]
        date = cols[8]

        try:
            data.append({
                "fund": fund,
                "nav": float(nav),
                "date": datetime.strptime(date, "%b %d, %Y").strftime("%Y-%m-%d")
            })
        except:
            continue

    return data


# 🔥 NEW: fund resolver
def get_or_create_fund(cursor, fund_name):
    cursor.execute("SELECT id FROM funds WHERE name = ?", (fund_name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute("INSERT INTO funds (name) VALUES (?)", (fund_name,))
    return cursor.lastrowid


def save(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for d in data:
        fund_id = get_or_create_fund(c, d["fund"])

        c.execute("""
        INSERT OR IGNORE INTO nav_history (fund_id, nav, nav_date, fetched_at)
        VALUES (?, ?, ?, ?)
        """, (
            fund_id,
            d["nav"],
            d["date"],
            datetime.utcnow().isoformat()
        ))

    conn.commit()
    conn.close()


def save_json(data):
    with open("navs.json", "w") as f:
        json.dump({
            "count": len(data),
            "data": data
        }, f, indent=2)

    print("navs.json updated with", len(data), "records")


# ✅ SINGLE entry point
if __name__ == "__main__":
    navs = scrape_navs()
    save(navs)
    save_json(navs)
    print(f"Saved {len(navs)} NAV records")
