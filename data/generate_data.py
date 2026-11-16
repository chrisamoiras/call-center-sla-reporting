"""Generate FICTIONAL (synthetic) multi-client BPO call center data for practice.
Daily CSV exports (one per day) like a telephony system would drop in a folder.
"""
import numpy as np, pandas as pd, os, datetime as dt

rng = np.random.default_rng(2026)
OUT = "call_center_practice"  # output folder, relative to where you run the script
for sub in ("daily_exports", "new_week", "reference"):
    os.makedirs(f"{OUT}/{sub}", exist_ok=True)

clients = pd.DataFrame([
    # client_id, client_name, queue_language, sla_target_pct, sla_threshold_sec, abandon_target_pct, aht_target_sec, csat_target, contract_start
    ["C01", "NordTech Software", "German", 80, 20, 5, 340, 4.2, "2025-03-01"],
    ["C02", "BrightMobile Telecom", "English", 80, 30, 6, 300, 4.0, "2024-06-01"],
    ["C03", "Gulf Home Retail", "Arabic", 75, 30, 7, 250, 4.0, "2025-09-01"],
    ["C04", "CloudNest Hosting", "English", 85, 20, 4, 480, 4.3, "2026-09-14"],  # new client launch mid-period
], columns=["client_id", "client_name", "queue_language", "sla_target_pct", "sla_threshold_sec",
            "abandon_target_pct", "aht_target_sec", "csat_target", "contract_start"])

# agents
first = ["Nikos","Maria","Giorgos","Eleni","Kostas","Anna","Dimitris","Sofia","Yannis","Katerina","Petros","Ioanna",
         "Lukas","Hannah","Jonas","Lea","Felix","Mia","Omar","Layla","Karim","Nour","Sami","Rania","Alex","Chloe",
         "Daniel","Emma","Leo","Zoe","Marco","Ines","Tom","Nina","Paul","Sara","Adam","Lina","Max","Eva"]
last_initials = list("ABCDEFGHKLMNPRSTVZ")
rows = []
team_plan = {"C01": 12, "C02": 16, "C03": 10, "C04": 11}
aid = 100
for cid, n in team_plan.items():
    for i in range(n):
        aid += 1
        if cid == "C04":
            hire = dt.date(2026, 8, 24) + dt.timedelta(days=int(rng.integers(0, 14)))
        else:
            hire = dt.date(2023, 1, 1) + dt.timedelta(days=int(rng.integers(0, 1200)))
        rows.append([f"A{aid}", f"{rng.choice(first)} {rng.choice(last_initials)}.", f"Team {cid}", cid,
                     clients.set_index("client_id").loc[cid, "queue_language"], hire.isoformat()])
agents = pd.DataFrame(rows, columns=["agent_id","agent_name","team","client_id","language","hire_date"])

start = dt.date(2026, 8, 3)   # Monday, ISO 2026-W32
hist_days = 13 * 7            # 13 weeks -> 2026-11-01
new_days = 7                  # 2026-11-02 .. 2026-11-08 (new week for refresh practice)
all_days = [start + dt.timedelta(days=i) for i in range(hist_days + new_days)]

base_daily = {"C01": 260, "C02": 420, "C03": 230, "C04": 210}
weekday_f = [1.15, 1.05, 1.0, 1.0, 0.95, 0.45, 0.30]
# intraday profile over 30-min intervals 08:00-20:00 (24 intervals)
prof = np.array([2,4,6,8,9,9,8,7,6,7,8,8,7,6,5,5,4,4,3,3,2,2,1,1], float); prof /= prof.sum()
# business-hour shapes per client (Arabic client earlier peak)
prof_c03 = np.roll(prof, -2); prof_c03 /= prof_c03.sum()

