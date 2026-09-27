-- Headline numbers for the year.
SELECT
    count(*)                                                     AS total_rides,
    round(count(*) / 365.0)                                      AS avg_rides_per_day,
    (SELECT count(*) FROM stations)                              AS stations,
    round(avg((member_casual = 'member')::INT), 3)               AS member_share,
    round(avg((rideable_type = 'electric_bike')::INT), 3)        AS ebike_share,
    round(median(duration_min), 1)                               AS median_duration_min,
    round(median(distance_km) FILTER (WHERE NOT missing_end), 2) AS median_distance_km
FROM trips;
