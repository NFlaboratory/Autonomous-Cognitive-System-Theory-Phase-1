# -*- coding: utf-8 -*-
"""MinACS: a minimal finite ACS on which every set of the paper is computed by full enumeration.

Everything here is a toy convention (a concrete realisation); the definitions computed on it
are in analysis.py and follow the definitions of the manuscript.

  cells      0 = shelter, 1 = resource cell
  X          x = (p, en, tp, s)   p in {0,1}, en in {0..5}, tp in {0,1,2}, s in {0,1}      |X| = 72
  U          {wait, L, R, eat}    wait = u_emptyset
  E_ext      e = (b, o),  b = (c, g, rho) in E^bg = {0,1}^3,  o = r in O = {0,1}          |E_ext| = 16
             c cold, g gift (+2 energy), rho regrowth of the resource; r resource present
  E          eta_heat(x,e) = 1  iff  c = 0 or p = 0        (shelter protects heat)
             eta_food(x,e) = 1  iff  r = 1 or g = 1
  Pi         Pi(x) = min(en - 1, tp - 1, s - 1)            theta = (en 1, tp 1, s 1)
  f          f = (+)(f_auto, f_dir),  (+)(a, b) = clip(a + b - o*),  o* = (1, 1, 1, 1)
             L / R move between the two cells; eat on the resource cell with r = 1 gives +3 energy
  g_O        r' = 1 if rho = 1, else 0 if the resource was eaten, else r
"""
from itertools import product
from collections import namedtuple

X_ = namedtuple("X", "p en tp s")
E_ = namedtuple("E", "c g rho r")

P_MAX, EN_MAX, TP_MAX = 1, 5, 2
SHELTER, RES = 0, 1
U = ("wait", "L", "R", "eat")
U_EMPTY = "wait"
OSTAR = X_(1, 1, 1, 1)
I_E = ("en", "tp")                  # environment-response coordinates (ass:env_response)
FIELDS = X_._fields
THETA = X_(None, 1, 1, 1)           # p carries no threshold

XS = [X_(p, en, tp, s) for p in range(P_MAX + 1) for en in range(EN_MAX + 1)
      for tp in range(TP_MAX + 1) for s in (0, 1)]
ES = [E_(c, g, rho, r) for c, g, rho, r in product((0, 1), repeat=4)]
BG = sorted({(e.c, e.g, e.rho) for e in ES})
OS = (0, 1)


def clip(v):
    p, en, tp, s = v
    return X_(min(P_MAX, max(0, p)), min(EN_MAX, max(0, en)), min(TP_MAX, max(0, tp)), min(1, max(0, s)))


def Pi(x):
    return min(x.en - 1, x.tp - 1, x.s - 1)


def in_K(x):
    return Pi(x) >= 0


def warm(x, e):
    return x.p == SHELTER or e.c == 0


def base_active(x):
    """base functions (energy supply, maintenance) are active: toy rule, fixed in advance."""
    return x.s == 1 and x.en > 0


def f_auto(x, e):
    if x.s == 0:
        return x                                   # structure lost: frozen
    en1 = x.en - (1 if x.en > 0 else 0) + 2 * e.g
    tp1 = x.tp + 1 if warm(x, e) else x.tp - 1
    s1 = 0 if ((x.en == 0 and e.g == 0) or (x.tp == 0 and not warm(x, e))) else 1
    return clip((x.p, en1, tp1, s1))


def f_dir(x, u, e):
    if u == U_EMPTY or not base_active(x):
        return OSTAR
    d = [0, 0, 0, 0]
    if u == "L":
        d[0] = -1
    elif u == "R":
        d[0] = 1
    elif u == "eat" and x.p == RES and e.r == 1:
        d[1] = 3
    return X_(*[o + k for o, k in zip(OSTAR, d)])


def oplus(a, b):
    return clip(tuple(ai + bi - oi for ai, bi, oi in zip(a, b, OSTAR)))


def f(x, u, e):
    return oplus(f_auto(x, e), f_dir(x, u, e))


def eaten(x, u, e):
    return u == "eat" and x.p == RES and e.r == 1 and base_active(x)


def g_O(o, x, u, b):
    c, g, rho = b
    if rho == 1:
        return 1
    return 0 if eaten(x, u, E_(c, g, rho, o)) else o


def eta_heat(x, e):
    return 1 if (e.c == 0 or x.p == SHELTER) else 0


def eta_food(x, e):
    return 1 if (e.r == 1 or e.g == 1) else 0


ETA = {"heat": eta_heat, "food": eta_food}

# admissible external actions Upsilon_adm (toy convention); no effect on a structure already lost
UPSILON = ("inject", "warm", "carry")


def upsilon(x, act):
    if x.s == 0:
        return x
    if act == "inject":
        return clip((x.p, x.en + 2, x.tp, x.s))
    if act == "warm":
        return clip((x.p, x.en, TP_MAX, x.s))
    if act == "carry":
        return clip((SHELTER, x.en, x.tp, x.s))
    raise ValueError(act)
