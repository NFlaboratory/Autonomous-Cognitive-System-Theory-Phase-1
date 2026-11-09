# -*- coding: utf-8 -*-
"""Judgment layer: the paper's definitions evaluated on the standard operation record.
Uses the true f, K, E, g_O.  The individuals' mechanisms (mind.py) never see these values.

Every "for all / exists e in E_ext" is evaluated exactly over the image of E_ext under the
local view lam (body.lam_space); this is exact because f and every eta read e only through lam.
"""
from itertools import product
from typing import Dict, List

from .body import U, U_EMPTY, CODE, DIRS, I_E, FIELDS, Lam
from .mind import CORR, AGE_MAX
from .sim import UPSILON, apply_upsilon, run as sim_run


# =========================================================================== per-state structure
class StateTables:
    """successor tables of one state x: for each u, {lam: f(x,u,lam)} over lam_space(x,[u])."""

    def __init__(self, body, x):
        self.body, self.x = body, x
        self.tab = {u: {lam: body.f(x, u, lam) for lam in body.lam_space(x, [u])} for u in U}
        self.rel = {u: body.relevant(x, [u]) for u in U}
        self.eta_fields = body.relevant(x, [])

    def eta_all(self, lam):
        return all(self.body.eta(n, self.x, lam) for n in self.body.ETA)

    # D_req / E_req(x) nonempty
    def Ereq_nonempty(self):
        return any(self.eta_all(l) for l in self.body.lam_space(self.x, []))

    def crit(self, name):
        """x in Crit^(1)_eta (def:eu_critical_domain), exactly."""
        b, x = self.body, self.x
        base = b.lam_space(x, [])
        if not any(b.eta(name, x, l) == 0 for l in base):                       # (i)
            return False
        for u in U:                                                              # (ii) = for all u, all e'
            for l, y in self.tab[u].items():
                if b.eta(name, x, l) == 0 and b.in_K(y):
                    return False
        return any(b.eta(name, x, l) == 1 and b.in_K(y) for u in U for l, y in self.tab[u].items())  # (iii)

    def phi_equal(self, u, v):
        """phi_u = phi_v on E_req(x) (def:mu_eff), evaluated on the union of the relevant fields."""
        b, x = self.body, self.x
        fields = tuple(sorted(set(self.rel[u]) | set(self.rel[v])))
        for l in b.lam_space(x, fields=fields):
            if not self.eta_all(l):
                continue
            lu = _restrict(l, self.rel[u])
            lv = _restrict(l, self.rel[v])
            if b.in_K(self.tab[u][lu]) != b.in_K(self.tab[v][lv]):
                return False
        return True

    def mu_eff(self, A):
        classes = []
        for u in A:
            for c in classes:
                if self.phi_equal(u, c[0]):
                    c.append(u)
                    break
            else:
                classes.append([u])
        return len(classes), classes

    def N_nonempty(self, u):
        """N(x,u) != empty (def:nonresponse_env_set)."""
        return any(self.eta_all(l) and not self.body.in_K(y) for l, y in self.tab[u].items())

    def U_rob(self):
        return tuple(u for u in U if not self.N_nonempty(u))

    def EC(self):
        """structural environment coupling EC(x) (def:env_coupling)."""
        idx = [FIELDS.index(k) for k in I_E]
        for u in U:
            seen = set()
            for l, y in self.tab[u].items():
                seen.add(tuple(y[k] for k in idx))
                if len(seen) > 1:
                    return True
        return False

    def robust_successors(self, u):
        return {y for l, y in self.tab[u].items() if self.eta_all(l)}


def _restrict(l, fields):
    return Lam(*[getattr(l, k) if k in fields else 0 for k in Lam._fields])


