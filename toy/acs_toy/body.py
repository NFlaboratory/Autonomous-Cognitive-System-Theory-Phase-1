# -*- coding: utf-8 -*-
"""The 7-tuple side of one ACS individual: X, U, E, f, Pi (sec.2 def:acs) and the
judgment-rule realisations that the paper leaves to the target system
(basic/base function activity, WF, (SC-1)).  Not part of the paper.

f depends on the external environment state e only through the *local view* lam(x, e)
(class Lam below).  Every quantifier "for all e in E_ext" in the judgment layer is evaluated
exactly by enumerating the image {lam(x, e) | e in E_ext}, which is a product of per-field
value sets determined by the position in x (see lam_space).  This is exact because f and
every eta read e only through lam.
"""
from collections import namedtuple
from itertools import product
from typing import Dict, Iterable, List, Tuple

# ---------------------------------------------------------------- state space X (finite)
FIELDS = ("px", "py", "energy", "integ", "temp", "hpsl", "hsens", "heff", "hmem",
          "carry", "starve", "alert", "beacon", "last_u")
LO = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
HI_BASE = (None, None, 20, 10, 8, 3, 3, 3, 3, 2, 3, 1, 1, 12)
X = namedtuple("X", FIELDS)

# Pi(x) = min_k (x_k - theta_k)   (def:Pi); coordinates without a role get a non-binding theta
THETA = {"energy": 3, "integ": 3, "temp": 3, "hpsl": 1}
THETA_FREE = -100
# environment-response coordinates I_E (ass:env_response): body temperature, energy, integrity
I_E = ("energy", "integ", "temp")

# ---------------------------------------------------------------- action space U (finite)
U = ("wait", "N", "E", "S", "W", "eat", "collect", "give", "open_door", "deposit", "repair", "vigil", "signal")
U_EMPTY = "wait"                        # selective waiting u_emptyset (rem:action_space_structure)
U_INT = ("vigil",)                      # actions on internal cognitive state
U_EXT = ("N", "E", "S", "W", "eat", "collect", "give", "open_door", "deposit", "signal")
CODE = {u: k for k, u in enumerate(U)}
DIRS = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

# local view of e: Lam(T, door, rock_cur, rock_dest[dir], res_cur, res_other, gift, partner_adj)
Lam = namedtuple("Lam", ("T", "door", "rock_cur", "rock_N", "rock_E", "rock_S", "rock_W",
                         "res_cur", "res_other", "gift", "partner_adj"))


