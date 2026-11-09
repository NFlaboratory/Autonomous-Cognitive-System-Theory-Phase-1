# -*- coding: utf-8 -*-
"""Parameters and scenario presets of the ACS toy (not part of the paper).

Everything here is a *toy convention*: a concrete choice for something the paper leaves
implementation-dependent or to Phase 1.alpha.  Changing a value changes the realisation,
never the definitions in the judgment layer (judge.py), which follow the paper.
"""
from dataclasses import dataclass, field, replace
from typing import Dict, Tuple, List

Cell = Tuple[int, int]


@dataclass(frozen=True)
class Config:
    name: str = "default"
    steps: int = 300
    seed: int = 1
    grid: int = 7                                  # grid x grid cells, coordinates 0..grid-1
    shelter: Cell = (1, 1)
    depot: Cell = (2, 1)
    resources: Tuple[Cell, ...] = ((1, 2), (3, 1), (5, 5), (5, 2))
    res_max: int = 3
    res_init: int = 3
    eat_gain: int = 5                              # energy units per eaten resource unit
    regen_period: int = 3                          # a resource cell regains 1 unit every regen_period steps (if below max)
    rock_cells: Tuple[Cell, ...] = ((3, 2), (4, 3), (3, 4), (2, 3))
    rock_every: int = 7                            # rockfall schedule (deterministic, seeded)
    day_length: int = 12                           # first half mild (T=0), second half cold (T=1)
    snaps: Tuple[Tuple[int, int], ...] = ((60, 8), (150, 12), (240, 20))   # (start, length) of severe cold (T=2)
    ablate: Tuple[str, ...] = ()                   # E2: removed principle-related function groups (empty = none)
    snap_jitter: int = 0                           # E4: seed-dependent jitter of the severe-cold periods (0 = off)
    wind_every: int = 9                            # wind closes an open door (exogenous)
    # agents
    start_i: Cell = (2, 2)
    start_j: Cell = (3, 3)
    energy0: int = 16
    with_partner: bool = True
    with_drone: bool = True
    with_org: bool = True
    drone_base: Cell = (0, 0)
    drone_charge: int = 3
    drone_low: int = 6                             # drone rescues an ACS whose displayed energy <= drone_low
    drone_recharge: int = 10
    gift: int = 3                                  # energy units per gift (partner or drone)
    # biases (sec.5 def:bias_tendency): reference standard = (energy weight 2, exploration 0)
    bias_i: Tuple[int, int] = (2, 0)               # (energy weight w_E in 0..4, exploration w_X in 0..3)
    bias_j: Tuple[int, int] = (3, 1)
    learn_bias: bool = True
    # judgment-layer conventions
    window_L: int = 5                              # sec.6 finite observation window
    tau: int = 3                                   # sec.5 prediction steps
    tstab: Tuple[float, float, int] = (0.15, 0.4, 5)   # (s_SM lower bound, delta_max, W_T)
    pi_ref: int = 2                                # sec.3 Pi_ref (max attainable Pi in this toy: hpsl 3 - theta 1)
    hor_every: int = 10                            # Hor_f computed every hor_every steps
    hor_cap: int = 2
    recover_horizon: int = 20
    # external events (intervention in the *world*, recorded on the trajectory, not upsilon)
    forced_events: Tuple[Tuple[int, str], ...] = ()

    def with_(self, **kw):
        return replace(self, **kw)


SCENARIOS: Dict[str, Config] = {
    "default": Config(),
    "harsh": Config(name="harsh", snaps=((40, 30), (110, 40), (190, 60)), energy0=10,
                    resources=((5, 2), (5, 5)), regen_period=8),
    "alone": Config(name="alone", with_partner=False, with_drone=False, with_org=False),
    "no_drone": Config(name="no_drone", with_drone=False),
    "cooperative": Config(name="cooperative", bias_i=(2, 0), bias_j=(1, 0)),
    "explorer": Config(name="explorer", bias_i=(1, 3), bias_j=(4, 0)),
    "rocky": Config(name="rocky", rock_cells=((3, 1), (3, 2), (4, 3), (2, 3)), rock_every=5),
    "long": Config(name="long", steps=600, snaps=((60, 8), (150, 12), (240, 16), (330, 20), (450, 30))),
}


def parse_overrides(base: Config, items: List[str]) -> Config:
    """key=value overrides from the command line (ints, bools, tuples via python literal)."""
    import ast
    kw = {}
    for it in items:
        k, v = it.split("=", 1)
        try:
            kw[k] = ast.literal_eval(v)
        except Exception:
            kw[k] = v
    return base.with_(**kw)
