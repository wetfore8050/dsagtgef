import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(exist_ok=True)

csv_files = sorted(DATA_DIR.glob("jma_eq_*.csv"))
html_path = OUT_DIR / "et_plot.html"

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
df = df.sort_values("datetime")

df["energy_joule"] = 10 ** (1.5 * df["magnitude"] + 4.8)
df["cum_energy_joule"] = df["energy_joule"].cumsum()
df["cum_count"] = np.arange(1, len(df) + 1)

fig = go.Figure()

# ---- ET（第1軸・対数）
fig.add_trace(
    go.Scatter(
        x=df["datetime"],
        y=df["cum_energy_joule"],
        mode="lines",
        name="Cumulative Energy (J)",
        yaxis="y1"
    )
)

# ---- NT（第2軸）
fig.add_trace(
    go.Scatter(
        x=df["datetime"],
        y=df["cum_count"],
        mode="lines",
        name="Cumulative Count",
        yaxis="y2"
    )
)


fig.update_layout(
    title="Cumulative Energy (ET) & Cumulative Number (NT)<br>青森県東方沖",
    template="plotly_white",
    hovermode="x unified",
    xaxis=dict(
        title="Time (JST)"
    ),
    yaxis=dict(
        title="Cumulative Energy (J)",
    ),
    yaxis2=dict(
        title="Cumulative Number",
        overlaying="y",
        side="right"
    ),
    legend=dict(
        x=0.01,
        y=0.99
    )
)

fig.write_html(
    html_path,
    include_plotlyjs="cdn",
    full_html=True
)

print(f"CSV files used: {len(csv_files)}")
print("Saved:", html_path)