# -*- coding: utf-8 -*-
"""Minimal TIPA + PSL for MinACS (toy convention).  Uses only I = P_sens(x, e) and M; never Pi, A, Viab.

  M = (M1, M2, M3)
    M1 : learning part (belief_cold, belief_food) in {0,1}^2
    M2 : learning part = hunger reference h_ref in {2} (fixed; the factor exists but does not learn)
    M3 : working part  = purpose record in {none, heat, food}
  |M| = 4 * 1 * 3 = 12

  P_sens : the weather c is observed only outside the shelter, the resource r only on the
           resource cell; nothing is sensed when the base functions are inactive.
  M1 -> (xhat, ehat)          ehat = (c or belief_cold, g, r or belief_food)
  M2 -> (Pi_eval, P, sig)     Pi_eval = min(en-1, tp-1) from xhat (proxy evaluation)
  M3 -> (purpose, mode, u)
  Update = Phi_upd(M, P_sens(x, e)) : beliefs take observed values; purpose record is stored.
"""
from collections import namedtuple

from .model import SHELTER, RES, U_EMPTY

M_ = namedtuple("M", "bc bf pur")         # belief_cold, belief_food, purpose record (M2 factor is a singleton)
MS = [M_(bc, bf, pur) for bc in (0, 1) for bf in (0, 1) for pur in ("none", "heat", "food")]
H_REF = 3


def P_sens(x, e):
    if not (x.s == 1 and x.en > 0):
        return ("I", x.p, x.en, x.tp, x.s, None, None, None)
    c = e.c if x.p != SHELTER else None
    r = e.r if x.p == RES else None
    return ("I", x.p, x.en, x.tp, x.s, c, e.g, r)


def M1(I, M):
    _, p, en, tp, s, c, g, r = I
    xhat = (p, en, tp, s)
    ehat = (M.bc if c is None else c, g, M.bf if r is None else r)
    return xhat, ehat


def M2(xhat, ehat, M):
    p, en, tp, s = xhat
    cold, g, food = ehat
    Pi_eval = min(en - 1, tp - 1)
    sig = []
    if cold == 1 and p != SHELTER:
        sig.append("heat")
    if en <= H_REF:
        sig.append("food")
    P = 1 if Pi_eval <= 0 else (2 if sig else None)
    return Pi_eval, P, tuple(sig)


def M3(xhat, ehat, out2, M):
    p, en, tp, s = xhat
    cold, g, food = ehat
    Pi_eval, P, sig = out2
    if "heat" in sig and en >= 2:
        pur = "heat"
    elif "food" in sig or (M.pur == "food" and en < 5):
        pur = "food"
    elif "heat" in sig:
        pur = "food"                     # too hungry to retreat: food first
    else:
        pur = "none"
    mode = "3A" if P == 1 else ("3B" if P == 2 else "3C")
    if pur == "heat":
        u = "L" if p > SHELTER else U_EMPTY
    elif pur == "food":
        if p == SHELTER and cold == 1 and en >= 3:
            u = U_EMPTY                  # wait out the cold while energy allows
        elif p < RES:
            u = "R"
        else:
            u = "eat" if food == 1 else U_EMPTY
    else:
        u = U_EMPTY
    return pur, mode, u


def operate(M, x, e):
    I = P_sens(x, e)
    if not (x.s == 1 and x.en > 0):
        return {"I": I, "u": U_EMPTY, "pur": M.pur, "mode": None, "P": None, "Pi_eval": None, "sig": ()}
    xhat, ehat = M1(I, M)
    out2 = M2(xhat, ehat, M)
    pur, mode, u = M3(xhat, ehat, out2, M)
    return {"I": I, "u": u, "pur": pur, "mode": mode, "P": out2[1], "Pi_eval": out2[0], "sig": out2[2]}


def Update(M, x, e, learn=True):
    I = P_sens(x, e)
    if not (x.s == 1 and x.en > 0):
        return M
    _, p, en, tp, s, c, g, r = I
    bc = M.bc if (c is None or not learn) else c
    bf = M.bf if (r is None or not learn) else r
    pur = operate(M, x, e)["pur"]
    return M_(bc, bf, pur)
