# -*- coding: utf-8 -*-
"""Self-contained HTML viewer of one judged run (reading aid; not part of the paper)."""
import json

KEEP = ["t", "px", "py", "energy", "integ", "temp", "hpsl", "hsens", "heff", "hmem", "carry", "u", "Pi", "blk",
        "B1", "B2", "WF", "FT", "Col", "T_P", "SM", "EU", "FR", "Crit", "mu_eff", "e_in_Ereq", "Viab_core", "Hor",
        "P", "mode", "style", "Pur", "Req", "sig", "fast", "r_local", "action_class", "zones", "Recover",
        "TSTAB", "beta_val", "d_eff", "tau_hat", "gift_lam", "chi_EI", "EC", "U_rob_n"]


def _j(v):
    if isinstance(v, (tuple, list, set, frozenset)):
        return repr(tuple(v))
    return v


def build_html(cfg, out, org, rec, events, title, B=None):
    names = sorted(out)
    data = {"cfg": {"grid": cfg.grid, "shelter": cfg.shelter, "depot": cfg.depot, "resources": cfg.resources,
                    "rocks": cfg.rock_cells, "steps": len(rec), "name": cfg.name},
            "agents": {n: [{k: _j(r.get(k, "")) for k in KEEP} for r in out[n]] for n in names},
            "world": [], "org": [{k: _j(v) for k, v in o.items()} for o in org],
            "events": [{"t": t, "who": w, "kind": k, "txt": s} for (t, w, k, s) in events]}
    for k, (w, info) in enumerate(rec):
        b = B[k] if B is not None else None
        data["world"].append({"T": (b.T if b is not None else None),
                              "rock": ([list(c) for c in b.rock_now] if b is not None else []),"res": {f"{c[0]},{c[1]}": lv for c, lv in w.res.items()}, "door": w.door,
                              "depot": w.depot,
                              "drone": ([w.drone.px, w.drone.py, w.drone.mode] if w.drone is not None else None)})
    payload = json.dumps(data, ensure_ascii=False, default=str)
    return TEMPLATE.replace("__TITLE__", title).replace("__DATA__", payload)


