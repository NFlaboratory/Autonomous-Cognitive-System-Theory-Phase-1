# -*- coding: utf-8 -*-
"""Adapters: one evaluation unit (seed x sweep point x condition x rule variant) -> registered metrics."""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINACS = HERE          # packages minacs, acs_toy, acsjudge, domains live at the repository root
TOY2 = HERE
for p in (MINACS, TOY2):
    if p not in sys.path:
        sys.path.insert(0, p)


def lcg(seed):
    s = (seed * 2654435761 + 12345) % (2 ** 32)
    while True:
        s = (1103515245 * s + 12345) % (2 ** 31)
        yield s


BG_LEN = 128          # fixed background length, independent of every judgment-rule variant (fix after P1 r1)


def minacs_background(seed, T, cold_len, regrow_period, gift_events, gift_window=None):
    """seed-indexed deterministic background b_t = (c, g, rho) for MinACS.
    cold spells of length cold_len start at seed-dependent times (one spell per 12-step block);
    regrowth every regrow_period steps (offset by seed); gift_events gift steps at seed-dependent times."""
    r = lcg(seed)
    off = next(r) % regrow_period
    cold = [0] * T
    for blk in range(0, T, 12):
        start = blk + next(r) % max(1, 12 - cold_len)
        for k in range(start, min(T, start + cold_len)):
            cold[k] = 1
    gifts = set()
    for _ in range(gift_events):
        gifts.add(next(r) % (gift_window or T))
    return [(cold[t], 1 if t in gifts else 0, 1 if (t + off) % regrow_period == 0 else 0) for t in range(T)]


_MODEL = {}


def minacs_unit(seed, point, condition, variant, T=60):
    from minacs.analysis import Model
    from minacs import trajectory as tr
    if "M" not in _MODEL:
        _MODEL["M"] = Model("base")
    M = _MODEL["M"]
    hz = variant.get("recover_horizon", 10)
    bg = minacs_background(seed, BG_LEN, point["cold_len"], point["regrow_period"], point["gift_events"],
                           gift_window=T)
    assert T + hz + 1 <= BG_LEN
    rows = tr.run(M, None, T=T, learn=(condition == "learn"), horizon=hz, bg=bg,
                  recover=variant.get("compute_recover", True), recover_rule=variant.get("recover_rule", "first"))
    tcol = next((r["t"] for r in rows if r["Col"]), None)
    alive = [r for r in rows if not r["Col"]]
    last = alive[-1] if (tcol is not None and alive) else None
    rec_last = last["Recover"] if last is not None else None
    return {"T_col": tcol, "blocked": sum(1 for r in alive if r["blk"]),
            "B1": sum(1 for r in alive if r["B1"]), "B2": sum(1 for r in alive if r["B2"]),
            "recover_at_last_alive": rec_last,
            "recover_count_last_alive": (rec_last.count("1") if isinstance(rec_last, str) and rec_last != "undef" else None)}


def v2_unit(seed, point, condition, variant):
    """v2 toy (acs_toy): simulation only; T_col = first time integ = 0 (the (SC-1) rule of v2)."""
    from acs_toy.config import SCENARIOS
    from acs_toy.sim import run
    base = SCENARIOS["default"]
    cfg = base.with_(seed=seed, steps=point.get("steps", 300), eat_gain=point["eat_gain"],
                     regen_period=point["regen_period"], snap_jitter=point.get("snap_jitter", 0),
                     with_drone=(condition == "drone"))
    rec, w, _ = run(cfg)
    worlds = [ww for (ww, _) in rec] + [w]
    out = {}
    for n in ("i", "j"):
        out[f"T_col_{n}"] = next((k for k, ww in enumerate(worlds) if ww.agents[n][0].integ == 0), None)
    return out


POLICIES = ("P-Viab-first", "P-Viab-last", "P-A-first", "P-A-greedy", "P-mech", "P-greedy", "P-fixed", "P-wait")


def e1_unit(seed, point, condition, variant, T=60):
    """E1: one policy on MinACS, judged exactly.  condition = policy name."""
    from minacs.analysis import Model
    from minacs import trajectory as tr
    from . import policies_minacs as pm
    if "M" not in _MODEL:
        _MODEL["M"] = Model("base")
    M = _MODEL["M"]
    pol = {"P-Viab-first": lambda: pm.p_viab("first"), "P-Viab-last": lambda: pm.p_viab("last"),
           "P-A-first": lambda: pm.p_A("first"), "P-A-greedy": lambda: pm.p_A("greedy"),
           "P-mech": lambda: None, "P-greedy": pm.p_greedy, "P-fixed": lambda: pm.p_fixed(seed),
           "P-wait": pm.p_wait}[condition]()
    bg = minacs_background(seed, BG_LEN, point["cold_len"], point["regrow_period"], point["gift_events"],
                           gift_window=T)
    rows = tr.run(M, None, T=T, learn=True, bg=bg, recover=False, policy=pol)
    tcol = next((r["t"] for r in rows if r["Col"]), None)
    alive = [r for r in rows if not r["Col"]]
    exits = []
    for k in range(len(rows) - 1):
        if rows[k]["Viab"] and not rows[k + 1]["Viab"] and not rows[k]["Col"]:
            exits.append({"t": k, "e_in_Ereq": rows[k]["e_in_Ereq"], "u_in_Uviab": rows[k]["u_in_Uviab"]})
    return {"T_col": tcol, "blocked": sum(1 for r in alive if r["blk"]),
            "e_not_in_Ereq_alive": sum(1 for r in alive if not r["e_in_Ereq"]),
            "in_Viab_alive": sum(1 for r in alive if r["Viab"]),
            "viab_exits": len(exits),
            "viab_exits_with_u_in_Uviab": sum(1 for x in exits if x["u_in_Uviab"] is True),
            "viab_exits_with_u_in_Uviab_and_e_in_Ereq": sum(1 for x in exits if x["u_in_Uviab"] is True and x["e_in_Ereq"])}


