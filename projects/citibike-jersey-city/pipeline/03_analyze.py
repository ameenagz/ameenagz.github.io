"""Run every analysis query, save results to outputs/, draw charts, and export dashboard data."""
import json
from pathlib import Path

import duckdb
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT, CHARTS = ROOT / "outputs", ROOT / "charts"

MEMBER, CASUAL, ACCENT, NEG = "#1D4ED8", "#14B8A6", "#0D9488", "#E11D48"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

plt.rcParams.update({
    "figure.dpi": 150, "font.size": 10, "axes.spines.top": False,
    "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlesize": 12,
})


def run_queries(con) -> dict[str, pd.DataFrame]:
    results = {}
    for path in sorted((ROOT / "sql").glob("0[2-9]_*.sql")):
        name = path.stem[3:]
        df = con.sql(path.read_text()).df()
        df.to_csv(OUT / f"{name}.csv", index=False)
        results[name] = df
    return results


def chart_monthly(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.2))
    labels = pd.to_datetime(df["month"]).dt.strftime("%b")
    ax.bar(labels, df["member_rides"] / 1000, color=MEMBER, label="Member")
    ax.bar(labels, df["casual_rides"] / 1000, bottom=df["member_rides"] / 1000, color=CASUAL, label="Casual")
    ax.set_ylabel("Rides (thousands)")
    ax.set_title("Ridership more than doubles from February to September")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(CHARTS / "monthly_rides.png")
    plt.close(fig)


def chart_heatmap(df: pd.DataFrame) -> None:
    grid = df.pivot(index="dow", columns="hour", values="avg_rides").reindex(range(1, 8)).fillna(0)
    fig, ax = plt.subplots(figsize=(10, 3.6))
    im = ax.imshow(grid.values, aspect="auto", cmap="Blues")
    ax.set_yticks(range(7), DAYS)
    ax.set_xticks(range(0, 24, 2), [f"{h}:00" for h in range(0, 24, 2)])
    ax.set_title("Weekday commute peaks at 8am and 5-6pm; weekends peak around midday")
    fig.colorbar(im, ax=ax, label="Avg rides / hour", shrink=0.8)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(CHARTS / "hour_by_weekday.png")
    plt.close(fig)


def chart_imbalance(df: pd.DataFrame, n: int = 8) -> None:
    top = pd.concat([df.head(n), df.tail(n)]).sort_values("net_per_morning")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    colors = [ACCENT if v > 0 else NEG for v in top["net_per_morning"]]
    ax.barh(top["station_name"], top["net_per_morning"], color=colors)
    ax.axvline(0, color="#555", lw=0.8)
    ax.set_xlabel("Net bikes gained per weekday morning, 7-10am (arrivals - departures)")
    fig.suptitle("Weekday mornings: bikes pile up at train terminals and drain from neighborhoods",
                 x=0.02, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "am_peak_imbalance.png")
    plt.close(fig)


def chart_segments(df: pd.DataFrame) -> None:
    metrics = [("median_duration_min", "Median ride (min)"), ("weekend_share", "Weekend share"),
               ("ebike_share", "E-bike share"), ("round_trip_share", "Round-trip share")]
    df = df.set_index("rider_type")
    fig, axes = plt.subplots(1, 4, figsize=(10, 3))
    for ax, (col, label) in zip(axes, metrics):
        vals = [df.loc["member", col], df.loc["casual", col]]
        ax.bar(["Member", "Casual"], vals, color=[MEMBER, CASUAL])
        ax.set_title(label, fontsize=10)
        fmt = "{:.1f}" if col.endswith("min") else "{:.0%}"
        for i, v in enumerate(vals):
            ax.text(i, v, fmt.format(v), ha="center", va="bottom", fontsize=9)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    fig.suptitle("Casual riders take longer, more leisurely trips", fontweight="bold")
    fig.tight_layout()
    fig.savefig(CHARTS / "rider_segments.png")
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    CHARTS.mkdir(exist_ok=True)
    con = duckdb.connect(str(ROOT / "data" / "citibike.duckdb"), read_only=True)
    r = run_queries(con)

    chart_monthly(r["monthly"])
    chart_heatmap(r["hour_by_weekday"])
    chart_imbalance(r["am_peak_imbalance"])
    chart_segments(r["rider_segments"])

    dashboard = {name: json.loads(df.to_json(orient="records")) for name, df in r.items()}
    (ROOT / "dashboard" / "data.json").write_text(json.dumps(dashboard, separators=(",", ":")))
    print("wrote", ", ".join(f"{k}.csv" for k in r))


if __name__ == "__main__":
    main()
