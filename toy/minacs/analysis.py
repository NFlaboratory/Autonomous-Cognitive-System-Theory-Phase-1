# -*- coding: utf-8 -*-
"""Exact computation of the paper's sets on a finite model by full enumeration.

The Model object carries (X, U, E_ext, f, E, Pi, g_O, Upsilon) so that the same analysis runs on
the base MinACS and on degenerate variants (7-tuple component removed or trivialised).
Every quantifier over X, U, E_ext, E^bg, O is evaluated over the whole finite set.
"""
from collections import Counter

from . import model as mm


class Model:
    def __init__(self, name, XS=None, U=None, ES=None, f=None, ETA=None, Pi=None, g_O=None):
        self.name = name
        self.XS = XS if XS is not None else mm.XS
        self.U = U if U is not None else mm.U
        self.ES = ES if ES is not None else mm.ES
        self.f = f if f is not None else mm.f
        self.ETA = ETA if ETA is not None else mm.ETA
        self.Pi = Pi if Pi is not None else mm.Pi
        self.g_O = g_O if g_O is not None else mm.g_O
        self._succ = {(x, u, e): self.f(x, u, e) for x in self.XS for u in self.U for e in self.ES}
        self._Ereq = {x: tuple(e for e in self.ES if all(h(x, e) for h in self.ETA.values())) for x in self.XS}

    # ------------------------------------------------------------------ sec.2
    def inK(self, x):
        return self.Pi(x) >= 0

    def A(self, x, e):
        return tuple(u for u in self.U if self.inK(self._succ[(x, u, e)]))

    def Ereq(self, x):
        return self._Ereq[x]

    def D_eta(self, name):
        h = self.ETA[name]
        return {x for x in self.XS if any(h(x, e) for e in self.ES)}

    def E_viab1(self, x):
        return tuple(e for e in self.ES if self.A(x, e))

    # ------------------------------------------------------------------ sec.3 one-step
    def D_req(self):
        return {x for x in self.XS if self.Ereq(x)}

    def K_req(self):
        return {x for x in self.XS if self.inK(x) and self.Ereq(x)}

    def crit(self, x, name):
        h = self.ETA[name]
        if not any(h(x, e) == 0 for e in self.ES):
            return False
        if any(h(x, e) == 0 and self.A(x, e) for e in self.ES):
            return False
        return any(h(x, e) == 1 and self.A(x, e) for e in self.ES)

    def Crit(self, x):
        return tuple(n for n in self.ETA if self.crit(x, n))

    def D_FR(self, x, e, crit=None):
        crit = self.Crit(x) if crit is None else crit
        return all(self.ETA[n](x, e) == 1 for n in crit)

    def mu_eff(self, x, e):
        A = self.A(x, e)
        sig = {u: tuple(self.inK(self._succ[(x, u, e2)]) for e2 in self.Ereq(x)) for u in A}
        return len(set(sig.values()))

    def N(self, x, u):
        return tuple(e for e in self.Ereq(x) if not self.inK(self._succ[(x, u, e)]))

    def U_rob(self, x):
        return tuple(u for u in self.U if not self.N(x, u))

    def EC(self, x):
        for u in self.U:
            vals = {tuple(getattr(self._succ[(x, u, e)], k) for k in mm.I_E) for e in self.ES}
            if len(vals) > 1:
                return True
        return False

    # ------------------------------------------------------------------ sec.3 robust sets
    def viab_stages(self):
        """[V^(0), V^(1), ...] until stabilisation (def:viab_stage)."""
        V = [self.K_req()]
        while True:
            prev = V[-1]
            nxt = {x for x in V[0] if any(all(self._succ[(x, u, e)] in prev for e in self.Ereq(x)) for u in self.U)}
            V.append(nxt)
            if nxt == prev:
                return V

    def viab_core(self):
        """greatest E_req-invariant subset of K_req (def:viab_core), computed as a greatest fixed point."""
        S = set(self.K_req())
        changed = True
        while changed:
            changed = False
            for x in list(S):
                if not any(all(self._succ[(x, u, e)] in S for e in self.Ereq(x)) for u in self.U):
                    S.discard(x)
                    changed = True
        return S

    def hor(self, V):
        """Hor_f (def:viab_horizon): sup{nu : x in V^(nu)}; 'inf' if x in the stabilised set."""
        last = V[-1]
        out = {}
        for x in self.XS:
            if x not in V[0]:
                out[x] = None
            elif x in last:
                out[x] = "inf"
            else:
                out[x] = max(k for k, Vk in enumerate(V) if x in Vk)
        return out

    def U_viab(self, x, core):
        return tuple(u for u in self.U if all(self._succ[(x, u, e)] in core for e in self.Ereq(x)))

    def viab_resp(self):
        """Viab^resp_f(K) on X x O (def:viab_resp)."""
        def Breq(x, o):
            return tuple((e.c, e.g, e.rho) for e in self.Ereq(x) if e.r == o)
        S = {(x, o) for x in self.XS for o in mm.OS if self.inK(x) and Breq(x, o)}
        changed = True
        while changed:
            changed = False
            for (x, o) in list(S):
                ok = False
                for u in self.U:
                    if all((self._succ[(x, u, mm.E_(b[0], b[1], b[2], o))], self.g_O(o, x, u, b)) in S
                           for b in Breq(x, o)):
                        ok = True
                        break
                if not ok:
                    S.discard((x, o))
                    changed = True
        return S

    def robust_all_e_kernel(self):
        """comparison set: largest subset of K invariant for some u against ALL e in E_ext
        (the E_req restriction removed).  Not a set of the paper; used only for contrast."""
        S = {x for x in self.XS if self.inK(x)}
        changed = True
        while changed:
            changed = False
            for x in list(S):
                if not any(all(self._succ[(x, u, e)] in S for e in self.ES) for u in self.U):
                    S.discard(x)
                    changed = True
        return S

    # ------------------------------------------------------------------ CR-1
    def eta0_graph(self, name):
        h = self.ETA[name]
        return {x: {self._succ[(x, u, e)] for u in self.U for e in self.ES if h(x, e) == 0} for x in self.XS}

    def inf_eta0(self, name):
        """states from which an infinite state-transition sequence with eta = 0 at every step exists."""
        G = self.eta0_graph(name)
        S = {x for x in self.XS if G[x]}
        changed = True
        while changed:
            changed = False
            for x in list(S):
                if not (G[x] & S):
                    S.discard(x)
                    changed = True
        return S, G

    def CR1(self, WF):
        res = {}
        for name, h in self.ETA.items():
            S, G = self.inf_eta0(name)
            Deta = self.D_eta(name)
            wit_i = wit_c = None
            for x in self.XS:
                if WF(x) != 1:
                    continue
                for e in self.ES:
                    if h(x, e) != 1:
                        continue
                    for u in self.U:
                        y = self._succ[(x, u, e)]
                        if y in S:
                            wit_i = wit_i or (x, u, e, y)
                            if y in Deta:
                                wit_c = wit_c or (x, u, e, y)
            # (ii): no infinite eta=0 path stays in WF=1 forever <=> no cycle among WF=1 nodes of G restricted to S
            nodes = {x for x in S if WF(x) == 1}
            sub = {x: {y for y in G[x] if y in nodes} for x in nodes}
            cyc = _has_cycle(sub)
            absorbing = all(all(WF(y) == 0 for y in G[x]) for x in self.XS if WF(x) == 0)
            res[name] = {"i": wit_i, "c": wit_c, "ii": (not cyc) and absorbing, "ii_cycle_found": cyc,
                         "ii_wf0_absorbing": absorbing}
        res["b"] = next(((x, self.Ereq(x)[0]) for x in self.XS if self.Ereq(x)), None)
        return res