ABLATIONS = {"full": (), "-integ": ("integ",), "-feas": ("feas",), "-resp": ("resp",), "-envuse": ("envuse",),
             "-select": ("select",), "-update": ("update",), "-phys": ("phys",), "-auto": ("auto",),
             "-relation": ("relation",), "-rescuers": ("relation",)}
CENSOR = 301


def e2_unit(seed, point, condition, variant):
    """E2: v2 toy with one principle-related function group removed from both individuals' mechanisms.
    '-rescuers' additionally removes the drone and the organisation (and the relation functions)."""
    from acs_toy.config import SCENARIOS
    from acs_toy.sim import run
    from acs_toy.body import U
    base = SCENARIOS["default"]
    kw = dict(seed=seed, steps=point.get("steps", 300), eat_gain=point["eat_gain"],
              regen_period=point["regen_period"], snap_jitter=point.get("snap_jitter", 0),
              ablate=ABLATIONS[condition])
    if condition == "-rescuers":
        kw.update(with_drone=False, with_org=False)
    cfg = base.with_(**kw)
    rec, w, (bodies, minds, B) = run(cfg)
    worlds = [ww for (ww, _) in rec] + [w]
    out = {}
    for n in ("i", "j"):
        tc = next((k for k, ww in enumerate(worlds) if ww.agents[n][0].integ == 0), None)
        out[f"T_col_{n}"] = tc
        blk = 0
        for k, (ww, info) in enumerate(rec):
            if tc is not None and k >= tc:
                break
            x = ww.agents[n][0]
            lam = info[n]["lam"]
            if not any(bodies[n].in_K(bodies[n].f(x, u, lam)) for u in U):
                blk += 1
        out[f"blocked_{n}"] = blk
    out["T_col_sum"] = sum(CENSOR if out[f"T_col_{n}"] is None else out[f"T_col_{n}"] for n in ("i", "j"))
    return out


E3_INDICATORS = {
    # principle-derived (sec.3 / sec.7 judged quantities)
    "notViab": lambda r: not r["Viab"],
    "notK": lambda r: not r["inK"],
    "blocked": lambda r: r["blk"],
    "B2": lambda r: r["B2"],
    "EUfalse": lambda r: r["EU"] is False,
    "eNotEreq": lambda r: not r["e_in_Ereq"],
    # naive (read the state directly; no principle predicate)
    "en<=1": lambda r: r["x"][1] <= 1,
    "en<=2": lambda r: r["x"][1] <= 2,
    "naive": lambda r: r["x"][1] <= 1 or r["x"][2] <= 1,
}
E3_WINDOW = 10


def e3_unit(seed, point, condition, variant, T=60):
    """E3: alarm indicators on MinACS trajectories of one policy.
    lead_<ind>: for a collapsing trajectory, T_col - (earliest alarm time within the last E3_WINDOW alive steps);
                0 if the indicator never fires in that window; None for non-collapsing trajectories.
    fa_<ind>  : for a trajectory alive for all T steps, -(share of steps with the alarm on) (larger = fewer
                false alarms); None for collapsing trajectories."""
    from minacs.analysis import Model
    from minacs import trajectory as tr
    from . import policies_minacs as pm
    if "M" not in _MODEL:
        _MODEL["M"] = Model("base")
    M = _MODEL["M"]
    pol = {"P-Viab-first": lambda: pm.p_viab("first"), "P-mech": lambda: None, "P-greedy": pm.p_greedy,
           "P-fixed": lambda: pm.p_fixed(seed)}[condition]()
    bg = minacs_background(seed, BG_LEN, point["cold_len"], point["regrow_period"], point["gift_events"],
                           gift_window=T)
    rows = tr.run(M, None, T=T, learn=True, bg=bg, recover=False, policy=pol)
    tcol = next((r["t"] for r in rows if r["Col"]), None)
    alive = [r for r in rows if not r["Col"]]
    out = {"T_col": tcol}
    for name, ind in E3_INDICATORS.items():
        if tcol is not None:
            win = [r for r in alive if r["t"] >= tcol - E3_WINDOW]
            fired = [r["t"] for r in win if ind(r)]
            out[f"lead_{name}"] = (tcol - min(fired)) if fired else 0
            out[f"fa_{name}"] = None
        else:
            out[f"lead_{name}"] = None
            out[f"fa_{name}"] = -round(sum(1 for r in alive if ind(r)) / len(alive), 4)
    return out


# ---------------------------------------------------------------- E7: estimation error (MinACS)
def _deg_identity(I):
    return I


def _deg_energy_over(k):
    def g(I):
        tag, p, en, tp, s, c, gg, r = I
        return (tag, p, min(5, en + k), tp, s, c, gg, r)
    return g


