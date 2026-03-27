import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

DB_PATH = "navs.db"
MUFAP_URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=3"
RETURNS_URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=1"


# -----------------------
# NAV SCRAPER
# -----------------------
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


# -----------------------
# FUND RESOLVER
# -----------------------
def get_or_create_fund(cursor, fund_name):
    cursor.execute("SELECT id FROM funds WHERE name = ?", (fund_name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    cursor.execute("INSERT INTO funds (name) VALUES (?)", (fund_name,))
    return cursor.lastrowid


# -----------------------
# SAVE NAVS TO DB
# -----------------------
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


# -----------------------
# SAVE NAV JSON
# -----------------------
def save_json(data):
    with open("navs.json", "w") as f:
        json.dump({
            "count": len(data),
            "data": data
        }, f, indent=2)

    print("navs.json updated with", len(data), "records")


# -----------------------
# RETURNS SCRAPER
# -----------------------
def to_float(val):
    if not val:
        return None

    val = val.replace("%", "").strip()

    try:
        if val.startswith("(") and val.endswith(")"):
            return -float(val[1:-1])
        return float(val)
    except:
        return None


def scrape_returns():
    res = requests.get(RETURNS_URL, timeout=30)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("table tbody tr")
    data = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]

        if len(cols) < 18:
            continue

        try:
            data.append({
                "fund": cols[2],
                "returns": {
                    "1d": to_float(cols[9]),
                    "15d": to_float(cols[10]),
                    "30d": to_float(cols[11]),
                    "90d": to_float(cols[12]),
                    "180d": to_float(cols[13]),
                    "270d": to_float(cols[14]),
                    "365d": to_float(cols[15]),
                    "2y": to_float(cols[16]),
                    "3y": to_float(cols[17])
                }
            })
        except:
            continue

    return data


# -----------------------
# SAVE RETURNS JSON
# -----------------------
def save_returns_json(data):
    with open("returns.json", "w") as f:
        json.dump({
            "count": len(data),
            "data": data
        }, f, indent=2)

    print("returns.json updated with", len(data), "records")


# -----------------------
# MAIN ENTRY
# -----------------------
if __name__ == "__main__":
    navs = scrape_navs()
    save(navs)
    save_json(navs)

    returns = scrape_returns()
    save_returns_json(returns)

    print(f"Saved {len(navs)} NAV records")
    print(f"Saved {len(returns)} return records")
