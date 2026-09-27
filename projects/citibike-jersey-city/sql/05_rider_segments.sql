-- How members and casual riders use the system differently.
SELECT
    member_casual                                              AS rider_type,
    count(*)                                                   AS rides,
    round(count(*) / sum(count(*)) OVER (), 3)                 AS share_of_rides,
    round(median(duration_min), 1)                             AS median_duration_min,
    round(median(distance_km) FILTER (WHERE NOT missing_end), 2) AS median_distance_km,
    round(avg(is_weekend::INT), 3)                             AS weekend_share,
    round(avg((rideable_type = 'electric_bike')::INT), 3)      AS ebike_share,
    round(avg((start_station_id = end_station_id)::INT), 3)    AS round_trip_share
FROM trips
GROUP BY member_casual
ORDER BY rides DESC;
