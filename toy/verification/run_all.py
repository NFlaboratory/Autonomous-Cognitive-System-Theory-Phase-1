# -*- coding: utf-8 -*-
"""Runs the whole verification suite and builds the coverage tables (about 5 minutes).
  python3 verification/run_all.py           all suites
  python3 verification/run_all.py --quick   skips MicroUniverse A3 and the Update-rule variants (about 2 minutes)
Results go to verification/out_run/ (not tracked).  verification/out/ holds the dated record shipped with
the repository; it is rewritten only with --record.
Exit code 1 if any check FAILs or a label is not found in the paper.
v2 record checks read outputs/v2/*/trace_*.csv only if they exist (python3 run_v2.py default).
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOY = os.path.dirname(HERE)


def run(args, out):
    print("\n$ python3", " ".join(args), flush=True)
    env = dict(os.environ, ACS_VERIFY_OUT=out)
    return subprocess.call([sys.executable, "-I"] + args, cwd=TOY, env=env)


def main(argv):
    quick = "--quick" in argv
    out = os.path.join(HERE, "out" if "--record" in argv else "out_run")
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".json") or f.endswith(".csv"):
            os.remove(os.path.join(out, f))
    rc = 0
    rc |= run(["verification/check_principles.py"], out)
    rc |= run(["verification/microuniverse.py", "A2", "B2"] if quick else ["verification/microuniverse.py"], out)
    rc |= run(["verification/check_structure.py"], out)
    rc |= run(["verification/dormancy.py"], out)
    if not quick:
        rc |= run(["verification/update_rules.py"], out)
    rc |= run(["verification/check_v2_records.py"], out)
    rc |= run(["verification/build_coverage.py"], out)
    print("\nRESULT:", "FAIL or unknown label (see above)" if rc else "no FAIL", "->", os.path.relpath(out, TOY))
    return 1 if rc else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
