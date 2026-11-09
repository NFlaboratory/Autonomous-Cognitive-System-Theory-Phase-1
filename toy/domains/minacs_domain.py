# -*- coding: utf-8 -*-
"""MinACS (E6) presented as a domain object for the common judgment layer.  No rule is changed:
every attribute is the corresponding object of MINACS/minacs/model.py and mind.py."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from minacs import model as mm   # noqa: E402
from minacs import mind as md    # noqa: E402


class _D:
    NAME = "MinACS"
    XS, U, U_EMPTY, ES, OS = mm.XS, mm.U, mm.U_EMPTY, mm.ES, mm.OS
    f, f_auto, Pi, ETA, I_E = staticmethod(mm.f), staticmethod(mm.f_auto), staticmethod(mm.Pi), mm.ETA, mm.I_E
    UPSILON = mm.UPSILON
    upsilon = staticmethod(mm.upsilon)
    base_active = staticmethod(mm.base_active)
    g_O = staticmethod(mm.g_O)

    @staticmethod
    def split(e):
        return (e.c, e.g, e.rho), e.r

    @staticmethod
    def make_e(b, o):
        return mm.E_(b[0], b[1], b[2], o)

    @staticmethod
    def WF(x):
        return x.s

    @staticmethod
    def CS(x):
        return 1 if x.s == 0 else 0

    @staticmethod
    def full_stop(x):
        return x.s == 1 and x.en == 0

    @staticmethod
    def margin(x):
        return x.en == 1 or x.tp == 1


D = _D()


class _Mind:
    operate = staticmethod(md.operate)
    Update = staticmethod(md.Update)


MIND = _Mind()
X0, O0, M0 = mm.X_(0, 4, 2, 1), 1, md.M_(0, 1, "none")
