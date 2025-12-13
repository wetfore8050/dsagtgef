import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(exist_ok=True)

csv_files = sorted(DATA_DIR.glob("jma_eq_*.csv"))
html_path = OUT_DIR / "xy_plot.html"

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

size = df["magnitude"] * 3

fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=[
        "XY (Longitude–Latitude)",
        "DY (Depth–Latitude)",
        "DX (Longitude–Depth)",
        ""
    ],
    horizontal_spacing=0.12,
    vertical_spacing=0.15
)


fig.add_trace(
    go.Scatter(
        x=df["longitude"],
        y=df["latitude"],
        mode="markers",
        marker=dict(
            size=size,
            color=df["magnitude"],
            colorscale="Viridis",
            cmin=0,
            cmax=10,
            colorbar=dict(title="Magnitude"),
            showscale=True
        ),
        name="XY"
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=df["depth_km"],
        y=df["latitude"],
        mode="markers",
        marker=dict(
            size=size,
            color=df["magnitude"],
            colorscale="Viridis",
            cmin=0,
            cmax=10,
            showscale=False
        ),
        name="DY"
    ),
    row=1, col=2
)


fig.add_trace(
    go.Scatter(
        x=df["longitude"],
        y=df["depth_km"],
        mode="markers",
        marker=dict(
            size=size,
            color=df["magnitude"],
            colorscale="Viridis",
            cmin=0,
            cmax=10,
            showscale=False
        ),
        name="DX"
    ),
    row=2, col=1
)


fig.update_xaxes(title_text="Longitude (°E)", row=1, col=1)
fig.update_yaxes(title_text="Latitude (°N)", row=1, col=1)

fig.update_xaxes(title_text="Depth (km)", row=1, col=2)
fig.update_yaxes(title_text="Latitude (°N)", row=1, col=2)

fig.update_xaxes(title_text="Longitude (°E)", row=2, col=1)
fig.update_yaxes(
    title_text="Depth (km)",
    autorange="reversed",
    row=2, col=1
)


fig.update_layout(
    title="XY / DY / DX Plots : 青森県東方沖",
    template="plotly_white",
    hovermode="closest",
    showlegend=False,
    height=800
)


fig.write_html(
    html_path,
    include_plotlyjs="cdn",
    full_html=True
)

print("Saved:", html_path)