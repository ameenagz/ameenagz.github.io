-- Seasonality: rides per month, split by rider type, plus e-bike share.
SELECT
    strftime(month, '%Y-%m')                                AS month,
    count(*)                                                AS rides,
    count(*) FILTER (WHERE member_casual = 'member')        AS member_rides,
    count(*) FILTER (WHERE member_casual = 'casual')        AS casual_rides,
    round(avg((rideable_type = 'electric_bike')::INT), 3)   AS ebike_share
FROM trips
GROUP BY month
ORDER BY month;