def _has_cycle(adj):
    WHITE, GRAY, BLACK = 0, 1, 2
    col = {v: WHITE for v in adj}
    for s in adj:
        if col[s] != WHITE:
            continue
        stack = [(s, iter(adj[s]))]
        col[s] = GRAY
        while stack:
            v, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                col[v] = BLACK
                stack.pop()
            elif col[nxt] == GRAY:
                return True
            elif col[nxt] == WHITE:
                col[nxt] = GRAY
                stack.append((nxt, iter(adj[nxt])))
    return False


# ---------------------------------------------------------------------- full tables
def state_table(M):
    V = M.viab_stages()
    core = M.viab_core()
    H = M.hor(V)
    rows = []
    for x in M.XS:
        rows.append({"x": x, "Pi": M.Pi(x), "inK": M.inK(x), "Ereq_n": len(M.Ereq(x)),
                     "D_heat": x in M.D_eta("heat") if "heat" in M.ETA else None,
                     "D_food": x in M.D_eta("food") if "food" in M.ETA else None,
                     "Crit": M.Crit(x), "U_rob": M.U_rob(x), "EC": M.EC(x),
                     "Viab": x in core, "Hor": H[x], "U_viab": M.U_viab(x, core) if x in core or M.inK(x) else (),
                     "E_viab1_n": len(M.E_viab1(x))})
    return rows, V, core


def pair_table(M):
    rows = []
    crit = {x: M.Crit(x) for x in M.XS}
    for x in M.XS:
        for e in M.ES:
            A = M.A(x, e)
            dfr = M.D_FR(x, e, crit[x])
            b1 = (not A) and any(M.ETA[n](x, e) == 0 for n in crit[x])
            b2 = (not A) and dfr
            rows.append({"x": x, "e": e, "A": A, "blk": not A, "e_in_Ereq": e in M.Ereq(x), "D_FR": dfr,
                         "B1": b1, "B2": b2, "mu_eff": M.mu_eff(x, e),
                         "weak": any(M.N(x, u) for u in A)})
    return rows
