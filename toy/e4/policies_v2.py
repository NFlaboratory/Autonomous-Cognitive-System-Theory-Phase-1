# -*- coding: utf-8 -*-
"""E1 on the v2 toy: policies imposed on individual i (the partner j, the drone and the organisation keep
their own rules).  Oracle policies read the true local view lam, the true A(x,e) and the judgment layer's
kernel certificates; they are reference trajectories, NOT mechanisms an ACS individual could implement.

Kernel-maintaining responses in v2.  Viab_f(K) is decided in v2 only by certificates (judge.ViabOracle):
'in' means an E_req-invariant closed subset S of K_req containing x was constructed, hence S is a subset of
Viab_f(K).  For x in such an S,
    U^Viab_cert(x) = {u : every robust successor of (x, u) lies in S}   (subset of U^Viab(x)).
Rule fixed before any run:
  - if the current certificate S contains x, use it; otherwise ask the oracle (in_core) for a new one;
  - if x is certified, choose from U^Viab_cert(x) (first / last in U order);
  - if the oracle answers 'not_in' or 'undetermined', choose from A(x,e) (same order); if A is empty, wait.
"""
from acs_toy.body import U, U_EMPTY
from acs_toy.judge import ViabOracle


class ViabPolicy:
    """oracle: a ViabOracle shared across units with the same body parameters (its successor tables and the
    memo of in_core answers depend only on x, so sharing changes no result, only the running time)."""

    def __init__(self, body, order, oracle=None, memo=None):
        self.body, self.order = body, order
        self.oracle = oracle if oracle is not None else ViabOracle(body)
        self.memo = memo if memo is not None else {}
        self.S = None
        self.log = {"cert_steps": 0, "undetermined_steps": 0, "not_in_steps": 0, "oracle_calls": 0}

    def certified(self, x):
        c = ViabOracle.canon(x)
        if self.S is not None and c in self.S:
            return True
        self.log["oracle_calls"] += 1
        if c not in self.memo:
            r = self.oracle.in_core(x)
            self.memo[c] = (r, self.oracle.last_certificate if r == "in" else None)
        r, S = self.memo[c]
        if r == "in":
            self.S = S
            return True
        self.log["undetermined_steps" if r == "undetermined" else "not_in_steps"] += 1
        return False

    def u_viab_cert(self, x):
        T = self.oracle.tables(x)
        return tuple(u for u in U if all(ViabOracle.canon(z) in self.S for z in T.robust_successors(u)))

    def __call__(self, x, lam):
        A = tuple(u for u in U if self.body.in_K(self.body.f(x, u, lam)))
        if self.certified(x):
            cand = self.u_viab_cert(x)
            self.log["cert_steps"] += 1
            self.last = ("cert", cand)
        else:
            cand = A
            self.last = ("fallback", cand)
        if not cand:
            return U_EMPTY
        return cand[0] if self.order == "first" else cand[-1]


def p_A(body, mode):
    def pol(x, lam):
        A = tuple(u for u in U if body.in_K(body.f(x, u, lam)))
        if not A:
            return U_EMPTY
        if mode == "first":
            return A[0]
        return max(A, key=lambda u: (body.f(x, u, lam).energy, body.f(x, u, lam).temp, body.f(x, u, lam).integ,
                                     -U.index(u)))
    return pol


def _toward(p, g):
    if g[0] > p[0]:
        return "E"
    if g[0] < p[0]:
        return "W"
    if g[1] > p[1]:
        return "S"
    if g[1] < p[1]:
        return "N"
    return None


def p_greedy(cfg, mind):
    """reflex on the observation I = P_sens(x, e) only (no memory, no evaluation of K):
    hungry (energy <= 10): eat if the current cell shows a resource, else step toward the nearest cell seen
    with a resource, else toward the nearest resource cell of the (known) geometry;
    cold (T >= 1) with temp <= 4: go to the shelter, open the door there if it is seen closed;
    otherwise wait."""
    def pol(x, e):
        I = mind.P_sens(x, e)
        _, sp, T, cells, peers, dr, gift, local = I
        if T is None:
            return U_EMPTY
        px, py, en, temp = sp[0], sp[1], sp[2], sp[4]
        p = (px, py)
        if en <= 10:
            here = [lv for (c, lv, rk, tr, dv) in cells if c == p]
            if here and here[0] > 0 and p in cfg.resources:
                return "eat"
            seen = [c for (c, lv, rk, tr, dv) in cells if lv > 0 and c in cfg.resources]
            goals = seen or list(cfg.resources)
            g = min(goals, key=lambda c: abs(c[0] - px) + abs(c[1] - py))
            return _toward(p, g) or U_EMPTY
        if T >= 1 and temp <= 4:
            if p == cfg.shelter:
                door = [dv for (c, lv, rk, tr, dv) in cells if c == cfg.shelter]
                return "open_door" if (door and door[0] == 0) else U_EMPTY
            return _toward(p, cfg.shelter) or U_EMPTY
        return U_EMPTY
    return pol


def p_fixed(seed, lcg):
    seq = []
    r = lcg(seed + 104729)
    for _ in range(512):
        seq.append(U[next(r) % len(U)])
    state = {"k": 0}

    def pol(*_):
        u = seq[state["k"] % len(seq)]
        state["k"] += 1
        return u
    return pol
