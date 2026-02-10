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
