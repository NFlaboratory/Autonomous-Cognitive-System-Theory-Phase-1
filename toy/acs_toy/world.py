# -*- coding: utf-8 -*-
"""External side: background b_t (exogenous schedule), action-responsive components o_t,
the rescue drone (a non-ACS agent with a fixed rule), the team depot, and the joint
transition from which each individual's g_O is obtained.  Not part of the paper.

E_ext = E^bg x O (def:Eext_decomposition).
  b_t = Bg(T, rock_now, tremor, wind, regen)            -- does not respond to any action
  o_t = slots a in A_O: res:<cell>, door, depot, drone, gift:<name>, other:<name>
For individual i, the slot other:<j> holds the other ACS's (x_j, M_j); i's own (x_i, M_i)
is not part of i's environment.
"""
from collections import namedtuple
from typing import Dict, Tuple, Optional

Bg = namedtuple("Bg", ("T", "rock_now", "tremor", "wind", "regen"))
Drone = namedtuple("Drone", ("px", "py", "charge", "mode", "target", "timer"))   # mode: patrol/go/return/charge
BOT = None                                  # absent state of a slot (bottom_a)


def lcg(seed):
    s = (seed * 1103515245 + 12345) & 0x7FFFFFFF
    while True:
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        yield s


def make_background(cfg):
    """deterministic background sequence (b_t)_{t>=0} (def:env_realization: given exogenously)."""
    n = cfg.steps + cfg.tau + cfg.recover_horizon + 5
    r = lcg(cfg.seed)
    T = []
    snaps = list(cfg.snaps)
    if cfg.snap_jitter > 0:                      # seed-dependent shift of start (+-jitter) and length (+-2)
        rj = lcg(cfg.seed + 7919)
        snaps = [(max(0, s + next(rj) % (2 * cfg.snap_jitter + 1) - cfg.snap_jitter),
                  max(1, ln + next(rj) % 5 - 2)) for (s, ln) in cfg.snaps]
    for t in range(n):
        lvl = 0 if (t % cfg.day_length) < cfg.day_length // 2 else 1
        for (s, ln) in snaps:
            if s <= t < s + ln:
                lvl = 2
        T.append(lvl)
    rock = [frozenset() for _ in range(n)]
    cells = list(cfg.rock_cells)
    for t in range(3, n):
        if t % cfg.rock_every == 0 and cells:
            c = cells[next(r) % len(cells)]
            rock[t] = frozenset({c})
    wind = [1 if (t % cfg.wind_every == cfg.wind_every - 1) else 0 for t in range(n)]
    regen = [1 if (t % cfg.regen_period == 0) else 0 for t in range(n)]
    out = []
    for t in range(n):
        tremor = rock[t + 1] if t + 1 < n else frozenset()
        out.append(Bg(T[t], rock[t], tremor, wind[t], regen[t]))
    return out


class World:
    """global state of everything outside the individuals plus the individuals themselves."""

    def __init__(self, cfg, res, door, depot, drone, gifts, agents, org_state=None):
        self.cfg = cfg
        self.res = res              # dict cell -> level
        self.door = door            # 1 closed, 0 open
        self.depot = depot          # stock units
        self.drone = drone          # Drone or BOT
        self.gifts = gifts          # dict name -> energy received at the start of this step
        self.agents = agents        # dict name -> (x, M)
        self.org_state = org_state  # org ledger state (org.py) or None

    def copy(self):
        return World(self.cfg, dict(self.res), self.door, self.depot, self.drone, dict(self.gifts),
                     dict(self.agents), self.org_state)

    # ------------------------------------------------------------ views
    def o_view(self, name):
        """o for individual `name` (its environment's action-responsive part)."""
        others = tuple((k, v) for k, v in sorted(self.agents.items()) if k != name)
        return (tuple(sorted(self.res.items())), self.door, self.depot, self.drone,
                self.gifts.get(name, 0), others, self.org_state)

    def lam(self, body, name, x, b):
        from .body import Lam
        p = (x.px, x.py)
        rock_d = {}
        other = 0
        for d, c in body.neighbors(p):
            rock_d[d] = 1 if c in b.rock_now else 0
            if self.res.get(c, 0) > 0:
                other = 1
        adj = 0
        for k, (xo, _) in self.agents.items():
            if k != name and xo.integ > 0 and abs(xo.px - x.px) + abs(xo.py - x.py) <= 1:
                adj = 1
        return Lam(T=b.T, door=self.door if p == self.cfg.shelter else 0,
                   rock_cur=1 if p in b.rock_now else 0,
                   rock_N=rock_d["N"], rock_E=rock_d["E"], rock_S=rock_d["S"], rock_W=rock_d["W"],
                   res_cur=1 if self.res.get(p, 0) > 0 else 0, res_other=other,
                   gift=self.gifts.get(name, 0), partner_adj=adj)


def initial_world(cfg, bodies, minds):
    from .body import X
    res = {c: cfg.res_init for c in cfg.resources}
    drone = Drone(cfg.drone_base[0], cfg.drone_base[1], cfg.drone_charge, "patrol", "", 0) if cfg.with_drone else BOT
    agents = {}
    starts = {"i": cfg.start_i, "j": cfg.start_j}
    for name in minds:
        x0 = X(px=starts[name][0], py=starts[name][1], energy=cfg.energy0, integ=10, temp=6, hpsl=3,
               hsens=3, heff=3, hmem=3, carry=0, starve=0, alert=0, beacon=0, last_u=0)
        agents[name] = (x0, minds[name].initial_M())
    org = None
    if cfg.with_org and len(minds) >= 2:
        from .org import initial_ledger
        org = initial_ledger()
    return World(cfg, res, 1, 2 if cfg.with_org else 0, drone, {k: 0 for k in minds}, agents, org)