class ViabOracle:
    """Viab_f^(nu)(K), Hor_f (def:viab_stage, def:viab_horizon) and membership in Viab_f(K)
    (def:viab_core) by an exact greatest-fixed-point on the explored robust-reachable graph."""

    def __init__(self, body, budget=4000):
        self.body = body
        self.cache = {}
        self.budget = budget

    def tables(self, x):
        t = self.cache.get(x)
        if t is None:
            t = StateTables(self.body, x)
            if len(self.cache) > 20000:
                self.cache.clear()
            self.cache[x] = t
        return t

    def in_Kreq(self, x):
        return self.body.in_K(x) and self.tables(x).Ereq_nonempty()

    def stage(self, x, nu, memo):
        key = (x, nu)
        if key in memo:
            return memo[key]
        if not self.in_Kreq(x):
            memo[key] = False
            return False
        if nu == 0:
            memo[key] = True
            return True
        T = self.tables(x)
        ok = any(all(self.stage(y, nu - 1, memo) for y in T.robust_successors(u)) for u in U)
        memo[key] = ok
        return ok

    def hor(self, x, cap):
        """(value, exact): exact Hor_f(x) if < cap, else (cap, False) meaning >= cap; None if x not in K_req."""
        if not self.in_Kreq(x):
            return None, True
        memo = {}
        nu = 0
        while nu < cap and self.stage(x, nu + 1, memo):
            nu += 1
        return nu, nu < cap

    @staticmethod
    def canon(x):
        """alert, beacon, last_u are read by no f, eta or Pi (THETA free): states differing only there
        have identical successor sets and K_req membership, so the quotient is exact."""
        return x._replace(alert=0, beacon=0, last_u=0)

    def in_core(self, x, hor=None):
        """'in' / 'not_in' / 'undetermined' for x in Viab_f(K) (def:viab_core).
        'in'     : an E_req-invariant K' containing x was constructed (a policy-closed set; certificate);
        'not_in' : x not in K_req, or Hor_f(x) finite (prop:viab_stage_core);
        otherwise 'undetermined' (the greedy construction failed within the budget)."""
        if not self.in_Kreq(x):
            return "not_in"
        if hor is not None and hor[1] and hor[0] is not None:
            return "not_in"
        res = self.body.cfg.resources

        def d_res(z):
            return min(abs(z.px - c[0]) + abs(z.py - c[1]) for c in res)
        for scorer in (lambda succ: (min(z.energy for z in succ), min(z.integ for z in succ)),
                       lambda succ: (-max(d_res(z) for z in succ), min(z.energy for z in succ))):
            r = self._closed_set(x, scorer)
            if r:
                return "in"
        return "undetermined"

    def _closed_set(self, x, scorer):
        S = {}
        frontier = [self.canon(x)]
        S[frontier[0]] = None
        while frontier:
            y = frontier.pop()
            T = self.tables(y)
            best = None
            for u in U:
                succ = {self.canon(z) for z in T.robust_successors(u)}
                if not succ or not all(self.in_Kreq(z) for z in succ):
                    continue
                score = scorer(succ) + (-len(succ - set(S)),)
                if best is None or score > best[0]:
                    best = (score, u, succ)
            if best is None:
                return False
            S[y] = best[1]
            for z in best[2]:
                if z not in S:
                    S[z] = None
                    frontier.append(z)
                    if len(S) > self.budget:
                        return False
        self.last_certificate = S
        return True


# =========================================================================== zones (toy rules, fixed)
def zones(body, x, A_empty, col, ft1):
    z = set()
    if col:
        return {"Z5"}
    act = body.activity(x)
    healths = (x.hpsl, x.hsens, x.heff, x.hmem)
    if A_empty:
        z.add("Z4")
    if ft1:
        z.add("Z3")
    if (not ft1) and (min(healths) <= 1 or not all(act.values())):
        z.add("Z2")
    if min(healths) == 2 or x.energy <= 6 or x.integ <= 6 or x.temp <= 4:
        z.add("Z1")
    if not z:
        z.add("Z0")
    return z


