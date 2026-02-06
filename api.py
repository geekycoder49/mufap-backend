import os
import sqlite3
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# -----------------------
# Database helper
# -----------------------
def db():
    return sqlite3.connect("navs.db")


# -----------------------
# HEALTH CHECK (important)
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
# SCRAPER (placeholder)
# -----------------------
def scrape_navs():
    """
    This should return a list like:
    [
      {"fund": "ABL Cash Fund", "nav": 10.87, "date": "2026-02-06"}
    ]
    Replace the body with your existing MUFAP scraper logic.
    """
    raise NotImplementedError("scrape_navs() not implemented")


# -----------------------
# SAVE TO DB
# -----------------------
def save_navs(data):
    conn = db()
    c = conn.cursor()

    for item in data:
        c.execute("""
            INSERT OR IGNORE INTO nav_history (fund, nav, nav_date)
            VALUES (?, ?, ?)
        """, (
            item["fund"],
            item["nav"],
            item["date"]
        ))

    conn.commit()
    conn.close()


# -----------------------
# CRON ENDPOINT (GitHub Actions)
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
# ENTRY POINT (Render-safe)
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
