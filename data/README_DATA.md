# Data dictionary

**Fictional (synthetic) practice data.** Clients, agents and calls are invented and do not describe any real company.

Scenario: a call-center outsourcing company (BPO) in Athens answers calls for 4 clients in 3 languages. Every night the phone system drops one CSV with the day's calls into a folder. The weekly contractual SLA report per client must be produced without manual copy-paste.

## Files created by `generate_data.py`

| File / folder | Content |
|---|---|
| `daily_exports/calls_YYYY-MM-DD.csv` | 91 files, one per day, 03/08/2026 – 01/11/2026 (13 weeks) |
| `new_week/` | 7 files for 02/11 – 08/11/2026, used to test the automatic refresh |
| `calls_history.csv` | All calls of the 13 weeks in one file (84,077 rows), for SQLite |
| `reference/clients_sla.csv` | The 4 clients and their contract targets |
| `reference/agents.csv` | 49 agents, team, language, hire date |

## Columns of `calls_*.csv`

| Column | Meaning |
|---|---|
| `call_id` | Unique call ID |
| `client_id` | Client (C01–C04) |
| `queue` | Queue language (German / English / Arabic) |
| `call_start` | Date and time the call entered the queue (`YYYY-MM-DD HH:MM:SS`) |
| `wait_sec` | Seconds waited until answered or abandoned |
| `answered` | 1 = answered, 0 = caller hung up (abandoned) |
| `agent_id` | Agent who answered (empty if abandoned) |
| `talk_sec` | Talk time |
| `hold_sec` | Hold time during the call |
| `acw_sec` | After-call work (notes after the call) |
| `resolved_first_contact` | 1 = resolved on first contact (FCR), 0 = not |
| `csat_score` | Satisfaction score 1–5 (only callers who answered the survey, ~22%) |
| `call_status` | Answered / Abandoned |

## Columns of `clients_sla.csv`

`sla_target_pct` and `sla_threshold_sec`: e.g. 80 / 20 means "80% of calls answered within 20 seconds". Also `abandon_target_pct` (maximum abandonment), `aht_target_sec` (maximum average handle time), `csat_target` (minimum), `contract_start` (C04 started on 14/09/2026).

## KPI definitions

- **Offered calls** = all calls (answered + abandoned).
- **Service Level (SLA %)** = calls answered within the client's threshold ÷ offered calls.
- **Abandon rate** = abandoned ÷ offered (lower is better).
- **AHT (Average Handle Time)** = average of talk + hold + after-call work on answered calls (lower is better, read together with FCR).
- **ASA (Average Speed of Answer)** = average wait on answered calls.
- **FCR %** = average of `resolved_first_contact` on answered calls.
- **CSAT** = average `csat_score` where a score exists.
