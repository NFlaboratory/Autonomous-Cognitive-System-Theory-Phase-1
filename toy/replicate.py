# -*- coding: utf-8 -*-
"""Replication of the registered experiments with the code in this repository.

For each registered spec (specs/<id>.json) that has recorded unit results (results/<id>_units.jsonl), every
evaluation unit is recomputed with the current code and compared with the recorded unit; the verdicts are then
recomputed with the registered decision rules and compared with the recorded verdicts.  Nothing is
re-registered and the registered files are not modified.

  python3 replicate.py [--jobs N] [id ...]       # default: every spec with recorded units
Output: replication/<id>.json and replication/SUMMARY.md (appended per id).
"""
import json
import multiprocessing as mp
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_prereg as rp            # noqa: E402
from e4 import prereg as pr        # noqa: E402


def _key(r):
    return (r["variant"], r["condition"], r["seed"], json.dumps(r["point"], sort_keys=True))


def replicate(sid, jobs):
    spec = json.load(open(os.path.join(HERE, "specs", sid + ".json")))
    rec_path = os.path.join(HERE, "results", sid + "_units.jsonl")
    res_path = os.path.join(HERE, "results", sid + "_result.json")
    recorded = {}
    for line in open(rec_path):
        r = json.loads(line)
        recorded[_key(r)] = {k: v for k, v in r.items() if k not in ("variant", "condition", "seed", "point")}
    pts = pr.sweep_points(spec["sweep"])
    tasks = [(spec["model"], vid, var, cond, seed, pts) for vid, var in spec["rule_variants"].items()
             for cond in spec["conditions"] for seed in spec["seeds"]["eval"]]
    t0 = time.time()
    data = {}
    if jobs > 1:
        with mp.Pool(jobs) as pool:
            for part in pool.imap_unordered(rp._task, tasks, chunksize=1):
                data.update(part)
    else:
        for t in tasks:
            data.update(rp._task(t))
    same = diff = missing = 0
    examples = []
    for (vid, cond, s, k), r in data.items():
        key = (vid, cond, s, json.dumps(pts[k], sort_keys=True))
        if key not in recorded:
            missing += 1
            continue
        if json.loads(json.dumps(r)) == recorded[key]:
            same += 1
        else:
            diff += 1
            if len(examples) < 5:
                d = {m: (recorded[key].get(m), r.get(m)) for m in set(r) | set(recorded[key])
                     if recorded[key].get(m) != json.loads(json.dumps(r.get(m)))}
                examples.append({"unit": list(key), "recorded_vs_now": d})
    verdicts, _ = rp.evaluate(spec, data, pts)
    old = json.load(open(res_path))["verdicts"]
    vd = []
    for a, b in zip(old, verdicts):
        for vid in a["per_variant"]:
            va, vb = a["per_variant"][vid], b["per_variant"][vid]
            if va["verdict"] != vb["verdict"] or va["counts"] != vb["counts"]:
                vd.append({"id": a["id"], "variant": vid, "recorded": va, "now": vb})
    out = {"id": sid, "seconds": round(time.time() - t0, 1), "units": len(data), "identical": same,
           "different": diff, "not_in_record": missing, "examples": examples,
           "verdicts_differing": vd, "verdicts_total": sum(len(a["per_variant"]) for a in old)}
    os.makedirs(os.path.join(HERE, "replication"), exist_ok=True)
    with open(os.path.join(HERE, "replication", sid + ".json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(HERE, "replication", "SUMMARY.md"), "a") as f:
        f.write(f"| {sid} | {len(data)} | {same} | {diff} | {missing} | "
                f"{out['verdicts_total'] - len(vd)}/{out['verdicts_total']} | {out['seconds']} |\n")
    print(json.dumps({k: v for k, v in out.items() if k != "examples"}, ensure_ascii=False))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    jobs = 1
    if "--jobs" in args:
        k = args.index("--jobs")
        jobs = int(args[k + 1])
        del args[k:k + 2]
    ids = args or sorted(f[:-len("_units.jsonl")] for f in os.listdir(os.path.join(HERE, "results"))
                         if f.endswith("_units.jsonl"))
    if not ids:
        sys.exit("No results/*_units.jsonl found: nothing was replicated. The raw unit records are archived "
                 "separately (see results/UNITS_SHA256.md); place them in results/ and run again.")
    missing = [sid for sid in ids if not os.path.exists(os.path.join(HERE, "results", sid + "_units.jsonl"))]
    if missing:
        sys.exit("Raw unit records not found: " + ", ".join(f"results/{sid}_units.jsonl" for sid in missing)
                 + ". They are archived separately (see results/UNITS_SHA256.md).")
    for sid in ids:
        replicate(sid, jobs)
