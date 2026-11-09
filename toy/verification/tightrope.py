# -*- coding: utf-8 -*-
"""Tightrope (toy convention): a finite domain built so that the premises (a)(b) of
prop:sd_robust_nonresponse can hold persistently AND the strong assumption ass:theta_exterior_blockage
holds on the whole domain.  It is the counterpart of the furnace, where the strong assumption fails.

This is a PARTIAL MODEL: (X, U, E, f, Pi, O, g_O) only.  No mechanism (TIPA/PSL) is attached, so
CR-2 is not judged and the domain is not called an ACS; statements of sec.3 that refer only to
(X, U, E, f, Pi) are checked on it.

  X   b  sway  in {-2,...,2}
      h  fatigue in {0,...,4}   (h <= 1: actions are effective; h >= 2: exhausted)
      s  on the rope {0,1}
  U   L, S, R   (S = u_emptyset: keep still)
  E   w  wind in {-1,0,1}, r rope present {0,1}, g strong gust {0,1}   (background); o single point
  Pi  min(1 - |b|, 3 - h, s - 1)          K = {|b| <= 1, h <= 3, s = 1}
  eta_rope(x,e) = r          eta_calm(x,e) = 1 - g      (required environmental factors)
  f   s = 0: unchanged (fallen)
      r = 0: fall (s = 0)
      a = -1/0/+1 for L/S/R if h <= 1, else 0 (exhausted: every action has the same effect)
      b' = b + a + w; |b'| > 2: fall
      h' = h + 1 if h >= 2 (cannot rest on the rope) or |b| = 2 (struggling at the edge),
           else h + g  (a strong gust tires)
"""
from collections import namedtuple
from itertools import product

X_ = namedtuple("X", "b h s")
E_ = namedtuple("E", "w r g o")
U = ("L", "S", "R")
U_EMPTY = "S"
H_MAX = 4
XS = [X_(b, h, s) for b in range(-2, 3) for h in range(H_MAX + 1) for s in (0, 1)]
ES = [E_(w, r, g, 0) for w, r, g in product((-1, 0, 1), (0, 1), (0, 1))]
OS = (0,)
I_E = ("b",)


def Pi(x):
    return min(1 - abs(x.b), 3 - x.h, x.s - 1)


def f(x, u, e):
    if x.s == 0:
        return x
    if e.r == 0:
        return X_(x.b, x.h, 0)
    a = {"L": -1, "S": 0, "R": 1}[u] if x.h <= 1 else 0
    b1 = x.b + a + e.w
    h1 = min(H_MAX, x.h + 1) if (x.h >= 2 or abs(x.b) == 2) else min(H_MAX, x.h + e.g)
    if abs(b1) > 2:
        return X_(max(-2, min(2, b1)), h1, 0)
    return X_(b1, h1, 1)


ETA = {"rope": lambda x, e: e.r, "calm": lambda x, e: 1 - e.g}


class _D:
    NAME = "Tightrope"


D = _D()
for _k, _v in dict(XS=XS, U=U, U_EMPTY=U_EMPTY, ES=ES, OS=OS, ETA=ETA, I_E=I_E).items():
    setattr(D, _k, _v)
D.f = f
D.Pi = Pi
D.split = lambda e: ((e.w, e.r, e.g), e.o)
D.make_e = lambda b, o: E_(b[0], b[1], b[2], o)
D.g_O = lambda o, x, u, b: o
D.WF = lambda x: x.s
D.CS = lambda x: 1 if x.s == 0 else 0
