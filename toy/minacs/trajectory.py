# -*- coding: utf-8 -*-
"""Closed-loop runs of MinACS with the minimal TIPA, judged exactly with the model tables."""
from . import model as mm
from . import mind as md

# deterministic background sequences b_t = (c, g, rho) (toy conventions, fixed before the runs)
def background(name, T):
    out = []
    for t in range(T):
        if name == "mild":
            c = 1 if (t % 12) in (6, 7, 8) else 0
            g = 0
            rho = 1 if t % 3 == 0 else 0
        elif name == "cold":
            c = 1 if (t % 12) >= 5 else 0
            g = 0
            rho = 1 if t % 3 == 0 else 0
        elif name == "famine":
            c = 1 if (t % 12) in (6, 7, 8) else 0
            g = 1 if t in (19, 20) else 0
            rho = 1 if (t < 10 and t % 3 == 0) else 0
        else:
            raise ValueError(name)
        out.append((c, g, rho))
    return out


def zones(M, x, e, col):
    if col:
        return "Z5"
    z = []
    if not M.A(x, e):
        z.append("Z4")
    if x.s == 1 and x.en == 0:
        z.append("Z3")
    if (not M.inK(x)) or x.en == 1 or x.tp == 1:
        z.append("Z1")
    return "+".join(sorted(z)) if z else "Z0"


def step(x, o, Mm, b, learn=True, policy=None):
    e = mm.E_(b[0], b[1], b[2], o)
    out = md.operate(Mm, x, e)
    u = out["u"] if policy is None else policy(x, e)
    x1 = mm.f(x, u, e)
    o1 = mm.g_O(o, x, u, b)
    M1 = md.Update(Mm, x, e, learn=learn) if policy is None else Mm
    return e, u, out, x1, o1, M1


def run(M, bname, T=48, x0=mm.X_(0, 4, 2, 1), o0=1, M0=md.M_(0, 1, "none"), learn=True, horizon=10,
        policy=None, bg=None, recover=True, recover_rule="first"):
    """bg: optional explicit background list (overrides bname); recover_rule: 'first' (in K with base active
    at some step within the horizon) or 'hold2' (two consecutive such steps)."""
    B = background(bname, T + horizon + 1) if bg is None else bg
    x, o, Mm = x0, o0, M0
    core = M.viab_core()
    V = M.viab_stages()
    H = M.hor(V)
    rows = []
    col = 0
    for t in range(T):
        e, u, out, x1, o1, Mn = step(x, o, Mm, B[t], learn, policy)
        A = M.A(x, e)
        crit = M.Crit(x)
        cs = 1 if x.s == 0 else 0
        col = 1 if (col or cs) else 0
        z = zones(M, x, e, col)
        rec = "undef"
        if recover and any(k in z for k in ("Z1", "Z2", "Z3", "Z4")) and not col:
            rec = "".join("1" if _recover(M, x, o, Mm, B, t, ups, horizon, learn, policy, recover_rule) else "0"
                          for ups in mm.UPSILON)
        rows.append({"t": t, "x": tuple(x), "o": o, "b": B[t], "M": tuple(Mm), "u": u, "pur": out["pur"],
                     "mode": out["mode"], "P": out["P"], "Pi_eval": out["Pi_eval"],
                     "Pi": M.Pi(x), "inK": M.inK(x), "A": A, "blk": not A,
                     "e_in_Ereq": e in M.Ereq(x), "Crit": crit,
                     "B1": (not A) and any(M.ETA[n](x, e) == 0 for n in crit),
                     "B2": (not A) and M.D_FR(x, e, crit),
                     "SM": M.inK(x) if not col else "undef",
                     "EU": M.D_FR(x, e, crit) if not col else "undef",
                     "FR": ((len(A) > 0) if M.D_FR(x, e, crit) else "undef") if not col else "undef",
                     "mu_eff": M.mu_eff(x, e), "Viab": x in core, "Hor": H[x],
                     "u_in_Uviab": (u in M.U_viab(x, core)) if x in core else "",
                     "WF": x.s, "CS": cs, "Col": col, "zones": z, "Recover": rec})
        x, o, Mm = x1, o1, Mn
    return rows


def _recover(M, x, o, Mm, B, t, ups, horizon, learn, policy, rule="first"):
    """toy recover rule (fixed in advance): apply upsilon at t, continue the closed loop with the realised
    background; 1 iff the structure is kept (s = 1) and within the horizon x is in K with base active
    (rule 'first': at one step; rule 'hold2': at two consecutive steps)."""
    x = mm.upsilon(x, ups)
    need = 1 if rule == "first" else 2
    run_ok = 0
    for k in range(horizon + 1):
        if x.s == 0:
            return False
        if M.inK(x) and mm.base_active(x):
            run_ok += 1
            if run_ok >= need:
                return True
        else:
            run_ok = 0
        if k < horizon:
            _, _, _, x, o, Mm = step(x, o, Mm, B[t + k], learn, policy)
    return False
