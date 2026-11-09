# -*- coding: utf-8 -*-
"""Builds the coverage tables from out/*.json:
  out/coverage_83.csv            the 83 definitions of sec.4 / sec.5 (design table COVERAGE_83_design.csv order)
  out/assumptions6_props6.csv    the 6 assumptions and 6 propositions of sec.4 / sec.5
  out/results_by_label.csv       every paper label touched by any check, with the aggregated status
Statuses are aggregated as: FAIL > PASS_NONVACUOUS > BLOCKED_ASSUMPTION > EXAMPLE_ONLY > PASS_VACUOUS > others.
A definition with no check gets NOT_RUN, or EXAMPLE_ONLY when a v2 trace column computes the quantity
(listed below; computing a quantity is an example, not a verification).
python3 verification/build_coverage.py
"""
import csv
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vlib import OUT, TOY  # noqa: E402

PAPER = os.path.join(os.path.dirname(TOY), "paper")
RANK = ["FAIL", "PASS_NONVACUOUS", "BLOCKED_ASSUMPTION", "EXAMPLE_ONLY", "PASS_VACUOUS", "BLOCKED_SOURCE",
        "NOT_APPLICABLE", "NOT_RUN"]

V2_COLUMNS = {   # definitions whose quantity the v2 trace computes (column names of trace_*.csv)
    "def:m1_map": "xi_tokens, eps_est", "def:s4_state_estimation_error": "eps_est",
    "def:id_vector": "xi_tokens", "def:prediction_record_check": "pred_internal_miss, pred_theory_miss",
    "def:m2_map": "P, sig, Pi_eval", "def:m2a_threat": "Pi_eval", "def:mech_mu_eff": "mu_hat",
    "def:m2_latent_instability": "C1, C2, C3", "def:m2_priority": "P", "def:m2_request_signal": "sig",
    "def:request_signal_types": "Req, sig", "def:purpose_formation": "Pur", "def:purpose_status": "stat",
    "def:request_response_mismatch": "Mis", "def:M3_modes": "mode", "def:m3_3b_styles": "style",
    "def:action_decision": "u_M3", "def:psl4": "r_local, psl4_override", "def:action_classes": "action_class",
    "def:integrated_fast_processing": "fast", "def:fast_memory_sets": "T_rout, T_sal, T_err, T_eval, T_resp",
    "def:functional_axis": "F_M1 ... F_ISL_eff", "def:s5_record_agreement": "rec_agree",
    "def:intertime_update": "delta_M, delta", "def:learning_intertime_change": "delta_L",
    "def:bias_tendency": "beta_val, beta_act", "def:beta_accumulated": "beta_val, beta_act",
    "def:s5_prediction_coefficient": "pi_tau", "def:tau_hat_section5": "tau_hat", "def:deff_section5": "d_eff",
    "def:s5_health_quantities": "h_psl, h_mem, h_sens, h_eff", "def:result_tuple": "Pur, stat, u",
}

PARTIAL = {"ass:functional_concurrency", "ass:psl_minimal"}
ITEMS_12 = ["ass:functional_concurrency", "ass:m1c_temporal", "ass:psl_minimal", "ass:impl_structure",
            "ass:fast_structural_consistency", "ass:s5_observation_factorization",
            "prop:purpose_self_attribution", "prop:purpose_ad_slot", "prop:s5_one_step", "prop:s5_continuation",
            "prop:s5_causality", "prop:s5_observation_causality"]
NOTES_12 = {
    "ass:functional_concurrency": "partial evidence only: S04 (M2 independent of the M3 record, with its mutation test); "
                                  "the full same-time generation dependency graph is not checked",
    "ass:m1c_temporal": "no check of the M1-c history window (NOT_RUN)",
    "ass:psl_minimal": "partial evidence only: S06 (PSL-4 from I only, resolution keeps the local component, "
                       "with mutation tests); PSL-1..3 and non-cognitivity are not checked",
    "ass:impl_structure": "no ISL role check (NOT_RUN); the toys do not model separate substrate carriers",
    "ass:fast_structural_consistency": "no check of the fast path (NOT_RUN)",
    "prop:purpose_ad_slot": "BLOCKED_SOURCE: no toy has frames A_O of the response component nor the action "
                            "difference over them; a new world is needed (design G7/G8)",
}


def labels_in_paper():
    labs = set()
    for fp in glob.glob(os.path.join(PAPER, "section*.tex")):
        labs |= set(re.findall(r"\\label\{([^}]*)\}", open(fp, encoding="utf-8").read()))
    return labs


def main():
    rows = []
    for fp in sorted(glob.glob(os.path.join(OUT, "*.json"))):
        rows += json.load(open(fp, encoding="utf-8"))
    paper = labels_in_paper()
    unknown = sorted({lb for r in rows for lb in r["labels"]} - paper)
    if unknown:
        print("labels not in the paper:", unknown)
    by = {}
    for r in rows:
        for lb in r["labels"]:
            by.setdefault(lb, []).append(r)

    def agg(lb):
        rs = by.get(lb, [])
        if not rs:
            return None, ""
        st = min((r["status"] for r in rs), key=RANK.index)
        ids = "; ".join(sorted({f'{r["check_id"]}@{r["domain"]}' for r in rs}))
        if lb in PARTIAL:
            return "NOT_RUN", "partial evidence: " + ids
        return st, ids
    with open(os.path.join(OUT, "results_by_label.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["label", "status", "checks"])
        for lb in sorted(by):
            st, ids = agg(lb)
            w.writerow([lb, st, ids])
    # 83 definitions
    design = os.path.join(os.path.dirname(os.path.abspath(__file__)), "COVERAGE_83_design.csv")
    with open(design, encoding="utf-8-sig") as fh:
        drows = list(csv.DictReader(fh))
    cnt = {}
    with open(os.path.join(OUT, "coverage_83.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["section", "no", "label", "title", "group", "status", "checks", "v2_column", "in_paper"])
        for d in drows:
            lb = d["ラベル"]
            st, ids = agg(lb)
            col = V2_COLUMNS.get(lb, "")
            if st is None:
                st = "EXAMPLE_ONLY" if col else "NOT_RUN"
            cnt[st] = cnt.get(st, 0) + 1
            w.writerow([d["節"], d["番号"], lb, d["表題"], d["検査群"], st, ids, col, lb in paper])
    print("coverage_83:", cnt, "total", sum(cnt.values()))
    with open(os.path.join(OUT, "assumptions6_props6.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["label", "status", "checks", "note"])
        for lb in ITEMS_12:
            st, ids = agg(lb)
            if lb == "prop:purpose_ad_slot":
                st = "BLOCKED_SOURCE"
            if lb in PARTIAL:      # only a part of the assumption is checked: not reported as a pass
                st = "NOT_RUN"
            w.writerow([lb, st or "NOT_RUN", ids, NOTES_12.get(lb, "")])
    nfail = sum(r["status"] == "FAIL" for r in rows)
    print(f"rows {len(rows)}, FAIL {nfail}, labels touched {len(by)}")
    return 1 if (nfail or unknown) else 0


if __name__ == "__main__":
    sys.exit(main())
