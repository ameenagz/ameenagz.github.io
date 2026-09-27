-- Average rides per hour for each day of the week (2025 has 52 or 53 of each weekday).
WITH days AS (
    SELECT isodow(d) AS dow, count(*) AS n_days
    FROM range(DATE '2025-01-01', DATE '2026-01-01', INTERVAL 1 DAY) t(d)
    GROUP BY 1
)
SELECT
    t.dow,
    t.hour,
    round(count(*) / any_value(days.n_days), 1) AS avg_rides
FROM trips t
JOIN days USING (dow)
GROUP BY t.dow, t.hour
ORDER BY t.dow, t.hour;
