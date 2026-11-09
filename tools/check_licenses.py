# -*- coding: utf-8 -*-
"""Assigns every file of the repository to exactly one license, following LICENSE.md.
  MIT          : *.py, .github/workflows/*.yml|*.yaml, paper/.latexmkrc, .gitignore
  LICENSE_DOC  : LICENSE.md, LICENSE-MIT, LICENSE-CC-BY-SA-4.0 (the license documents themselves)
  CC-BY-SA-4.0 : every other file
Exit code 1 if a license document is missing, or a file that looks like code (by extension) is not MIT.
python3 tools/check_licenses.py [repo_root]
"""
import os
import sys
from collections import Counter

LICENSE_DOCS = {"LICENSE.md", "LICENSE-MIT", "LICENSE-CC-BY-SA-4.0"}
CODE_LIKE = (".py", ".sh", ".js", ".ts", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".mk", ".bat", ".ps1")
SKIP_DIRS = {".git", "__pycache__", "out_run"}


def assign(rel):
    rel = rel.replace(os.sep, "/")
    if rel in LICENSE_DOCS:
        return "LICENSE_DOC"
    if rel.endswith(".py"):
        return "MIT"
    if rel.startswith(".github/workflows/") and rel.endswith((".yml", ".yaml")):
        return "MIT"
    if rel in ("paper/.latexmkrc", ".gitignore"):
        return "MIT"
    return "CC-BY-SA-4.0"


def main(argv):
    root = os.path.abspath(argv[0] if argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    files = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            files.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    cnt = Counter(assign(f) for f in files)
    bad = [f for f in files if f.lower().endswith(CODE_LIKE) and assign(f) != "MIT"]
    missing = sorted(d for d in LICENSE_DOCS if not os.path.exists(os.path.join(root, d)))
    print(f"files {len(files)}: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())))
    for f in bad:
        print("code-like file not under MIT:", f)
    for d in missing:
        print("missing license document:", d)
    print("OK" if not (bad or missing) else "NG")
    return 1 if (bad or missing) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
