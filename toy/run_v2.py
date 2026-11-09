# -*- coding: utf-8 -*-
"""ACS toy: run one experiment and write its judged record.

  python3 run_v2.py [scenario] [key=value ...] [--out DIR] [--no-checks]

scenario: default | harsh | alone | no_drone | cooperative | explorer | long
key=value: any Config field, e.g.  steps=400  seed=3  snaps="((50,30),)"  bias_j="(4,2)"
Outputs (DIR, default outputs/v2/<scenario>):
  trace_<agent>.csv   every judged quantity per time step (sec.2-sec.7)
  org.csv             sec.8 organisation layer
  relations.csv       sec.6 relation descriptors per window
  events.md           timeline of state changes read off the judged record
  summary.json        paths (T_blk, T_col), counts of zones, blockage kinds, rescues, ...
  checks.txt          CR-1 / CR-2 / assumption witnesses / record checks (unless --no-checks)
  viewer.html         self-contained viewer (map, judged quantities per step, zone bands, events)
"""
import csv
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from acs_toy.config import SCENARIOS, parse_overrides           # noqa: E402
from acs_toy.sim import run                                       # noqa: E402
from acs_toy.judge import judge_run                               # noqa: E402
from acs_toy.events import timeline                               # noqa: E402

COLS = ["t", "name", "px", "py", "energy", "integ", "temp", "hpsl", "hsens", "heff", "hmem", "carry", "starve",
        "T", "gift_lam", "u",
        # sec.2
        "Pi", "inK", "A", "blk", "WF", "SC1", "FT1", "base_active", "act_sens", "act_disc", "act_val", "act_act",
        "CS", "FTS", "FT", "Col", "T_P", "in_I_ACS",
        # sec.3
        "SM", "EU", "FR", "Crit", "eta_heat", "eta_food", "e_in_Ereq", "Ereq_nonempty", "D_FR", "B1", "B2",
        "mu_eff", "weak_point", "U_rob_n", "EC", "V_minus", "V_minus_E", "d_minus", "argmin_Pi", "piE_sensitive",
        "chi_EI", "sel_resp", "in_Viab1", "Hor", "Viab_core", "s_SM", "TSTAB",
        # sec.4
        "P", "Pi_eval", "C1", "C2", "C3", "mu_hat", "Req", "sig", "Pur", "stat", "mode", "style", "fast",
        "u_M3", "r_local", "psl4_override", "Mis", "eps_est", "pred_internal_miss", "pred_theory_miss",
        "action_class", "xi_tokens",
        # sec.5
        "delta_M", "delta", "delta_L", "rec_agree", "beta_val", "beta_act", "d_eff", "pi_tau", "tau_hat",
        "h_psl", "h_mem", "h_sens", "h_eff", "T_rout", "T_sal", "T_err", "T_eval", "T_resp",
        "F_M1", "F_M2", "F_M3", "F_PSL", "F_ISL_sens", "F_ISL_mem", "F_ISL_eff",
        # sec.7
        "zones", "Recover", "blk_recovered"]