# ------------------------------------------------------------------ the drone (non-ACS agent, fixed rule)
PATROL = ((0, 0), (3, 0), (6, 0), (6, 3), (6, 6), (3, 6), (0, 6), (0, 3))


def drone_step(cfg, d: Drone, agents, t):
    """returns (new drone, delivery target name or '')."""
    if d is BOT:
        return BOT, ""
    if d.mode == "charge":
        if d.timer <= 1:
            return Drone(d.px, d.py, cfg.drone_charge, "patrol", "", 0), ""
        return d._replace(timer=d.timer - 1), ""
    # choose target: an individual whose physical display shows low energy (scanner reads x)
    tgt = ""
    best = None
    for k, (x, _) in sorted(agents.items()):
        if x.integ > 0 and x.energy <= cfg.drone_low:
            dist = abs(x.px - d.px) + abs(x.py - d.py)
            if best is None or dist < best:
                best, tgt = dist, k
    if d.charge > 0 and tgt:
        x = agents[tgt][0]
        if (x.px, x.py) == (d.px, d.py):
            nd = d._replace(charge=d.charge - 1, mode="go", target=tgt)
            if nd.charge == 0:
                nd = nd._replace(mode="return")
            return nd, tgt
        return _move(d, (x.px, x.py))._replace(mode="go", target=tgt), ""
    if d.charge == 0 or d.mode == "return":
        if (d.px, d.py) == cfg.drone_base:
            return Drone(d.px, d.py, 0, "charge", "", cfg.drone_recharge), ""
        return _move(d, cfg.drone_base)._replace(mode="return"), ""
    # patrol
    k = (t // 2) % len(PATROL)
    return _move(d, PATROL[k])._replace(mode="patrol", target=""), ""


def _move(d, goal):
    dx = (goal[0] > d.px) - (goal[0] < d.px)
    dy = 0 if dx else (goal[1] > d.py) - (goal[1] < d.py)
    return d._replace(px=d.px + dx, py=d.py + dy)


# ------------------------------------------------------------------ the joint transition
def joint_step(cfg, bodies, minds, world: World, b, t, actions: Optional[Dict[str, str]] = None,
               org_action: Optional[str] = None):
    """one step of the whole system.  If `actions` is given, those individuals use the given
    effective action (used to evaluate g_O from one individual's viewpoint); otherwise every
    individual's action is generated by its own mechanism from (M, I).
    Returns (new_world, info) where info holds the per-individual step records."""
    from .body import Lam
    info = {}
    eff = {}
    acts = {}
    lams = {}
    for name, (x, M) in sorted(world.agents.items()):
        body = bodies[name]
        lam = world.lam(body, name, x, b)
        lams[name] = lam
        e = (b, world.o_view(name))
        if actions is not None and name in actions:
            u = actions[name]
            rec = None
        else:
            rec = minds[name].operate(M, x, e, lam)     # standard step: I, r, v, u from (M, I)
            u = rec["u"]
        acts[name] = u
        eff[name] = body.effect(x, u, lam)
        info[name] = {"lam": lam, "e": e, "u": u, "rec": rec}
    # organisation (team ledger) acts on the depot
    new_org, alloc_to, org_rec = world.org_state, "", None
    if world.org_state is not None:
        from .org import org_operate
        new_org, alloc_to, org_rec = org_operate(cfg, world, b, org_action)
    # drone
    new_drone, deliver_to = drone_step(cfg, world.drone, world.agents, t)
    # resources
    res = dict(world.res)
    for name, (x, _) in world.agents.items():
        p = (x.px, x.py)
        if eff[name] in ("eat_cell", "collect") and res.get(p, 0) > 0:
            res[p] -= 1
    if b.regen:
        for c in res:
            if res[c] < cfg.res_max:
                res[c] += 1
    # door
    door = world.door
    if any(eff[name] == "open_door" for name in world.agents):   # one door operation per step (toy rule)
        door = 1 - door
    if b.wind and door == 1:
        door = 0
    # depot and gifts for the next step
    depot = world.depot
    gifts = {k: 0 for k in world.agents}
    for name, (x, _) in world.agents.items():
        if eff[name] == "deposit":
            depot = min(10, depot + 1)
        if eff[name] == "give":
            for k, (xo, _) in world.agents.items():
                if k != name and xo.integ > 0 and abs(xo.px - x.px) + abs(xo.py - x.py) <= 1:
                    gifts[k] += cfg.gift
                    break
    if alloc_to and depot > 0:
        depot -= 1
        gifts[alloc_to] = gifts.get(alloc_to, 0) + cfg.gift
    if deliver_to:
        gifts[deliver_to] = gifts.get(deliver_to, 0) + cfg.gift
    # individuals
    agents = {}
    for name, (x, M) in world.agents.items():
        body = bodies[name]
        x1 = body.f(x, acts[name], lams[name])
        M1 = minds[name].Update(M, x, info[name]["e"])
        agents[name] = (x1, M1)
    nw = World(cfg, res, door, depot, new_drone, gifts, agents, new_org)
    info["_org"] = org_rec
    info["_deliver"] = deliver_to
    info["_alloc"] = alloc_to
    return nw, info


def g_O(cfg, bodies, minds, world: World, name, u, b, t):
    """g_O(o_t, x_t, u, b_t) from individual `name`'s viewpoint: the next o of `name` when
    `name` takes effective action u and everything else follows its own rule."""
    nw, _ = joint_step(cfg, bodies, minds, world, b, t, actions={name: u})
    return nw.o_view(name)