# =========================================================================== main evaluation
def judge_run(cfg, rec, final_world, sysobjs, progress=None):
    bodies, minds, B = sysobjs
    names = sorted(rec[0][0].agents)
    out = {n: [] for n in names}
    oracles = {n: ViabOracle(bodies[n]) for n in names}
    worlds = [w for (w, _) in rec] + [final_world]
    Tn = len(rec)
    for t in range(Tn):
        w, info = rec[t]
        w1 = worlds[t + 1]
        for n in names:
            body, mind = bodies[n], minds[n]
            x, M = w.agents[n]
            x1, M1 = w1.agents[n]
            lam = info[n]["lam"]
            u = info[n]["u"]
            r = info[n]["rec"]
            T = oracles[n].tables(x)
            row = {"t": t, "name": n}
            row.update({f: getattr(x, f) for f in FIELDS})
            row["T"] = B[t].T
            row["u"] = u
            row["gift_lam"] = lam.gift
            # ---- sec.2: Pi, K, A, blockage, WF, SC-1, FT-1, activity
            Pi = body.Pi(x)
            row["Pi"] = Pi
            row["inK"] = Pi >= 0
            A = tuple(v for v in U if body.in_K(body.f(x, v, lam)))
            row["A"] = A
            row["blk"] = len(A) == 0
            row["WF"] = body.WF(x)
            row["SC1"] = body.SC1(x)
            row["FT1"] = body.FT1(x)
            act = body.activity(x)
            row.update({f"act_{k}": v for k, v in act.items()})
            row["base_active"] = body.active_base(x)
            row["E_viab1"] = None  # computed lazily (one-step viable environment) below
            # ---- sec.3: SM / Crit / EU / D_FR / FR
            crit = tuple(nm for nm in body.ETA if T.crit(nm))
            row["Crit"] = crit
            eta_now = {nm: body.eta(nm, x, lam) for nm in body.ETA}
            row.update({f"eta_{k}": v for k, v in eta_now.items()})
            row["e_in_Ereq"] = all(eta_now.values())
            row["Ereq_nonempty"] = T.Ereq_nonempty()
            dfr = all(eta_now[nm] == 1 for nm in crit)
            row["D_FR"] = dfr
            row["EU_cond"] = dfr                         # EU_t truth condition (value used only on T_P)
            row["FR_cond"] = (len(A) > 0) if dfr else None
            row["B1"] = row["blk"] and any(eta_now[nm] == 0 for nm in crit)
            row["B2"] = row["blk"] and dfr
            mu, classes = T.mu_eff(A)
            row["mu_eff"] = mu
            row["weak_point"] = any(T.N_nonempty(v) for v in A)
            urob = T.U_rob()
            row["U_rob_n"] = len(urob)
            row["EC"] = T.EC()
            Vm = tuple(f for f in FIELDS if getattr(x, f) - body.theta[FIELDS.index(f)] < 0)
            row["V_minus"] = Vm
            row["V_minus_E"] = tuple(f for f in Vm if f in I_E)
            row["d_minus"] = tuple((f, body.theta[FIELDS.index(f)] - getattr(x, f)) for f in Vm)
            mins = [f for f in FIELDS if getattr(x, f) - body.theta[FIELDS.index(f)] == Pi]
            row["argmin_Pi"] = tuple(mins)
            row["piE_sensitive"] = any(f in I_E for f in mins)
            row["s_SM"] = min(1.0, max(0.0, Pi / cfg.pi_ref))
            row["sel_resp"] = (u not in A)
            # ---- chi_EI: a boundary-crossing action realised (intake, release, contact)
            eff = body.effect(x, u, lam)
            row["chi_EI"] = 1 if (eff in ("eat_cell", "collect", "give", "deposit", "open_door", "move", "signal")
                                  or lam.gift > 0 or lam.rock_cur) else 0
            # ---- Viab stages (sampled)
            if t % cfg.hor_every == 0:
                h, exact = oracles[n].hor(x, cfg.hor_cap)
                row["Hor"] = None if h is None else (h if exact else f">={cfg.hor_cap}")
                row["Viab_core"] = oracles[n].in_core(x, (h, exact))
                row["in_Viab1"] = oracles[n].stage(x, 1, {})
            else:
                row["Hor"] = row["Viab_core"] = row["in_Viab1"] = ""
            # ---- sec.4: mechanism outputs (attributed only if WF=1)
            if row["WF"] and r is not None:
                P, ev, sig, evrq, Req = r["out2"]
                o3 = r["o3"]
                row["P"] = P
                row["Pi_eval"] = ev[0]
                row["C1"] = ev[1]
                row["C2"] = "".join(str(b) for b in ev[2])
                row["C3"] = ev[3]
                row["mu_hat"] = ev[4]
                row["Req"] = Req
                row["sig"] = sig
                row["mode"] = o3["mode"]
                row["style"] = o3["style"]
                row["Pur"] = o3["Pur"]
                row["stat"] = o3["stat"]
                row["fast"] = o3["fast"]
                row["u_M3"] = o3["u"]
                row["r_local"] = r["r_local"]
                row["psl4_override"] = r["r_local"] is not None and r["r_local"] != o3["u"]
                row["Mis"] = tuple((q, c) for (q, c) in sig if (c, o3["mode"]) not in CORR)
                row["eps_est"] = max(abs(a - b) for a, b in zip(r["S1"][0][2:5], (x.energy, x.integ, x.temp)))
                row["action_class"] = action_class(mind, M, r)
                row["xi_tokens"] = tuple(tok for tok, _ in r["S1"][2][1])
            else:
                for k in ("P", "Pi_eval", "C1", "C2", "C3", "mu_hat", "Req", "sig", "mode", "style", "Pur", "stat",
                          "fast", "u_M3", "r_local", "psl4_override", "Mis", "eps_est", "action_class", "xi_tokens"):
                    row[k] = "undef"
            # ---- sec.5: delta_M, learning, records, readouts
            dvec = tuple(round(_dist_c(M[c], M1[c]), 4) for c in range(3))
            row["delta_M"] = dvec
            row["delta"] = max(dvec)
            row["delta_L"] = max(round(_dist_part(M[c][0], M1[c][0]), 4) for c in range(3))
            row.update(readouts(cfg, body, mind, x, M))
            row["rec_agree"] = record_agreement(mind, M1, r) if (r is not None and row["WF"]) else "undef"
            out[n].append(row)
        if progress and t % 50 == 0:
            progress(t)
    for n in names:
        trajectory_level(cfg, out[n], rec, final_world, sysobjs, n)
        posthoc_prediction(cfg, out[n], rec, worlds, minds[n], n)
        tstab(cfg, out[n])
    relations(cfg, out, rec, worlds, names)
    org = org_layer(cfg, rec, worlds, sysobjs) if cfg.with_org and len(names) >= 2 else []
    return out, org


