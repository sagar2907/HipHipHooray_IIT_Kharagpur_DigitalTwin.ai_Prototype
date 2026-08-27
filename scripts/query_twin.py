#!/usr/bin/env python3
"""Ask the twin's database the questions a long run exists to answer.

    python scripts/query_twin.py                 # the standard report
    python scripts/query_twin.py --sql "SELECT ..."   # anything else

Safe to run WHILE the plant is running - the store is in WAL mode, so reads
do not block the writer.

Every number this prints is traceable: results/twin.db, one row per tick, per
station, per alert. That is the point of keeping it rather than streaming it
into a browser and forgetting it.
"""

import argparse
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "results", "twin.db")

REPORT = [
 ("SESSIONS", """
  SELECT id, started_iso, run, speed, step_s,
         CASE calibrated WHEN 1 THEN printf('%.3f',ece_after) ELSE 'no' END AS ece,
         printf('%.3f', base_rate) AS base_rate
  FROM sessions ORDER BY id"""),

 ("VOLUME CAPTURED", """
  SELECT (SELECT COUNT(*) FROM frames)            AS frames,
         (SELECT COUNT(*) FROM rankings)          AS station_rows,
         (SELECT COUNT(*) FROM alerts)            AS alerts,
         (SELECT COUNT(*) FROM forming)           AS forming_rows,
         (SELECT COUNT(*) FROM tool_assessments)  AS tool_rows,
         (SELECT COUNT(*) FROM shifts)            AS shifts_done,
         (SELECT COUNT(DISTINCT run) FROM frames) AS distinct_runs"""),

 ("CONSTRAINT OCCUPANCY — who holds the line, across everything recorded", """
  SELECT constraint_st AS station, COUNT(*) AS ticks,
         printf('%.1f%%', 100.0*COUNT(*)/(SELECT COUNT(*) FROM frames
                                          WHERE constraint_st IS NOT NULL)) AS share
  FROM frames WHERE constraint_st IS NOT NULL
  GROUP BY constraint_st ORDER BY ticks DESC LIMIT 10"""),

 ("PRESCRIPTIONS ISSUED", """
  SELECT presc_sig AS signature, COUNT(*) AS n,
         printf('%.1f%%', 100.0*COUNT(*)/(SELECT COUNT(*) FROM frames
                                          WHERE presc_sig IS NOT NULL)) AS share
  FROM frames WHERE presc_sig IS NOT NULL
  GROUP BY presc_sig ORDER BY n DESC"""),

 ("ALERTS — rate and cost, vs the ISA-18.2 budget of 150/shift", """
  SELECT kind, COUNT(*) AS n,
         printf('%.2f', AVG(cost_vehicles)) AS avg_cost_vehicles,
         printf('%.2f', MAX(cost_vehicles)) AS max_cost_vehicles,
         printf('%.1f', AVG(persistence_min)) AS avg_persist_min
  FROM alerts GROUP BY kind"""),

 ("FORMING WARNINGS — how many name a station with NO sensors", """
  SELECT COUNT(*) AS forming_warnings,
         SUM(dark) AS naming_a_dark_station,
         printf('%.1f%%', 100.0*SUM(dark)/COUNT(*)) AS pct_dark
  FROM forming"""),

 ("TOOL DIAGNOSIS — repair vs recalibrate are opposite answers", """
  SELECT classification, COUNT(*) AS snapshots,
         COUNT(DISTINCT station||run) AS distinct_tools,
         printf('%.0f', AVG(contained_total)) AS avg_vehicles_contained
  FROM tool_assessments WHERE alarm=1
  GROUP BY classification ORDER BY snapshots DESC"""),

 ("STOP-OR-CONTINUE — the same fault gets opposite calls", """
  SELECT stop_decision, COUNT(*) AS n
  FROM tool_assessments WHERE alarm=1 AND stop_decision IS NOT NULL
  GROUP BY stop_decision ORDER BY n DESC"""),

 ("LOOP COST — is it real-time?", """
  SELECT printf('%.1f', AVG(compute_ms)) AS mean_ms,
         printf('%.1f', MAX(compute_ms)) AS max_ms,
         COUNT(*) AS ticks
  FROM frames"""),

 ("EVIDENCE DEPTH — station-rows per constraint call", """
  SELECT station, COUNT(*) AS times_ranked,
         printf('%.1f', AVG(effective_ct)) AS avg_eff_ct,
         printf('%.2f', AVG(blocked)) AS avg_blocked,
         printf('%.2f', AVG(starved)) AS avg_starved
  FROM rankings GROUP BY station ORDER BY avg_eff_ct DESC LIMIT 8"""),
]


def show(db, title, sql):
    try:
        cur = db.execute(sql)
    except sqlite3.Error as e:
        print(f"\n--- {title} ---\n  (query failed: {e})")
        return
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    print(f"\n--- {title} ---")
    if not rows:
        print("  (no data yet)")
        return
    w = [max(len(str(c)), max((len(str(r[i])) for r in rows), default=0))
         for i, c in enumerate(cols)]
    print("  " + "  ".join(str(c).ljust(w[i]) for i, c in enumerate(cols)))
    print("  " + "  ".join("-" * w[i] for i in range(len(cols))))
    for r in rows:
        print("  " + "  ".join(str(v).ljust(w[i]) for i, v in enumerate(r)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DB)
    ap.add_argument("--sql", help="run one query instead of the report")
    a = ap.parse_args()

    if not os.path.exists(a.db):
        sys.exit(f"no database at {a.db}\nStart the server without --no-record.")

    # read-only, so this can never disturb a running plant
    db = sqlite3.connect(f"file:{os.path.abspath(a.db)}?mode=ro", uri=True)
    if a.sql:
        show(db, "QUERY", a.sql)
    else:
        print(f"twin.db — {os.path.getsize(a.db)/1024:.0f} KB")
        for title, sql in REPORT:
            show(db, title, sql)
    db.close()


if __name__ == "__main__":
    main()