aht_base = {"C01": 400, "C02": 340, "C03": 290, "C04": 470}
call_rows = []
cid_counter = 0
for d in all_days:
    wd = d.weekday()
    for c in clients.itertuples():
        cs = dt.date.fromisoformat(c.contract_start)
        if d < cs:
            continue
        vol = base_daily[c.client_id] * weekday_f[wd]
        # trend & events
        if c.client_id == "C02":
            vol *= 1 + 0.002 * (d - start).days  # growing
            if dt.date(2026, 9, 21) <= d <= dt.date(2026, 9, 25):
                vol *= 1.6  # billing outage spike
        if c.client_id == "C04":
            weeks_live = (d - cs).days / 7
            vol *= 1.5 if weeks_live < 2 else 1.0  # launch spike
        if c.client_id == "C03" and d.month == 10:
            vol *= 1.1
        if d == dt.date(2026, 8, 15):
            vol *= 0.8
        n_calls = rng.poisson(vol)
        if n_calls == 0:
            continue
        p = prof_c03 if c.client_id == "C03" else prof
        interval_counts = rng.multinomial(n_calls, p)
        team = agents[agents.client_id == c.client_id]
        # staffing: available agents per day (absences); understaffing events
        avail_share = rng.uniform(0.78, 0.95)
        if c.client_id == "C01" and dt.date(2026, 10, 12) <= d <= dt.date(2026, 10, 23):
            avail_share *= 0.72  # sickness wave / 2 agents resigned
        if c.client_id == "C04" and (d - cs).days < 14:
            avail_share *= 0.85
        eligible = team[team.hire_date <= d.isoformat()]
        n_av = max(2, round(len(eligible) * avail_share * (0.5 if wd >= 5 else 1)))
        on_shift = eligible.sample(n_av, random_state=int(rng.integers(0, 1e9)))
        for k, cnt in enumerate(interval_counts):
            if cnt == 0:
                continue
            # load-based wait: occupancy proxy
            staff = max(2, n_av * (0.55 if k < 2 or k > 20 else 1.0))
            load = cnt * aht_base[c.client_id] / 1800  # erlangs in 30 min
            occ = min(load / staff, 0.995)
            mean_wait = 4 + 75 * occ ** 3 / (1 - occ + 0.05)
            mean_wait = min(mean_wait, 600)
            t0 = dt.datetime.combine(d, dt.time(8, 0)) + dt.timedelta(minutes=30 * k)
            for _ in range(cnt):
                cid_counter += 1
                call_start = t0 + dt.timedelta(seconds=int(rng.integers(0, 1800)))
                wait = int(rng.exponential(mean_wait))
                patience = rng.exponential(170 if c.client_id != "C03" else 130)
                abandoned = wait > patience and wait > 5
                if abandoned:
                    wait = int(max(6, patience))
                    call_rows.append([f"CL{cid_counter:07d}", c.client_id, c.queue_language, call_start, wait, 0,
                                      "", "", "", "", "", "", "Abandoned"])
                    continue
                ag = on_shift.sample(1, random_state=int(rng.integers(0, 1e9))).iloc[0]
                tenure_days = (d - dt.date.fromisoformat(ag.hire_date)).days
                newbie = 1.35 if tenure_days < 60 else (1.12 if tenure_days < 120 else 1.0)
                talk = int(rng.gamma(4, aht_base[c.client_id] * 0.62 * newbie / 4))
                hold = int(rng.exponential(25 * newbie)) if rng.random() < 0.35 else 0
                acw = int(rng.gamma(3, aht_base[c.client_id] * 0.18 * newbie / 3))
                fcr_p = 0.78 - 0.08 * (newbie - 1) * 3 - (0.1 if c.client_id == "C02" and dt.date(2026, 9, 21) <= d <= dt.date(2026, 9, 25) else 0)
                fcr = int(rng.random() < max(0.4, fcr_p))
                csat = ""
                if rng.random() < 0.22:
                    mu = 4.4 - 0.004 * wait - (0.6 if not fcr else 0) - 0.15 * (newbie - 1) * 3
                    csat = int(np.clip(round(rng.normal(mu, 0.8)), 1, 5))
                call_rows.append([f"CL{cid_counter:07d}", c.client_id, c.queue_language, call_start, wait, 1,
                                  ag.agent_id, talk, hold, acw, fcr, csat, "Answered"])

calls = pd.DataFrame(call_rows, columns=["call_id","client_id","queue","call_start","wait_sec","answered",
                                         "agent_id","talk_sec","hold_sec","acw_sec","resolved_first_contact",
                                         "csat_score","call_status"])
calls = calls.sort_values("call_start").reset_index(drop=True)
calls["call_start"] = calls.call_start.dt.strftime("%Y-%m-%d %H:%M:%S")
calls["_date"] = calls.call_start.str[:10]

last_hist = (start + dt.timedelta(days=hist_days - 1)).isoformat()
for day, g in calls.groupby("_date"):
    folder = "daily_exports" if day <= last_hist else "new_week"
    g.drop(columns="_date").to_csv(f"{OUT}/{folder}/calls_{day}.csv", index=False)

hist = calls[calls._date <= last_hist].drop(columns="_date")
hist.to_csv(f"{OUT}/calls_history.csv", index=False)
clients.to_csv(f"{OUT}/reference/clients_sla.csv", index=False)
agents.to_csv(f"{OUT}/reference/agents.csv", index=False)
print(len(calls), len(hist), calls._date.min(), calls._date.max(), last_hist)