def _deg_blind_weather(I):
    tag, p, en, tp, s, c, gg, r = I
    return (tag, p, en, tp, s, None, gg, r)


def _deg_stale_food(I):
    tag, p, en, tp, s, c, gg, r = I
    return (tag, p, en, tp, s, c, gg, None)


def _deg_temp_over(I):
    tag, p, en, tp, s, c, gg, r = I
    return (tag, p, en, min(2, tp + 1), s, c, gg, r)


E7_DEGRADATIONS = {
    "D0": _deg_identity,                     # baseline
    "D-en+1": _deg_energy_over(1),            # energy over-estimated by 1
    "D-en+2": _deg_energy_over(2),            # energy over-estimated by 2
    "D-tp+1": _deg_temp_over,                 # body temperature over-estimated by 1
    "D-blindcold": _deg_blind_weather,        # weather never sensed (belief stays at its initial value)
    "D-stalefood": _deg_stale_food,           # resource never sensed (belief stays at its initial value)
}


def _run_degraded(seed, point, deg, T):
    """closed loop with P_sens composed with a degradation map (the true x, e and the judgment layer are
    untouched); returns the judged rows."""
    from minacs.analysis import Model
    from minacs import trajectory as tr
    from minacs import mind as md
    if "M" not in _MODEL:
        _MODEL["M"] = Model("base")
    M = _MODEL["M"]
    bg = minacs_background(seed, BG_LEN, point["cold_len"], point["regrow_period"], point["gift_events"],
                           gift_window=T)
    orig = md.P_sens
    md.P_sens = lambda x, e: E7_DEGRADATIONS[deg](orig(x, e))
    try:
        rows = tr.run(M, None, T=T, learn=True, bg=bg, recover=False)
    finally:
        md.P_sens = orig
    return rows


def _e7_metrics(rows):
    """sign_mismatch : steps with sign(Pi_eval) != sign(Pi) (internal proxy evaluation vs true Pi)
    sel_violation : steps with A_t nonempty and u_t not in A_t (prop:selection_responsibility antecedent)
    divergence    : steps where the action differs from the one the same M would give on the undegraded
                    observation (decision-relevant estimation error)"""
    from minacs import model as mm
    from minacs import mind as md
    tcol = next((r["t"] for r in rows if r["Col"]), None)
    alive = [r for r in rows if not r["Col"]]
    act = [r for r in alive if r["Pi_eval"] is not None]
    mism = sum(1 for r in act if (r["Pi_eval"] >= 0) != (r["Pi"] >= 0))
    viol = sum(1 for r in act if r["A"] and r["u"] not in r["A"])
    div = 0
    for r in act:
        x = mm.X_(*r["x"])
        e = mm.E_(r["b"][0], r["b"][1], r["b"][2], r["o"])
        if md.operate(md.M_(*r["M"]), x, e)["u"] != r["u"]:
            div += 1
    return {"T_col": tcol, "sign_mismatch": mism, "sel_violation": viol, "divergence": div}


def e7_unit(seed, point, condition, variant, T=60):
    out = _e7_metrics(_run_degraded(seed, point, condition, T))
    if condition != "D0":
        base = _e7_metrics(_run_degraded(seed, point, "D0", T))
        out.update({f"base_{k}": v for k, v in base.items()})
    return out


# ====================================================================== E8: second domain (furnace keeper)
E8 = HERE
FURNACE_POLICIES = ("P-Viab-first", "P-Viab-last", "P-A-first", "P-A-greedy", "P-mech", "P-greedy", "P-fixed",
                    "P-wait")
FURNACE_ABLATIONS = {"full": (), "-integ": ("integ",), "-feas": ("feas",), "-resp": ("resp",),
                     "-envuse": ("envuse",), "-select": ("select",), "-update": ("update",), "-phys": ("phys",)}


def _e8_path():
    if E8 not in sys.path:
        sys.path.insert(0, E8)


def furnace_background(seed, T, hot_len, deliv_period, draught):
    """seed-indexed deterministic background b_t = (h, d, k) for the furnace keeper.
    one hot spell of length hot_len per 12-step block at a seed-dependent start (cold otherwise);
    fuel delivery every deliv_period steps (offset by seed); `draught` bad-draught steps per 12-step block at
    seed-dependent times."""
    r = lcg(seed + 7919)
    off = next(r) % deliv_period
    hot = [0] * T
    kk = [0] * T
    for blk in range(0, T, 12):
        start = blk + next(r) % max(1, 12 - hot_len)
        for k in range(start, min(T, start + hot_len)):
            hot[k] = 1
        for _ in range(draught):
            t = blk + next(r) % 12
            if t < T:
                kk[t] = 1
    return [(hot[t], 1 if (t + off) % deliv_period == 0 else 0, kk[t]) for t in range(T)]


