import pandas as pd
import plotly.express as px
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(exist_ok=True)

csv_files = sorted(DATA_DIR.glob("jma_eq_*.csv"))
html_path = OUT_DIR / "yt_plot.html"

if len(csv_files) == 0:
    raise RuntimeError("CSVなし")

dfs = []
for csv_path in csv_files:
    df = pd.read_csv(csv_path)
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

df = df[df["region"] == "青森県東方沖"]
df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")
df["depth_km"] = pd.to_numeric(df["depth_km"], errors="coerce")

df["datetime"] = pd.to_datetime(
    df["year"].astype(str) + "-" +
    df["month"].astype(str).str.zfill(2) + "-" +
    df["day"].astype(str).str.zfill(2) + " " +
    df["time_hm"] + ":" +
    df["second"].astype(str),
    errors="coerce"
)

df = df.dropna(subset=["datetime", "latitude", "magnitude", "depth_km"])
df = df.sort_values("datetime")

fig = px.scatter(
    df,
    x="datetime",
    y="longitude",
    size="magnitude",
    color="depth_km",
    range_color=(0, 70),  
    color_continuous_scale="Viridis",
    size_max=18,
    hover_data={
        "longitude": True,
        "depth_km": True,
        "magnitude": True,
        "region": False
    },
    labels={
        "datetime": "Time (JST)",
        "latitude": "Longitude (°E)",
        "depth_km": "Depth (km)",
        "magnitude": "Magnitude"
    },
    title="XT Plot (Longitude–Time) : 青森県東方沖"
)

fig.update_layout(
    template="plotly_white",
    hovermode="closest",
    xaxis=dict(
        title="Time (JST)"
    ),
    yaxis=dict(
        title="Longitude (°E)"
    )
)

fig.write_html(
    html_path,
    include_plotlyjs="cdn",
    full_html=True
)

print(f"CSV files used: {len(csv_files)}")
print("Saved:", html_path)