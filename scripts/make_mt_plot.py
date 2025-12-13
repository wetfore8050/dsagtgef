import pandas as pd
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(exist_ok=True)

csv_files = sorted(DATA_DIR.glob("jma_eq_*.csv"))
html_path = OUT_DIR / "mt_plot.html"

if len(csv_files) == 0:
    raise RuntimeError("CSVなし")

dfs = []
for csv_path in csv_files:
    df = pd.read_csv(csv_path)
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

df = df[df["region"] == "青森県東方沖"]
df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")

df["datetime"] = pd.to_datetime(
    df["year"].astype(str) + "-" +
    df["month"].astype(str).str.zfill(2) + "-" +
    df["day"].astype(str).str.zfill(2) + " " +
    df["time_hm"] + ":" +
    df["second"].astype(str),
    errors="coerce"
)

df = df.dropna(subset=["datetime", "magnitude"])

fig = px.scatter(
    df,
    x="datetime",
    y="magnitude",
    size="magnitude",
    color="depth_km",
    hover_data={
        "latitude": True,
        "longitude": True,
        "depth_km": True,
        "region": True
    },
    labels={
        "datetime": "Time (JST)",
        "magnitude": "Magnitude",
        "depth_km": "Depth (km)"
    },
    title = "MT Plot"
)

fig.update_layout(
    template="plotly_white",
    hovermode="closest"
)

fig.write_html(
    html_path,
    include_plotlyjs="cdn",
    full_html=True
)

print("OK")