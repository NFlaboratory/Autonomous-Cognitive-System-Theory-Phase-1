# -*- coding: utf-8 -*-
"""Domain-independent judgment layer: exact computation of the paper's sets on a finite domain.

A domain object D supplies only the domain-dependent parts:
  D.XS, D.U, D.U_EMPTY, D.ES            finite X, U, E_ext
  D.f(x, u, e)                          transition
  D.ETA = {name: eta(x, e) -> 0/1}      required environmental factors (E)
  D.Pi(x)                               feasibility function (K = {Pi >= 0})
  D.OS, D.split(e) -> (b, o), D.make_e(b, o), D.g_O(o, x, u, b)
                                        response-dependent environment part O and its update
  D.I_E                                 environment-response coordinates (names of fields of x)
Nothing here refers to a particular domain.  The code is the MinACS analysis (E6) with every
domain reference replaced by a call to D; run_checks.py verifies that both give identical results
on MinACS.
"""


class Judge:
    def __init__(self, D, name=None, U=None, ETA=None, Pi=None, f=None):
        self.D = D
        self.name = name or D.NAME
        self.XS = D.XS
        self.U = U if U is not None else D.U
        self.ES = D.ES
        self.f = f if f is not None else D.f
        self.ETA = ETA if ETA is not None else D.ETA
        self.Pi = Pi if Pi is not None else D.Pi
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
            vals = {tuple(getattr(self._succ[(x, u, e)], k) for k in self.D.I_E) for e in self.ES}
            if len(vals) > 1:
                return True
        return False

    # ------------------------------------------------------------------ sec.3 robust sets
    def viab_stages(self):
        V = [self.K_req()]
        while True:
            prev = V[-1]
            nxt = {x for x in V[0] if any(all(self._succ[(x, u, e)] in prev for e in self.Ereq(x)) for u in self.U)}
            V.append(nxt)
            if nxt == prev:
                return V

    def viab_core(self):
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

    def Breq(self, x, o):
        return tuple(self.D.split(e)[0] for e in self.Ereq(x) if self.D.split(e)[1] == o)

    def viab_resp(self):
        D = self.D
        S = {(x, o) for x in self.XS for o in D.OS if self.inK(x) and self.Breq(x, o)}
        changed = True
        while changed:
            changed = False
            for (x, o) in list(S):
                ok = False
                for u in self.U:
                    if all((self._succ[(x, u, D.make_e(b, o))], D.g_O(o, x, u, b)) in S for b in self.Breq(x, o)):
                        ok = True
                        break
                if not ok:
                    S.discard((x, o))
                    changed = True
        return S

    def resp_invariant(self, resp):
        D = self.D
        return all(any(all((self._succ[(x, u, D.make_e(b, o))], D.g_O(o, x, u, b)) in resp for b in self.Breq(x, o))
                       for u in self.U) for (x, o) in resp)

    def robust_all_e_kernel(self):
        """comparison set (not a set of the paper): largest subset of K invariant for some u against ALL e."""
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


def pair_table(J):
    rows = []
    crit = {x: J.Crit(x) for x in J.XS}
    for x in J.XS:
        for e in J.ES:
            A = J.A(x, e)
            dfr = J.D_FR(x, e, crit[x])
            rows.append({"x": x, "e": e, "A": A, "blk": not A, "e_in_Ereq": e in J.Ereq(x), "D_FR": dfr,
                         "B1": (not A) and any(J.ETA[n](x, e) == 0 for n in crit[x]),
                         "B2": (not A) and dfr, "mu_eff": J.mu_eff(x, e),
                         "weak": any(J.N(x, u) for u in A)})
    return rows
