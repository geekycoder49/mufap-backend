from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def db():
    return sqlite3.connect("navs.db")

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
    """)
    rows = c.fetchall()
    conn.close()
    return jsonify([{"fund": r[0], "nav": r[1], "date": r[2]} for r in rows])

@app.route("/navs/history/<fund>")
def history(fund):
    conn = db()
    c = conn.cursor()
    c.execute("SELECT nav, nav_date FROM nav_history WHERE fund=?", (fund,))
    rows = c.fetchall()
    conn.close()
    return jsonify([{"nav": r[0], "date": r[1]} for r in rows])

app.run(host="0.0.0.0", port=5000)
