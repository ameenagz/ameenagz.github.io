"""Load the raw CSVs into DuckDB and build the cleaned `trips` and `stations` tables."""
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    con = duckdb.connect(str(ROOT / "data" / "citibike.duckdb"))
    # SQL paths are relative to the project root
    con.execute(f"SET file_search_path = '{ROOT}'")
    con.execute((ROOT / "sql" / "01_clean.sql").read_text())

    raw = con.sql("SELECT count(*) FROM read_csv('data/raw/*.csv')").fetchone()[0]
    kept = con.sql("SELECT count(*) FROM trips").fetchone()[0]
    print(f"raw rides: {raw:,}  kept: {kept:,}  removed: {raw - kept:,}")


if __name__ == "__main__":
    main()
