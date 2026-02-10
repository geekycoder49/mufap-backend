import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup
from datetime import datetime
import os

app = Flask(__name__)

NAV_URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=3"
RETURNS_URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=1"


@app.route("/")
def home():
    return {"status": "ok", "source": "live MUFAP"}


# -----------------------
# LATEST NAVs
# -----------------------
@app.route("/navs/latest")
def latest_navs():
    response = requests.get(NAV_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    rows = table.find("tbody").find_all("tr")

    navs = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 9:
            continue

        try:
            navs.append({
                "fund": cols[2],
                "nav": float(cols[7]),
                "date": cols[8]
            })
        except:
            continue

    return jsonify({
        "updated_at": datetime.utcnow().isoformat(),
        "count": len(navs),
        "data": navs
    })


# -----------------------
# FUND RETURNS
# -----------------------
@app.route("/returns/latest")
def fund_returns():
    response = requests.get(RETURNS_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    rows = table.find("tbody").find_all("tr")

    results = []

    def to_float(val):
        if not val:
            return None

        val = val.replace("%", "").strip()

        try:
            # (1.81) → -1.81
            if val.startswith("(") and val.endswith(")"):
                return -float(val[1:-1])
            return float(val)
        except:
            return None

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 13:
            continue

        results.append({
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

    return jsonify({
        "updated_at": datetime.utcnow().isoformat(),
        "count": len(results),
        "data": results
    })


# -----------------------
# ENTRY POINT (LAST LINE)
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



