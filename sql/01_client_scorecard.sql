-- Client scorecard for the whole period (03/08 – 01/11/2026), fictional data
-- KPIs per client next to the contract targets
SELECT
    c.client_id,
    cl.client_name,
    COUNT(*)                                            AS offered,
    SUM(c.answered)                                     AS answered,
    ROUND(100.0 * SUM(CASE WHEN c.answered = 1
                            AND c.wait_sec <= cl.sla_threshold_sec
                           THEN 1 ELSE 0 END) / COUNT(*), 1) AS sla_pct,
    cl.sla_target_pct,
    ROUND(100.0 * SUM(1 - c.answered) / COUNT(*), 1)   AS abandon_pct,
    cl.abandon_target_pct,
    ROUND(AVG(c.talk_sec + c.hold_sec + c.acw_sec), 0) AS aht_sec,      -- NULL for abandoned calls, ignored by AVG
    cl.aht_target_sec,
    ROUND(AVG(CASE WHEN c.answered = 1 THEN c.wait_sec END), 1) AS asa_sec,
    ROUND(100.0 * AVG(c.resolved_first_contact), 1)    AS fcr_pct,
    ROUND(AVG(c.csat_score), 2)                         AS csat,
    cl.csat_target
FROM calls c
JOIN clients cl ON cl.client_id = c.client_id
GROUP BY c.client_id, cl.client_name
ORDER BY c.client_id;
