-- Weekly Service Level and abandonment per client (week starts on Monday), fictional data
WITH weekly AS (
    SELECT
        c.client_id,
        date(c.call_start, 'weekday 0', '-6 days') AS week_start,   -- Monday of the call's week
        COUNT(*) AS offered,
        SUM(CASE WHEN c.answered = 1
                  AND c.wait_sec <= cl.sla_threshold_sec
                 THEN 1 ELSE 0 END)                AS answered_in_sla,
        SUM(1 - c.answered)                        AS abandoned
    FROM calls c
    JOIN clients cl ON cl.client_id = c.client_id
    GROUP BY c.client_id, week_start
)
SELECT
    w.client_id,
    w.week_start,
    w.offered,
    ROUND(100.0 * w.answered_in_sla / w.offered, 1) AS sla_pct,
    cl.sla_target_pct,
    ROUND(100.0 * w.abandoned / w.offered, 1)       AS abandon_pct,
    cl.abandon_target_pct,
    CASE WHEN 100.0 * w.answered_in_sla / w.offered < cl.sla_target_pct
         THEN 'MISS' ELSE 'OK' END                  AS sla_status
FROM weekly w
JOIN clients cl ON cl.client_id = w.client_id
ORDER BY w.client_id, w.week_start;
