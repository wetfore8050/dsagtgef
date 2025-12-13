import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(exist_ok=True)

csv_files = sorted(DATA_DIR.glob("jma_eq_*.csv"))
html_path = OUT_DIR / "xyt_plot.html"

if len(csv_files) == 0:
    raise RuntimeError("CSVなし")

dfs = []
for csv_path in csv_files:
    df = pd.read_csv(csv_path)
    dfs.append(df)

df = pd.concat(dfs, ignore_index=True)

df = df[df["region"] == "青森県東方沖"]
df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
df["depth_km"] = pd.to_numeric(df["depth_km"], errors="coerce")
df["magnitude"] = pd.to_numeric(df["magnitude"], errors="coerce")

df = df.dropna(subset=["longitude", "latitude", "depth_km", "magnitude"])

df["datetime"] = pd.to_datetime(
    df["year"].astype(str) + "-" +
    df["month"].astype(str).str.zfill(2) + "-" +
    df["day"].astype(str).str.zfill(2) + " " +
    df["time_hm"] + ":" +
    df["second"].astype(str),
    errors="coerce"
)

# 日単位
df["date"] = df["datetime"].dt.date
dates = sorted(df["date"].unique())

# マーカーサイズ
df["size"] = df["magnitude"] * 4

lon_min = df["longitude"].min()
lon_max = df["longitude"].max()
lat_min = df["latitude"].min()
lat_max = df["latitude"].max()

fig = go.Figure()

for i, d in enumerate(dates):
    ddf = df[df["date"] == d]

    fig.add_trace(
        go.Scatter(
            x=ddf["longitude"],
            y=ddf["latitude"],
            mode="markers",
            visible=(i == 0),
            marker=dict(
                size=ddf["size"],
                color=ddf["depth_km"],
                colorscale="Viridis",
                cmin=0,
                cmax=70,
                showscale=True,               # ← 常にカラーバー表示
                colorbar=dict(
                    title="Depth (km)",
                    len=0.9
                ),
                opacity=0.8
            ),
            hovertemplate=(
                "Lon: %{x:.2f}<br>"
                "Lat: %{y:.2f}<br>"
                "Depth: %{marker.color:.1f} km<br>"
                "M: %{marker.size:.1f}<extra></extra>"
            )
        )
    )


steps = []
for i, d in enumerate(dates):
    steps.append(
        dict(
            method="update",
            args=[
                {"visible": [j == i for j in range(len(dates))]},
                {"title": f"XY Plot（青森県東方沖） : {d}"}
            ],
            label=str(d)
        )
    )

fig.update_layout(
    title=f"XY Plot（青森県東方沖） : {dates[0]}",
    xaxis=dict(
        title="Longitude (°E)",
        range=[lon_min, lon_max],   # ← 固定
        fixedrange=True
    ),
    yaxis=dict(
        title="Latitude (°N)",
        range=[lat_min, lat_max],   # ← 固定
        fixedrange=True
    ),
    sliders=[dict(
        active=0,
        currentvalue={"prefix": "Date: "},
        pad={"t": 50},
        steps=steps
    )],
    template="plotly_white",
    height=700,
    showlegend=False
)


fig.write_html(
    html_path,
    include_plotlyjs="cdn",
    full_html=True
)

print("Saved:", html_path)