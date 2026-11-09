# -*- coding: utf-8 -*-
"""Internal model M = (M1, M2, M3), Update, and the standard primitive maps
P_sens, P_disc, P_val, P_act realised by TIPA + PSL + ISL (sec.4 def:s4_primitive_composition).
Not part of the paper.

Separation rule (sec.1 subsec:description_levels_global, sec.4 def:m3_fit, def:principles_tipa_connection):
this module never imports the judgment layer and never evaluates the true Pi, K, A_t,
Crit^(1), mu_eff, Q, s_t or T-STAB.  Everything the mechanisms use comes from
I_t = P_sens(x_t, e_t) and M_t.

Update is realised through the observation (ass:s5_observation_factorization):
Update(M, x, e) = Phi_upd(M, P_sens(x, e)), with the component-wise detailed types
Update_1(M1, I), Update_2(M2, I, M1'), Update_3(M3, I, M1', M2') (def:update_operator).
"""
from collections import namedtuple
from typing import Dict, Tuple

from .body import U, U_EMPTY, CODE, DIRS

QUAL = ("lack", "warn", "approach", "avoid")                 # toy enumeration of Qual (Phase 1.alpha in the paper)
REQ_BASE = ("energy", "heat", "integrity", "safety")
MODES = ("3A", "3B", "3C")
STYLES = ("3B-a", "3B-b", "3B-c", "none")
CORR = {("lack", "3A"), ("lack", "3B"), ("warn", "3A"), ("warn", "3B"), ("avoid", "3A"),
        ("approach", "3B"), ("approach", "3C")}             # toy Corr (def:request_response_mismatch)
D_LONG = 4                                                  # Delta t_long (def:m2_latent_instability)
W_HIST = 3
W_SHORT = 2
AGE_MAX = 40


def _dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _steps_toward(p, g):
    out = set()
    if g[0] > p[0]:
        out.add("E")
    if g[0] < p[0]:
        out.add("W")
    if g[1] > p[1]:
        out.add("S")
    if g[1] < p[1]:
        out.add("N")
    return out


def _step_toward(p, g):
    if p == g:
        return None
    if g[0] > p[0]:
        return "E"
    if g[0] < p[0]:
        return "W"
    if g[1] > p[1]:
        return "S"
    return "N"


