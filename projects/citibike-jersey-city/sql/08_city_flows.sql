-- Trips between and within Hoboken and Jersey City.
SELECT
    so.city AS from_city,
    se.city AS to_city,
    count(*) AS rides,
    round(count(*) / sum(count(*)) OVER (), 3) AS share
FROM trips t
JOIN stations so ON so.station_id = t.start_station_id
JOIN stations se ON se.station_id = t.end_station_id
GROUP BY ALL
ORDER BY rides DESC;
