import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime

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


def save(data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for d in data:
        c.execute("""
        INSERT OR IGNORE INTO nav_history (fund, nav, nav_date)
        VALUES (?, ?, ?)
        """, (d["fund"], d["nav"], d["date"]))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    navs = scrape_navs()
    save(navs)
    print(f"Saved {len(navs)} NAV records")
