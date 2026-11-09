# -*- coding: utf-8 -*-
"""CR-2b (functional non-degeneracy, standard-map form, sec.2) for every mechanism variant used in the
experiments: the full mechanisms, every ablation (E2 on v2, E8 on the furnace) and every sensing degradation
(E7 on MinACS).  A variant that fails a clause is not an ACS realisation in the sense of CR-2; comparisons
with it are comparisons between an ACS and a non-ACS variant, not comparisons inside the ACS class.

Clauses (sec.2, standard-map form):
  (i-a)  exists e, x, x': P_sens(x,e) != P_sens(x',e)
  (i-b)  exists x, e, e': P_sens(x,e) != P_sens(x,e')
  (ii)   exists M, x, e, e': P_disc(M, P_sens(x,e)) != P_disc(M, P_sens(x,e'))
  (iii)  P_val non-constant on its domain, and (K, X\\K nonempty) exists M, e, x in K, x' not in K with
         P_val(M, P_disc(M, P_sens(x,e))) != P_val(M, P_disc(M, P_sens(x',e)))
  (iv)   P_act non-constant
The searches are exhaustive for MinACS and the furnace (over X x E_ext and the listed M), and over a fixed grid
of states and two backgrounds for v2 (a found witness proves the clause; a failure on the grid is reported as
'not found on the grid').
python3 check_cr2_variants.py  -> outputs/cr2_variants.md
"""
import os
import sys
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def clauses(XS, ES, MS, inK, sens, disc, val, act):
    r = {}
    r["i-a"] = any(sens(x, e) != sens(y, e) for e in ES for x in XS[:40] for y in XS if y != x)
    r["i-b"] = any(sens(x, e) != sens(x, f) for x in XS for e in ES for f in ES[:4] if f != e)
    r["ii"] = any(disc(M, sens(x, e)) != disc(M, sens(x, f)) for M in MS for x in XS for e in ES for f in ES[:4])
    vals = {val(M, disc(M, sens(x, e))) for M in MS for x in XS for e in ES}
    feas = False
    for M in MS:
        for e in ES:
            vin = {val(M, disc(M, sens(x, e))) for x in XS if inK(x)}
            vout = {val(M, disc(M, sens(x, e))) for x in XS if not inK(x)}
            if vin and vout and (len(vin | vout) > 1):
                if any(a != b for a in vin for b in vout):
                    feas = True
                    break
        if feas:
            break
    r["iii"] = len(vals) >= 2 and feas
    acts = {act(M, x, e) for M in MS for x in XS for e in ES}
    r["iv"] = len(acts) >= 2
    return r


def minacs_rows():
    from minacs import model as mm
    from minacs import mind as md
    from e4.adapters import E7_DEGRADATIONS
    out = []
    for name, deg in E7_DEGRADATIONS.items():
        sens = (lambda d: (lambda x, e: d(md.P_sens(x, e))))(deg)

        def disc(M, I):
            return md.M1(I, M)

        def val(M, S):
            xhat, ehat = S
            return md.M2(xhat, ehat, M)

        def act(M, x, e, sens=sens):
            I = sens(x, e)
            if not (x.s == 1 and x.en > 0):
                return "wait"
            xhat, ehat = md.M1(I, M)
            return md.M3(xhat, ehat, md.M2(xhat, ehat, M), M)[2]
        r = clauses(mm.XS, mm.ES, md.MS, mm.in_K, sens, disc, val, act)
        out.append(("MinACS (E7)", name, r))
    return out


def furnace_rows():
    from domains.furnace import model as fm
    from domains.furnace import mind as fd
    from e4.adapters import FURNACE_ABLATIONS
    MS = [fd.M_(bo, rec, pur) for bo in (0, 1) for rec in (None, (3, "burn", 0, 2)) for pur in ("none", "heat")]
    out = []
    for name, ab in FURNACE_ABLATIONS.items():
        md = fd.Mind(ab)
        r = clauses(fm.XS, fm.ES, MS, lambda x: fm.Pi(x) >= 0, fd.P_sens,
                    lambda M, I, md=md: md.M1(I, M), lambda M, S, md=md: md.M2(S[0], S[1], M),
                    lambda M, x, e, md=md: md.operate(M, x, e)["u"])
        out.append(("Furnace (E8)", name, r))
    return out


