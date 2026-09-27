-- Build a clean trips table from the raw monthly CSVs.
-- Rules (documented in README "Data cleaning"):
--   * keep rides that START in 2025 (the Jan file includes a few Dec-31-2024 rides)
--   * drop rides under 60 seconds (false starts / re-docks, per Citi Bike's own guidance)
--   * drop rides over 24 hours (lost, stolen or unreturned bikes)
--   * keep rides with a missing end station, but flag them; they are excluded from flow analysis
CREATE OR REPLACE TABLE trips AS
WITH raw AS (
    SELECT *
    FROM read_csv('data/raw/*.csv', header = true,
                  types = {'start_station_id': 'VARCHAR', 'end_station_id': 'VARCHAR'})
)
SELECT
    ride_id,
    rideable_type,
    member_casual,
    started_at,
    ended_at,
    date_diff('second', started_at, ended_at) / 60.0              AS duration_min,
    start_station_id,
    start_station_name,
    end_station_id,
    end_station_name,
    start_lat, start_lng, end_lat, end_lng,
    -- straight-line (haversine) distance in km; a lower bound on distance ridden
    2 * 6371 * asin(sqrt(
        power(sin(radians(end_lat - start_lat) / 2), 2) +
        cos(radians(start_lat)) * cos(radians(end_lat)) *
        power(sin(radians(end_lng - start_lng) / 2), 2)))         AS distance_km,
    end_station_id IS NULL                                        AS missing_end,
    date_trunc('month', started_at)::DATE                         AS month,
    hour(started_at)                                              AS hour,
    isodow(started_at)                                            AS dow,       -- 1 = Mon
    isodow(started_at) >= 6                                       AS is_weekend
FROM raw
WHERE year(started_at) = 2025
  AND date_diff('second', started_at, ended_at) BETWEEN 60 AND 86400;

-- One row per station. A few IDs appear under more than one spelling of the name,
-- so take the most common name and the average coordinates.
CREATE OR REPLACE TABLE stations AS
SELECT
    start_station_id                               AS station_id,
    mode(start_station_name)                       AS station_name,
    CASE WHEN start_station_id LIKE 'HB%' THEN 'Hoboken' ELSE 'Jersey City' END AS city,
    avg(start_lat)                                 AS lat,
    avg(start_lng)                                 AS lng
FROM trips
WHERE start_station_id IS NOT NULL
GROUP BY start_station_id;