def _furnace_run(seed, point, policy_name=None, ablate=(), T=60):
    _e8_path()
    from acsjudge.judge import Judge
    from acsjudge import trajectory as gtr
    from domains.furnace import model as fm
    from domains.furnace import mind as fd
    from domains.furnace import policies as fp
    if "F" not in _MODEL:
        J = Judge(fm.D)
        V = J.viab_stages()
        _MODEL["F"] = (J, J.viab_core(), V, J.hor(V))
    J, core, V, H = _MODEL["F"]
    pol = None
    if policy_name is not None and policy_name != "P-mech":
        pol = {"P-Viab-first": lambda: fp.p_viab("first"), "P-Viab-last": lambda: fp.p_viab("last"),
               "P-A-first": lambda: fp.p_A("first"), "P-A-greedy": lambda: fp.p_A("greedy"),
               "P-greedy": fp.p_greedy, "P-fixed": lambda: fp.p_fixed(seed, lcg), "P-wait": fp.p_wait}[policy_name]()
    bg = furnace_background(seed, BG_LEN, point["hot_len"], point["deliv_period"], point["draught"])
    return gtr.run(J, fd.Mind(ablate), bg, T, fm.X0, fm.O0, fd.M0, learn=True, policy=pol, recover=False,
                   core=core, V=V, H=H)


def _e8_metrics(rows):
    tcol = next((r["t"] for r in rows if r["Col"]), None)
    alive = [r for r in rows if not r["Col"]]
    exits = []
    for k in range(len(rows) - 1):
        if rows[k]["Viab"] and not rows[k + 1]["Viab"] and not rows[k]["Col"]:
            exits.append({"e_in_Ereq": rows[k]["e_in_Ereq"], "u_in_Uviab": rows[k]["u_in_Uviab"]})
    last = alive[-1] if alive else None
    return {"T_col": tcol, "blocked": sum(1 for r in alive if r["blk"]),
            "blocked_before_collapse": (sum(1 for r in alive if r["blk"]) > 0) if tcol is not None else None,
            "collapse_cause": (None if tcol is None else ("overheat" if last["x"][1] == 5 else
                                                          ("freeze" if last["x"][1] == 0 else "other"))),
            "outside_K_alive": sum(1 for r in alive if not r["inK"]),
            "e_not_in_Ereq_alive": sum(1 for r in alive if not r["e_in_Ereq"]),
            "in_Viab_alive": sum(1 for r in alive if r["Viab"]),
            "viab_exits": len(exits),
            "viab_exits_with_u_in_Uviab": sum(1 for x in exits if x["u_in_Uviab"] is True),
            "viab_exits_with_u_in_Uviab_and_e_in_Ereq": sum(1 for x in exits if x["u_in_Uviab"] is True
                                                            and x["e_in_Ereq"])}


def e8_e1_unit(seed, point, condition, variant, T=60):
    """E8-E1: one policy on the furnace keeper, judged by the common judgment layer."""
    return _e8_metrics(_furnace_run(seed, point, policy_name=condition, T=T))


def e8_e2_unit(seed, point, condition, variant, T=60):
    """E8-E2: the furnace mechanism with one principle-related function group removed."""
    return _e8_metrics(_furnace_run(seed, point, ablate=FURNACE_ABLATIONS[condition], T=T))


# ====================================================================== E1 on the v2 toy
V2_POLICIES = ("P-Viab-first", "P-Viab-last", "P-A-first", "P-A-greedy", "P-mech", "P-greedy", "P-fixed", "P-wait")
V2_WORLDS = {"alone": dict(with_partner=False, with_drone=False, with_org=False), "default": {}}
_V2_ORACLES = {}      # (world, eat_gain) -> (ViabOracle, in_core memo); body parameters depend only on these


def e1v2_unit(seed, point, condition, variant):
    """E1 on the v2 toy.  condition = '<world>:<policy>'; the policy acts for individual i only.
    world 'alone' = no partner, drone or organisation; 'default' = partner j (own mechanism), drone, organisation."""
    from acs_toy.config import SCENARIOS
    from acs_toy.sim import build
    from acs_toy.world import joint_step
    from acs_toy.body import U
    from acs_toy.judge import ViabOracle, _restrict
    from . import policies_v2 as pv
    world, pname = condition.split(":")
    cfg = SCENARIOS["default"].with_(seed=seed, steps=point.get("steps", 300), eat_gain=point["eat_gain"],
                                     regen_period=point["regen_period"], snap_jitter=point.get("snap_jitter", 0),
                                     **V2_WORLDS[world])
    bodies, minds, B, w = build(cfg)
    body = bodies["i"]
    pol = None
    if pname in ("P-Viab-first", "P-Viab-last"):
        key = (world, point["eat_gain"])
        if key not in _V2_ORACLES:
            if len(_V2_ORACLES) >= 3:
                _V2_ORACLES.clear()
            _V2_ORACLES[key] = (ViabOracle(body), {})
        orc, memo = _V2_ORACLES[key]
        pol = pv.ViabPolicy(body, "first" if pname.endswith("first") else "last", oracle=orc, memo=memo)
    elif pname == "P-A-first":
        pol = pv.p_A(body, "first")
    elif pname == "P-A-greedy":
        pol = pv.p_A(body, "greedy")
    elif pname == "P-greedy":
        pol = pv.p_greedy(cfg, minds["i"])
    elif pname == "P-fixed":
        pol = pv.p_fixed(seed, lcg)
    elif pname == "P-wait":
        pol = lambda *_: "wait"
    names = sorted(w.agents)
    tcol = {n: None for n in names}
    m = {"blocked": 0, "e_not_in_Ereq_alive": 0, "u_not_in_A": 0, "cert_steps": 0,
         "cert_steps_e_not_in_Ereq": 0, "cert_exit": 0, "cert_exit_e_in_Ereq": 0, "f_table_mismatch": 0}
    for t in range(cfg.steps):
        for n in names:
            if tcol[n] is None and w.agents[n][0].integ == 0:
                tcol[n] = t
        x, M = w.agents["i"]
        lam = w.lam(body, "i", x, B[t])
        alive = x.integ > 0
        A = tuple(u for u in U if body.in_K(body.f(x, u, lam)))
        inEreq = all(body.eta(nm, x, lam) for nm in body.ETA)
        if alive:
            m["blocked"] += 0 if A else 1
            m["e_not_in_Ereq_alive"] += 0 if inEreq else 1
        u = None
        if pol is not None:
            if pname == "P-greedy":
                u = pol(x, (B[t], w.o_view("i")))
            elif not alive:
                u = "wait"
            else:
                u = pol(x, lam)
        nw, info = joint_step(cfg, bodies, minds, w, B[t], t, actions=None if u is None else {"i": u})
        u_eff = info["i"]["u"]
        x1 = nw.agents["i"][0]
        if alive:
            if A and u_eff not in A:
                m["u_not_in_A"] += 1
            if isinstance(pol, pv.ViabPolicy) and pol.last[0] == "cert" and u_eff in pol.last[1]:
                m["cert_steps"] += 1
                Tb = pol.oracle.tables(x)
                if Tb.tab[u_eff][_restrict(lam, Tb.rel[u_eff])] != x1:
                    m["f_table_mismatch"] += 1
                if not inEreq:
                    m["cert_steps_e_not_in_Ereq"] += 1
                if ViabOracle.canon(x1) not in pol.S:
                    m["cert_exit"] += 1
                    if inEreq:
                        m["cert_exit_e_in_Ereq"] += 1
        w = nw
    for n in names:
        if tcol[n] is None and w.agents[n][0].integ == 0:
            tcol[n] = cfg.steps
    out = {"T_col": tcol["i"], "T_col_j": tcol.get("j"), **m}
    if isinstance(pol, pv.ViabPolicy):
        out.update({k: v for k, v in pol.log.items()})
    return out


