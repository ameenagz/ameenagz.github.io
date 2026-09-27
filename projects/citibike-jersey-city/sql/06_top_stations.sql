-- Busiest stations by total activity (departures + arrivals).
WITH dep AS (
    SELECT start_station_id AS station_id, count(*) AS departures FROM trips GROUP BY 1
), arr AS (
    SELECT end_station_id AS station_id, count(*) AS arrivals FROM trips WHERE NOT missing_end GROUP BY 1
)
SELECT
    s.station_name,
    s.city,
    dep.departures,
    coalesce(arr.arrivals, 0)                  AS arrivals,
    dep.departures + coalesce(arr.arrivals, 0) AS total_activity
FROM dep
JOIN stations s USING (station_id)
LEFT JOIN arr USING (station_id)
ORDER BY total_activity DESC
LIMIT 15;
