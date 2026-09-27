"""Download the 2025 Citi Bike Jersey City trip files and unzip the CSVs into data/raw/."""
import io
import urllib.request
import zipfile
from pathlib import Path

BASE_URL = "https://s3.amazonaws.com/tripdata/"
YEAR = 2025
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def file_names(month: int) -> list[str]:
    # Citi Bike isn't consistent with names (e.g. JC-202510-citibike-tripdata.zip), so try both.
    stem = f"JC-{YEAR}{month:02d}-citibike-tripdata"
    return [f"{stem}.csv.zip", f"{stem}.zip"]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for month in range(1, 13):
        for name in file_names(month):
            try:
                with urllib.request.urlopen(BASE_URL + name) as resp:
                    payload = resp.read()
            except urllib.error.HTTPError:
                continue
            with zipfile.ZipFile(io.BytesIO(payload)) as zf:
                for member in zf.namelist():
                    if member.endswith(".csv") and not member.startswith("__MACOSX"):
                        (RAW_DIR / Path(member).name).write_bytes(zf.read(member))
            print(f"downloaded {name}")
            break
        else:
            raise SystemExit(f"no file found for {YEAR}-{month:02d}")


if __name__ == "__main__":
    main()
