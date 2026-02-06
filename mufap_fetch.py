import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.mufap.com.pk/Industry/IndustryStatDaily?tab=3"

response = requests.get(URL, timeout=30)
soup = BeautifulSoup(response.text, "html.parser")

table = soup.find("table")

# Read headers (including hidden)
headers = [th.text.strip() for th in table.find_all("th")]

def idx(name):
    return headers.index(name)

fund_i = idx("Fund")
nav_i = idx("NAV")
date_i = idx("Validity Date")

rows = table.find_all("tr")[1:]

data = []

for row in rows:
    cols = [td.text.strip() for td in row.find_all("td")]

    if len(cols) > max(fund_i, nav_i, date_i):
        data.append({
            "fund": cols[fund_i],
            "nav": float(cols[nav_i]),
            "date": cols[date_i]
        })

# Print JSON (for testing)
print(json.dumps(data, indent=2))
