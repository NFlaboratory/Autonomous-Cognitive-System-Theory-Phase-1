# -*- coding: utf-8 -*-
"""Checks of the toy realisation against the paper's requirements, assumptions and propositions.

Three kinds of result are reported, and they are kept apart in the output:
  WITNESS : an explicit example found (existence claims: CR-1a(i), CR-1b, CR-1c, CR-2b, nondegeneracy ...)
  GRID    : a per-step inequality checked on a finite grid of states that covers every value of the
            fields the inequality reads (the remaining fields are fixed; that they are not read is a
            code-inspection statement written next to the check).  Used for universally quantified
            requirements (CR-1a(ii), (SC-2), (FT-2) for the toy rule).  A GRID result is not a proof
            for states outside the grid unless the code-inspection statement holds.
  RECORD  : a proposition of the paper re-checked on the judged record of this run (regression;
            a failure would indicate an implementation error, not a counterexample to the paper).
"""
from itertools import product

from .body import Body, X, U, U_EMPTY, Lam, FIELDS
from .sim import UPSILON, apply_upsilon, build
from .world import g_O


def _x(cfg, **kw):
    base = dict(px=3, py=3, energy=12, integ=10, temp=6, hpsl=3, hsens=3, heff=3, hmem=3, carry=0, starve=0,
                alert=0, beacon=0, last_u=0)
    base.update(kw)
    return X(**base)


def _lam(**kw):
    d = dict(T=0, door=0, rock_cur=0, rock_N=0, rock_E=0, rock_S=0, rock_W=0, res_cur=0, res_other=0, gift=0,
             partner_adj=0)
    d.update(kw)
    return Lam(**d)


def grid_states(cfg, body):
    cells = sorted({cfg.shelter, cfg.depot, cfg.resources[0], cfg.rock_cells[0], (0, 0), (cfg.grid - 1, cfg.grid - 1)})
    for c, en, ig, tp, hp, he, ca in product(cells, (0, 1, 2, 4, 15, 20), (0, 1, 2, 9, 10),
                                             (0, 1, 2, 3, 4, 5, 8), (0, 1, 3), (0, 3), (0, 2)):
        yield _x(cfg, px=c[0], py=c[1], energy=en, integ=ig, temp=tp, hpsl=hp, heff=he, carry=ca)


def lams_where(body, x, pred, u):
    """realisable local views varying every field read by f(x,u,.) or by an eta (exact for f(x,u,.) and eta)."""
    return [l for l in body.lam_space(x, [u]) if pred(l)]