class Mind:
    """TIPA-PSL-ISL mechanisms of one individual."""

    def __init__(self, cfg, name, other, bias):
        self.cfg = cfg
        self.name = name
        self.other = other                         # name of the other ACS ('' if none)
        self.bias0 = bias                          # (w_E, w_X)
        self.ab = frozenset(getattr(cfg, "ablate", ()))   # E2 ablations (empty = full mechanism)
        self.res_cells = tuple(cfg.resources)
        self.rock_cells = tuple(cfg.rock_cells)
        self.tokens = (tuple(f"r{k}" for k in range(len(self.res_cells))) + ("S", "D")
                       + tuple(f"k{k}" for k in range(len(self.rock_cells)))
                       + (("P",) if other else ()) + (("Dr",) if cfg.with_drone else ()))

    # ================================================================ M: initial state and readouts
    def initial_M(self):
        cfg = self.cfg
        m1L = {"res": tuple((cfg.res_init, 10) for _ in self.res_cells),         # (believed level, age): known map
               "depot": (2 if cfg.with_org else 0, 10),
               "rock": tuple(0 for _ in self.rock_cells),                        # salience 0..3 (T_sal)
               "tdrop": (0, -1, -1),                                             # believed outdoor dT per T level
               "door": (1, AGE_MAX),
               "peer": (-1, -1, 0, AGE_MAX),                                     # (px, py, distress, age)
               "drone": (-1, -1, AGE_MAX),
               "err": ()}                                                        # T_err: recent surprises (<=4)
        m1W = {"S1": None, "xh": (), "Ih": (), "pred": None, "model": None}
        m2L = {"wE": self.bias0[0], "trustP": 1 if self.other else 0, "trustD": 1 if cfg.with_drone else 0,
               "hunger": 0}
        m2W = {"P": None, "ev": None, "sig": None, "evrq": None, "Req": None, "ring": (), "trust_prev": None}
        m3L = {"rout": (), "resp": (), "wX": self.bias0[1]}                     # rout: ((key, act, strength),...)
        m3W = {"Pur": (), "mode": None, "u": None, "G": None, "key": None, "stat": None, "Pi_prev": None}
        return ((_fz(m1L), _fz(m1W)), (_fz(m2L), _fz(m2W)), (_fz(m3L), _fz(m3W)))

    # ---------------------------------------------------------------- readouts rho
    @staticmethod
    def part(M, c, lw):
        return dict(M[c - 1][0 if lw == "L" else 1])

    def rho_req(self, M):
        """rho_req : M -> P_fin(Req) (def:request_signal_types); reads M2^L only."""
        m2L = self.part(M, 2, "L")
        return tuple(REQ_BASE) + (("relation",) if (m2L["trustP"] >= 1 and "relation" not in self.ab) else ())

    def rho_past(self, M):
        """rho_past : M^W -> (P_{t-1}, u_{t-1}, xhat history, S_M1,t-1, I history, Pur_{t-1}, G record)."""
        m1W, m2W, m3W = self.part(M, 1, "W"), self.part(M, 2, "W"), self.part(M, 3, "W")
        return (m2W["P"], m3W["u"], m1W["xh"], m1W["S1"], m1W["Ih"], m3W["Pur"], m3W["G"])

    def memory_sets(self, M):
        """the five functional memory sets T_l = rho_l(M^L) (def:fast_memory_sets)."""
        m1L, m2L, m3L = self.part(M, 1, "L"), self.part(M, 2, "L"), self.part(M, 3, "L")
        return {"rout": frozenset((k, a) for (k, a, s) in m3L["rout"] if s >= 1),
                "sal": frozenset(self.rock_cells[k] for k, s in enumerate(m1L["rock"]) if s >= 1),
                "err": frozenset(m1L["err"]),
                "eval": frozenset((self.res_cells[k], lv) for k, (lv, age) in enumerate(m1L["res"]) if age < AGE_MAX),
                "resp": frozenset(m3L["resp"])}

    # ================================================================ PSL-1 / P_sens
    def gamma_in(self, x):
        """rho_Gamma,in : X -> admissible input sensitivities (sensing radius); depends on x only."""
        if x.hsens == 0:
            return 0
        r = 1 if x.hsens == 1 else 2
        return min(3, r + x.alert)

    def P_sens(self, x, e):
        """I = Gamma_in(x)(Phi_sense(rho_in(x, e)))  (def:s4_psl_sources)."""
        b, o = e
        res, door, depot, drone, gift, others, _org = o
        resd = dict(res)
        base_ok = x.integ > 0 and x.energy > 0 and x.hpsl > 0
        coarse_e = x.hpsl <= 1
        coarse_i = x.hsens <= 1
        self_part = (x.px, x.py,
                     (x.energy // 4) * 4 if coarse_e else x.energy,
                     (x.integ // 3) * 3 if coarse_i else x.integ,
                     x.temp, x.hpsl, x.hsens, x.heff, x.hmem, x.carry, x.alert, x.last_u)
        if not (base_ok and x.hsens > 0):
            return ("I", self_part, None, (), (), (), gift, (0, 0))
        r = self.gamma_in(x)
        cells = []
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if abs(dx) + abs(dy) > r:
                    continue
                c = (x.px + dx, x.py + dy)
                if not (0 <= c[0] < self.cfg.grid and 0 <= c[1] < self.cfg.grid):
                    continue
                lv = resd.get(c, -1)
                if c == self.cfg.depot and self.cfg.with_org:
                    lv = depot
                cells.append((c, lv, 1 if c in b.rock_now else 0, 1 if c in b.tremor else 0,
                              door if c == self.cfg.shelter else -1))
        peers = []
        for k, (xo, _M) in others:
            dd = abs(xo.px - x.px) + abs(xo.py - x.py)
            if dd <= r or (xo.beacon and dd <= r + 3):          # a beacon is perceivable farther (toy rule)
                peers.append((k, xo.px, xo.py, xo.beacon, 1 if xo.integ > 0 else 0))
        dr = ()
        if drone is not None and abs(drone.px - x.px) + abs(drone.py - x.py) <= r:
            dr = (drone.px, drone.py)
        local = (1 if (x.px, x.py) in b.tremor else 0, 1 if (x.px, x.py) in b.rock_now else 0)
        return ("I", self_part, b.T, tuple(cells), tuple(peers), dr, gift, local)

    # ================================================================ M1 (information integration)
    def M1(self, I, M, use_tgt=True):
        """(xhat, ehat, xi, w, D_M1) = M1(I, M, ...)  (def:m1_map).  Depends on M1 (and, for the
        target-identification axis only, on the purpose record in M3^W)."""
        m1L, m1W = self.part(M, 1, "L"), self.part(M, 1, "W")
        _, sp, T, cells, peers, dr, gift, local = I
        # M1-a: preliminary estimate (Phi_pre), baseline (Phi_hist), integration (Phi_integrate)
        xt = sp
        hist = m1W["xh"]
        base = hist[-1] if hist else sp
        w = (0.7, 0.3) if (self_coarse(sp, base)) else (1.0, 0.0)
        xh = tuple(int(round(w[0] * a + w[1] * c)) if k in (2, 3) else a for k, (a, c) in enumerate(zip(xt, base)))
        # ehat: background estimate + believed o
        res_b = list(m1L["res"])
        seen = {}
        for (c, lv, rk, tr, dv) in cells:
            seen[c] = (lv, rk, tr, dv)
        for k, c in enumerate(self.res_cells):
            if c in seen:
                res_b[k] = (seen[c][0], 0)
        door_b = m1L["door"]
        if self.cfg.shelter in seen:
            door_b = (seen[self.cfg.shelter][3], 0)
        peer_b = m1L["peer"]
        for (k, px, py, bc, alive) in peers:
            peer_b = (px, py, bc, 0)
        drone_b = m1L["drone"]
        if dr:
            drone_b = (dr[0], dr[1], 0)
        rock_seen = frozenset(c for c, v in seen.items() if v[1] or v[2])
        depot_b = m1L.get("depot", (0, AGE_MAX))
        if self.cfg.depot in seen and self.cfg.with_org:
            depot_b = (seen[self.cfg.depot][0], 0)
        ehat = (T if T is not None else -1, rock_seen, tuple(res_b), door_b, peer_b, drone_b, gift, depot_b)
        # M1-b: identification rows (global row + token rows), 8 axes
        tgt_set = self.tgt_set(M) if use_tgt else None
        xi = self.identify(xh, ehat, seen, m1L, local, tgt_set)
        # M1-c: temporal features (trend, prediction-consistency error, surprise)
        prev = m1W["S1"]
        if prev is not None:
            pxh = prev[0]
            trend = (xh[2] - pxh[2], xh[4] - pxh[4])
        else:
            trend = (0, 0)
        pred = m1W["pred"]
        surprise = 0
        eps_pred = 0
        if pred is not None:
            pr_x, pr_G = pred.get(CODE_INV[sp[11]], (None, None))
            if pr_x is not None:
                eps_pred = max(abs(pr_x[0] - xh[2]), abs(pr_x[1] - xh[4]))
            if pr_G is not None and pr_G[0] in seen:
                c, lo, hi = pr_G
                lv = seen[c][0]
                if not (lo <= lv <= hi):
                    surprise = 1
        D = (trend, eps_pred, surprise)
        wv = self._weights(xh)
        return (xh, ehat, xi, wv, D)

    def tgt_set(self, M):
        out = set()
        for p in self.part(M, 3, "W")["Pur"]:
            d = p[1]
            out.add(d[1] if isinstance(d, tuple) else d)
        return out

    def identify(self, xh, ehat, seen, m1L, local, tgt_set):
        """M1-b identification state xi = (global row, token rows); tgt_set None -> target axis 'und'."""
        pos = (xh[0], xh[1])
        rows = []
        for tok in self.tokens:
            loc, visible, mval, dyn = self._token_info(tok, ehat, seen, m1L)
            if loc is None:
                continue
            tg = "und" if tgt_set is None else ("target" if tok in tgt_set else "non")
            row = ("env", "now" if visible else "past", "sense" if visible else "memory", dyn,
                   "direct" if visible else "inferred", mval, "near" if _dist(pos, loc) <= 1 else "far", tg)
            rows.append((tok, row))
        tg = "und" if tgt_set is None else ("target" if "self" in tgt_set else "non")
        global_row = ("self", "now", "sense", "moving", "direct",
                      "harm" if local[0] or local[1] else "neutral", "near", tg)
        return (global_row, tuple(rows))

    @staticmethod
    def seen_of(I):
        return {c: (lv, rk, tr, dv) for (c, lv, rk, tr, dv) in I[3]}

    def _token_info(self, tok, ehat, seen, m1L):
        if tok.startswith("r"):
            k = int(tok[1:])
            c = self.res_cells[k]
            lv, age = ehat[2][k]
            return c, c in seen, ("benefit" if lv > 0 else "neutral") if age < AGE_MAX else "und", "static"
        if tok == "S":
            return self.cfg.shelter, self.cfg.shelter in seen, "benefit", "static"
        if tok == "D":
            return self.cfg.depot, self.cfg.depot in seen, "benefit" if self.cfg.with_org else "neutral", "static"
        if tok.startswith("k"):
            k = int(tok[1:])
            c = self.rock_cells[k]
            s = m1L["rock"][k]
            if s == 0 and c not in seen:
                return None, False, "und", "static"
            return c, c in seen, "harm" if s >= 1 else "neutral", "static"
        if tok == "P":
            px, py, dist_, age = ehat[4]
            if px < 0:
                return None, False, "und", "moving"
            return (px, py), age == 0, "benefit", "moving"
        if tok == "Dr":
            px, py, age = ehat[5]
            if px < 0:
                return None, False, "und", "moving"
            return (px, py), age == 0, "benefit", "moving"
        return None, False, "und", "static"

    @staticmethod
    def _weights(xh):
        """dynamic weights w_t in the simplex over the 14 state coordinates (M1-a)."""
        raw = [1.0] * 14
        raw[2] += max(0, 8 - xh[2])
        raw[4] += max(0, 5 - xh[4])
        raw[3] += max(0, 6 - xh[3])
        s = sum(raw)
        return tuple(round(v / s, 4) for v in raw)

    # ---------------------------------------------------------------- internal one-step model fhat (M1^L)
    def fhat(self, model, xh, ehat, u):
        """internal prediction of (energy, temp, integ, pos) after u.  Not the true f."""
        T, rock_seen, res_b, door_b, peer_b, drone_b, gift, depot_b = ehat
        tdrop = model["tdrop"]
        e, tp, ig = xh[2], xh[4], xh[3]
        pos = (xh[0], xh[1])
        sealed = pos == self.cfg.shelter and door_b[0] == 1
        if e <= 0:                                              # belief: nothing can be done at zero energy
            return (min(20, gift), tp, max(0, ig - 1), pos)
        e = e - 1 + gift
        if sealed:
            tp = min(6, tp + 1)
        else:
            dT = tdrop[T] if 0 <= T <= 2 else -1
            tp = tp + dT if dT <= 0 else min(6, tp + dT)
        if tp <= 0:
            ig -= 1
        if u in DIRS:
            dx, dy = DIRS[u]
            q = (pos[0] + dx, pos[1] + dy)
            if 0 <= q[0] < self.cfg.grid and 0 <= q[1] < self.cfg.grid:
                pos = q
            e -= 1
            if q in self.rock_cells:
                k = self.rock_cells.index(q)
                if model["rock"][k] >= 2:
                    ig -= 3 * model["rock"][k] // 3
        elif u == "eat":
            if pos in self.res_cells and res_b[self.res_cells.index(pos)][0] > 0:
                e += self.cfg.eat_gain
            elif xh[9] > 0:
                e += self.cfg.eat_gain
        elif u == "repair":
            if xh[2] >= 2 and xh[4] >= 3:
                e -= 2
                ig += 1
        elif u == U_EMPTY and pos == self.cfg.depot and ehat[7][0] > 0 and xh[2] <= 8:
            e += self.cfg.gift                                  # expected allocation from the team ledger
        elif u in ("give",):
            e -= self.cfg.gift
        elif u == "signal":
            e -= 1
            if peer_b[0] >= 0 and peer_b[3] <= 3 and _dist(pos, (peer_b[0], peer_b[1])) <= 2:
                e += self.cfg.gift                              # expected help from a near partner (belief)
        elif u in ("vigil", "open_door"):
            e -= 1
        return (max(0, min(20, e)), max(0, min(8, tp)), max(0, min(10, ig)), pos)

    def predict_G(self, model, xh, ehat, u):
        """G_t(u): predicted set of o_{t+1}, as a constraint on the resource slot of the current cell."""
        pos = (xh[0], xh[1])
        if pos not in self.res_cells:
            return None                                       # no prediction (bottom)
        k = self.res_cells.index(pos)
        lv = ehat[2][k][0]
        if lv < 0:
            return None
        take = 1 if (u in ("eat", "collect") and lv > 0) else 0
        lo = max(0, lv - take - 1)                            # another individual may also take one
        hi = min(self.cfg.res_max, lv - take + 1)             # regeneration may add one
        return (pos, lo, hi)

    # ================================================================ M2 (adaptive evaluation)
    def M2(self, S1, M, Ih):
        """(P, ev, sig, evrq) = M2(xhat, ehat, xi, w, D, M, ...)  (def:m2_map).
        Uses M2 only (never M3's outputs, purpose records, or the target axis)."""
        m2L, m2W = self.part(M, 2, "L"), self.part(M, 2, "W")
        xh, ehat, xi, w, D = S1
        T, rock_seen, res_b, door_b, peer_b, drone_b, gift, depot_b = ehat
        pos = (xh[0], xh[1])
        thE = 3 + (m2L["wE"] - 2)                              # internal energy reference shifted by the val-bias
        Pi_eval = min(xh[2] - thE, xh[3] - 3, xh[4] - 3, xh[5] - 1) if "feas" not in self.ab else 10
        sealed = pos == self.cfg.shelter and door_b[0] == 1
        tremor_near = any(_dist(pos, c) <= 1 for c in rock_seen)
        C1 = 1 if (tremor_near or Pi_eval <= 0 or (T == 2 and not sealed and xh[4] <= 4)) else 0
        known = [(c, res_b[k][0]) for k, c in enumerate(self.res_cells) if res_b[k][0] > 0 and res_b[k][1] < AGE_MAX]
        reach = [c for c, lv in known if _dist(pos, c) <= max(1, xh[2] // 2)]
        C2 = (1 if (Pi_eval <= 1 and not reach and xh[9] == 0) else 0,                 # 対応不可能性
              1 if xh[7] <= 1 else 0,                                                  # 手段不足性
              1 if not known and xh[9] == 0 else 0,                                    # 資源不足性
              1 if (xh[2] <= 7 and m2L["trustP"] == 0 and m2L["trustD"] == 0) else 0,  # 支援不足性
              1 if (m2W["trust_prev"] is not None and m2L["trustP"] < m2W["trust_prev"]) else 0)  # 関係品質劣化
        mu_hat = len({self._class_hat(xh, ehat, u) for u in U if self._viable_hat(xh, ehat, u)})
        C3 = None
        ring = m2W["ring"]
        if len(ring) >= D_LONG:
            a, bb = ring[0]
            C3 = 1 if (Pi_eval - a > 0 and mu_hat - bb < 0) else 0
        trend = D[0]
        if C1:
            P = 1
        elif any(C2):
            P = 2
        elif C3 == 1 or trend[0] < -1 or (T == 2 and not sealed):
            P = 3
        else:
            P = None
        Req = self.rho_req(M)
        sig = set()
        if "feas" not in self.ab and xh[2] - thE <= 7:
            sig.add(("energy", "lack"))
        if (T == 2 and not sealed) or ("feas" not in self.ab and xh[4] <= 4):
            sig.add(("heat", "warn"))
        if "feas" not in self.ab and (xh[3] <= 5 or min(xh[6], xh[7], xh[8]) <= 1):
            sig.add(("integrity", "lack"))
        if tremor_near:
            sig.add(("safety", "avoid"))
        if "relation" in Req and peer_b[0] >= 0 and peer_b[2] == 1 and peer_b[3] <= 3:
            sig.add(("relation", "approach"))
        sig = tuple(sorted(sig))
        evrq = {}
        for k, c in enumerate(self.res_cells):
            lv, age = res_b[k]
            if age < AGE_MAX:
                evrq[("energy", f"r{k}")] = (3 * lv - _dist(pos, c)) if lv > 0 else -3 - 2 * _dist(pos, c)   # depleted cells regrow (initial belief)
        evrq[("heat", "S")] = 3 - _dist(pos, self.cfg.shelter)
        if "relation" in Req and peer_b[0] >= 0:
            evrq[("relation", "P")] = m2L["trustP"] + (2 if peer_b[2] else 0)
        for k, c in enumerate(self.rock_cells):
            s = self.part(M, 1, "L")["rock"][k]
            if s >= 1:
                evrq[("safety", f"k{k}")] = -s
        evrq[("integrity", "*")] = -(10 - xh[3])
        if self.cfg.with_org:
            st, age = ehat[7]
            evrq[("energy", "D")] = (2 * min(st, 3) - _dist(pos, self.cfg.depot)) if (st > 0 and age < AGE_MAX) else -10
        evrq = tuple(sorted(evrq.items()))
        ev = (Pi_eval, C1, C2, C3, mu_hat)
        return P, ev, sig, evrq, Req

    def _viable_hat(self, xh, ehat, u):
        e, tp, ig, pos = self.fhat_simple(xh, ehat, u)
        return e >= 3 and tp >= 3 and ig >= 3

    def fhat_simple(self, xh, ehat, u):
        """M2's own coarse outcome rule (does not use M1's learned model)."""
        e, tp, ig = xh[2] - 1 + ehat[6], xh[4], xh[3]
        pos = (xh[0], xh[1])
        if u in DIRS:
            e -= 1
            dx, dy = DIRS[u]
            q = (pos[0] + dx, pos[1] + dy)
            if 0 <= q[0] < self.cfg.grid and 0 <= q[1] < self.cfg.grid:
                pos = q
        elif u == "eat" and (xh[9] > 0 or (pos in self.res_cells and ehat[2][self.res_cells.index(pos)][0] > 0)):
            e += self.cfg.eat_gain
        elif u == "repair" and xh[2] >= 2:
            e -= 2
            ig += 1
        if ehat[0] == 2 and not (pos == self.cfg.shelter and ehat[3][0] == 1):
            tp -= 1
        return e, tp, ig, pos

    def _class_hat(self, xh, ehat, u):
        e, tp, ig, pos = self.fhat_simple(xh, ehat, u)
        return (e >= 8, tp >= 5, pos == self.cfg.shelter)

    # ================================================================ M3 (response formation)
    def M3(self, S1, out2, M, model):
        """(u_M3, mode, style, Pur, stat) = M3(...)  (def:m3_map).  Also returns internals."""
        m3L, m3W = self.part(M, 3, "L"), self.part(M, 3, "W")
        P, ev, sig, evrq, Req = out2
        xh, ehat, xi, w, D = S1
        T, rock_seen, res_b, door_b, peer_b, drone_b, gift, depot_b = ehat
        pos = (xh[0], xh[1])
        evd = dict(evrq)
        sigq = {q for (q, c) in sig}
        # --- purpose status judgement (def:purpose_status) over the purpose record
        stat = {}
        keep = []
        for p in m3W["Pur"]:
            q, d, z = p
            s = self._judge_purpose(p, xh, ehat, sigq, Req)
            stat[p] = s
            if s in ("cont", "und"):
                keep.append(p)
        # --- purpose formation (def:purpose_formation)
        roots = {p[0] for p in keep}
        new = []
        if "envuse" not in self.ab and "energy" in sigq and "energy" not in roots:
            best = None
            for (q, tok), v in evd.items():
                if q == "energy" and (best is None or v > best[1]):
                    best = (tok, v)
            peer = ehat[4]
            near_peer = peer[0] >= 0 and peer[3] <= 3 and _dist(pos, (peer[0], peer[1])) <= 2
            if xh[9] > 0:
                new.append(("energy", "self", "eat_carry"))
            elif xh[2] <= 4 and "relation" in Req and near_peer:
                new.append(("energy", "self", "call"))
            elif best is not None and best[1] > -6:
                new.append(("energy", best[0], "eat" if best[0] != "D" else "draw"))
            elif "relation" in Req:
                new.append(("energy", "self", "call"))
        if ("envuse" not in self.ab and "energy" in sigq and xh[2] <= 4 and "relation" in Req and ("energy", "self", "call") not in keep + new):
            peer = ehat[4]
            if peer[0] >= 0 and peer[3] <= 3 and _dist(pos, (peer[0], peer[1])) <= 2:
                new.append(("energy", "self", "call"))              # a second energy purpose: call the partner
        if "envuse" not in self.ab and "heat" in sigq and "heat" not in roots:
            new.append(("heat", "S", "seal"))
        if "integrity" in sigq and "integrity" not in roots and xh[2] >= 6:
            new.append(("integrity", "self", "repair"))
        if "safety" in sigq and "safety" not in roots:
            new.append(("safety", "self", "avoid"))
        if "relation" in sigq and "relation" not in roots and xh[2] >= 8:
            new.append(("relation", ("self", "P"), "give"))
        pur = tuple(sorted(set(keep + new), key=_prio))[:3]
        # --- mode (def:mode_judgment) and style (def:m3_3b_styles)
        if P == 1:
            mode = "3A"
        elif P in (2, 3) or len(pur) >= 2:
            mode = "3B"
        else:
            mode = "3C"
        style = "none"
        if mode == "3B":
            rs = {p[0] for p in pur}
            if "relation" in rs and rs & {"energy", "heat", "integrity"}:
                style = "3B-c"
            elif "relation" in rs:
                style = "3B-b"
            else:
                style = "3B-a"
        # --- candidates (def:s4_candidate_sources)
        cand = {U_EMPTY, "vigil"} | (set() if "phys" in self.ab else {"repair"})
        for p in pur:
            g = self._goal(p, ehat, pos)
            if g is None:
                cand |= self._at_goal_actions(p)
            else:
                st = _steps_toward(pos, g)
                if st:
                    cand |= st
                else:
                    cand |= self._at_goal_actions(p)
        if not pur:
            cand |= {"N", "E", "S", "W"}
        if self.cfg.with_org and xh[9] > 0:
            st = _step_toward(pos, self.cfg.depot)
            cand.add(st if st else "deposit")
        if "envuse" not in self.ab and "energy" in sigq and pos in self.res_cells:
            cand |= {"eat", "collect"}
        if "resp" in self.ab:
            cand = set(U) - ({"repair"} if "phys" in self.ab else set())
        cand = tuple(sorted(cand, key=lambda u: CODE[u]))
        # --- automaticity: routine response without comparison (def:integrated_fast_processing)
        key = (pos, T)
        fast = False
        routine = None
        for (k, a, s) in m3L["rout"]:
            if k == key and s >= 2:
                routine = a
        if mode == "3C" and routine is not None and not pur and "auto" not in self.ab:
            u_m3 = routine
            fast = True
            fit = {routine: 0.0}
        else:
            fit = ({u: self._fit(u, mode, style, pur, xh, ehat, m3L, model) for u in cand}
                   if "select" not in self.ab else {u: 0.0 for u in cand})
            u_m3 = proj_sel(cand, fit)
        return {"u": u_m3, "mode": mode, "style": style, "Pur": pur, "stat": tuple(sorted(stat.items(), key=lambda kv: repr(kv[0]))),
                "cand": cand, "fit": tuple(sorted(fit.items())), "fast": fast, "key": key}

    def _judge_purpose(self, p, xh, ehat, sigq, Req):
        q, d, z = p
        pos = (xh[0], xh[1])
        T, rock_seen, res_b, door_b, peer_b, drone_b, gift, depot_b = ehat
        if q == "energy":
            if xh[2] >= 14 or (z == "call" and xh[2] >= 9):
                return "ach"
            if z == "call" and (peer_b[0] < 0 or peer_b[3] > 3):
                return "term"
            if d == "D" and depot_b[0] == 0 and depot_b[1] <= 1:
                return "term"
            if d not in ("self", "D") and isinstance(d, str) and d.startswith("r"):
                lv, age = res_b[int(d[1:])]
                if lv == 0 and age == 0:
                    return "term"
            return "cont" if "energy" in sigq or xh[2] < 14 else "und"
        if q == "heat":
            sealed = pos == self.cfg.shelter and door_b[0] == 1
            if sealed and xh[4] >= 5:
                return "ach"
            if "heat" not in sigq and T != 2:
                return "term"
            return "cont"
        if q == "integrity":
            if xh[3] >= 8 and min(xh[6], xh[7], xh[8]) >= 2:
                return "ach"
            return "cont"
        if q == "safety":
            return "cont" if "safety" in sigq else "ach"
        if q == "relation":
            if xh[11] == CODE["give"]:
                return "ach"
            if xh[2] < 6:
                return "term"
            if "relation" not in Req or peer_b[0] < 0:
                return "term"
            return "cont" if "relation" in sigq else "und"
        return "und"

    def _goal(self, p, ehat, pos):
        q, d, z = p
        if z in ("eat_carry", "repair", "avoid", "call"):
            return None
        if isinstance(d, tuple):
            peer = ehat[4]
            return (peer[0], peer[1]) if peer[0] >= 0 else None
        if d == "S":
            return self.cfg.shelter
        if d == "D":
            return self.cfg.depot
        if isinstance(d, str) and d.startswith("r"):
            return self.res_cells[int(d[1:])]
        return None

    def _at_goal_actions(self, p):
        q, d, z = p
        return {"eat": {"eat", "collect"}, "seal": {"open_door", U_EMPTY}, "give": {"give"},
                "draw": {U_EMPTY}, "eat_carry": {"eat"}, "repair": {"repair"},
                "avoid": {"N", "E", "S", "W"}, "call": {"signal"}}.get(z, {U_EMPTY})

    LOOK = ("wait", "N", "E", "S", "W", "eat", "open_door")

    def _hyp(self, model, xh, ehat, u):
        """one hypothetical internal step: (value inputs, next xh, next ehat)."""
        e, tp, ig, pos = self.fhat(model, xh, ehat, u)
        eh = ehat
        if u == "open_door" and _dist((xh[0], xh[1]), self.cfg.shelter) <= 1:
            eh = ehat[:3] + ((1 - ehat[3][0], ehat[3][1]),) + ehat[4:]
        xh2 = (pos[0], pos[1], e, ig, tp) + tuple(xh[5:])
        return (e, tp, ig, pos), xh2, eh

    def _fit(self, u, mode, style, pur, xh, ehat, m3L, model):
        """fit_t(u): purpose-referenced evaluation (def:m3_fit); internal model only."""
        depth = 1 if "resp" in self.ab else {"3A": 2, "3B": 3, "3C": 1}[mode]
        (e, tp, ig, pos), xh2, eh2 = self._hyp(model, xh, ehat, u)
        score = self._value(e, tp, ig, pos, pur, eh2, style, m3L, xh, u)
        if depth > 1:
            best = -1e9
            for u2 in self.LOOK:
                (e2, tp2, ig2, pos2), xh3, eh3 = self._hyp(model, xh2, eh2, u2)
                v2 = self._value(e2, tp2, ig2, pos2, pur, eh3, style, m3L, xh2, u2)
                if depth > 2:
                    b3 = -1e9
                    for u3 in self.LOOK:
                        (e3, tp3, ig3, pos3), _x4, eh4 = self._hyp(model, xh3, eh3, u3)
                        b3 = max(b3, self._value(e3, tp3, ig3, pos3, pur, eh4, style, m3L, xh3, u3))
                    v2 = 0.5 * v2 + 0.5 * b3
                best = max(best, v2)
            score = 0.5 * score + 0.5 * best
        if mode == "3A" and pos in ehat[1]:
            score -= 20
        return round(score, 4)

    def _value(self, e, tp, ig, pos, pur, ehat, style, m3L, xh, u):
        wE = 1.0
        v = wE * min(e, 14) + 1.5 * min(tp, 6) + 1.5 * min(ig, 10)
        v -= 6 * (max(0, 3 - e) + max(0, 3 - tp) + max(0, 3 - ig))
        if e <= 0:
            v -= 30                                             # belief: at zero energy nothing can be done
        for p in pur:
            g = self._goal(p, ehat, pos)
            if g is not None:
                v -= (5.0 if (p[0] == "heat" and ehat[0] == 2) else 2.5) * _dist(pos, g)
                if p[0] == "energy":
                    v += 2.0 * min(0, e - 2 * _dist(pos, g) - 2)  # can the goal still be reached (with margin)?
                if _dist(pos, g) == 0 and u in self._at_goal_actions(p) and u != U_EMPTY:
                    v += 3
            elif u in self._at_goal_actions(p) and u != U_EMPTY:
                v += 2
            if p[2] == "give" and u == "give":
                v += 6 if style in ("3B-b", "3B-c", "none") else 2
            if p[2] == "seal" and pos == self.cfg.shelter and ehat[3][0] == 1:
                v += 5
            if p[2] == "call" and u == "signal":
                v += 3
        wX = m3L["wX"]
        if wX and u in DIRS:
            k = None
            for kk, c in enumerate(self.res_cells):
                if _dist(pos, c) < _dist((xh[0], xh[1]), c) and ehat[2][kk][1] >= 6:
                    k = kk
            if k is not None:
                v += 0.8 * wX
        return v

    # ================================================================ PSL-4, resolve, the standard maps
    def rho_local(self, I):
        return I[7]

    def Phi_prot(self, s_local, I):
        """local protective response (def:psl4): step out of a cell with tremor."""
        if s_local[0] == 0:
            return None
        _, sp, T, cells, peers, dr, gift, local = I
        pos = (sp[0], sp[1])
        trem = {c for (c, lv, rk, tr, dv) in cells if tr or rk}
        for d in ("N", "E", "S", "W"):
            dx, dy = DIRS[d]
            q = (pos[0] + dx, pos[1] + dy)
            if 0 <= q[0] < self.cfg.grid and 0 <= q[1] < self.cfg.grid and q not in trem:
                return d
        return None

    @staticmethod
    def pr_loc(u):
        return u if u in DIRS else "none"

    @staticmethod
    def resolve(u_m3, r_local, R):
        """Phi_resolve (def:effective_action_resolve): the local protective response is kept."""
        return u_m3 if r_local is None else r_local

    def pipeline(self, M, I):
        """r = P_disc(M, I), v = P_val(M, r), u = P_act(M, r, v)  (def:s4_primitive_composition)."""
        S1 = self.M1(I, M)
        m1W = self.part(M, 1, "W")
        out2 = self.M2(S1, M, m1W["Ih"])
        model = self.part(M, 1, "L")
        o3 = self.M3(S1, out2, M, model)
        r_local = None if "phys" in self.ab else self.Phi_prot(self.rho_local(I), I)
        u = self.resolve(o3["u"], r_local, "std")
        return S1, out2, o3, r_local, u

    def operate(self, M, x, e, lam=None):
        I = self.P_sens(x, e)
        S1, out2, o3, r_local, u = self.pipeline(M, I)
        return {"I": I, "S1": S1, "out2": out2, "o3": o3, "r_local": r_local, "u": u}

    # ================================================================ Update (via the observation only)
    def Update(self, M, x, e):
        return self.Phi_upd(M, self.P_sens(x, e))

    def Phi_upd(self, M, I):
        if "update" in self.ab:
            return M                                             # E2: Update replaced by the identity
        (m1L, m1W), (m2L, m2W), (m3L, m3W) = M
        M1n = self.Update_1(M[0], I)
        M2n = self.Update_2(M[1], I, M1n)
        M3n = self.Update_3(M[2], I, M1n, M2n)
        return (M1n, M2n, M3n)

    def Update_1(self, M1c, I):
        L, W = dict(M1c[0]), dict(M1c[1])
        Mfake = ((M1c[0], M1c[1]), ((), ()), ((), _fz({"Pur": ()})))
        _, sp, T, cells, peers, dr, gift, local = I
        if T is None:                                            # no activity: memory frozen, records kept
            return M1c
        S1 = self.M1(I, Mfake, use_tgt=False)                    # record: target axis cannot be recovered here
        xh, ehat = S1[0], S1[1]
        forget = 2 if sp[8] <= 1 else 1                          # weak memory substrate ages beliefs faster
        step_age = 1
        if "integ" in self.ab:                                   # E2: no integration over time
            forget = step_age = AGE_MAX
        res = []
        seen = {c: lv for (c, lv, rk, tr, dv) in cells}
        for k, c in enumerate(self.res_cells):
            lv, age = L["res"][k]
            res.append((seen[c], 0) if c in seen else (lv, min(AGE_MAX, age + forget)))
        rock = list(L["rock"])
        rseen = {c: (rk, tr) for (c, lv, rk, tr, dv) in cells}
        for k, c in enumerate(self.rock_cells):
            if c in rseen:
                rk, tr = rseen[c]
                if rk or tr:
                    rock[k] = min(3, rock[k] + 1)
        tdrop = list(L["tdrop"])
        hist = W["xh"]
        if hist and T is not None and 0 <= T <= 2:
            prev = hist[-1]
            Ih = W["Ih"]
            if Ih and Ih[-1][0] == T and (prev[0], prev[1]) != self.cfg.shelter:
                obs = xh[4] - prev[4]
                if obs < tdrop[T]:
                    tdrop[T] -= 1
                elif obs > tdrop[T]:
                    tdrop[T] += 1
                tdrop[T] = max(-3, min(1, tdrop[T]))
        door = (ehat[3][0], 0) if ehat[3][1] == 0 else (L["door"][0], min(AGE_MAX, L["door"][1] + step_age))
        peer = ehat[4] if ehat[4][3] == 0 else (L["peer"][0], L["peer"][1], L["peer"][2], min(AGE_MAX, L["peer"][3] + step_age))
        drone = ehat[5] if ehat[5][2] == 0 else (L["drone"][0], L["drone"][1], min(AGE_MAX, L["drone"][2] + step_age))
        err = list(L["err"])
        if S1[4][2]:
            err = (err + [("res", (sp[0], sp[1]))])[-4:]
        if S1[4][1] >= 3:
            err = (err + [("self", S1[4][1])])[-4:]
        dep = ehat[7] if ehat[7][1] == 0 else (L["depot"][0], min(AGE_MAX, L["depot"][1] + forget))
        L.update(res=tuple(res), rock=tuple(rock), tdrop=tuple(tdrop), door=door, peer=peer, drone=drone,
                 err=tuple(err), depot=dep)
        # working records: S_M1 record, histories, model snapshot, predictions for every action
        model_t = dict(M1c[0])
        pred = {}
        for u in U:
            pr = self.fhat(model_t, xh, ehat, u)
            pred[u] = ((pr[0], pr[1]), self.predict_G(model_t, xh, ehat, u))
        W.update(S1=S1, xh=(tuple(W["xh"]) + (xh,))[-W_HIST:], Ih=(tuple(W["Ih"]) + ((T, local),))[-W_SHORT:],
                 pred=_FzDict(pred), model=_fz(model_t))
        return (_fz(L), _fz(W))

    def Update_2(self, M2c, I, M1n):
        L, W = dict(M2c[0]), dict(M2c[1])
        _, sp, T, cells, peers, dr, gift, local = I
        if T is None:
            return M2c
        m1Wn = dict(M1n[1])
        S1 = m1Wn["S1"]
        Mtmp = ((m1Wn["model"], M1n[1]), M2c, ((), _fz({"Pur": ()})))
        P, ev, sig, evrq, Req = self.M2(S1, Mtmp, m1Wn["Ih"])
        # learning of the evaluation side (M2^L)
        trust_prev = L["trustP"]
        if self.cfg.learn_bias:
            if S1[0][2] <= 5:
                L["hunger"] = min(3, L["hunger"] + 1)
                if L["hunger"] == 3:
                    L["wE"] = min(4, L["wE"] + 1)
                    L["hunger"] = 0
        if gift > 0:
            if any(p[0] == self.other for p in peers):
                L["trustP"] = min(3, L["trustP"] + 1)
            if dr:
                L["trustD"] = min(3, L["trustD"] + 1)
        ring = (tuple(W["ring"]) + ((ev[0], ev[4]),))[-D_LONG:]
        W.update(P=P, ev=ev, sig=sig, evrq=evrq, Req=Req, ring=ring, trust_prev=trust_prev)
        return (_fz(L), _fz(W))

    def Update_3(self, M3c, I, M1n, M2n):
        L, W = dict(M3c[0]), dict(M3c[1])
        _, sp, T, cells, peers, dr, gift, local = I
        if T is None:
            return M3c
        m1Wn, m2Wn = dict(M1n[1]), dict(M2n[1])
        S1r = m1Wn["S1"]
        # restore the target axis from this mechanism's own purpose record
        Mt = (M1n, M2n, M3c)
        model_t = dict(m1Wn["model"])
        xi_full = self.identify(S1r[0], S1r[1], self.seen_of(I), model_t, local,
                                self.tgt_set(((), (), M3c)))
        S1 = (S1r[0], S1r[1], xi_full, S1r[3], S1r[4])
        out2 = (m2Wn["P"], m2Wn["ev"], m2Wn["sig"], m2Wn["evrq"], m2Wn["Req"])
        o3 = self.M3(S1, out2, Mt, model_t)
        r_local = None if "phys" in self.ab else self.Phi_prot(local, I)
        u = self.resolve(o3["u"], r_local, "std")
        G = m1Wn["pred"][u][1]
        # routine learning (automaticity / de-automatisation) from the last step's outcome
        Pi_now = out2[1][0]
        rout = {(k, a): s for (k, a, s) in L["rout"]}
        if W["key"] is not None and W["u"] is not None and W["Pi_prev"] is not None:
            k0, a0 = W["key"], W["u"]
            s0 = rout.get((k0, a0), 0)
            if Pi_now >= W["Pi_prev"] and Pi_now >= 2 and S1[4][2] == 0:
                s0 = min(3, s0 + 1)
            else:
                s0 = max(0, s0 - 1)
            rout[(k0, a0)] = s0
        rout = tuple(sorted(((k, a, s) for (k, a), s in rout.items() if s > 0), key=repr))[-40:]
        resp = list(L["resp"])
        if r_local is not None:
            resp = (resp + [("tremor", r_local)])[-4:]
        L.update(rout=rout, resp=tuple(resp))
        W.update(Pur=o3["Pur"], mode=o3["mode"], u=u, G=G, key=o3["key"], stat=o3["stat"], Pi_prev=Pi_now)
        return (_fz(L), _fz(W))


# ------------------------------------------------------------------ helpers
CODE_INV = {v: k for k, v in CODE.items()}


def self_coarse(sp, base):
    return sp[5] <= 1 or sp[6] <= 1


def _prio(p):
    order = {"safety": 0, "heat": 1, "energy": 2, "integrity": 3, "relation": 4}
    return (order.get(p[0], 9), repr(p))


def proj_sel(cand, fit):
    """deterministic selection projection Proj_sel (def:sel_proj): max fit, ties by the order of U."""
    return max(cand, key=lambda u: (fit[u], 0 if u == U_EMPTY else 1, -CODE[u]))


class _FzDict(tuple):
    """hashable read-only mapping (finite carrier)."""

    def __new__(cls, d):
        return super().__new__(cls, tuple(sorted(d.items(), key=lambda kv: kv[0])))

    def __getitem__(self, k):
        if isinstance(k, int):
            return tuple.__getitem__(self, k)
        for kk, v in tuple.__iter__(self):
            if kk == k:
                return v
        raise KeyError(k)

    def get(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            return default


def _fz(d):
    return tuple(sorted(d.items()))
