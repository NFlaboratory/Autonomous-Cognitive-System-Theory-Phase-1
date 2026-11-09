# -*- coding: utf-8 -*-
"""E1 policies on MinACS.  Oracle policies use the true sets of the judgment layer; they are NOT
realisable by the individual (they read Viab_f(K), A(x,e) and the true e), and serve only as reference
trajectories.  Mechanism-free policies use the observation P_sens only."""
from .adapters import lcg

_CACHE = {}


def _sets():
    if "core" not in _CACHE:
        from minacs.analysis import Model
        M = Model("base")
        core = M.viab_core()
        _CACHE.update(M=M, core=core, uviab={x: M.U_viab(x, core) for x in core})
    return _CACHE["M"], _CACHE["core"], _CACHE["uviab"]


def p_viab(order):
    """kernel-maintaining responses: u in U^Viab(x) if x in Viab_f(K) (choice by `order`);
    otherwise a u in A(x,e) (same order); otherwise u_emptyset."""
    def pol(x, e):
        M, core, uv = _sets()
        if x in core and uv[x]:
            cand = uv[x]
        else:
            cand = M.A(x, e)
        if not cand:
            return "wait"
        return cand[0] if order == "first" else cand[-1]
    return pol


def p_A(mode):
    """one-step oracle: a u in A(x,e); 'first' = first in U order, 'greedy' = max (en, tp) of the successor."""
    def pol(x, e):
        M, core, uv = _sets()
        A = M.A(x, e)
        if not A:
            return "wait"
        if mode == "first":
            return A[0]
        return max(A, key=lambda u: (M._succ[(x, u, e)].en, M._succ[(x, u, e)].tp, -M.U.index(u)))
    return pol


def p_greedy():
    """reflex on the observation only (no memory, no evaluation of K)."""
    from minacs import mind as md
    from minacs import model as mm

    def pol(x, e):
        I = md.P_sens(x, e)
        _, p, en, tp, s, c, g, r = I
        if not (s == 1 and en > 0):
            return "wait"
        if en <= 3:
            if p == mm.RES:
                return "eat"
            return "R"
        if c == 1 and p != mm.SHELTER:
            return "L"
        return "wait"
    return pol


def p_fixed(seed):
    """a fixed action sequence generated from the seed (deterministic; independent of x and e)."""
    seq = []
    r = lcg(seed + 104729)
    for _ in range(256):
        seq.append(("wait", "L", "R", "eat")[next(r) % 4])
    state = {"k": 0}

    def pol(x, e):
        u = seq[state["k"] % len(seq)]
        state["k"] += 1
        return u
    return pol


def p_wait():
    return lambda x, e: "wait"
