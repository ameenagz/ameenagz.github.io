"""Export compact summary tables to a SQLite file for the in-browser SQL playground."""
import sqlite3
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "playground" / "citibike.sqlite"

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


if __name__ == "__main__":
    main()