# =========================================================================== helpers for sec.4 / sec.5
def action_class(mind, M, r):
    """def:req_involvement / def:action_classes via counterfactual M3 calls (M3 is total)."""
    P, ev, sig, evrq, Req = r["out2"]
    S1 = r["S1"]
    model = mind.part(M, 1, "L")
    u_ref = mind.resolve(mind.M3(S1, r["out2"], M, model)["u"], r["r_local"], "std")
    involved = []
    for q in Req:
        R2 = tuple(a for a in Req if a != q)
        sig2 = tuple(s for s in sig if s[0] != q)
        ev2 = tuple(kv for kv in evrq if kv[0][0] != q)
        u2 = mind.resolve(mind.M3(S1, (P, ev, sig2, ev2, R2), M, model)["u"], r["r_local"], "std")
        if u2 != u_ref:
            involved.append(q)
    return ("purpose:" + "+".join(involved)) if involved else "non-purpose"


def _flat(part):
    return tuple(part)


def _dist_part(a, b):
    """normalised Hamming distance over the fields of one factor (diameter 1, ass:M_compact)."""
    da, db = dict(a), dict(b)
    keys = sorted(set(da) | set(db))
    if not keys:
        return 0.0
    return sum(1 for k in keys if da.get(k) != db.get(k)) / len(keys)


def _dist_c(Mc, Mc1):
    return max(_dist_part(Mc[0], Mc1[0]), _dist_part(Mc[1], Mc1[1]))


