# -*- coding: utf-8 -*-
"""Minimal TIPA + PSL for the furnace keeper (toy convention).  Uses only I = P_sens(x, e) and M;
never Pi, A, Viab or the true flue state o.

  P_sens   fu, tp, s, ambient h and delivery d are sensed; the flue state o and the draught k are not.
           Nothing is sensed when the base functions are inactive (s = 0 or tp = 0).
  M        (bo, rec, pur)
             bo  belief that the flue is clear (M1, learned)
             rec record of the previous step (tp, u, h, fu) used for temporal integration (M1-c)
             pur purpose record (M3)
  M1       xhat = (fu, tp, s); ehat = (h, d, bo').  bo' integrates over time: after a burn with fuel,
           a temperature change lower than burn + ambient predicts means the flue is sooted (bo' = 0);
           after open, bo' = 1.
  M2       Pi_eval = tp - 1 (proxy evaluation);  signals: cold (h = 0 and tp <= 2), hot (tp >= 4, or h = 1 and
           tp >= 3), fuel (fu <= 1), flue (bo' = 0);  Priority 1 if Pi_eval <= 0 or tp >= 4, 2 if any signal.
  M3       purpose: cool > heat > flue > fuel > none (from the signals);
           candidates generated from the purpose; one-step lookahead with the internal model
           (ambient assumed to persist) removes candidates predicted to leave K or reach TP_MAX;
           fit = (purpose achieved by the prediction, -|predicted tp - target|, predicted fuel), target 3
           (2 when cooling); ties by U order.  Purpose achieved: fuel -> more fuel, flue -> open,
           heat -> tp not lower than now, cool -> tp not higher than now.
  PSL-4    local acute anomaly: hot ambient at tp >= TP_MAX - 1 -> protective response 'open'.
           Phi_resolve: the protective response, if any, replaces the TIPA command.

Ablation switches (E8-E2), each removing one principle-related function group (toy mapping):
  integ   no temporal integration: bo' is not inferred from the record (stays as stored; only open sets it)
  feas    Pi_eval constant, no threshold-based signals (cold, hot, fuel); Priority never 1
  resp    candidates not generated from the purpose (= U), no lookahead; fit from a fixed purpose-action table
  envuse  no purposes or candidates concerning the environmental factors (fuel gathering, flue opening)
  select  fit constant: the first candidate in U order is chosen
  update  Update is the identity (M stays M0)
  phys    no PSL-4 protective response
"""
from collections import namedtuple

from .model import TP_MAX, U, U_EMPTY

M_ = namedtuple("M", "bo rec pur")
M0 = M_(1, None, "none")
TARGET = {"cool": 2, "heat": 3, "flue": 3, "fuel": 3, "none": 3}
TABLE = {"cool": "open", "heat": "burn", "flue": "open", "fuel": "gather", "none": "wait"}


def P_sens(x, e):
    if not (x.s == 1 and x.tp > 0):
        return ("I", x.fu, x.tp, x.s, None, None)
    return ("I", x.fu, x.tp, x.s, e.h, e.d)


