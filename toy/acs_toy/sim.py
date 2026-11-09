# -*- coding: utf-8 -*-
"""Building and running the joint system; Upsilon_adm (toy convention).  Not part of the paper."""
from .body import Body
from .mind import Mind
from .world import make_background, initial_world, joint_step


def build(cfg):
    names = ["i"] + (["j"] if cfg.with_partner else [])
    bodies = {n: Body(cfg) for n in names}
    minds = {"i": Mind(cfg, "i", "j" if cfg.with_partner else "", cfg.bias_i)}
    if cfg.with_partner:
        minds["j"] = Mind(cfg, "j", "i", cfg.bias_j)
    B = make_background(cfg)
    w0 = initial_world(cfg, bodies, minds)
    return bodies, minds, B, w0


def run(cfg, w0=None, t0=0, steps=None, bodies=None, minds=None, B=None, upsilon=None):
    """standard operation record of the joint system: list of (world_t, info_t) for t0..t0+steps-1,
    plus the final world.  `upsilon` = (name, act) applies an admissible external action at t0."""
    if bodies is None:
        bodies, minds, B, w = build(cfg)
    else:
        w = w0
    if upsilon is not None:
        w = apply_upsilon(cfg, bodies, w, *upsilon)
    steps = cfg.steps if steps is None else steps
    rec = []
    for t in range(t0, t0 + steps):
        nw, info = joint_step(cfg, bodies, minds, w, B[t], t)
        rec.append((w, info))
        w = nw
    return rec, w, (bodies, minds, B)


# ------------------------------------------------------------------ Upsilon_adm (fixed before any judgement)
UPSILON = ("inject", "mend", "carry_to_shelter")


def apply_upsilon(cfg, bodies, world, name, act):
    """effect rule of an admissible external action (toy convention; the paper gives no general operator)."""
    w = world.copy()
    x, M = w.agents[name]
    if x.integ == 0:                    # parts without the binding relation cannot be re-assembled
        return w
    if act == "inject":
        x = x._replace(energy=min(20, x.energy + 8))
    elif act == "mend":
        x = x._replace(integ=min(10, x.integ + 4))
    elif act == "carry_to_shelter":
        x = x._replace(px=cfg.shelter[0], py=cfg.shelter[1])
        w.door = 1
    w.agents[name] = (x, M)
    return w