def readouts(cfg, body, mind, x, M):
    """sec.5 readouts: beta (def:beta_intertime_update), d_eff, h, memory sets (sizes)."""
    m2L, m3L = mind.part(M, 2, "L"), mind.part(M, 3, "L")
    beta_val = abs(m2L["wE"] - 2) / 2.0             # reference standard: energy weight 2 (attributed to val)
    beta_act = m3L["wX"] / 3.0                      # reference standard: no exploration preference (act)
    # d_eff = number of internally distinct believed options (toy rule; Phase 1.alpha in the paper)
    m1L = mind.part(M, 1, "L")
    opts = {"shelter"}
    for k, (lv, age) in enumerate(m1L["res"]):
        if lv > 0 and age < AGE_MAX:
            opts.add(f"r{k}")
    if m2L["trustP"] >= 1:
        opts.add("partner")
    if m2L["trustD"] >= 1:
        opts.add("drone")
    d_eff = min(10, len(opts) * (1 if x.energy > 0 else 0))
    ms = mind.memory_sets(M)
    return {"beta_val": beta_val, "beta_act": round(beta_act, 3), "d_eff": d_eff,
            "h_psl": x.hpsl / 3, "h_mem": x.hmem / 3, "h_sens": x.hsens / 3, "h_eff": x.heff / 3,
            **{f"T_{k}": len(v) for k, v in ms.items()},
            "F_M1": (1.0 if body.activity(x)["disc"] else 0.0) * x.hsens / 3,
            "F_M2": 1.0 if body.activity(x)["val"] else 0.0,
            "F_M3": (1.0 if body.activity(x)["act"] else 0.0) * x.heff / 3,
            "F_PSL": x.hpsl / 3 * (1.0 if x.energy > 0 else 0.0),
            "F_ISL_sens": x.hsens / 3, "F_ISL_mem": x.hmem / 3, "F_ISL_eff": x.heff / 3}


def record_agreement(mind, M1, r):
    """def:s5_record_agreement: which of the 7 record components equal the actual time-t values."""
    past = mind.rho_past(M1)
    S1 = r["S1"]
    P = r["out2"][0]
    names = []
    vals = [P, r["u"], None, S1, None, r["o3"]["Pur"], None]
    for k in (0, 1, 3, 5):
        names.append(("PuxSIPG"[k] if False else ["P", "u", "xh", "S1", "I", "Pur", "G"][k],
                      past[k] == vals[k]))
    return "".join(("1" if ok else "0") for _, ok in names)    # order: P, u, S1, Pur


# =========================================================================== trajectory-level (sec.2, sec.7)
def trajectory_level(cfg, rows, rec, final_world, sysobjs, n):
    bodies = sysobjs[0]
    body = bodies[n]
    CS = []
    FTS = []
    col = 0
    ft = 0
    first_cs = None
    for k, r in enumerate(rows):
        x = rec[k][0].agents[n][0]
        # (SC-1)+(SC-2): integ==0 is a fixed point of f for all u,e and of every upsilon (checked in checks.py)
        cs = 1 if body.SC1(x) else 0
        if cs and first_cs is None:
            first_cs = k
        CS.append(cs)
        col = 1 if (col or cs) else 0
        r["CS"] = cs
        r["Col"] = col
        in_TFT = first_cs is None or k <= first_cs
        if in_TFT:
            # (FT-1)+(FT-2): integ==0 or hpsl==0 cannot be left (hpsl never increases); energy==0 alone can
            fts = 1 if (body.FT1(x) and (x.integ == 0 or x.hpsl == 0)) else 0
            r["FTS"] = fts
            ft = 1 if (ft or fts) else 0
        else:
            r["FTS"] = "undef"
        r["FT"] = ft
        r["T_P"] = (ft == 0)
        # predicates are defined only on T_P
        if r["T_P"]:
            r["SM"] = r["inK"]
            r["EU"] = r["EU_cond"]
            r["FR"] = r["FR_cond"] if r["D_FR"] else "undef"
        else:
            r["SM"] = r["EU"] = r["FR"] = "undef"
        r["zones"] = "+".join(sorted(zones(body, x, r["blk"], col, r["FT1"])))
    # paths (def:blk_path_set ... def:col_reaching_time)
    I_ACS = [r["t"] for r in rows if r["Col"] == 0]
    T_blk = next((r["t"] for r in rows if r["Col"] == 0 and r["blk"]), None)
    T_col = next((r["t"] for r in rows if r["Col"] == 1), None)
    for r in rows:
        r["in_I_ACS"] = r["Col"] == 0
    for r in rows:
        if r["Col"]:
            r["chi_EI"] = "undef"                     # no realisation attributed to Sigma_i after CS (def:collapse)
    t_iso = None
    for r in reversed([r for r in rows if r["Col"] == 0]):
        if r["chi_EI"] == 0:
            t_iso = r["t"]
        else:
            break
    rows[0]["_paths"] = {"chi0_through_record_end_from": t_iso,"I_ACS_end": (I_ACS[-1] if I_ACS else None), "T_blk": T_blk, "T_col": T_col,
                         "in_P_blk": T_blk is not None, "in_P_col": T_col is not None}
    # external recoverability on Z1..Z4 (def:external_recoverability)
    recover(cfg, rows, rec, sysobjs, n)
    # recovery from blockage: first non-blocked time after a blocked run, and its source
    prev_blk = False
    for k, r in enumerate(rows):
        r["blk_recovered"] = ""
        if prev_blk and not r["blk"] and r["Col"] == 0:
            r["blk_recovered"] = _blk_end_source(body, rec, k, n, rows)
        prev_blk = r["blk"]


