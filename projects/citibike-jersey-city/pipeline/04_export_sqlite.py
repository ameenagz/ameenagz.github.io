"""Export compact summary tables for the website: a SQLite file for the in-browser SQL
playground, and station positions plus the busiest routes for the homepage animation."""
import json
import math
import sqlite3
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "playground" / "citibike.sqlite"
FLOWS = ROOT / "playground" / "flows.json"
TOP_ROUTES = 400
PER_STATION = 3

TABLES = {
    "stations": """
        SELECT station_id, station_name, city, round(lat, 5) AS lat, round(lng, 5) AS lng
        FROM stations ORDER BY station_id
    """,
    "daily": """
        SELECT strftime(started_at::DATE, '%Y-%m-%d')                    AS date,
               strftime(started_at::DATE, '%a')                          AS weekday,
               count(*)                                                  AS rides,
               count(*) FILTER (WHERE member_casual = 'member')          AS member_rides,
               count(*) FILTER (WHERE member_casual = 'casual')          AS casual_rides,
               count(*) FILTER (WHERE rideable_type = 'electric_bike')   AS ebike_rides,
               round(median(duration_min), 1)                            AS median_duration_min
        FROM trips GROUP BY 1, 2 ORDER BY 1
    """,
    "hourly": """
        SELECT dow AS weekday_num,
               ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][dow] AS weekday,
               hour, member_casual AS rider_type, count(*) AS rides
        FROM trips GROUP BY ALL ORDER BY 1, 3, 4
    """,
    "routes": """
        SELECT start_station_id, end_station_id,
               count(*)                                          AS rides,
               count(*) FILTER (WHERE member_casual = 'member')  AS member_rides,
               count(*) FILTER (WHERE member_casual = 'casual')  AS casual_rides,
               round(median(duration_min), 1)                    AS median_duration_min
        FROM trips WHERE NOT missing_end
        GROUP BY 1, 2 ORDER BY rides DESC
    """,
}


def export_flows(src) -> None:
    """Stations projected to a 0-1 box (north up) and the busiest routes between them."""
    stations = src.sql("""
        SELECT s.station_id, s.lat, s.lng, count(t.ride_id) AS departures
        FROM stations s LEFT JOIN trips t ON t.start_station_id = s.station_id
        GROUP BY ALL ORDER BY s.station_id
    """).fetchall()
    # The busiest routes overall, plus each station's own top routes so quieter
    # neighborhoods still show up in the animation.
    routes = src.sql(f"""
        WITH pairs AS (
            SELECT start_station_id, end_station_id, count(*) AS rides
            FROM trips
            WHERE NOT missing_end AND start_station_id <> end_station_id
              AND end_station_id IN (SELECT station_id FROM stations)
            GROUP BY ALL
        ), ranked AS (
            SELECT *,
                   row_number() OVER (ORDER BY rides DESC, start_station_id, end_station_id) AS overall,
                   row_number() OVER (PARTITION BY start_station_id
                                      ORDER BY rides DESC, end_station_id) AS per_station
            FROM pairs
        )
        SELECT start_station_id, end_station_id, rides
        FROM ranked
        WHERE overall <= {TOP_ROUTES} OR per_station <= {PER_STATION}
        ORDER BY rides DESC, start_station_id, end_station_id
    """).fetchall()

    mid_lat = math.radians(sum(r[1] for r in stations) / len(stations))
    xs = [r[2] * math.cos(mid_lat) for r in stations]
    ys = [-r[1] for r in stations]
    x0, y0 = min(xs), min(ys)
    span = max(max(xs) - x0, max(ys) - y0)
    top = max(r[3] for r in stations)
    index = {r[0]: i for i, r in enumerate(stations)}
    FLOWS.write_text(json.dumps({
        "w": round((max(xs) - x0) / span, 3),
        "h": round((max(ys) - y0) / span, 3),
        # [x, y, activity 0-1] per station
        "stations": [[round((x - x0) / span, 4), round((y - y0) / span, 4), round(r[3] / top, 3)]
                     for x, y, r in zip(xs, ys, stations)],
        # [from, to, rides] using station indexes
        "routes": [[index[a], index[b], n] for a, b, n in routes],
    }, separators=(",", ":")))
    print(f"wrote {FLOWS.relative_to(ROOT)} ({FLOWS.stat().st_size / 1024:.0f} KB)")


def main() -> None:
    src = duckdb.connect(str(ROOT / "data" / "citibike.duckdb"), read_only=True)
    OUT.parent.mkdir(exist_ok=True)
    OUT.unlink(missing_ok=True)
    dst = sqlite3.connect(OUT)
    for name, query in TABLES.items():
        df = src.sql(query).df()
        df.to_sql(name, dst, index=False)
        print(f"{name}: {len(df):,} rows")
    dst.execute("CREATE INDEX idx_routes_start ON routes(start_station_id)")
    dst.execute("CREATE INDEX idx_routes_end ON routes(end_station_id)")
    dst.commit()
    dst.execute("VACUUM")
    dst.close()
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1024:.0f} KB)")
    export_flows(src)


if __name__ == "__main__":
    main()