class Body:
    """X, U, f, Pi, E for one individual on a fixed world geometry (cfg)."""

    def __init__(self, cfg):
        self.cfg = cfg
        g = cfg.grid
        self.hi = tuple(g - 1 if h is None else h for h in HI_BASE)
        self.theta = tuple(THETA.get(f, THETA_FREE) for f in FIELDS)
        self.res_cells = set(cfg.resources)
        self.rock_cells = set(cfg.rock_cells)
        # o-star: reference element of X for the binary operation (+) (ass:f_decomposition)
        self.ostar = X(px=3, py=3, energy=10, integ=5, temp=4, hpsl=1, hsens=1, heff=1, hmem=1,
                       carry=1, starve=0, alert=0, beacon=0, last_u=0)
        self.gift_values = self._gift_values()

    def _gift_values(self):
        n = (1 if self.cfg.with_partner else 0) + (1 if self.cfg.with_drone else 0) + (1 if self.cfg.with_org else 0)
        return tuple(self.cfg.gift * k for k in range(n + 1))

    # ---------------------------------------------------------------- basic predicates
    def clip(self, v):
        return X(*[min(h, max(l, a)) for a, l, h in zip(v, LO, self.hi)])

    def Pi(self, x):
        return min(a - t for a, t in zip(x, self.theta))

    def in_K(self, x):
        return self.Pi(x) >= 0

    def pos(self, x):
        return (x.px, x.py)

    def in_grid(self, c):
        return 0 <= c[0] < self.cfg.grid and 0 <= c[1] < self.cfg.grid

    def neighbors(self, c):
        return [(d, (c[0] + dx, c[1] + dy)) for d, (dx, dy) in DIRS.items()]

    def near_shelter(self, x):
        p, s = self.pos(x), self.cfg.shelter
        return abs(p[0] - s[0]) + abs(p[1] - s[1]) <= 1

    # ---------------------------------------------------------------- activity (judgment rule, fixed in advance)
    def active_base(self, x):
        """base functions (def:base_functions): energy supply/transport and repair are active."""
        return x.integ > 0 and x.energy > 0 and x.hpsl > 0

    def activity(self, x):
        """functional activity of the basic functions per primitive division (def:basic_functions)."""
        b = self.active_base(x)
        return {"sens": b and x.hsens > 0, "disc": b and x.hmem > 0,
                "val": b and x.hmem > 0, "act": b and x.heff > 0}

    def base_functions(self, x):
        b = self.active_base(x)
        return {"supply": b, "repair": b}

    def FT1(self, x):
        """(FT-1): all basic-function activity and all base functions stopped."""
        return not any(self.activity(x).values()) and not any(self.base_functions(x).values())

    def SC1(self, x):
        """(SC-1): the organisational/binding relation that made the individual one structure is lost."""
        return x.integ == 0

    def WF(self, x):
        return 1 if x.integ > 0 else 0

    # ---------------------------------------------------------------- f = (+)(f_auto, f_dir)
    def oplus(self, a, b):
        return self.clip([ai + bi - si for ai, bi, si in zip(a, b, self.ostar)])

    def f_auto(self, x, lam):
        if x.integ == 0:                                   # structure lost: frozen (absorbing)
            return x
        d = dict(x._asdict())
        base = x.hpsl > 0 and x.energy > 0
        sealed = (self.pos(x) == self.cfg.shelter and lam.door == 1)
        e = x.energy - (1 if base else 0) + lam.gift       # metabolism (the shelter protects heat, not energy)
        heat = 1 if base else 0
        if sealed:
            temp = min(6, x.temp + 1) if x.temp < 6 else x.temp
        else:
            dT = (0, -1, -2)[lam.T] + heat
            temp = min(6, x.temp + dT) if dT > 0 else x.temp + dT
        integ = x.integ
        starve = x.starve
        hpsl = x.hpsl
        heff = x.heff
        if temp <= 0:
            integ -= 1                                     # hypothermia (temp below theta alone leaves K, not the structure)
        if not base:
            integ -= 1                                     # starvation / unmaintained substrate
            starve = min(3, starve + 1)
            if starve >= 3:
                hpsl -= 1                                  # substrate damage (not self-repairable)
        else:
            starve = 0
            if x.energy >= 15 and temp >= 4 and integ < 10:
                integ += 1                                 # natural healing
                e -= 1
        if lam.rock_cur:
            integ -= 3
            heff -= 1
        d.update(energy=e, temp=temp, integ=integ, starve=starve, hpsl=hpsl, heff=heff,
                 alert=0, beacon=0, last_u=0)
        return self.clip(X(**d))

    def f_dir(self, x, u, lam):
        o = dict(self.ostar._asdict())
        if u == U_EMPTY or not self.active_base(x):
            return self.ostar
        o["last_u"] = CODE[u]
        ext_ok = x.heff > 0
        if u in DIRS:
            if not ext_ok:
                return X(**o)
            dx, dy = DIRS[u]
            dest = (x.px + dx, x.py + dy)
            o["energy"] -= 1
            if self.in_grid(dest):
                o["px"] += dx
                o["py"] += dy
                if getattr(lam, "rock_" + u):
                    o["integ"] -= 3
                    o["heff"] -= 1
        elif u == "eat":
            if ext_ok and lam.res_cur:
                o["energy"] += self.cfg.eat_gain
            elif ext_ok and x.carry > 0:
                o["energy"] += self.cfg.eat_gain
                o["carry"] -= 1
        elif u == "collect":
            if ext_ok and lam.res_cur and x.carry < 2:
                o["carry"] += 1
        elif u == "give":
            if ext_ok and lam.partner_adj and x.energy >= 4:
                o["energy"] -= self.cfg.gift
        elif u == "open_door":
            if ext_ok and self.near_shelter(x):
                o["energy"] -= 1
        elif u == "deposit":
            if ext_ok and self.pos(x) == self.cfg.depot and x.carry > 0:
                o["carry"] -= 1
        elif u == "repair":
            if x.energy >= 2 and x.temp >= 3:
                o["energy"] -= 2
                if x.integ < 10:
                    o["integ"] += 1
                else:
                    k = min(("hsens", "heff", "hmem"), key=lambda f: getattr(x, f))
                    o[k] += 1
        elif u == "vigil":
            o["energy"] -= 1
            o["alert"] += 1
        elif u == "signal":
            if ext_ok:
                o["energy"] -= 1
                o["beacon"] += 1
        return X(**o)

    def f(self, x, u, lam):
        return self.oplus(self.f_auto(x, lam), self.f_dir(x, u, lam))

    # effect flags used by g_O (did the action act on the world?)
    def effect(self, x, u, lam):
        if u == U_EMPTY or not self.active_base(x) or (u in U_EXT and x.heff == 0):
            return None
        if u in DIRS:
            return "move"
        if u == "eat":
            return "eat_cell" if lam.res_cur else ("eat_carry" if x.carry > 0 else None)
        if u == "collect":
            return "collect" if (lam.res_cur and x.carry < 2) else None
        if u == "give":
            return "give" if (lam.partner_adj and x.energy >= 4) else None
        if u == "open_door":
            return "open_door" if self.near_shelter(x) else None
        if u == "deposit":
            return "deposit" if (self.pos(x) == self.cfg.depot and x.carry > 0) else None
        if u == "signal":
            return "signal"
        return u

    # ---------------------------------------------------------------- required environment factors E
    def eta_heat(self, x, lam):
        return 1 if (lam.T <= 1 or (self.pos(x) == self.cfg.shelter and lam.door == 1)) else 0

    def eta_food(self, x, lam):
        return 1 if (lam.res_cur or lam.res_other or lam.gift > 0) else 0

    ETA = ("heat", "food")

    def eta(self, name, x, lam):
        return self.eta_heat(x, lam) if name == "heat" else self.eta_food(x, lam)

    # ---------------------------------------------------------------- image of E_ext under lam
    def lam_values(self, x) -> Dict[str, Tuple[int, ...]]:
        p = self.pos(x)
        vals = {"T": (0, 1, 2),
                "door": (0, 1) if p == self.cfg.shelter else (0,),
                "rock_cur": (0, 1) if p in self.rock_cells else (0,),
                "res_cur": (0, 1) if p in self.res_cells else (0,),
                "gift": self.gift_values,
                "partner_adj": (0, 1) if self.cfg.with_partner else (0,)}
        other = False
        for d, c in self.neighbors(p):
            vals["rock_" + d] = (0, 1) if c in self.rock_cells else (0,)
            other = other or (c in self.res_cells)
        vals["res_other"] = (0, 1) if other else (0,)
        return vals

    def relevant(self, x, acts: Iterable[str]) -> Tuple[str, ...]:
        """fields of lam read by f(x,u,.) for u in acts, or by some eta (always included)."""
        rel = {"T", "res_cur", "res_other", "gift"}
        if self.pos(x) == self.cfg.shelter:
            rel.add("door")
        rel.add("rock_cur")
        for u in acts:
            if u in DIRS:
                rel.add("rock_" + u)
            if u == "give":
                rel.add("partner_adj")
        return tuple(sorted(rel))

    def lam_space(self, x, acts: Iterable[str] = (), fields: Tuple[str, ...] = None) -> List[Lam]:
        """all realisable local views, varying only the fields relevant for acts (others fixed to 0).

        Exact for any predicate that reads e only through f(x,u,.) for u in acts and the etas."""
        vals = self.lam_values(x)
        rel = fields if fields is not None else self.relevant(x, acts)
        keys = Lam._fields
        choices = [vals[k] if k in rel else (0,) for k in keys]
        return [Lam(*c) for c in product(*choices)]

    def lam_full(self, x) -> List[Lam]:
        vals = self.lam_values(x)
        return [Lam(*c) for c in product(*[vals[k] for k in Lam._fields])]
