-- Agents on shift and workload per week (weekdays only), fictional data
-- Used to test whether missed SLA weeks were caused by fewer agents or by more calls
WITH daily AS (
    SELECT
        client_id,
        date(call_start)                     AS call_date,
        COUNT(*)                             AS offered,
        COUNT(DISTINCT agent_id)             AS agents_on_shift,   -- NULL agent_id (abandoned) not counted
        SUM(answered)                        AS answered,
        SUM(talk_sec + hold_sec + acw_sec)   AS handle_sec
    FROM calls
    WHERE strftime('%w', call_start) NOT IN ('0', '6')   -- 0 = Sunday, 6 = Saturday
    GROUP BY client_id, call_date
)
SELECT
    client_id,
    date(call_date, 'weekday 0', '-6 days')              AS week_start,
    ROUND(AVG(offered), 0)                               AS avg_daily_offered,
    ROUND(AVG(agents_on_shift), 1)                       AS avg_agents_on_shift,
    ROUND(1.0 * SUM(answered) / SUM(agents_on_shift), 1) AS calls_per_agent_day,
    ROUND(1.0 * SUM(handle_sec) / SUM(answered), 0)      AS aht_sec
FROM daily
GROUP BY client_id, week_start
ORDER BY client_id, week_start;