# ====================================================================== P10: experiments A, B, C
# A : how far the antecedents of prop:kernel_maintenance (e_s in E_req(x_s), u_s in U^Viab(x_s)) hold on realised
#     trajectories of the TIPA mechanism (persistence, joint persistence, first kernel exit).
# B1: selection tendency of kernel-maintaining responses (finite-time; not the acquisition of the paper).
# B2: acquisition in the sense of def:kernel_response_acquisition, decided exactly on PERIODIC backgrounds by
#     detecting a recurrence of the joint state (x, o, M, phase); 'undetermined' otherwise.
# C : at each step, which antecedent is false (C0 x not in Viab, C1 environment only, C2 selection only,
#     C3 both, OK none), recorded beside the realised outcome (stay in / leave the kernel) and the events
#     (blockage, leaving K, collapse).  Attribution is logical (which antecedent failed), not causal.

def _minacs_periodic_background(seed, L, cold_len, regrow_period, gift_events):
    """period-lcm(12, regrow) background: one cold spell per 12-step block at a seed-fixed offset (the same in
    every block), regrowth every regrow_period steps, gift_events gifts at seed-fixed positions in each period."""
    from math import gcd
    per = 12 * regrow_period // gcd(12, regrow_period)
    r = lcg(seed + 31337)
    start = next(r) % max(1, 12 - cold_len)
    off = next(r) % regrow_period
    gifts = {next(r) % per for _ in range(gift_events)}
    return [(1 if start <= (t % 12) < start + cold_len else 0, 1 if (t % per) in gifts else 0,
             1 if (t + off) % regrow_period == 0 else 0) for t in range(L)], per


def _furnace_periodic_background(seed, L, hot_len, deliv_period, draught):
    """period-12 background: one hot spell per block at a seed-fixed offset, delivery every deliv_period steps
    (deliv_period divides 12), `draught` bad-draught steps at seed-fixed positions in every block."""
    r = lcg(seed + 4242)
    start = next(r) % max(1, 12 - hot_len)
    off = next(r) % deliv_period
    kk = {next(r) % 12 for _ in range(draught)}
    return [(1 if start <= (t % 12) < start + hot_len else 0, 1 if (t + off) % deliv_period == 0 else 0,
             1 if (t % 12) in kk else 0) for t in range(L)], 12


def _exact_domain(dom):
    _e8_path()
    from acsjudge.judge import Judge
    key = "J_" + dom
    if key not in _MODEL:
        if dom == "minacs":
            from domains import minacs_domain as dm
            J = Judge(dm.D)
            ctx = dict(D=dm.D, mind=dm.MIND, x0=dm.X0, o0=dm.O0, M0=dm.M0)
        else:
            from domains.furnace import model as fm
            from domains.furnace import mind as fd
            J = Judge(fm.D)
            ctx = dict(D=fm.D, mind=fd.Mind(), x0=fm.X0, o0=fm.O0, M0=fd.M0)
        core = J.viab_core()
        ctx.update(J=J, core=core, uviab={x: J.U_viab(x, core) for x in J.XS},
                   vac={x: len(J.Ereq(x)) == 0 for x in J.XS})
        _MODEL[key] = ctx
    return _MODEL[key]