TEMPLATE = r"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#f7f6f2;--fg:#1d1d1b;--mut:#6b6a66;--card:#fff;--line:#d9d7cf;--i:#2f6db5;--j:#c0582b;--ok:#3d8b4f;
--z1:#e9c46a;--z2:#f4a261;--z3:#b56576;--z4:#7b2cbf;--z5:#222;--grid:#ecebe6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#17171a;--fg:#ecebe6;--mut:#a3a29c;--card:#202024;--line:#3a3a40;--grid:#2a2a30;--z5:#ddd}}
:root[data-theme="dark"]{--bg:#17171a;--fg:#ecebe6;--mut:#a3a29c;--card:#202024;--line:#3a3a40;--grid:#2a2a30;--z5:#ddd}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,"Hiragino Sans","Noto Sans JP",sans-serif}
main{max-width:1180px;margin:0 auto;padding:16px}
h1{font-size:18px;margin:4px 0 2px}.sub{color:var(--mut);font-size:12px;margin-bottom:12px}
.row{display:flex;gap:12px;flex-wrap:wrap}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
#mapc{flex:0 1 auto;max-width:100%;box-sizing:border-box}#side{flex:1 1 380px;min-width:280px}
canvas{display:block;max-width:100%}
.ctl{display:flex;gap:8px;align-items:center;margin:10px 0;flex-wrap:wrap}
input[type=range]{flex:1 1 300px}button{background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:4px 10px;cursor:pointer}
table{border-collapse:collapse;width:100%;font-size:12.5px}td{padding:2px 6px;border-bottom:1px solid var(--line);vertical-align:top}
td:first-child{color:var(--mut);white-space:nowrap;width:120px}
.tag{display:inline-block;padding:0 6px;border-radius:4px;font-size:12px;margin-right:3px;border:1px solid var(--line)}
#ev{max-height:260px;overflow:auto;font-size:12.5px}#ev div{padding:2px 0;border-bottom:1px dotted var(--line);cursor:pointer}
#ev div.cur{background:color-mix(in srgb,var(--z1) 30%,transparent)}
.legend span{margin-right:10px;font-size:12px}.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:3px;vertical-align:-1px}
.note{color:var(--mut);font-size:12px;max-width:350px;overflow-wrap:anywhere}
</style></head><body><main>
<h1>__TITLE__</h1>
<div class="sub">判定層（judge.py）で計算した量の表示。表示は記述者の読解補助であり、新しい定義を導入しない。</div>
<div class="ctl"><button id="play">再生</button><button id="prev">◀</button><button id="next">▶</button>
<input id="slider" type="range" min="0" value="0"><span id="tlab"></span>
<select id="who"></select></div>
<div class="row"><div class="card" id="mapc"><canvas id="map" width="350" height="350"></canvas>
<div class="note" style="margin-top:6px">■ 避難所（扉:実線=閉）／◆ 共有貯蔵庫／● 資源（数字=量）／× 落石セル（赤=落石中）／▲ ドローン</div></div>
<div class="card" id="side"><table id="tab"></table></div></div>
<div class="card" style="margin-top:12px"><canvas id="chart" width="1140" height="300"></canvas>
<div class="legend" id="leg"></div></div>
<div class="card" style="margin-top:12px"><b>出来事（判定量の変化）</b> <select id="kind"><option value="">すべて</option></select><div id="ev"></div></div>
</main>
<script>
const D=__DATA__;const C=D.cfg;const names=Object.keys(D.agents);
const col={i:getComputedStyle(document.documentElement).getPropertyValue('--i'),j:getComputedStyle(document.documentElement).getPropertyValue('--j')};
const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
let t=0,timer=null;const S=document.getElementById('slider');S.max=C.steps-1;
const W=document.getElementById('who');names.forEach(n=>{const o=document.createElement('option');o.value=n;o.textContent='個体 '+n;W.appendChild(o)});
function key(c){return c[0]+','+c[1]}
function drawMap(){const cv=document.getElementById('map'),g=cv.getContext('2d');const n=C.grid,s=cv.width/n;
g.clearRect(0,0,cv.width,cv.height);g.fillStyle=css('--card');g.fillRect(0,0,cv.width,cv.height);
g.strokeStyle=css('--grid');for(let k=0;k<=n;k++){g.beginPath();g.moveTo(k*s,0);g.lineTo(k*s,n*s);g.stroke();g.beginPath();g.moveTo(0,k*s);g.lineTo(n*s,k*s);g.stroke()}
const w=D.world[t];const rockNow=new Set();
const rn=new Set((w.rock||[]).map(key));
C.rocks.forEach(c=>{g.strokeStyle=rn.has(key(c))?'#d62828':css('--mut');g.lineWidth=1.5;g.beginPath();g.moveTo(c[0]*s+8,c[1]*s+8);g.lineTo(c[0]*s+s-8,c[1]*s+s-8);g.moveTo(c[0]*s+s-8,c[1]*s+8);g.lineTo(c[0]*s+8,c[1]*s+s-8);g.stroke()});
const sh=C.shelter;g.lineWidth=w.door==1?3:1;g.strokeStyle=css('--fg');g.setLineDash(w.door==1?[]:[4,3]);g.strokeRect(sh[0]*s+4,sh[1]*s+4,s-8,s-8);g.setLineDash([]);g.lineWidth=1;
const dp=C.depot;g.fillStyle=css('--mut');g.beginPath();g.moveTo(dp[0]*s+s/2,dp[1]*s+6);g.lineTo(dp[0]*s+s-6,dp[1]*s+s/2);g.lineTo(dp[0]*s+s/2,dp[1]*s+s-6);g.lineTo(dp[0]*s+6,dp[1]*s+s/2);g.fill();
g.fillStyle=css('--fg');g.font='11px system-ui';g.fillText(w.depot,dp[0]*s+s/2-3,dp[1]*s+s/2+4);
C.resources.forEach(c=>{const lv=w.res[key(c)];g.fillStyle=lv>0?css('--ok'):css('--line');g.beginPath();g.arc(c[0]*s+s/2,c[1]*s+s/2,s/5,0,7);g.fill();g.fillStyle=css('--fg');g.fillText(lv,c[0]*s+s/2+s/5,c[1]*s+s/2-s/5)});
if(w.drone){const d=w.drone;g.fillStyle=css('--mut');g.beginPath();g.moveTo(d[0]*s+s/2,d[1]*s+8);g.lineTo(d[0]*s+s-10,d[1]*s+s-10);g.lineTo(d[0]*s+10,d[1]*s+s-10);g.fill()}
names.forEach((n,k)=>{const r=D.agents[n][t];const off=(k-0.5)*s*0.22;g.fillStyle=r.Col?css('--mut'):col[n];g.beginPath();g.arc(r.px*s+s/2+off,r.py*s+s/2+off,s/6,0,7);g.fill();g.fillStyle='#fff';g.font='bold 11px system-ui';g.fillText(n,r.px*s+s/2+off-3,r.py*s+s/2+off+4)})}
function fmt(v){if(v===true)return '真';if(v===false)return '偽';if(v===''||v===null||v===undefined)return '—';return String(v)}
function drawTab(){const n=W.value,r=D.agents[n][t];const rows=[
['時刻 t',r.t],['位置',`(${r.px},${r.py})`],['energy / integ / temp',`${r.energy} / ${r.integ} / ${r.temp}`],['健全度 psl,sens,eff,mem',`${r.hpsl},${r.hsens},${r.heff},${r.hmem}`],
['実効行動 u_t',r.u],['Π(x_t)・x∈K',`${r.Pi}・${fmt(r.Pi>=0)}`],['A_t 閉塞',fmt(r.blk)+(r.blk?(r.B1?'（B1）':(r.B2?'（B2）':'')):'')],
['SM / EU / FR（T_P上）',`${fmt(r.SM)} / ${fmt(r.EU)} / ${fmt(r.FR)}`],['Crit⁽¹⁾(x_t)',r.Crit],['μ_eff',r.mu_eff],['e_t∈E_req(x_t)',fmt(r.e_in_Ereq)],
['Viab_f(K)・Hor',`${fmt(r.Viab_core)}・${fmt(r.Hor)}`],['WF / FT / Col',`${r.WF} / ${r.FT} / ${r.Col}`],['状態帯',r.zones],['Recover(inject,mend,carry)',r.Recover],
['Priority / mode / style',`${fmt(r.P)} / ${fmt(r.mode)} / ${fmt(r.style)}`],['要請 sig',r.sig],['目的 Pur',r.Pur],['行為区分',r.action_class],['自動化 / PSL-4',`${fmt(r.fast)} / ${fmt(r.r_local)}`],
['T-STAB',fmt(r.TSTAB)],['偏向 β(val)・d_eff・τ̂',`${r.beta_val}・${r.d_eff}・${r.tau_hat}`],['gift（e_t の贈与成分）',r.gift_lam]];
document.getElementById('tab').innerHTML=rows.map(a=>`<tr><td>${a[0]}</td><td>${fmt(a[1])}</td></tr>`).join('');
const Tw=D.world[t].T;document.getElementById('tlab').textContent='t = '+t+' / '+(C.steps-1)+(Tw===null?'':'　T='+Tw+(Tw==2?'（厳寒）':Tw==1?'（夜）':'（昼）'))}
const series=[['energy','--i',20],['integ','--ok',10],['temp','--z2',8]];
function drawChart(){const cv=document.getElementById('chart'),g=cv.getContext('2d');const n=W.value,R=D.agents[n];const L=40,T0=10,H=200,Wd=cv.width-L-10;
g.clearRect(0,0,cv.width,cv.height);const x=k=>L+Wd*k/(R.length-1);
const zc={Z1:'--z1',Z2:'--z2',Z3:'--z3',Z4:'--z4',Z5:'--z5'};const bands=['Z1','Z2','Z3','Z4','Z5'];
bands.forEach((z,b)=>{for(let k=0;k<R.length;k++){if(String(R[k].zones).split('+').includes(z)){g.fillStyle=css(zc[z]);g.fillRect(x(k),T0+H+14+b*12,Math.max(1,Wd/R.length),10)}}g.fillStyle=css('--mut');g.font='10px system-ui';g.fillText(z,6,T0+H+23+b*12)});
g.strokeStyle=css('--line');g.strokeRect(L,T0,Wd,H);
series.forEach(([f,c,mx])=>{g.strokeStyle=f=='energy'?col[n]:css(c);g.lineWidth=1.5;g.beginPath();R.forEach((r,k)=>{const y=T0+H-H*Math.min(1,r[f]/mx);k?g.lineTo(x(k),y):g.moveTo(x(k),y)});g.stroke()});
g.fillStyle=css('--fg');R.forEach((r,k)=>{if(r.blk&&!r.Col){g.fillRect(x(k),T0+H-4,Math.max(1,Wd/R.length),4)}});
g.strokeStyle=css('--fg');g.setLineDash([3,3]);g.beginPath();g.moveTo(x(t),T0);g.lineTo(x(t),cv.height);g.stroke();g.setLineDash([]);
document.getElementById('leg').innerHTML=`<span><i class="sw" style="background:${col[n]}"></i>energy (/20)</span><span><i class="sw" style="background:${css('--ok')}"></i>integ (/10)</span><span><i class="sw" style="background:${css('--z2')}"></i>temp (/8)</span><span><i class="sw" style="background:${css('--fg')}"></i>下端の黒＝閉塞 A_t=∅</span><span>帯：Z1〜Z5（状態空間の分割ではない）</span>`}
const KS=document.getElementById('kind');[...new Set(D.events.map(e=>e.kind))].forEach(k=>{const o=document.createElement('option');o.value=k;o.textContent=k;KS.appendChild(o)});
KS.onchange=()=>{document.getElementById('ev').dataset.init='';drawEv()};
function drawEv(){const box=document.getElementById('ev');if(!box.dataset.init){const kf=KS.value;box.innerHTML=D.events.filter(e=>!kf||e.kind==kf).map((e,k)=>`<div data-t="${e.t}">t=${e.t} [${e.who}] <b>${e.kind}</b>: ${e.txt}</div>`).join('');box.dataset.init=1;
box.querySelectorAll('div').forEach(d=>d.onclick=()=>{set(+d.dataset.t)})}
box.querySelectorAll('div').forEach(d=>d.classList.toggle('cur',+d.dataset.t==t))}
function set(v){t=Math.max(0,Math.min(C.steps-1,v));S.value=t;drawMap();drawTab();drawChart();drawEv()}
S.oninput=()=>set(+S.value);document.getElementById('prev').onclick=()=>set(t-1);document.getElementById('next').onclick=()=>set(t+1);
W.onchange=()=>set(t);
document.getElementById('play').onclick=function(){if(timer){clearInterval(timer);timer=null;this.textContent='再生'}else{timer=setInterval(()=>{if(t>=C.steps-1){clearInterval(timer);timer=null}else set(t+1)},120);this.textContent='停止'}};
document.getElementById('chart').onclick=e=>{const cv=e.target,rc=cv.getBoundingClientRect();const k=Math.round(((e.clientX-rc.left)*cv.width/rc.width-40)/(cv.width-50)*(C.steps-1));set(k)};
set(0);
</script></body></html>
"""