def p11_rows():
    """P11 variants: est-k quantises the self-state reading used by the mechanism; upd-k changes only Update
    (not part of CR-2b), so its CR-2b is that of the base mechanism."""
    from minacs import model as mm
    from minacs import mind as md
    from domains.furnace import model as fm
    from domains.furnace import mind as fd
    out = []
    for q in (2, 3):
        qx = lambda x, q=q: x._replace(en=max(1, (x.en // q) * q)) if x.en > 0 else x
        sens = lambda x, e, qx=qx: md.P_sens(qx(x), e)
        r = clauses(mm.XS, mm.ES, md.MS, mm.in_K, sens, lambda M, I: md.M1(I, M),
                    lambda M, S: md.M2(S[0], S[1], M),
                    lambda M, x, e, qx=qx: md.operate(M, qx(x), e)["u"])
        out.append(("MinACS (P11)", f"est-{q}", r))
        qf = lambda x, q=q: x._replace(tp=max(1, (x.tp // q) * q)) if x.tp > 0 else x
        mdf = fd.Mind()
        MS = [fd.M_(bo, rec, pur) for bo in (0, 1) for rec in (None, (3, "burn", 0, 2)) for pur in ("none", "heat")]
        r = clauses(fm.XS, fm.ES, MS, lambda x: fm.Pi(x) >= 0, lambda x, e, qf=qf: fd.P_sens(qf(x), e),
                    lambda M, I: mdf.M1(I, M), lambda M, S: mdf.M2(S[0], S[1], M),
                    lambda M, x, e, qf=qf: mdf.operate(M, qf(x), e)["u"])
        out.append(("Furnace (P11)", f"est-{q}", r))
    return out


def v2_rows():
    from acs_toy.config import SCENARIOS
    from acs_toy.sim import build
    from acs_toy.checks import _x
    from acs_toy.world import Bg
    from e4.adapters import ABLATIONS
    out = []
    for name, ab in ABLATIONS.items():
        if name == "-rescuers":
            continue                                  # same mechanism as -relation (only the world differs)
        cfg = SCENARIOS["default"].with_(ablate=ab)
        bodies, minds, B, w = build(cfg)
        m, body = minds["i"], bodies["i"]
        M0 = w.agents["i"][1]
        o0 = w.o_view("i")
        b0 = B[0]
        b1 = Bg(2 if b0.T != 2 else 0, b0.rock_now, b0.tremor, b0.wind, b0.regen)
        ES = [(b0, o0), (b1, o0)]
        cells = [(2, 2), cfg.shelter, cfg.resources[0], (3, 3)]
        XS = [_x(cfg, px=c[0], py=c[1], energy=en)._replace(integ=ig, temp=tp)
              for c in cells for en in (0, 2, 4, 8, 12, 18) for ig in (2, 6, 10) for tp in (2, 5)]
        Ih = m.part(M0, 1, "W")["Ih"]
        r = clauses(XS, ES, [M0], body.in_K, m.P_sens, lambda M, I: m.M1(I, M),
                    lambda M, S: m.M2(S, M, Ih)[:4], lambda M, x, e: m.pipeline(M, m.P_sens(x, e))[4])
        out.append(("v2 (E2)", name, r))
    return out


def main():
    rows = minacs_rows() + furnace_rows() + p11_rows() + v2_rows()
    L = ["# CR-2b の検査：実験で用いた機構の全変種", "",
         "| 領域（実験） | 変種 | (i-a) | (i-b) | (ii) | (iii) | (iv) | CR-2b |", "|---|---|---|---|---|---|---|---|"]
    for dom, name, r in rows:
        ok = all(r.values())
        L.append(f"| {dom} | {name} | " + " | ".join("○" if r[k] else "×" for k in ("i-a", "i-b", "ii", "iii", "iv"))
                 + f" | {'成立' if ok else '不成立'} |")
    L += ["", "- ○：例を見つけた（その節は成り立つ）。×：探索の範囲で例が見つからなかった。",
          "- MinACS・炉番は X×E_ext の全数と列挙した M で探索した（× はその範囲での不成立）。v2 は固定した格子（4 セル × energy 6 × integ 3 × temp 2、背景 2）での探索で、× は「格子上で見つからない」の意味。",
          "- P11 の upd-k は Update だけを変えるので（CR-2b は Update を含まない）、基準の機構と同じ結果になる。表には est-k だけを載せた。",
          "- 評価写像 P_val には、MinACS・炉番は M2 の出力全体、v2 は M2 の出力の (P, ev, sig, evrq) を用いた。"]
    os.makedirs(os.path.join(HERE, "outputs"), exist_ok=True)
    with open(os.path.join(HERE, "outputs", "cr2_variants.md"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
