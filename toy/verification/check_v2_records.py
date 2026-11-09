# -*- coding: utf-8 -*-
"""T01/T03-T06/T08-T11 (record level): conditions checked on the v2 traces written by run_v2.py.
The traces are not shipped; generate them first, e.g.  python3 run_v2.py default   (about 1 minute).
Every scenario directory outputs/v2/<name>/ that contains trace_i.csv / trace_j.csv is read.
A record check covers only the realised records (it is not exhaustive over the state space).
python3 verification/check_v2_records.py
"""
import ast
import csv
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import Report, TOY  # noqa: E402

MODES = {"3A", "3B", "3C"}
STYLES_3B = {"3B-a", "3B-b", "3B-c"}   # toy strings kept for source-hash reasons = 3B-own / 3B-rel / 3B-comb


def num(v):
    try:
        return float(v)
    except ValueError:
        return None


def main():
    R = Report("v2_records")
    files = sorted(glob.glob(os.path.join(TOY, "outputs", "v2", "*", "trace_*.csv")))
    if not files:
        R.add("V2_records", ["prop:tstab_zero_margin"], "v2", "NOT_RUN", None, None,
              "no trace files; run  python3 run_v2.py default  (or other scenarios) first")
        return R.save()
    runs = []
    for fp in files:
        with open(fp, encoding="utf-8") as fh:
            runs.append((os.path.relpath(fp, TOY), list(csv.DictReader(fh))))
    print(f"{len(files)} trace files, {sum(len(r) for _, r in runs)} records")
    C = {}

    def chk(cid, labels, pred, prem_pred, detail):
        n = p = 0
        bad = []
        for name, rows in runs:
            for i, r in enumerate(rows):
                n += 1
                if prem_pred(rows, i, r):
                    p += 1
                    if not pred(rows, i, r):
                        bad.append((name, r["t"]))
        R.check(cid, labels, "v2-records", n, p, bad[:3], detail, "records")

    tp = lambda r: r["T_P"] == "1"   # noqa: E731
    chk("R01_tstab_zero_margin", "prop:tstab_zero_margin",
        lambda rows, i, r: r["TSTAB"] == "0",
        lambda rows, i, r: tp(r) and r["SM"] == "1" and r["EU"] == "1" and r["FR"] == "1" and r["Pi"] == "0",
        "on T_P with SM, EU, FR true and Pi = 0: T-STAB not satisfied")
    chk("R02_principle_time_domain_down", "lem:principle_time_domain_down",
        lambda rows, i, r: r["Col"] == "0" and all(tp(q) for q in rows[:i]), lambda rows, i, r: tp(r),
        "T_P downward closed, Col = 0 on T_P")
    chk("R03_undefined_outside_TP", ["def:principle_time_domain", "def:tstab"],
        lambda rows, i, r: all(r[k] == "undef" for k in ("SM", "EU", "FR", "TSTAB")), lambda rows, i, r: not tp(r),
        "outside T_P: SM, EU, FR, T-STAB are undefined (not false)")
    chk("R04_sm_K_equiv", "prop:sm_K_equiv",
        lambda rows, i, r: (r["SM"] == "1") == (r["inK"] == "1") == (num(r["Pi"]) >= 0), lambda rows, i, r: tp(r),
        "on T_P: SM <=> x in K <=> Pi >= 0")
    chk("R05_fr_undefined_when_eu_false", ["def:fr_domain", "def:FR"],
        lambda rows, i, r: r["FR"] == "undef", lambda rows, i, r: tp(r) and r["D_FR"] == "0",
        "outside D_FR the local FR is undefined")
    chk("R06_fr_next_sm", "prop:fr_next_sm",
        lambda rows, i, r: rows[i + 1]["inK"] == "0" and (rows[i + 1]["T_P"] != "1" or rows[i + 1]["SM"] == "0"),
        lambda rows, i, r: tp(r) and r["FR"] == "0" and i + 1 < len(rows),
        "FR false => x_{t+1} not in K (and SM_{t+1} false on T_P)")
    chk("R07_sm_one_step_A", "prop:sm_one_step_A",
        lambda rows, i, r: (rows[i + 1]["inK"] == "1") == (r["u"] in ast.literal_eval(r["A"])),
        lambda rows, i, r: i + 1 < len(rows) and r["A"] not in ("", "undef"),
        "(ii) x_{t+1} in K <=> u_t in A_t")
    chk("R08_output_attribution", ["def:s4_output_attribution", "def:result_tuple"],
        lambda rows, i, r: all(r[k] == "undef" for k in ("mode", "style", "P", "Pur", "stat", "sig", "action_class")),
        lambda rows, i, r: r["WF"] == "0",
        "WF = 0: mechanism outputs are not attributed to the individual (recorded as undef, not 0 / empty)")
    chk("R09_modes_styles", ["def:M3_modes", "def:m3_3b_styles", "def:mode_judgment"],
        lambda rows, i, r: r["mode"] in MODES and ((r["mode"] == "3B") == (r["style"] in STYLES_3B))
        and (r["mode"] == "3B" or r["style"] == "none"),
        lambda rows, i, r: r["WF"] == "1",
        "mode in {3A,3B,3C}; style is one of the three 3B styles iff mode = 3B, else none")
    chk("R10_resolve_on_records", ["def:effective_action_resolve", "def:psl4"],
        lambda rows, i, r: r["u"] == r["r_local"], lambda rows, i, r: r["WF"] == "1" and r["r_local"] not in ("", "undef", "None"),
        "an issued protective response is the effective action")
    chk("R11_readout_ranges", ["def:functional_axis", "def:s5_health_quantities", "def:beta_accumulated",
                               "def:s5_readout_types", "def:tau_hat_section5", "def:deff_section5"],
        lambda rows, i, r: all(0 <= num(r[k]) <= 1 for k in ("F_M1", "F_M2", "F_M3", "F_PSL", "F_ISL_sens", "F_ISL_mem",
                                                          "F_ISL_eff", "h_psl", "h_mem", "h_sens", "h_eff")
                               if num(r[k]) is not None)
        and all(num(r[k]) is None or num(r[k]) >= 0 for k in ("beta_val", "beta_act", "d_eff", "tau_hat")),
        lambda rows, i, r: True,
        "F and health in [0,1]; beta, d_eff, tau_hat >= 0 (values 'undef' skipped)")
    chk("R12_tau_hat", "def:tau_hat_section5",
        lambda rows, i, r: abs(num(r["tau_hat"]) - 3 * num(r["pi_tau"])) <= 0.0015 * 3 if (num(r["tau_hat"]) is not None) else True,
        lambda rows, i, r: num(r["pi_tau"]) is not None,
        "tau_hat = tau * pi_tau (tau = 3 in the v2 configuration; both columns are rounded to 3 decimals)")
    chk("R13_termination_order", "prop:termination_order",
        lambda rows, i, r: r["FT"] == "1" and r["WF"] == "0", lambda rows, i, r: r["Col"] == "1",
        "Col = 1 => FT = 1 and WF = 0 (parts (ii) and (iv))")
    return R.save()


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