def _blk_end_source(body, rec, k, n, rows):
    """how A_t became nonempty at k after A_{k-1} = empty (describer's reading, from the record):
    'e_t (gift at k)'  : A(x_k, e_k) would be empty with the gift slot of e_k set to 0;
    'x_k via gift at k-1': otherwise, if the transition into x_k received a gift;
    'autonomous'       : neither (f_auto + f_dir from the individual's own action and the environment)."""
    w, info = rec[k]
    x = w.agents[n][0]
    lam = info[n]["lam"]
    if lam.gift > 0:
        lam0 = lam._replace(gift=0)
        if not any(body.in_K(body.f(x, v, lam0)) for v in U):
            return "e_t (gift at k)"
    if rows[k - 1]["gift_lam"] > 0:
        return "x_k via gift at k-1"
    return "autonomous"


def recover(cfg, rows, rec, sysobjs, n):
    bodies, minds, B = sysobjs
    body = bodies[n]
    cache = {}
    for k, r in enumerate(rows):
        zs = set(r["zones"].split("+"))
        if not (zs & {"Z1", "Z2", "Z3", "Z4"}) or r["Col"]:
            r["Recover"] = "undef"
            continue
        if not (zs & {"Z2", "Z3", "Z4"}) and k % 5:
            r["Recover"] = "skip"                    # Z1 only: evaluated every 5th step to save time
            continue
        res = []
        for ups in UPSILON:
            ok = _recover_one(cfg, rec, sysobjs, n, k, ups)
            res.append("1" if ok else "0")
        r["Recover"] = "".join(res)


def _recover_one(cfg, rec, sysobjs, n, k, ups):
    """apply upsilon at time k and continue with the realised background and every mechanism:
    1 iff the same individual keeps its structure and, within the horizon, is in K with
    basic-function activity (toy judgment rule, fixed in advance)."""
    bodies, minds, B = sysobjs
    w = rec[k][0]
    h = min(cfg.recover_horizon, len(B) - k - 1)
    rr, wf, _ = sim_run(cfg, w0=w, t0=k, steps=h, bodies=bodies, minds=minds, B=B, upsilon=(n, ups))
    body = bodies[n]
    seq = [ww.agents[n][0] for (ww, _) in rr[1:]] + [wf.agents[n][0]]
    for x in seq:
        if x.integ == 0:
            return False
        if body.in_K(x) and body.active_base(x) and any(body.activity(x).values()):
            return True
    return False


