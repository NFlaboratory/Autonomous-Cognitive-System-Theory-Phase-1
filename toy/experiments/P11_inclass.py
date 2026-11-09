# -*- coding: utf-8 -*-
"""Preregistration P11: comparisons inside the ACS class (every variant satisfies CR-2b, check_cr2_variants.py)."""
import os
PAIR = {"geq_min": 0.9, "gt_min": 0.25, "lt_max_for_reject": 0.25}
CHAINS = [("base", "est-2"), ("est-2", "est-3"), ("base", "est-3"),
          ("base", "upd-2"), ("upd-2", "upd-4"), ("upd-4", "upd-none"), ("base", "upd-none")]
SMOKE = {"minacs": "tuning seed 1 (cold_len 3, regrow 5, gifts 3): T_col base 11, est-2 11, est-3 11, upd-2 15, "
                   "upd-4 15, upd-none 15",
         "furnace": "tuning seed 1 (hot_len 5, deliv 3, draught 1): T_col base 27, est-2 11, est-3 27, upd-2 11, "
                    "upd-4 13, upd-none 27"}


def spec(dom, sweep):
    return {
        "id": f"P11_inclass_{dom}_r1", "model": "e11_exact",
        "purpose": "Comparisons inside the ACS class: graded variants of the TIPA mechanism that keep CR-2b.  est-k: the "
                   "self-state reading used by the mechanism (MinACS energy / furnace temperature) is quantised to "
                   "multiples of k (floor; a positive value is never read as 0).  upd-k: the internal model is updated "
                   "only every k steps; upd-none: never.  The A/B1/C records of P10 are kept for each run.",
        "tuning_history": "Nothing tuned.  Variants written before any run; one smoke test: " + SMOKE[dom] + ".",
        "cr2_note": "check_cr2_variants.py: est-2 and est-3 satisfy CR-2b in both domains; upd-k changes only Update, "
                    "which CR-2b does not involve.",
        "sources": ["acsjudge/*.py", "domains/*.py", "domains/furnace/*.py", "minacs/*.py", "e4/*.py", "run_prereg.py"],
        "seeds": {"tune": list(range(1, 11)), "eval": list(range(11, 61))},
        "sweep": sweep,
        "conditions": ["base", "est-2", "est-3", "upd-2", "upd-4", "upd-none"],
        "rule_variants": {"R0": {}}, "rule_independent_metrics": [],
        "hypotheses": [
            {"id": f"H{n + 1}", "kind": "paired", "metric": "T_col", "conditions": [a, b],
             "statement": f"{a} の崩壊到達時刻は {b} 以上である（推定の分解能または更新の頻度が高い方が長く存続する）。",
             "how_it_could_fail": "推定の粗さや更新の遅れが、行動の時機を偶然に有利にずらす場合がある（E7 の天候を見ない劣化では 172 単位で"
                                  "劣化の方が長く存続した）。登録前の試運転：" + SMOKE[dom] + "。",
             "rule": PAIR}
            for n, (a, b) in enumerate(CHAINS)],
    }
