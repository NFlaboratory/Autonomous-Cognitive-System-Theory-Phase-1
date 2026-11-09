# -*- coding: utf-8 -*-
"""Shared helpers for the verification suite (toy/verification/).

Nothing here is a definition of the paper.  The suite only reads the existing toy sources;
it never writes into the registered experiment files (experiments/, specs/, results/, registry.log).

Result status (fixed before running):
  PASS_NONVACUOUS   the statement was checked on every case of the stated finite range and its
                    premise held in at least one case
  PASS_VACUOUS      checked on the whole range, but the premise never held (no evidence)
  EXAMPLE_ONLY      an example / realisation was exhibited; no universal check was made
  FAIL              a case violating the statement was found (evidence is stored)
  NOT_RUN           not executed in this suite (reason given)
  NOT_APPLICABLE    the item does not apply to the toy (reason given)
  BLOCKED_SOURCE    the needed part does not exist in the toy source (reason given)
  BLOCKED_ASSUMPTION the premise (an assumption of the paper) does not hold in the toy; the
                    conclusion is reported separately and is not a counterexample
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOY = os.path.dirname(HERE)
if TOY not in sys.path:
    sys.path.insert(0, TOY)
OUT = os.environ.get("ACS_VERIFY_OUT") or os.path.join(HERE, "out_run")

STATUSES = ("PASS_NONVACUOUS", "PASS_VACUOUS", "EXAMPLE_ONLY", "FAIL", "NOT_RUN", "NOT_APPLICABLE",
            "BLOCKED_SOURCE", "BLOCKED_ASSUMPTION")


class Report:
    def __init__(self, suite):
        self.suite = suite
        self.rows = []

    def add(self, check_id, labels, domain, status, cases=None, premise=None, detail="", evidence=None,
            kind=""):
        assert status in STATUSES, status
        if isinstance(labels, str):
            labels = [labels]
        self.rows.append({"suite": self.suite, "check_id": check_id, "labels": list(labels), "domain": domain,
                          "status": status, "cases": cases, "premise_cases": premise, "kind": kind,
                          "detail": detail, "evidence": _jsonable(evidence)})
        mark = {"PASS_NONVACUOUS": "OK  ", "PASS_VACUOUS": "VAC ", "FAIL": "FAIL"}.get(status, status[:4] + " ")
        print(f"[{mark}] {check_id:34s} {domain:12s} cases={cases} premise={premise} {detail}"[:220])
        return status

    def check(self, check_id, labels, domain, cases, premise, bad, detail="", kind="exhaustive"):
        """bad: list of counterexamples (empty = none)."""
        if bad:
            st = "FAIL"
        elif premise == 0:
            st = "PASS_VACUOUS"
        else:
            st = "PASS_NONVACUOUS"
        return self.add(check_id, labels, domain, st, cases, premise, detail, bad[:3] if bad else None, kind)

    def save(self):
        os.makedirs(OUT, exist_ok=True)
        p = os.path.join(OUT, f"{self.suite}.json")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(self.rows, fh, ensure_ascii=False, indent=1)
        nf = sum(r["status"] == "FAIL" for r in self.rows)
        print(f"== {self.suite}: {len(self.rows)} rows, FAIL {nf} -> {os.path.relpath(p, TOY)}")
        return nf


def _jsonable(v):
    if v is None:
        return None
    try:
        json.dumps(v)
        return v
    except TypeError:
        if isinstance(v, (list, tuple, set, frozenset)):
            return [_jsonable(a) for a in v]
        if isinstance(v, dict):
            return {str(k): _jsonable(a) for k, a in v.items()}
        return repr(v)


# ---------------------------------------------------------------- finite graphs
def greatest_infinite(nodes, succ):
    """largest S within nodes such that every x in S has a successor in S
    (= the states from which an infinite path inside `nodes` exists)."""
    S = set(nodes)
    changed = True
    while changed:
        changed = False
        for x in list(S):
            if not (succ(x) & S):
                S.discard(x)
                changed = True
    return S


def lcg_seq(seed, n, choices):
    """deterministic sequence (fixed linear congruential rule; not a random-sampling claim)."""
    a, c, m = 1103515245, 12345, 2 ** 31
    s = (seed * 2654435761 + 1) % m
    out = []
    for _ in range(n):
        s = (a * s + c) % m
        out.append(choices[(s >> 8) % len(choices)])
    return out


def backgrounds(D):
    return sorted({D.split(e)[0] for e in D.ES}, key=repr)