def posthoc_prediction(cfg, rows, rec, worlds, mind, n):
    """pi_tau,t and tau_hat (def:s5_prediction_coefficient): theoretical prediction hits over (t, t+tau]."""
    tau = cfg.tau
    hits = []
    for k in range(len(rows)):
        r = rec[k][1][n]["rec"]
        G = None
        if r is not None:
            S1 = r["S1"]
            model = mind.part(rec[k][0].agents[n][1], 1, "L")
            G = mind.predict_G(model, S1[0], S1[1], r["u"])
        if G is None:
            hits.append(None)
            rows[k]["pred_theory_miss"] = "undef"
        else:
            c, lo, hi = G
            lv = worlds[k + 1].res.get(c, -1)
            miss = not (lo <= lv <= hi)
            hits.append(0 if miss else 1)
            rows[k]["pred_theory_miss"] = miss
        r1 = rec[k + 1][1][n]["rec"] if k + 1 < len(rec) else None
        rows[k]["pred_internal_miss"] = (r1["S1"][4][2] == 1) if (r1 is not None and rows[k]["WF"]) else "undef"
    for k in range(len(rows)):
        if k + tau < len(rows) and all(rows[s]["Col"] == 0 for s in range(k, k + tau + 1)):
            seg = [hits[s] for s in range(k, k + tau)]
            pi = sum(1 for h in seg if h == 1) / tau          # toy rule: a missing prediction counts as no hit
            rows[k]["pi_tau"] = round(pi, 3)
            rows[k]["tau_hat"] = round(tau * pi, 3)
        else:
            rows[k]["pi_tau"] = rows[k]["tau_hat"] = "undef"


def tstab(cfg, rows):
    """def:tstab on T_P."""
    s_lo, dmax, W = cfg.tstab
    for k, r in enumerate(rows):
        if not r["T_P"]:
            r["TSTAB"] = "undef"
            continue
        win = range(max(0, k - W + 1), k + 1)
        t1 = all(rows[q]["s_SM"] >= s_lo for q in win)
        t2 = all((not rows[q]["D_FR"]) or len(rows[q]["A"]) > 0 for q in win)
        t3 = all(rows[q]["EU"] is True for q in win)
        t4 = all(abs(rows[q]["s_SM"] - rows[q - 1]["s_SM"]) <= dmax for q in win if q - 1 in win)
        r["TSTAB"] = t1 and t2 and t3 and t4


# =========================================================================== sec.6 relations (record layer)
def relations(cfg, out, rec, worlds, names):
    L = cfg.window_L
    for n in names:
        others = [m for m in names if m != n]
        objs = {}
        for m in others:
            objs[m] = ("ACS", "P")
        if cfg.with_drone:
            objs["drone"] = ("agent", "Dr")
        for k, c in enumerate(cfg.resources):
            objs[f"res{k}"] = ("obj", f"r{k}")
        rows = out[n]
        for t, r in enumerate(rows):
            rel = {}
            for Y, (typ, tok) in objs.items():
                if t < L:
                    continue
                win = range(t - L, t + 1)
                if not all(rows[s]["in_I_ACS"] for s in win):
                    continue
                cont = all(isinstance(rows[s]["xi_tokens"], tuple) and tok in rows[s]["xi_tokens"] for s in win)
                if not cont:
                    continue
                cat, cost, pert = category(cfg, Y, typ, n, rows, rec, win)
                d_a = len(rows[t]["A"]) - len(rows[t - L]["A"])
                d_d = rows[t]["d_eff"] - rows[t - L]["d_eff"]
                if rows[t]["tau_hat"] == "undef" or rows[t - L]["tau_hat"] == "undef":
                    continue
                d_tau = round(rows[t]["tau_hat"] - rows[t - L]["tau_hat"], 3)
                rel[Y] = (cat, cost, pert, d_a, d_d, d_tau, Q_value(cfg, Y, typ, n, rows, rec, win))
            r["Rel"] = rel
    # bidirectional composition for ACS pairs
    if len(names) >= 2:
        a, b = names[0], names[1]
        for t in range(len(out[a])):
            ra, rb = out[a][t].get("Rel", {}), out[b][t].get("Rel", {})
            if b in ra and a in rb:
                ca, cb = ra[b][0], rb[a][0]
                both = "coop" if (ca == "sup" and cb == "sup") else ("conf" if (ca == "comp" and cb == "comp") else
                       ("sym" if (ca in ("sup", "dep") and cb in ("sup", "dep")) else ""))
                out[a][t]["Bi"] = out[b][t]["Bi"] = {"pair": (a, b), "homo": ca == cb, "cat_bi": both or "unassigned",
                                                     "dir": "undetermined"}
            else:
                out[a][t]["Bi"] = out[b][t]["Bi"] = None


