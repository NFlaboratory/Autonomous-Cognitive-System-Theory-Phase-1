# -*- coding: utf-8 -*-
"""Furnace keeper: the second domain of E8 (toy convention).

Structurally different from MinACS:
  - no movement (a stationary system);
  - the danger is two-sided: freezing in the cold and overheating in the heat;
  - one required factor is of the sink type (a clear flue), and the individual's own action (burning)
    can destroy it, while another action (opening) restores it;
  - overheating removes the structure in one step, so collapse can occur without prior blockage.

  X      x = (fu, tp, s)   fu fuel 0..4, tp temperature 0..5, s structure {0,1}           |X| = 60
  U      {wait, burn, gather, open}     wait = u_emptyset
  E_ext  e = (h, d, k, o)   b = (h, d, k) in {0,1}^3, o in O = {0,1}                         |E_ext| = 16
         h ambient (1 hot: +1, 0 cold: -1), d delivery of fuel, k bad draught (burning soots the flue),
         o flue clear
  E      eta_fuel(x,e) = 1  iff  fu >= 1 or d = 1 or h = 1      (material: fuel, or heat from outside)
         eta_flue(x,e) = 1  iff  o = 1 or h = 1                 (sink: exhaust, needed only when heating)
  Pi     Pi(x) = min(tp - 1, s - 1)
  f      f = (+)(f_auto, f_dir),  (+)(a, b) = clip(a + b - o*),  o* = (1, 1, 1)
         f_auto: tp +1 (hot) / -1 (cold); s -> 0 if tp = 0 in the cold (freezing) or tp = TP_MAX in the heat
                 (overheating); a structure lost is frozen.
         f_dir (base active, i.e. s = 1 and tp > 0):
                 burn   fu >= 1: fu - 1, and tp + 2 if o = 1; burning at tp >= TP_MAX - 1 cracks (s - 1)
                 gather d = 1: fu + 2
                 open   tp - 1 (heat released)
  g_O    o' = 1 after open; o' = 0 after an effective burn when k = 1; otherwise o' = o
"""
from itertools import product
from collections import namedtuple

X_ = namedtuple("X", "fu tp s")
E_ = namedtuple("E", "h d k o")

FU_MAX, TP_MAX = 4, 5
U = ("wait", "burn", "gather", "open")
U_EMPTY = "wait"
OSTAR = X_(1, 1, 1)
I_E = ("fu", "tp")

XS = [X_(fu, tp, s) for fu in range(FU_MAX + 1) for tp in range(TP_MAX + 1) for s in (0, 1)]
ES = [E_(h, d, k, o) for h, d, k, o in product((0, 1), repeat=4)]
OS = (0, 1)


def clip(v):
    fu, tp, s = v
    return X_(min(FU_MAX, max(0, fu)), min(TP_MAX, max(0, tp)), min(1, max(0, s)))


def Pi(x):
    return min(x.tp - 1, x.s - 1)


def base_active(x):
    return x.s == 1 and x.tp > 0


def f_auto(x, e):
    if x.s == 0:
        return x
    tp1 = x.tp + (1 if e.h == 1 else -1)
    s1 = 0 if ((x.tp == 0 and e.h == 0) or (x.tp == TP_MAX and e.h == 1)) else 1
    return clip((x.fu, tp1, s1))


def burned(x, u):
    return u == "burn" and base_active(x) and x.fu >= 1


def f_dir(x, u, e):
    if u == U_EMPTY or not base_active(x):
        return OSTAR
    d = [0, 0, 0]
    if u == "burn" and x.fu >= 1:
        d[0] = -1
        if e.o == 1:
            d[1] = 2
            if x.tp >= TP_MAX - 1:
                d[2] = -1
    elif u == "gather" and e.d == 1:
        d[0] = 2
    elif u == "open":
        d[1] = -1
    return X_(*[o + k for o, k in zip(OSTAR, d)])


def oplus(a, b):
    return clip(tuple(ai + bi - oi for ai, bi, oi in zip(a, b, OSTAR)))


def f(x, u, e):
    return oplus(f_auto(x, e), f_dir(x, u, e))


def g_O(o, x, u, b):
    h, d, k = b
    if u == "open" and base_active(x):
        return 1
    if burned(x, u) and o == 1 and k == 1:
        return 0
    return o


def eta_fuel(x, e):
    return 1 if (x.fu >= 1 or e.d == 1 or e.h == 1) else 0


def eta_flue(x, e):
    return 1 if (e.o == 1 or e.h == 1) else 0


ETA = {"fuel": eta_fuel, "flue": eta_flue}

UPSILON = ("supply", "warm", "cool")


def upsilon(x, act):
    if x.s == 0:
        return x
    if act == "supply":
        return clip((x.fu + 2, x.tp, x.s))
    if act == "warm":
        return clip((x.fu, max(x.tp, 2), x.s))
    if act == "cool":
        return clip((x.fu, min(x.tp, 3), x.s))
    raise ValueError(act)


class _D:
    NAME = "Furnace"
    pass


D = _D()
for _k, _v in dict(XS=XS, U=U, U_EMPTY=U_EMPTY, ES=ES, OS=OS, ETA=ETA, I_E=I_E, UPSILON=UPSILON).items():
    setattr(D, _k, _v)
for _k, _v in dict(f=f, f_auto=f_auto, Pi=Pi, g_O=g_O, upsilon=upsilon, base_active=base_active).items():
    setattr(D, _k, _v)
D.split = lambda e: ((e.h, e.d, e.k), e.o)
D.make_e = lambda b, o: E_(b[0], b[1], b[2], o)
D.WF = lambda x: x.s
D.CS = lambda x: 1 if x.s == 0 else 0
D.full_stop = lambda x: x.s == 1 and x.tp == 0
D.margin = lambda x: x.tp == 1 or x.tp == TP_MAX - 1
X0, O0 = X_(2, 3, 1), 1