def fmt(v):
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (tuple, list, dict, set)):
        return repr(v)
    return v


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    outdir = None
    if "--out" in argv:
        k = argv.index("--out")
        outdir = argv[k + 1]
        args = [a for a in args if a != outdir]
    scen = args[0] if args and "=" not in args[0] else "default"
    over = [a for a in args if "=" in a]
    cfg = parse_overrides(SCENARIOS[scen], over)
    outdir = outdir or os.path.join("outputs", "v2", scen + ("_" + "_".join(o.replace("=", "-") for o in over) if over else ""))
    outdir = "".join(c if (c.isalnum() or c in "-_./") else "_" for c in outdir)
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    rec, wf, so = run(cfg)
    out, org = judge_run(cfg, rec, wf, so)
    names = sorted(out)
    for n in names:
        with open(os.path.join(outdir, f"trace_{n}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(COLS)
            for r in out[n]:
                w.writerow([fmt(r.get(c, "")) for c in COLS])
    with open(os.path.join(outdir, "relations.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "i", "Y", "cat", "cost", "p_pert", "dL_A", "dL_d_eff", "dL_tau_hat", "Q"])
        for n in names:
            for r in out[n]:
                for Y, v in sorted(r.get("Rel", {}).items()):
                    w.writerow([r["t"], n, Y] + list(v))
        w.writerow([])
        w.writerow(["t", "pair", "homo", "cat_bi", "dir"])
        for r in out[names[0]]:
            b = r.get("Bi")
            if b:
                w.writerow([r["t"], b["pair"], b["homo"], b["cat_bi"], b["dir"]])
    if org:
        with open(os.path.join(outdir, "org.csv"), "w", newline="") as f:
            w = csv.writer(f)
            ks = list(org[0].keys())
            w.writerow(ks)
            for o in org:
                w.writerow([fmt(o[k]) for k in ks])
    ev, src = timeline(cfg, out, org, rec)
    with open(os.path.join(outdir, "events.md"), "w") as f:
        f.write(f"# events: scenario {scen} {' '.join(over)}\n\n")
        f.write("Each line reports a change of a judged quantity (judge.py). t = time step.\n\n")
        for t, who, kind, txt in ev:
            f.write(f"- t={t:4d} [{who}] {kind}: {txt}\n")
    from acs_toy.viewer import build_html
    with open(os.path.join(outdir, "viewer.html"), "w") as f:
        f.write(build_html(cfg, out, org, rec, ev, f"ACS toy: {scen} {' '.join(over)}".strip(), B=so[2]))
    summ = {"scenario": scen, "overrides": over, "steps": cfg.steps, "seconds": round(time.time() - t0, 1)}
    for n in names:
        rows = out[n]
        p = rows[0]["_paths"]
        zc = Counter()
        for r in rows:
            for z in r["zones"].split("+"):
                zc[z] += 1
        resc = Counter()
        for (t, m), s in src.items():
            if m == n and t < len(rows) and rows[t]["Col"] == 0:
                for x in s:
                    resc[x.split(":")[0]] += 1
        live = [r for r in rows if r["T_P"]]
        summ[n] = {
            "T_blk": p["T_blk"], "T_col": p["T_col"], "in_P_blk": p["in_P_blk"], "in_P_col": p["in_P_col"],
            "T_FT": next((r["t"] for r in rows if r["FT"]), None),
            "chi_EI_0_from_until_record_end": p["chi0_through_record_end_from"],
            "zone_counts": dict(zc),
            "blocked_steps": sum(1 for r in rows if r["blk"] and r["Col"] == 0),
            "B1_steps": sum(1 for r in rows if r["B1"] and r["T_P"]),
            "B2_steps": sum(1 for r in rows if r["B2"] and r["T_P"]),
            "blockage_ends": dict(Counter(r["blk_recovered"] for r in rows if r["blk_recovered"])),
            "SM_fail_steps_on_T_P": sum(1 for r in live if r["SM"] is False),
            "EU_fail_steps_on_T_P": sum(1 for r in live if r["EU"] is False),
            "TSTAB_true_steps": sum(1 for r in live if r["TSTAB"] is True),
            "gifts_received_alive": dict(resc),
            "purposes_seen": sorted({repr(p) for r in rows if r["Pur"] != "undef" for p in r["Pur"]}),
            "mode_counts": dict(Counter(r["mode"] for r in rows if r["mode"] != "undef")),
            "psl4_overrides": sum(1 for r in rows if r.get("psl4_override") is True),
            "fast_steps": sum(1 for r in rows if r.get("fast") is True),
            "action_classes": dict(Counter(r["action_class"] for r in rows if r["action_class"] != "undef")),
            "final_beta_val": rows[-1]["beta_val"],
        }
    if org:
        summ["org"] = {"org_ACS_steps": sum(1 for o in org if o["org_ACS"]),
                       "org_blocked_steps": sum(1 for o in org if o["blk_org"]),
                       "allocations": sum(1 for o in org if o["u_org"] not in ("", "hold"))}
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(summ, f, ensure_ascii=False, indent=1, default=str)
    if "--no-checks" not in flags:
        from acs_toy.checks import run_checks, record_props
        txt = run_checks(cfg, rec, wf, so) + record_props(out, org)
        with open(os.path.join(outdir, "checks.txt"), "w") as f:
            f.write(txt)
        summ["checks_NG"] = sum(1 for ln in txt.splitlines() if " NG " in ln)
        with open(os.path.join(outdir, "summary.json"), "w") as f:
            json.dump(summ, f, ensure_ascii=False, indent=1, default=str)
    print(json.dumps(summ, ensure_ascii=False, indent=1, default=str))
    print("written to", outdir)


if __name__ == "__main__":
    main(sys.argv[1:])