def category(cfg, Y, typ, n, rows, rec, win):
    """toy recording rule for cat (the paper gives no establishment conditions: Phase 1.alpha)."""
    gifts = sum(rec[s][0].gifts.get(n, 0) for s in win if s < len(rec))
    if typ == "ACS":
        gave = any(rec[s][1][Y]["u"] == "give" and rows[s]["t"] >= 0 for s in win if s < len(rec))
        same = any((rec[s][0].agents[Y][0].px, rec[s][0].agents[Y][0].py) ==
                   (rec[s][0].agents[n][0].px, rec[s][0].agents[n][0].py) and rec[s][1][n]["u"] == "eat"
                   and rec[s][1][Y]["u"] == "eat" for s in win if s < len(rec))
        cat = "sup" if gave and gifts else ("comp" if same else "obs")
        return cat, 0, ("gain" if gifts else "none")
    if typ == "agent":
        return ("sup" if gifts else "obs"), 0, ("gain" if gifts else "none")
    k = int(Y[3:])
    c = cfg.resources[k]
    used = any((rec[s][0].agents[n][0].px, rec[s][0].agents[n][0].py) == c and rec[s][1][n]["u"] in ("eat", "collect")
               for s in win if s < len(rec))
    return ("use" if used else "ref"), (1 if used else 0), ("gain" if used else "none")


def Q_value(cfg, Y, typ, n, rows, rec, win):
    """relation quality under a describer-fixed rule (def:Q_rule): Q = 0.5 Q_res + 0.5 Q_via."""
    gain = 0
    for s in win:
        if s >= len(rec):
            continue
        if typ in ("ACS", "agent"):
            gain += rec[s][0].gifts.get(n, 0)
        else:
            x = rec[s][0].agents[n][0]
            if (x.px, x.py) == cfg.resources[int(Y[3:])] and rec[s][1][n]["u"] in ("eat", "collect"):
                gain += cfg.eat_gain
    q_res = max(-1.0, min(1.0, gain / 12.0))
    dpi = rows[win[-1]]["Pi"] - rows[win[0]]["Pi"]
    q_via = max(-1.0, min(1.0, dpi / 6.0)) if gain else 0.0
    return round(0.5 * q_res + 0.5 * q_via, 3)


# =========================================================================== sec.8 organisation
def org_layer(cfg, rec, worlds, sysobjs):
    from .org import x_org, Pi_org, U_ORG
    from .world import joint_step
    bodies, minds, B = sysobjs
    out = []
    for t, (w, info) in enumerate(rec):
        xo = x_org(w, bodies)
        po = Pi_org(xo)
        A_org = []
        for uo in U_ORG:
            nw, _ = joint_step(cfg, bodies, minds, w, B[t], t, org_action=uo)
            if Pi_org(x_org(nw, bodies)) >= 0:
                A_org.append(uo)
        n_org = sum(1 for k, (x, _) in w.agents.items() if x.integ > 0)
        # toy rule (fixed in advance): the organisation's state contains the participants' states (org.py);
        # WF_org = 1 while some participant keeps its structure (integ > 0), and the organisational relations
        # of (SC-1) are lost when none does ((SC-2): integ = 0 is absorbing, checks.py).  This is a rule of
        # this model, not a consequence of the paper (rem:org_qualification_loss).
        wf_org = 1 if n_org >= 1 else 0
        cs_org = 1 if n_org == 0 else 0
        org_rec = info.get("_org") or {}
        out.append({"t": t, "stock": xo[0], "n_act": xo[1], "Pi_org": po, "inK_org": po >= 0,
                    "A_org": tuple(A_org), "blk_org": len(A_org) == 0, "n_org": n_org, "WF_org": wf_org,
                    "org_ACS": wf_org == 1,
                    "org_type": (("participating" if n_org >= 1 else "non-participating") if wf_org == 1 else ""),
                    "CS_org": cs_org, "u_org": org_rec.get("u_org", "")})
    return out
