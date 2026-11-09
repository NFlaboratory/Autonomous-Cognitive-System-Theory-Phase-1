# -*- coding: utf-8 -*-
"""E4 runner.

  python3 run_prereg.py register experiments/P1_minacs_learning.py   # writes specs/<id>.json, logs md5
  python3 run_prereg.py run specs/<id>.json [--deviation "<reason>"] [--jobs N]   # verifies, runs, evaluates
"""
import datetime
import importlib.util
import json
import os
import platform
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from e4 import prereg as pr          # noqa: E402
from e4 import adapters as ad        # noqa: E402

UNITS = {"minacs": ad.minacs_unit, "v2": ad.v2_unit, "e1_minacs": ad.e1_unit, "e2_v2": ad.e2_unit, "e3_minacs": ad.e3_unit, "e7_minacs": ad.e7_unit,
         "e8_e1_furnace": ad.e8_e1_unit, "e8_e2_furnace": ad.e8_e2_unit,
         "e1_v2": ad.e1v2_unit, "e10_exact": ad.e10_unit, "e10_v2": ad.e10_v2_unit,
         "e11_exact": ad.p11_unit}


def load_spec_module(path):
    spec = importlib.util.spec_from_file_location("spec", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SPEC


def cmd_register(path):
    spec = load_spec_module(path)
    os.makedirs(os.path.join(HERE, "specs"), exist_ok=True)
    out = os.path.join(HERE, "specs", spec["id"] + ".json")
    if os.path.exists(out):
        raise SystemExit(f"{out} exists: a registered spec is never overwritten; register a new id")
    d = pr.register(spec, out)
    print(f"registered {spec['id']}  md5={d}  -> {out}")


def _task(args):
    model, vid, var, cond, seed, pts = args
    unit = UNITS[model]
    return {(vid, cond, seed, k): unit(seed, pt, cond, var) for k, pt in enumerate(pts)}


def evaluate(spec, data, pts):
    """judge every hypothesis by its registered rule; consistency of rule-independent metrics."""
    verdicts = []
    for H in spec["hypotheses"]:
        vids = H.get("variants", list(spec["rule_variants"]))
        per = {}
        for vid in vids:
            if H["kind"] == "paired":
                a, b = H["conditions"]
                pairs = [(data[(vid, a, s, k)][H["metric"]], data[(vid, b, s, k)][H["metric"]])
                         for s in spec["seeds"]["eval"] for k in range(len(pts))]
                per[vid] = pr.paired_rule(pairs, H["rule"])
            elif H["kind"] == "paired_within":
                a, b = H["metrics"]
                pairs = []
                for cond in H["conditions"]:
                    for s in spec["seeds"]["eval"]:
                        for k in range(len(pts)):
                            r = data[(vid, cond, s, k)]
                            if r[a] is not None and r[b] is not None:
                                pairs.append((r[a], r[b]))
                per[vid] = pr.paired_rule(pairs, H["rule"])
            elif H["kind"] == "share":
                flags = []
                for cond in H["conditions"]:
                    for s in spec["seeds"]["eval"]:
                        for k in range(len(pts)):
                            r = data[(vid, cond, s, k)]
                            v = _predicate(H["predicate"], r)
                            if v is not None:
                                flags.append(v)
                per[vid] = pr.share_rule(flags, H["rule"])
        vs = {v[0] for v in per.values()}
        verdicts.append({"id": H["id"], "statement": H["statement"],
                         "per_variant": {k: {"verdict": v[0], "counts": v[1]} for k, v in per.items()},
                         "rule_dependent": len(vs) > 1})
    # consistency: metrics that the spec declares rule-independent must coincide across variants
    consistency = []
    for m in spec.get("rule_independent_metrics", []):
        vids = list(spec["rule_variants"])
        bad = sum(1 for cond in spec["conditions"] for s in spec["seeds"]["eval"] for k in range(len(pts))
                  if len({json.dumps(data[(v, cond, s, k)][m]) for v in vids}) > 1)
        consistency.append({"metric": m, "units_differing_across_variants": bad})
    return verdicts, consistency


def cmd_run(path, deviation=None, jobs=1):
    spec, digest, entry, problems = pr.load_and_verify(path, deviation)
    unit = UNITS[spec["model"]]
    pts = pr.sweep_points(spec["sweep"])
    t0 = time.time()
    data = {}
    if jobs > 1:
        # parallel execution changes only the running time: every unit is a pure function of its arguments
        import multiprocessing as mp
        tasks = [(spec["model"], vid, var, cond, seed, pts) for vid, var in spec["rule_variants"].items()
                 for cond in spec["conditions"] for seed in spec["seeds"]["eval"]]
        with mp.Pool(jobs) as pool:
            for n, part in enumerate(pool.imap_unordered(_task, tasks, chunksize=1)):
                data.update(part)
                if n % 50 == 0:
                    print(f"  {n + 1}/{len(tasks)} tasks ({round(time.time() - t0, 1)} s)", flush=True)
    else:
        for vid, var in spec["rule_variants"].items():
            for cond in spec["conditions"]:
                for seed in spec["seeds"]["eval"]:
                    for k, pt in enumerate(pts):
                        data[(vid, cond, seed, k)] = unit(seed, pt, cond, var)
            print(f"  variant {vid} done ({round(time.time() - t0, 1)} s)", flush=True)
    verdicts, consistency = evaluate(spec, data, pts)
    res = {"id": spec["id"], "spec_md5": digest, "registry_entry": entry,
           "run_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "python": platform.python_version(), "seconds": round(time.time() - t0, 1),
           "deviation": deviation, "problems_at_run": problems,
           "n_units_per_variant_condition": len(spec["seeds"]["eval"]) * len(pts),
           "verdicts": verdicts, "consistency": consistency}
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    base = os.path.join(HERE, "results", spec["id"])
    with open(base + "_result.json", "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    with open(base + "_units.jsonl", "w") as f:
        for (vid, cond, s, k), r in sorted(data.items(), key=lambda kv: str(kv[0])):
            f.write(json.dumps({"variant": vid, "condition": cond, "seed": s, "point": pts[k], **r}) + "\n")
    with open(base + "_result.md", "w") as f:
        f.write(render(spec, res, pts))
    print(render(spec, res, pts))


def _predicate(name, r):
    if name == "recover_narrowed_before_collapse":
        if r["T_col"] is None or r["recover_count_last_alive"] is None:
            return None
        return r["recover_count_last_alive"] < 3
    if name == "kernel_exit_only_outside_Ereq":
        if r.get("viab_exits_with_u_in_Uviab", 0) == 0:
            return None
        return r["viab_exits_with_u_in_Uviab_and_e_in_Ereq"] == 0
    if name == "shorter_survival_has_more_estimation_error":
        if "base_T_col" not in r:
            return None
        inf = float("inf")
        a = inf if r["T_col"] is None else r["T_col"]
        b = inf if r["base_T_col"] is None else r["base_T_col"]
        if not a < b:
            return None
        return (r["sign_mismatch"] > r["base_sign_mismatch"]) or (r["sel_violation"] > r["base_sel_violation"])
    if name == "cert_exit_only_outside_Ereq":
        if r.get("cert_exit", 0) == 0:
            return None
        return r["cert_exit_e_in_Ereq"] == 0
    if name == "ok_steps_never_leave_kernel":
        if "C_OK_leaveV_regression" not in r:
            return None
        return r["C_OK_leaveV_regression"] == 0
    if name == "f_table_consistent":
        if r.get("cert_steps", 0) == 0:
            return None
        return r["f_table_mismatch"] == 0
    if name == "sign_mismatch_present":
        return r["sign_mismatch"] > 0
    if name == "blockage_before_collapse":
        if r["T_col"] is None:
            return None
        return r["blocked"] > 0
    raise ValueError(name)


def render(spec, res, pts):
    L = [f"# {spec['id']}：事前登録実験の結果", "",
         f"- 登録 md5：`{res['spec_md5']}`", f"- 登録記録：`{res['registry_entry']}`",
         f"- 実行：{res['run_at']}（{res['seconds']} 秒、Python {res['python']}）",
         f"- 逸脱：{res['deviation'] or 'なし'}" + (f"（検出事項：{res['problems_at_run']}）" if res['problems_at_run'] else ""),
         f"- 評価単位：条件ごとに {res['n_units_per_variant_condition']}（評価 seed {len(spec['seeds']['eval'])} 本 × 掃引点 {len(pts)}）",
         "", "| 仮説 | 判定規則の変種 | 判定 | 件数 |", "|---|---|---|---|"]
    for v in res["verdicts"]:
        for vid, x in v["per_variant"].items():
            L.append(f"| {v['id']} | {vid} | {x['verdict']} | {x['counts']} |")
    L.append("")
    for v in res["verdicts"]:
        L.append(f"- {v['id']}：{v['statement']}" + ("（判定が規則の変種に依存した）" if v["rule_dependent"] else ""))
    if res["consistency"]:
        L.append("")
        for c in res["consistency"]:
            L.append(f"- 規則に依存しないと登録した指標 `{c['metric']}`：変種間で値が異なった単位 {c['units_differing_across_variants']} 件")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    if sys.argv[1] == "register":
        cmd_register(sys.argv[2])
    elif sys.argv[1] == "run":
        dev = sys.argv[sys.argv.index("--deviation") + 1] if "--deviation" in sys.argv else None
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 1
        cmd_run(sys.argv[2], dev, jobs)