def _est_error(dom, M, x, e, mind):
    """internal estimate differs from the true environment components it represents (toy rule)."""
    if dom == "minacs":
        from minacs import mind as md
        if not (x.s == 1 and x.en > 0):
            return None
        xhat, ehat = md.M1(md.P_sens(x, e), M)
        return ehat != (e.c, e.g, e.r)
    from domains.furnace import mind as fd
    if not (x.s == 1 and x.tp > 0):
        return None
    xhat, ehat = mind.M1(fd.P_sens(x, e), M)
    return ehat != (e.h, e.d, e.o)


def _abc_record(dom, bg, T):
    """closed loop of the TIPA mechanism with exact judgement; per step: x, in Viab, e in E_req, u in U^Viab,
    vacuous U^Viab, class, outcome, events, estimate error."""
    c = _exact_domain(dom)
    J, D, mind, core, uv = c["J"], c["D"], c["mind"], c["core"], c["uviab"]
    x, o, M = c["x0"], c["o0"], c["M0"]
    rows = []
    for t in range(T):
        b = bg[t]
        e = D.make_e(b, o)
        u = mind.operate(M, x, e)["u"]
        x1 = J.f(x, u, e)
        o1 = D.g_O(o, x, u, b)
        M1 = mind.Update(M, x, e, learn=True)
        inV, inE, inU = x in core, e in J.Ereq(x), u in uv[x]
        cls = "C0" if not inV else ("OK" if (inE and inU) else ("C1" if inU else ("C2" if inE else "C3")))
        rows.append(dict(t=t, inV=inV, inE=inE, inU=inU, vac=c["vac"][x], cls=cls, nextV=x1 in core,
                         blk=not J.A(x, e), leaveK=J.inK(x) and not J.inK(x1), cs=D.CS(x), cs1=D.CS(x1),
                         est=_est_error(dom, M, x, e, mind)))
        x, o, M = x1, o1, M1
    return rows


def _runs(rows, pred):
    best = cur = 0
    for r in rows:
        cur = cur + 1 if pred(r) else 0
        best = max(best, cur)
    return best


def _abc_metrics(rows):
    alive = [r for r in rows if not r["cs"]]
    out = {"alive_steps": len(alive),
           "T_col": next((r["t"] + 1 for r in rows if not r["cs"] and r["cs1"]), None)}
    # A
    out["A_e_in_Ereq"] = sum(r["inE"] for r in alive)
    out["A_longest_e_in_Ereq"] = _runs(alive, lambda r: r["inE"])
    out["A_in_Viab"] = sum(r["inV"] for r in alive)
    out["A_longest_both_antecedents_in_Viab"] = _runs(alive, lambda r: r["inV"] and r["inE"] and r["inU"])
    out["A_first_kernel_exit"] = next((r["t"] for r in alive if r["inV"] and not r["nextV"]), None)
    # B1
    inv = [r for r in alive if r["inV"]]
    out["B1_inV_steps"] = len(inv)
    out["B1_inV_u_in_Uviab"] = sum(r["inU"] for r in inv)
    out["B1_inV_EreqTrue_steps"] = sum(r["inE"] for r in inv)
    out["B1_inV_EreqTrue_u_in_Uviab"] = sum(r["inU"] for r in inv if r["inE"])
    out["B1_longest_u_in_Uviab_inV"] = _runs(alive, lambda r: r["inV"] and r["inU"])
    out["B1_outV_u_in_Uviab"] = sum(1 for r in alive if not r["inV"] and r["inU"])
    out["B1_outV_vacuous"] = sum(1 for r in alive if not r["inV"] and r["vac"])
    # C
    for k in ("C0", "C1", "C2", "C3", "OK"):
        out[f"C_{k}"] = sum(1 for r in alive if r["cls"] == k)
        out[f"C_{k}_leaveV"] = sum(1 for r in alive if r["cls"] == k and r["inV"] and not r["nextV"])
        out[f"C_{k}_est_err"] = sum(1 for r in alive if r["cls"] == k and r["est"])
    out["C_OK_leaveV_regression"] = out["C_OK_leaveV"]          # must be 0 (prop:kernel_maintenance, one step)
    last_in = None
    ev = {"blk": [], "leaveK": [], "col": []}
    for r in alive:
        if r["inV"]:
            last_in = r
        tag = (last_in["cls"] + ("+est" if last_in["est"] else "")) if last_in else "never_in_Viab"
        if r["blk"]:
            ev["blk"].append(tag)
        if r["leaveK"]:
            ev["leaveK"].append(tag)
        if r["cs1"]:
            ev["col"].append(tag)
    for k, v in ev.items():
        for tag in sorted(set(v)):
            out[f"C_event_{k}_lastInViab_{tag}"] = v.count(tag)
    return out


def _b2(dom, bg_fn, cap=200000):
    """acquisition on a periodic background, decided by recurrence of (x, o, M, phase)."""
    c = _exact_domain(dom)
    J, D, mind, core, uv = c["J"], c["D"], c["mind"], c["core"], c["uviab"]
    bg, per = bg_fn(1)
    x, o, M = c["x0"], c["o0"], c["M0"]
    seen = {}
    hist = []
    for t in range(cap):
        key = (x, o, M, t % per)
        if key in seen:
            t0 = seen[key]
            cyc = hist[t0:]
            acquired = all(h["inU"] for h in cyc)
            return {"B2_status": ("acquired" if acquired else "not_acquired"),
                    "B2_cycle_start": t0, "B2_cycle_len": len(cyc),
                    "B2_cycle_after_collapse": all(h["cs"] for h in cyc),
                    "B2_cycle_all_in_Viab": all(h["inV"] for h in cyc),
                    "B2_cycle_all_e_in_Ereq": all(h["inE"] for h in cyc),
                    "B2_cycle_vacuous_steps": sum(h["vac"] for h in cyc),
                    "B2_first_u_not_in_Uviab_after_T": (None if acquired else
                                                        t0 + next(i for i, h in enumerate(cyc) if not h["inU"]))}
        seen[key] = t
        b = bg[t % per]
        e = D.make_e(b, o)
        u = mind.operate(M, x, e)["u"]
        hist.append(dict(inU=u in uv[x], inV=x in core, inE=e in J.Ereq(x), vac=c["vac"][x], cs=D.CS(x)))
        x1 = J.f(x, u, e)
        o, M = D.g_O(o, x, u, b), mind.Update(M, x, e, learn=True)
        x = x1
    return {"B2_status": "undetermined"}


