# -*- coding: utf-8 -*-
"""Team organisation with a depot (sec.8).  Not part of the paper.

Description by the describer (def:org_structural_form): the organisation O = the two
individuals as participants plus the depot ledger as a non-agent element.
  X_org   = (stock, n_act, ledger, x_i, M_i, x_j, M_j)       -- participants' states are part of the org
  U_org   = {hold, alloc_i, alloc_j}                          -- the ledger's allocation decision
  E_ext,org = (b, resources, door, drone)                    -- everything outside the organisation
  Pi_org(x_org) = min(stock - 1, n_act - 1)                   -- min-type over two coordinates
  E_org   = {eta_res}: some resource cell has a positive level
  M_org   = the ledger's record (allocations, last needs)
The organisational primitive functions: sensing = reading the members' displays at the depot,
identification = which member is in need, evaluation = need against stock, action = allocation.
This construction is a choice of description; it does not decide non-reducibility (def:org_acs).
"""
from collections import namedtuple

Ledger = namedtuple("Ledger", ("alloc_i", "alloc_j", "last", "need_i", "need_j"))
U_ORG = ("hold", "alloc_i", "alloc_j")


def initial_ledger():
    return Ledger(0, 0, "hold", 0, 0)


def org_sense(cfg, world):
    out = {}
    for k, (x, _) in world.agents.items():
        at = (x.px, x.py) == cfg.depot
        out[k] = (at, x.energy if at else -1, 1 if x.integ > 0 else 0)
    return out


def org_policy(cfg, world, sensed):
    if world.depot <= 0:
        return "hold"
    needy = [(e, k) for k, (at, e, alive) in sorted(sensed.items()) if at and alive and 0 <= e <= 8]
    if not needy:
        return "hold"
    e, k = min(needy)
    return "alloc_" + k


def org_operate(cfg, world, b, org_action=None):
    sensed = org_sense(cfg, world)
    u = org_action if org_action is not None else org_policy(cfg, world, sensed)
    led = world.org_state
    alloc_to = ""
    if u.startswith("alloc_") and world.depot > 0:
        alloc_to = u[len("alloc_"):]
        if alloc_to not in world.agents or world.agents[alloc_to][0].integ == 0:
            alloc_to = ""
    led2 = Ledger(min(9, led.alloc_i + (1 if alloc_to == "i" else 0)),
                  min(9, led.alloc_j + (1 if alloc_to == "j" else 0)), u,
                  min(3, sensed.get("i", (0, -1, 0))[1] // 3 if sensed.get("i", (0, -1, 0))[1] >= 0 else led.need_i),
                  min(3, sensed.get("j", (0, -1, 0))[1] // 3 if sensed.get("j", (0, -1, 0))[1] >= 0 else led.need_j))
    return led2, alloc_to, {"u_org": u, "sensed": sensed}


def n_act(world, bodies):
    return sum(1 for k, (x, _) in world.agents.items() if bodies[k].active_base(x))


def x_org(world, bodies):
    return (world.depot, n_act(world, bodies), world.org_state)


def Pi_org(xo):
    stock, na, _ = xo
    return min(stock - 1, na - 1)
