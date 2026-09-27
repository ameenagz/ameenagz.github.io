-- Weekday morning peak (7:00-9:59): which stations fill up and which empty out?
-- net_per_morning > 0  -> more bikes arrive than leave (station fills; docks run out)
-- net_per_morning < 0  -> more bikes leave than arrive (station drains; bikes run out)
WITH peak AS (
    SELECT * FROM trips
    WHERE NOT is_weekend AND hour BETWEEN 7 AND 9 AND NOT missing_end
),
n_weekdays AS (
    SELECT count(*) AS n
    FROM range(DATE '2025-01-01', DATE '2026-01-01', INTERVAL 1 DAY) t(d)
    WHERE isodow(d) <= 5
),
dep AS (SELECT start_station_id AS station_id, count(*) AS departures FROM peak GROUP BY 1),
arr AS (SELECT end_station_id   AS station_id, count(*) AS arrivals   FROM peak GROUP BY 1)
SELECT
    s.station_name,
    s.city,
    s.lat,
    s.lng,
    coalesce(dep.departures, 0)                                        AS departures,
    coalesce(arr.arrivals, 0)                                          AS arrivals,
    round((coalesce(arr.arrivals, 0) - coalesce(dep.departures, 0))
          / (SELECT n FROM n_weekdays), 1)                             AS net_per_morning
FROM stations s
LEFT JOIN dep USING (station_id)
LEFT JOIN arr USING (station_id)
ORDER BY net_per_morning DESC, s.station_name;