def e10_unit(seed, point, condition, variant, T=60):
    """condition 'aper' : A, B1, C on the held-out aperiodic backgrounds (as in E1 / E8);
    condition 'periodic': B2 on the seed-fixed periodic background built from the same sweep point."""
    dom = point["domain"]
    if dom == "minacs":
        if condition == "aper":
            bg = minacs_background(seed, BG_LEN, point["cold_len"], point["regrow_period"], point["gift_events"],
                                   gift_window=T)
            return _abc_metrics(_abc_record(dom, bg, T))
        return _b2(dom, lambda _: _minacs_periodic_background(seed, 60, point["cold_len"], point["regrow_period"],
                                                               point["gift_events"]))
    if condition == "aper":
        bg = furnace_background(seed, BG_LEN, point["hot_len"], point["deliv_period"], point["draught"])
        return _abc_metrics(_abc_record(dom, bg, T))
    return _b2(dom, lambda _: _furnace_periodic_background(seed, 12, point["hot_len"], point["deliv_period"],
                                                           point["draught"]))


def e10_v2_unit(seed, point, condition, variant):
    """A, B1, C on the v2 toy for individual i under its own mechanism (world 'alone' or 'default').
    Viab_f(K) is decided by certificates: 'in' (a certified E_req-invariant set S containing x), 'not_in', or
    'undetermined'.  U^Viab_cert(x) (successors in S) is a subset of U^Viab(x), so u in U^Viab_cert is a lower
    bound of u in U^Viab, and the classes C2 / C3 are upper bounds."""
    from acs_toy.config import SCENARIOS
    from acs_toy.sim import build
    from acs_toy.world import joint_step
    from acs_toy.body import U
    from acs_toy.judge import ViabOracle
    world = condition
    cfg = SCENARIOS["default"].with_(seed=seed, steps=point.get("steps", 300), eat_gain=point["eat_gain"],
                                     regen_period=point["regen_period"], snap_jitter=point.get("snap_jitter", 0),
                                     **V2_WORLDS[world])
    bodies, minds, B, w = build(cfg)
    body = bodies["i"]
    key = ("e10", world, point["eat_gain"])
    if key not in _V2_ORACLES:
        if len(_V2_ORACLES) >= 3:
            _V2_ORACLES.clear()
        _V2_ORACLES[key] = (ViabOracle(body), None)
    orc = _V2_ORACLES[key][0]                       # successor tables only (pure functions of x): shared
    memo = {}                                       # certificate memo: local to the unit, so that the result of a
                                                    # unit does not depend on the order in which units are run
    S = None
    rows = []
    for t in range(cfg.steps):
        x, M = w.agents["i"]
        if x.integ == 0:
            break
        lam = w.lam(body, "i", x, B[t])
        c = ViabOracle.canon(x)
        if S is not None and c in S:
            status = "in"
        else:
            if c not in memo:
                r = orc.in_core(x)
                if r == "in":
                    cert = orc.last_certificate
                    for z in cert:                     # every state of a certificate is certified by it
                        memo.setdefault(z, ("in", cert))
                    memo[c] = ("in", cert)
                else:
                    memo[c] = (r, None)
            status, S2 = memo[c]
            if status == "in":
                S = S2
        if len(orc.cache) > 2000:                     # bound the successor-table cache (recomputed on demand;
            orc.cache.clear()                         # results unchanged, only memory and time)
        nw, info = joint_step(cfg, bodies, minds, w, B[t], t)
        u = info["i"]["u"]
        x1 = nw.agents["i"][0]
        inE = all(body.eta(nm, x, lam) for nm in body.ETA)
        if status == "in":
            T_ = orc.tables(x)
            inU = all(ViabOracle.canon(z) in S for z in T_.robust_successors(u))
        else:
            inU = None
        nextV = None                                   # filled below from the next step's oracle status
        A = [v for v in U if body.in_K(body.f(x, v, lam))]
        cls = ("C0" if status == "not_in" else "C0?" if status == "undetermined" else
               ("OK" if (inE and inU) else ("C1" if inU else ("C2" if inE else "C3"))))
        rows.append(dict(t=t, status=status, inE=inE, inU=inU, cls=cls, nextV=nextV, blk=not A,
                         leaveK=body.in_K(x) and not body.in_K(x1), col1=x1.integ == 0))
        w = nw
    for k in range(len(rows)):
        if rows[k]["col1"]:
            rows[k]["nextV"] = False
        elif k + 1 < len(rows):
            rows[k]["nextV"] = {"in": True, "not_in": False}.get(rows[k + 1]["status"])   # undetermined -> None
        # the last recorded step without collapse: next status left undetermined (None)
    out = {"alive_steps": len(rows), "T_col": next((r["t"] + 1 for r in rows if r["col1"]), None)}
    out["A_e_in_Ereq"] = sum(r["inE"] for r in rows)
    out["A_longest_e_in_Ereq"] = _runs(rows, lambda r: r["inE"])
    out["A_in_Viab_cert"] = sum(r["status"] == "in" for r in rows)
    out["A_undetermined"] = sum(r["status"] == "undetermined" for r in rows)
    out["A_longest_both_antecedents_cert"] = _runs(rows, lambda r: r["status"] == "in" and r["inE"] and r["inU"])
    out["A_first_cert_exit"] = next((r["t"] for r in rows if r["status"] == "in" and r["nextV"] is False), None)
    inv = [r for r in rows if r["status"] == "in"]
    out["B1_inV_steps"] = len(inv)
    out["B1_inV_u_in_Uviab_cert"] = sum(1 for r in inv if r["inU"])
    out["B1_inV_EreqTrue_steps"] = sum(1 for r in inv if r["inE"])
    out["B1_inV_EreqTrue_u_in_Uviab_cert"] = sum(1 for r in inv if r["inE"] and r["inU"])
    for k in ("C0", "C0?", "C1", "C2", "C3", "OK"):
        out[f"C_{k}"] = sum(1 for r in rows if r["cls"] == k)
        out[f"C_{k}_leaveV"] = sum(1 for r in rows if r["cls"] == k and r["status"] == "in" and r["nextV"] is False)
    out["C_OK_leaveV_regression"] = out["C_OK_leaveV"]
    last_in = None
    ev = {"blk": [], "leaveK": [], "col": []}
    for r in rows:
        if r["status"] == "in":
            last_in = r
        tag = last_in["cls"] if last_in else "never_in_Viab"
        if r["blk"]:
            ev["blk"].append(tag)
        if r["leaveK"]:
            ev["leaveK"].append(tag)
        if r["col1"]:
            ev["col"].append(tag)
    for k, v in ev.items():
        for tag in sorted(set(v)):
            out[f"C_event_{k}_lastInViab_{tag}"] = v.count(tag)
    return out


