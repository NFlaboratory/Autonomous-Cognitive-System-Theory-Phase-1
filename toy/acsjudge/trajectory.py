# -*- coding: utf-8 -*-
"""Domain-independent closed loop with exact judgement at every step.

The domain D supplies, in addition to the judge's parts:
  D.make_e(b, o), D.g_O(o, x, u, b)            realised environment and its response part
  D.WF(x), D.CS(x)                              well-formed realisation indicator, structural-loss indicator
  D.full_stop(x), D.margin(x)                   toy zone rules for Z3 (all base functions stopped) and Z1
  D.base_active(x), D.UPSILON, D.upsilon(x, a)  toy recover rule
A mechanism object `mind` supplies operate(M, x, e) -> dict with key 'u' (and optionally
'pur', 'mode', 'P', 'Pi_eval'), and Update(M, x, e, learn) -> M.
The code is the MinACS trajectory (E6) with every domain reference replaced by a call to D.
"""


def zones(J, x, e, col):
    D = J.D
    if col:
        return "Z5"
    z = []
    if not J.A(x, e):
        z.append("Z4")
    if D.full_stop(x):
        z.append("Z3")
    if (not J.inK(x)) or D.margin(x):
        z.append("Z1")
    return "+".join(sorted(z)) if z else "Z0"


def step(D, mind, x, o, Mm, b, learn=True, policy=None):
    e = D.make_e(b, o)
    out = mind.operate(Mm, x, e)
    u = out["u"] if policy is None else policy(x, e)
    x1 = D.f(x, u, e)
    o1 = D.g_O(o, x, u, b)
    M1 = mind.Update(Mm, x, e, learn=learn) if policy is None else Mm
    return e, u, out, x1, o1, M1


def run(J, mind, bg, T, x0, o0, M0, learn=True, horizon=10, policy=None, recover=True, recover_rule="first",
        core=None, V=None, H=None):
    D = J.D
    B = bg
    x, o, Mm = x0, o0, M0
    core = J.viab_core() if core is None else core
    V = J.viab_stages() if V is None else V
    H = J.hor(V) if H is None else H
    rows = []
    col = 0
    for t in range(T):
        e, u, out, x1, o1, Mn = step(D, mind, x, o, Mm, B[t], learn, policy)
        A = J.A(x, e)
        crit = J.Crit(x)
        cs = D.CS(x)
        col = 1 if (col or cs) else 0
        z = zones(J, x, e, col)
        rec = "undef"
        if recover and any(k in z for k in ("Z1", "Z2", "Z3", "Z4")) and not col:
            rec = "".join("1" if _recover(J, mind, x, o, Mm, B, t, ups, horizon, learn, policy, recover_rule) else "0"
                          for ups in D.UPSILON)
        rows.append({"t": t, "x": tuple(x), "o": o, "b": B[t], "M": tuple(Mm), "u": u, "pur": out.get("pur"),
                     "mode": out.get("mode"), "P": out.get("P"), "Pi_eval": out.get("Pi_eval"),
                     "Pi": J.Pi(x), "inK": J.inK(x), "A": A, "blk": not A,
                     "e_in_Ereq": e in J.Ereq(x), "Crit": crit,
                     "B1": (not A) and any(J.ETA[n](x, e) == 0 for n in crit),
                     "B2": (not A) and J.D_FR(x, e, crit),
                     "SM": J.inK(x) if not col else "undef",
                     "EU": J.D_FR(x, e, crit) if not col else "undef",
                     "FR": ((len(A) > 0) if J.D_FR(x, e, crit) else "undef") if not col else "undef",
                     "mu_eff": J.mu_eff(x, e), "Viab": x in core, "Hor": H[x],
                     "u_in_Uviab": (u in J.U_viab(x, core)) if x in core else "",
                     "WF": D.WF(x), "CS": cs, "Col": col, "zones": z, "Recover": rec})
        x, o, Mm = x1, o1, Mn
    return rows


def _recover(J, mind, x, o, Mm, B, t, ups, horizon, learn, policy, rule="first"):
    """toy recover rule (fixed in advance; same as E6): apply upsilon at t, continue the closed loop with the
    realised background; 1 iff WF is kept and within the horizon x is in K with base active."""
    D = J.D
    x = D.upsilon(x, ups)
    need = 1 if rule == "first" else 2
    run_ok = 0
    for k in range(horizon + 1):
        if D.WF(x) == 0:
            return False
        if J.inK(x) and D.base_active(x):
            run_ok += 1
            if run_ok >= need:
                return True
        else:
            run_ok = 0
        if k < horizon:
            _, _, _, x, o, Mm = step(D, mind, x, o, Mm, B[t + k], learn, policy)
    return False
