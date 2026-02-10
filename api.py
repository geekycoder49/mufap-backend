import os
import sqlite3
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# -----------------------
# Database helper
# -----------------------
def db():
    return sqlite3.connect("navs.db")


# -----------------------
# HEALTH CHECK
# -----------------------
@app.route("/")
def home():
    return {
        "status": "ok",
        "message": "MUFAP NAV API running"
    }


# -----------------------
# LATEST NAVs
# -----------------------
@app.route("/navs/latest")
def latest():
    conn = db()
    c = conn.cursor()

    c.execute("""
        SELECT fund, nav, nav_date
        FROM nav_history
        WHERE (fund, nav_date) IN (
            SELECT fund, MAX(nav_date)
            FROM nav_history
            GROUP BY fund
        )
        ORDER BY fund
    """)

    rows = c.fetchall()
    conn.close()

    return jsonify([
        {"fund": r[0], "nav": float(r[1]), "date": r[2]}
        for r in rows
    ])


# -----------------------
# NAV HISTORY (per fund)
# -----------------------
@app.route("/navs/history/<fund>")
def history(fund):
    conn = db()
    c = conn.cursor()

    c.execute("""
        SELECT nav, nav_date
        FROM nav_history
        WHERE fund = ?
        ORDER BY nav_date ASC
    """, (fund,))

    rows = c.fetchall()
    conn.close()

    return jsonify([
        {"nav": float(r[0]), "date": r[1]}
        for r in rows
    ])


# -----------------------
# MUFAP SCRAPER (REAL)
# -----------------------
def scrape_navs():
    url = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=3"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("table tbody tr")

    data = []

    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]

        # We need at least Fund, NAV, Validity Date
        if len(cols) < 9:
            continue

        fund = cols[2].strip()
        nav_text = cols[7].replace(",", "")
        nav_date = cols[8].strip()

        try:
            nav = float(nav_text)
        except ValueError:
            continue

        data.append({
            "fund": fund,
            "nav": nav,
            "date": nav_date
        })

    return data


# -----------------------
# SAVE TO DB
# -----------------------
def save_navs(data):
    conn = db()
    c = conn.cursor()

    today = data[0]["date"] if data else None

    if today:
        c.execute(
            "DELETE FROM nav_history WHERE nav_date = ?",
            (today,)
        )

    for item in data:
        c.execute("""
            INSERT INTO nav_history (fund, nav, nav_date)
            VALUES (?, ?, ?)
        """, (
            item["fund"],
            item["nav"],
            item["date"]
        ))

    conn.commit()
    conn.close()


# -----------------------
# CRON ENDPOINT
# -----------------------
@app.route("/cron/fetch")
def cron_fetch():
    key = request.headers.get("X-CRON-KEY")

    if key != os.environ.get("CRON_KEY"):
        return {"error": "unauthorized"}, 401

    data = scrape_navs()
    save_navs(data)

    return {
        "status": "success",
        "records_saved": len(data),
        "timestamp": datetime.utcnow().isoformat()
    }


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

