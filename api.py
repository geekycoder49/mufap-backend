import requests
from flask import Flask, jsonify
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

MUFAP_URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=3"


@app.route("/")
def home():
    return {"status": "ok", "source": "live MUFAP"}


@app.route("/navs/latest")
def latest_navs():
    response = requests.get(MUFAP_URL, timeout=20)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    rows = table.find("tbody").find_all("tr")

    navs = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) < 8:
            continue

        fund = cols[2]
        nav = cols[7]
        date = cols[8]

        try:
            navs.append({
                "fund": fund,
                "nav": float(nav),
                "date": date
            })
        except:
            continue

    return jsonify({
        "updated_at": datetime.utcnow().isoformat(),
        "count": len(navs),
        "data": navs
    })


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

@app.route("/returns/latest")
def fund_returns():
    import requests
    from bs4 import BeautifulSoup

    url = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=1"
    response = requests.get(url, timeout=20)

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    rows = table.find("tbody").find_all("tr")

    results = []

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]

        if len(cols) < 13:
            continue

        fund = cols[2]

        def to_float(val):
            try:
                return float(val.replace("%", ""))
            except:
                return None

        results.append({
            "fund": fund,
            "returns": {
                "1d": to_float(cols[4]),
                "15d": to_float(cols[5]),
                "30d": to_float(cols[6]),
                "90d": to_float(cols[7]),
                "180d": to_float(cols[8]),
                "270d": to_float(cols[9]),
                "365d": to_float(cols[10]),
                "2y": to_float(cols[11]),
                "3y": to_float(cols[12])
            }
        })

    return {
        "count": len(results),
        "data": results
    }