class Mind:
    def __init__(self, ablate=()):
        self.ab = frozenset(ablate)

    # ---------------------------------------------------------------- M1
    def M1(self, I, M):
        _, fu, tp, s, h, d = I
        bo = M.bo
        if M.rec is not None and "integ" not in self.ab:
            tp0, u0, h0, fu0 = M.rec
            if u0 == "open":
                bo = 1
            elif u0 == "burn" and fu0 >= 1:
                expect = min(TP_MAX, tp0 + (1 if h0 == 1 else -1) + 2)
                bo = 0 if tp < expect else 1
        elif M.rec is not None and M.rec[1] == "open":
            bo = 1
        return (fu, tp, s), (h, d, bo)

    # ---------------------------------------------------------------- M2
    def M2(self, xhat, ehat, M):
        fu, tp, s = xhat
        h, d, bo = ehat
        if "feas" in self.ab:
            return 10, None, (("flue",) if bo == 0 else ())
        Pi_eval = tp - 1
        sig = []
        if tp >= 4 or (h == 1 and tp >= 3):
            sig.append("hot")
        if h == 0 and tp <= 2:
            sig.append("cold")
        if bo == 0:
            sig.append("flue")
        if fu <= 1:
            sig.append("fuel")
        P = 1 if (Pi_eval <= 0 or tp >= 4) else (2 if sig else None)
        return Pi_eval, P, tuple(sig)

    # ---------------------------------------------------------------- M3
    def predict(self, xhat, ehat, u):
        fu, tp, s = xhat
        h, d, bo = ehat
        tp1 = tp + (1 if h == 1 else -1)
        fu1 = fu
        if u == "burn" and fu >= 1:
            fu1 -= 1
            if bo == 1:
                tp1 += 2
        elif u == "gather" and d == 1:
            fu1 += 2
        elif u == "open":
            tp1 -= 1
        return min(4, max(0, fu1)), min(TP_MAX, max(0, tp1))

    def M3(self, xhat, ehat, out2, M):
        fu, tp, s = xhat
        h, d, bo = ehat
        Pi_eval, P, sig = out2
        env = "envuse" not in self.ab
        if "hot" in sig:
            pur = "cool"
        elif "cold" in sig:
            pur = "heat"
        elif "flue" in sig and env:
            pur = "flue"
        elif "fuel" in sig and env:
            pur = "fuel"
        else:
            pur = "none"
        mode = "3A" if P == 1 else ("3B" if P == 2 else "3C")
        if "resp" in self.ab:
            cand = list(U)
        else:
            if pur == "cool":
                cand = ["open", U_EMPTY] if env else [U_EMPTY]
            elif pur == "heat":
                cand = []
                if fu >= 1 and bo == 1:
                    cand.append("burn")
                if env and bo == 0:
                    cand.append("open")
                if env and d == 1:
                    cand.append("gather")
                cand.append(U_EMPTY)
            elif pur == "flue":
                cand = ["open", U_EMPTY]
            elif pur == "fuel":
                cand = (["gather"] if d == 1 else []) + [U_EMPTY]
            else:
                cand = [U_EMPTY] + (["gather"] if (env and d == 1 and fu < 4) else [])
            ok = [u for u in cand if 1 <= self.predict(xhat, ehat, u)[1] < TP_MAX]
            cand = ok or cand
        cand = sorted(set(cand), key=U.index)
        if "select" in self.ab:
            u = cand[0]
        elif "resp" in self.ab:
            u = max(cand, key=lambda v: (1 if v == TABLE[pur] else 0, -U.index(v)))
        else:
            tgt = TARGET[pur]

            def fit(v):
                fu1, tp1 = self.predict(xhat, ehat, v)
                ach = {"fuel": fu1 > fu, "flue": v == "open", "heat": tp1 >= tp, "cool": tp1 <= tp}.get(pur, False)
                return (1 if ach else 0, -abs(tp1 - tgt), fu1, -U.index(v))
            u = max(cand, key=fit)
        return pur, mode, u

    # ---------------------------------------------------------------- PSL-4
    def Phi_prot(self, I):
        _, fu, tp, s, h, d = I
        if "phys" in self.ab or h is None:
            return None
        return "open" if (h == 1 and tp >= TP_MAX - 1) else None

    # ---------------------------------------------------------------- operate / Update
    def operate(self, M, x, e):
        I = P_sens(x, e)
        if not (x.s == 1 and x.tp > 0):
            return {"I": I, "u": U_EMPTY, "pur": M.pur, "mode": None, "P": None, "Pi_eval": None, "sig": ()}
        xhat, ehat = self.M1(I, M)
        out2 = self.M2(xhat, ehat, M)
        pur, mode, u3 = self.M3(xhat, ehat, out2, M)
        r = self.Phi_prot(I)
        u = r if r is not None else u3
        return {"I": I, "u": u, "u_M3": u3, "r_local": r, "pur": pur, "mode": mode, "P": out2[1],
                "Pi_eval": out2[0], "sig": out2[2], "bo": ehat[2]}

    def Update(self, M, x, e, learn=True):
        if "update" in self.ab:
            return M
        I = P_sens(x, e)
        if not (x.s == 1 and x.tp > 0):
            return M_(M.bo, None, M.pur)
        out = self.operate(M, x, e)
        bo = out["bo"] if learn else M.bo
        return M_(bo, (x.tp, out["u"], e.h, x.fu), out["pur"])
