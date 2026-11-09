# -*- coding: utf-8 -*-
"""Timeline extraction from the judged record (describer's reading aid, not part of the paper).

Each event line cites the judged quantities it is read from.  No event is a new definition:
the narrative only reports changes of values already computed in judge.py.
"""


def gift_sources(rec, names):
    """for each (t+1, receiver): list of sources of the gift arriving at t+1 (partner / drone / org)."""
    src = {}
    for t, (w, info) in enumerate(rec):
        for n in names:
            x = w.agents[n][0]
            if info[n]["u"] == "give" and x.integ > 0 and x.heff > 0 and x.energy >= 4 and x.hpsl > 0:
                for m in names:
                    if m == n:
                        continue
                    xo = w.agents[m][0]
                    if xo.integ > 0 and abs(xo.px - x.px) + abs(xo.py - x.py) <= 1:
                        src.setdefault((t + 1, m), []).append(f"partner:{n}")
                        break
        if info.get("_deliver"):
            src.setdefault((t + 1, info["_deliver"]), []).append("drone")
        if info.get("_alloc") and w.depot > 0:
            src.setdefault((t + 1, info["_alloc"]), []).append("org")
    return src


def timeline(cfg, out, org, rec):
    names = sorted(out)
    src = gift_sources(rec, names)
    ev = []
    for n in names:
        rows = out[n]
        prev = None
        for r in rows:
            t = r["t"]
            s = src.get((t, n))
            if s and r["Col"] == 0:
                ev.append((t, n, "rescue_via_e", f"gift arrives (lam.gift={r.get('gift_lam', '')}) from {'+'.join(s)}; "
                                                 f"energy {r['energy']}, A size {len(r['A'])}"))
            if prev is not None:
                if r["zones"] != prev["zones"]:
                    ev.append((t, n, "zone", f"{prev['zones']} -> {r['zones']}"))
                if r["inK"] != prev["inK"] and r["T_P"]:
                    ev.append((t, n, "SM", ("x leaves K (SM fails)" if not r["inK"] else "x re-enters K (SM holds)")
                               + f"; Pi={r['Pi']}, V^-={r['V_minus']}"))
                if r["blk"] and not prev["blk"] and r["Col"] == 0:
                    kind = "B1 (a critical factor absent: " + ",".join(n2 for n2 in r["Crit"] if r[f"eta_{n2}"] == 0) + ")" \
                        if r["B1"] else ("B2 (on D_FR: FR fails)" if r["B2"] else "neither B1 nor B2 (not on T_P)")
                    ev.append((t, n, "blockage", f"A_t = empty, {kind}"))
                if r["blk_recovered"]:
                    ev.append((t, n, "blockage_end", f"A_t nonempty again ({r['blk_recovered']}); |A|={len(r['A'])}"))
                if r["FT"] and not prev["FT"]:
                    ev.append((t, n, "FT", "functional termination: FTS_t=1 (FT-1 and FT-2), T_P ends"))
                if r["CS"] and not prev["CS"]:
                    ev.append((t, n, "CS/Col", "structural termination CS_t=1 ((SC-1),(SC-2)); Col_t=1"))
                if r["WF"] and r["Pur"] != "undef" and prev["Pur"] != "undef":
                    newp = set(r["Pur"]) - set(prev["Pur"])
                    for p in sorted(newp, key=repr):
                        ev.append((t, n, "purpose", f"purpose formed {p} (Req={r['Req']}, P={r['P']})"))
                    if r["mode"] != prev["mode"]:
                        ev.append((t, n, "mode", f"{prev['mode']} -> {r['mode']} (P={r['P']}, style {r['style']})"))
                if r.get("psl4_override") is True:
                    ev.append((t, n, "PSL-4", f"local protective response {r['r_local']} replaced {r['u_M3']}"))
                if r.get("fast") is True and prev.get("fast") is not True:
                    ev.append((t, n, "automaticity", f"routine response {r['u']} without comparison (mode 3C)"))
                if r["beta_val"] != prev["beta_val"]:
                    ev.append((t, n, "bias", f"val-side bias readout {prev['beta_val']} -> {r['beta_val']} (wE learned)"))
                if r["T_P"] and r["TSTAB"] is not prev["TSTAB"] and prev["TSTAB"] != "undef":
                    ev.append((t, n, "T-STAB", f"T-STAB {prev['TSTAB']} -> {r['TSTAB']}"))
                if r["Recover"] not in ("undef", "skip") and prev["Recover"] in ("undef", "skip", None) and r["Col"] == 0:
                    ev.append((t, n, "Recover", f"Recover over Upsilon_adm (inject,mend,carry) = {r['Recover']}"))
            prev = r
    prevo = None
    for o in org:
        if prevo is not None:
            if o["org_ACS"] != prevo["org_ACS"]:
                ev.append((o["t"], "org", "org_ACS", f"organisational ACS {'established' if o['org_ACS'] else 'lost'} (n_org={o['n_org']})"))
            if o["blk_org"] != prevo["blk_org"]:
                ev.append((o["t"], "org", "org_blockage", f"A(Sigma_org) {'= empty' if o['blk_org'] else 'nonempty'}; Pi_org={o['Pi_org']}"))
        if o["u_org"] not in ("", "hold") and o["n_org"] >= 1:
            ev.append((o["t"], "org", "org_action", f"{o['u_org']} (stock {o['stock']})"))
        prevo = o
    ev.sort(key=lambda e: (e[0], e[1]))
    return ev, src