def run_checks(cfg, rec, final_world, sysobjs):
    bodies, minds, B = sysobjs
    body = Body(cfg)
    out = []

    def rep(kind, name, ok, detail=""):
        out.append(f"[{kind}] {'OK ' if ok else 'NG '} {name}" + (f" -- {detail}" if detail else ""))

    # ------------------------------------------------------------------ CR-1
    # (a)(i) and (c): witness sequences.  heat: away from the shelter, T=0 then T=2 forever.
    for name, lam_ok, lam_bad, x0 in (
            ("heat", _lam(T=0), _lam(T=2), _x(cfg)),
            ("food", _lam(res_cur=1), _lam(), _x(cfg, px=cfg.resources[0][0], py=cfg.resources[0][1]))):
        xs = [x0]
        x = x0
        seq_ok = body.WF(x) == 1 and body.eta(name, x, lam_ok) == 1
        x = body.f(x, U_EMPTY, lam_ok)
        t0_state = x
        in_D = any(body.eta(name, t0_state, l) for l in body.lam_full(t0_state))
        T_end = None
        for s in range(200):
            if body.eta(name, x, lam_bad) != 0:
                seq_ok = False
            if body.WF(x) == 0 and T_end is None:
                T_end = s + 1
            x = body.f(x, U_EMPTY, lam_bad)
        rep("WITNESS", f"CR-1a(i)/CR-1c for eta_{name}", seq_ok and in_D,
            f"WF=1 and eta=1 at t0-1, eta=0 for all s>=t0 (200 steps), x_t0 in D_eta={in_D}; "
            f"WF reaches 0 at t0+{T_end - 1 if T_end else None} on this sequence")
    # (a)(ii): universally quantified; per-step inequalities on the grid
    bad = 0
    n = 0
    for x in grid_states(cfg, body):
        if x.integ == 0:
            continue
        for u in U:
            for l in lams_where(body, x, lambda l: body.eta("heat", x, l) == 0, u):
                y = body.f(x, u, l)
                n += 1
                if not (y.temp <= max(0, x.temp - 1)):
                    bad += 1
                if x.temp <= 1 and not (y.integ <= max(0, x.integ - 1)):
                    bad += 1
    rep("GRID", "CR-1a(ii) eta_heat: under eta_heat=0, temp' <= max(0,temp-1); temp<=1 => integ' <= integ-1",
        bad == 0, f"{n} (x,u,e) triples, {bad} violations.  Hence WF=0 within temp0+integ0 <= 18 steps of "
                  f"persistent non-satisfaction.  Fields read by temp'/integ': pos, door, T, rock, energy, integ, "
                  f"temp, hpsl, heff (code inspection of f_auto/f_dir)")
    bad = 0
    n = 0
    for x in grid_states(cfg, body):
        if x.integ == 0:
            continue
        for u in U:
            for l in lams_where(body, x, lambda l: body.eta("food", x, l) == 0, u):
                y = body.f(x, u, l)
                n += 1
                phi_x = x.energy + cfg.eat_gain * x.carry
                phi_y = y.energy + cfg.eat_gain * y.carry
                if body.active_base(x):
                    if not (phi_y <= phi_x - 1):
                        bad += 1
                else:
                    if not (y.energy <= x.energy and y.integ <= max(0, x.integ - 1) and y.hpsl <= x.hpsl):
                        bad += 1
    rep("GRID", "CR-1a(ii) eta_food: under eta_food=0, Phi=energy+eat_gain*carry drops by >=1 while base active; "
                "base inactive => energy, hpsl do not rise and integ' <= integ-1", bad == 0,
        f"{n} triples, {bad} violations.  Hence base activity ends within Phi0 steps and WF=0 within Phi0+10 steps")
    # (b)
    w = [(x, l) for x in [_x(cfg, px=cfg.resources[0][0], py=cfg.resources[0][1])]
         for l in body.lam_full(x) if all(body.eta(nm, x, l) for nm in body.ETA)]
    rep("WITNESS", "CR-1b joint satisfiability", bool(w), f"x at {cfg.resources[0]}, e with T=0 and res_cur=1")

    # ------------------------------------------------------------------ CR-2 (realisation level)
    m = minds["i"]
    M0 = rec[0][0].agents["i"][1]
    b0 = B[0]
    o0 = rec[0][0].o_view("i")
    e0 = (b0, o0)
    xa, xb = _x(cfg, px=2, py=2, energy=12), _x(cfg, px=2, py=2, energy=5)
    rep("WITNESS", "CR-2b(i) sensing: fixed e, different x -> different I", m.P_sens(xa, e0) != m.P_sens(xb, e0))
    from .world import Bg
    b1 = Bg(2 if b0.T != 2 else 0, b0.rock_now, b0.tremor, b0.wind, b0.regen)
    rep("WITNESS", "CR-2b(i) sensing: fixed x, different e -> different I", m.P_sens(xa, (b0, o0)) != m.P_sens(xa, (b1, o0)))
    S_a = m.M1(m.P_sens(xa, (b0, o0)), M0)
    S_b = m.M1(m.P_sens(xa, (b1, o0)), M0)
    rep("WITNESS", "CR-2b(ii) discrimination: e difference -> different internal representation", S_a != S_b)
    Ih = m.part(M0, 1, "W")["Ih"]
    xin, xout = _x(cfg, px=2, py=2, energy=12), _x(cfg, px=2, py=2, energy=2)
    e_same = (b0, o0)
    v_in = m.M2(m.M1(m.P_sens(xin, e_same), M0), M0, Ih)
    v_out = m.M2(m.M1(m.P_sens(xout, e_same), M0), M0, Ih)
    rep("WITNESS", "CR-2b(iii) valuation incl. feasibility sensitivity: x in K vs x not in K -> different evaluation",
        body.in_K(xin) and not body.in_K(xout) and v_in[:2] != v_out[:2],
        f"Pi_eval {v_in[1][0]} vs {v_out[1][0]} (same M, same e)")
    cand = [_x(cfg, px=c[0], py=c[1], energy=en) for c in ((2, 2), cfg.shelter, cfg.resources[0], (3, 3))
            for en in (2, 6, 12, 18)]
    resp = {}
    for xc in cand:
        resp.setdefault(m.pipeline(M0, m.P_sens(xc, e_same))[4], xc)
    rep("WITNESS", "CR-2b(iv) action: different representation/evaluation -> different response", len(resp) >= 2,
        f"responses found over {len(cand)} states (same M, same b): {sorted(resp)}")
    rep("WITNESS", "CR-2a/c basic functions per division and base functions exist (activity map)",
        all(body.activity(_x(cfg)).values()) and all(body.base_functions(_x(cfg)).values()))

    # ------------------------------------------------------------------ section-2 assumptions
    bad = 0
    n = 0
    for x in grid_states(cfg, body):
        for l in body.lam_space(x, ()):
            n += 1
            if body.f(x, U_EMPTY, l) != body.f_auto(x, l):
                bad += 1
    rep("GRID", "ass:f_decomposition f = (+)(f_auto, f_dir) and f(x,u_empty,e) = f_auto(x,e)", bad == 0,
        f"f is defined as oplus(f_auto,f_dir) (construction); u_empty identity checked on {n} pairs, {bad} violations")
    xw = _x(cfg)
    rep("WITNESS", "ass:env_input_nondegeneracy", body.f(xw, U_EMPTY, _lam(T=0)) != body.f(xw, U_EMPTY, _lam(T=2)))
    A1 = tuple(u for u in U if body.in_K(body.f(_x(cfg, temp=3), u, _lam(T=0))))
    A2 = tuple(u for u in U if body.in_K(body.f(_x(cfg, temp=3), u, _lam(T=2))))
    rep("WITNESS", "ass:env_viable_nondegeneracy A(x,e) != A(x,e')", A1 != A2, f"|A|={len(A1)} vs {len(A2)}")
    xr = _x(cfg, px=cfg.resources[0][0], py=cfg.resources[0][1])
    lr = _lam(T=0, res_cur=1)
    rep("WITNESS", "ass:viable_realizability", body.in_K(xr) and all(body.eta(nm, xr, lr) for nm in body.ETA)
        and body.in_K(body.f(xr, "eat", lr)))
    rep("WITNESS", "ass:compact_spaces / ass:M_compact: X, U finite (discrete topology); M finite-valued",
        True, "by construction (finite ranges in body.py, bounded memories in mind.py)")

    # ------------------------------------------------------------------ (SC-2) and the toy (FT-2) rule
    bad = 0
    n = 0
    for x in grid_states(cfg, body):
        if x.integ != 0:
            continue
        for u in U:
            for l in body.lam_space(x, [u]):
                n += 1
                if body.f(x, u, l).integ != 0:
                    bad += 1
        for ups in UPSILON:
            w0 = rec[0][0].copy()
            w0.agents["i"] = (x, w0.agents["i"][1])
            if apply_upsilon(cfg, bodies, w0, "i", ups).agents["i"][0].integ != 0:
                bad += 1
    rep("GRID", "(SC-2) toy rule: integ=0 is invariant under f for all u,e and under every upsilon in Upsilon_adm",
        bad == 0, f"{n} triples, {bad} violations")
    bad = 0
    for x in grid_states(cfg, body):
        if x.hpsl != 0 or x.integ == 0:
            continue
        for u in U:
            for l in body.lam_space(x, [u]):
                y = body.f(x, u, l)
                if y.hpsl != 0 or body.activity(y)["sens"] or body.active_base(y):
                    bad += 1
    rep("GRID", "(FT-2) toy rule: hpsl=0 cannot be left (no f step raises hpsl; Upsilon does not act on hpsl)",
        bad == 0, f"{bad} violations")

    # ------------------------------------------------------------------ record-level checks of the joint system
    mism = 0
    dep = 0
    fact = 0
    m2free = 0
    nchk = 0
    for t in range(0, min(len(rec) - 1, 120), 3):
        w, info = rec[t]
        for name in sorted(w.agents):
            if info[name]["rec"] is None:
                continue
            nchk += 1
            u = info[name]["u"]
            ov = g_O(cfg, bodies, minds, w, name, u, B[t], t)
            if ov != rec[t + 1][0].o_view(name):
                mism += 1
            w2 = w.copy()
            x, M = w2.agents[name]
            w2.agents[name] = (x, minds[name].initial_M())
            if g_O(cfg, bodies, minds, w2, name, u, B[t], t) != ov:
                dep += 1
            mm = minds[name]
            r = info[name]["rec"]
            if mm.pipeline(M, mm.P_sens(x, info[name]["e"]))[4] != u:
                fact += 1
            M_alt = (M[0], M[1], mm.initial_M()[2])
            if mm.M2(r["S1"], M_alt, mm.part(M, 1, "W")["Ih"]) != r["out2"]:
                m2free += 1
    rep("RECORD", "g_O(o_t,x_t,u_t,b_t) equals the realised next o of the joint simulation", mism == 0,
        f"{nchk} checks, {mism} mismatches")
    rep("RECORD", "g_O does not depend on M of the individual (effective action fixed)", dep == 0, f"{dep} mismatches")
    rep("RECORD", "observation factorisation: u_t = pipeline(M_t, P_sens(x_t,e_t))", fact == 0, f"{fact} mismatches")
    rep("RECORD", "M2 output does not depend on the M3 factor (def:m2_map)", m2free == 0, f"{m2free} mismatches")
    out.append("")
    out.append("Not checked here: ass:no_branching (one instance per name by construction), ass:Eext_time_fixed "
               "(types fixed by construction), section-3..6 assumptions (see README 'assumptions').")
    return "\n".join(out) + "\n"