# ====================================================================== P11: comparisons inside the ACS class
# Graded variants of the TIPA mechanism that keep CR-2 (checked by check_cr2_variants.py):
#   est-k : the self-state reading used by the mechanism is quantised to multiples of k (floor, but a positive
#           value is never read as 0, so the base-activity reading is unchanged) -- MinACS energy, furnace
#           temperature; the true x, e and the judgment layer are untouched.
#   upd-k : the internal model is updated only at steps t with t % k == 0 (otherwise M is kept); 'upd-none' never.
P11_VARIANTS = ("base", "est-2", "est-3", "upd-2", "upd-4", "upd-none")


class _VariantMind:
    """wraps a mechanism (operate / Update) with a sensing quantisation and an update schedule."""

    def __init__(self, dom, inner, variant):
        self.dom, self.inner, self.variant = dom, inner, variant
        self.t = 0
        self.q = int(variant.split("-")[1]) if variant.startswith("est-") else 1
        self.k = (None if variant == "upd-none" else int(variant.split("-")[1])) if variant.startswith("upd-") else 1

    def _quant(self, x):
        if self.q == 1:
            return x
        if self.dom == "minacs":
            return x._replace(en=max(1, (x.en // self.q) * self.q)) if x.en > 0 else x
        return x._replace(tp=max(1, (x.tp // self.q) * self.q)) if x.tp > 0 else x

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def operate(self, M, x, e):
        return self.inner.operate(M, self._quant(x), e)

    def Update(self, M, x, e, learn=True):
        t = self.t
        self.t += 1
        if self.k is None or t % self.k != 0:
            return M
        return self.inner.Update(M, self._quant(x), e, learn=learn)


def p11_mind(dom, variant):
    c = _exact_domain(dom)
    if dom == "minacs":
        return _VariantMind(dom, c["mind"], variant)
    from domains.furnace import mind as fd
    return _VariantMind(dom, fd.Mind(), variant)


def p11_unit(seed, point, condition, variant, T=60):
    """one TIPA variant on the held-out aperiodic backgrounds of E1 (MinACS) / E8 (furnace); T_col plus the
    A/B1/C records of P10 for the same run."""
    dom = point["domain"]
    c = _exact_domain(dom)
    if dom == "minacs":
        bg = minacs_background(seed, BG_LEN, point["cold_len"], point["regrow_period"], point["gift_events"],
                               gift_window=T)
    else:
        bg = furnace_background(seed, BG_LEN, point["hot_len"], point["deliv_period"], point["draught"])
    saved = c["mind"]
    c["mind"] = p11_mind(dom, condition)
    try:
        rows = _abc_record(dom, bg, T)
    finally:
        c["mind"] = saved
    m = _abc_metrics(rows)
    return {k: v for k, v in m.items() if k in ("T_col", "alive_steps", "B1_inV_steps", "B1_inV_u_in_Uviab",
                                                "B1_inV_EreqTrue_steps", "B1_inV_EreqTrue_u_in_Uviab",
                                                "C_C2", "C_C3", "C_C1", "C_OK", "A_e_in_Ereq")}
