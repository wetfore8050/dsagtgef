import requests
from lxml import html
from datetime import datetime, timedelta, timezone
import csv
import re
from pathlib import Path

JST = timezone(timedelta(hours=9))
target_date = datetime.now(JST).date() - timedelta(days=1)

#yyyymmdd = target_date.strftime("%Y%m%d")
yyyymmdd = "20251208"
#yyyy = target_date.strftime("%Y")
#mm = target_date.strftime("%m")
#dd = target_date.strftime("%d")

url = f"https://www.data.jma.go.jp/eqev/data/daily_map/{yyyymmdd}.html"
print("URL:", url)


#エラー対策
headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers)
res.raise_for_status()

tree = html.fromstring(res.content)

texts = tree.xpath("//pre/text()")
if len(texts) == 0:
    raise RuntimeError("preテキストが取得できません")

full_text = "".join(texts)

def degmin_to_decimal(deg, minute, hemi):
    deg = float(deg)
    minute = float(minute)

    val = deg + minute / 60.0
    if hemi in ("S", "W"):
        val *= -1

    return round(val, 5)

pattern = re.compile(
    r"""
    (\d{4})\s+
    (\d{1,2})\s+
    (\d{1,2})\s+
    (\d{2}:\d{2})\s+
    ([\d.]+)\s+
    (\d+)\s*[°]\s*([\d.]+)'\s*([NS])\s+
    (\d+)\s*[°]\s*([\d.]+)'\s*([EW])\s+
    (\d{1,3})\s+
    (-?[\d.]+|-)\s+
    (.+)
    """,
    re.VERBOSE
)

out_dir = Path("data")
out_dir.mkdir(exist_ok=True, parents=True)

csv_path = out_dir / f"jma_eq_{yyyymmdd}.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "year", "month", "day", 
        "time_hm", "second",
        "latitude", "longitude",
        "depth_km", "magnitude", 
        "region"
    ])

    for line in full_text.splitlines():
        m = pattern.match(line)
        if not m:
            continue

        (year, month, day, time, sec, lat_deg, lat_min, lat_ns, lon_deg, lon_min, lon_ew, depth, mag, region) = m.groups()
        lat = degmin_to_decimal(lat_deg, lat_min, lat_ns)
        lon = degmin_to_decimal(lon_deg, lon_min, lon_ew)

        writer.writerow([
            year, month, day, time,
            sec, lat, lon, depth, mag, region.strip()
        ])
    
print("Saved:", csv_path)