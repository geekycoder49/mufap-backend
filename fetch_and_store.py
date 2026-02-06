import requests, sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=3"

conn = sqlite3.connect("navs.db")
cursor = conn.cursor()

response = requests.get(URL, timeout=30)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")
headers = [th.text.strip() for th in table.find_all("th")]

def idx(name):
    return headers.index(name)

fund_i = idx("Fund")
nav_i = idx("NAV")
date_i = idx("Validity Date")

rows = table.find_all("tr")[1:]
now = datetime.utcnow().isoformat()

for row in rows:
    cols = [td.text.strip() for td in row.find_all("td")]
    if len(cols) > max(fund_i, nav_i, date_i):
        cursor.execute(
            "INSERT INTO nav_history (fund, nav, nav_date, fetched_at) VALUES (?, ?, ?, ?)",
            (cols[fund_i], float(cols[nav_i]), cols[date_i], now)
        )

conn.commit()
conn.close()
print("NAVs stored")