def record_props(out, org):
    """proposition regressions on the judged rows (RECORD)."""
    lines = []

    def rep(name, ok, detail=""):
        lines.append(f"[RECORD] {'OK ' if ok else 'NG '} {name}" + (f" -- {detail}" if detail else ""))

    for n, rows in out.items():
        blk = [r for r in rows if r["blk"]]
        rep(f"{n}: prop:blockage_dichotomy (exactly one of B1, B2 at every blocked time)",
            all((r["B1"] != r["B2"]) for r in blk), f"{len(blk)} blocked steps")
        rep(f"{n}: prop:eu_blockage (EU false on T_P => A empty)",
            all(r["blk"] for r in rows if r["T_P"] and r["EU"] is False))
        rep(f"{n}: prop:fr_mu_eff (A empty <=> mu_eff = 0)", all((r["blk"]) == (r["mu_eff"] == 0) for r in rows))
        rep(f"{n}: prop:selection_responsibility (u_t not in A_t => x_t+1 not in K)",
            all((not rows[k]["sel_resp"]) or (not rows[k + 1]["inK"]) for k in range(len(rows) - 1)))
        rep(f"{n}: prop:blockage_viability_kernel (blk and e in E_req => x not in Viab_f(K))",
            all(r["Viab_core"] != "in" for r in rows if r["blk"] and r["e_in_Ereq"]))
        rep(f"{n}: prop:viab_stage_core (x in Viab_f(K) => Hor not finite below cap)",
            all(r["Viab_core"] != "in" or (isinstance(r["Hor"], str) and r["Hor"].startswith(">="))
                for r in rows if r["Viab_core"] != ""))
        rep(f"{n}: prop:collapse_basic (C-2) absorption of Col and FT",
            all(rows[k + 1]["Col"] >= rows[k]["Col"] and rows[k + 1]["FT"] >= rows[k]["FT"] for k in range(len(rows) - 1)))
        tc = next((r["t"] for r in rows if r["CS"]), None)
        tf = next((r["t"] for r in rows if r["FT"]), None)
        rep(f"{n}: prop:termination_order (FT reached no later than the first CS; WF=0 under Col)",
            (tc is None or (tf is not None and tf <= tc)) and all(r["WF"] == 0 for r in rows if r["Col"]),
            f"T_FT={tf}, t_C={tc}")
        rep(f"{n}: prop:recover_excludes_termination (Recover=1 for some upsilon => CS=0)",
            all(r["CS"] == 0 for r in rows if isinstance(r["Recover"], str) and "1" in r["Recover"]))
        rep(f"{n}: prop:tstab_implies_principles (T-STAB => SM, EU and (FR where defined) in the window)",
            all(r["SM"] is True and r["EU"] is True and r["FR"] in (True, "undef") for r in rows if r["TSTAB"] is True))
        rep(f"{n}: zones: Z5 iff Col=1; Recover defined only on Z1..Z4",
            all(("Z5" in r["zones"]) == (r["Col"] == 1) for r in rows)
            and all(r["Recover"] == "undef" for r in rows if not (set(r["zones"].split("+")) & {"Z1", "Z2", "Z3", "Z4"})))
    if org:
        rep("org: prop:org_blockage_characterization (A(Sigma_org)=empty <=> no org action keeps Pi_org >= 0)",
            all(o["blk_org"] == (len(o["A_org"]) == 0) for o in org))
        rep("org: def:org_acs (org_ACS iff WF_org = 1; n_org is not part of the condition) and "
            "def:org_class_terms (participating iff n_org >= 1)",
            all(o["org_ACS"] == (o["WF_org"] == 1)
                and o["org_type"] == (("participating" if o["n_org"] >= 1 else "non-participating")
                                      if o["org_ACS"] else "") for o in org))
    return "\n".join(lines) + "\n"
