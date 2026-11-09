# 可行性核の包含（C-3）と有限段の一致（C-2）を、ランダムな有限系の総当たりで確かめる。証明の代わりではない。
# 実行：python3 tools/kernel_inclusion_check.py（数分）
import random, itertools
def gfp(cands, ok):
    S=set(cands)
    while True:
        T={x for x in S if ok(x,S)}
        if T==S: return S
        S=T
def run(seed):
    r=random.Random(seed)
    nX=r.randint(2,6); nU=r.randint(1,3); nE=r.randint(1,3)
    X=range(nX); U=range(nU); E=range(nE)
    f={(x,u,e):r.randrange(nX) for x in X for u in U for e in E}
    K={x for x in X if r.random()<0.7}
    nEta=r.randint(1,2)
    eta=[{(x,e):int(r.random()<0.7) for x in X for e in E} for _ in range(nEta)]
    Ereq={x:{e for e in E if all(h[(x,e)] for h in eta)} for x in X}
    Dreq={x for x in X if Ereq[x]}
    Kreq=K&Dreq
    V=gfp(Kreq, lambda x,S: any(all(f[(x,u,e)] in S for e in Ereq[x]) for u in U))
    R=gfp(K, lambda x,S: any(all(f[(x,u,e)] in S for e in E) for u in U))
    O=gfp(K, lambda x,S: any(any(f[(x,u,e)] in S for e in E) for u in U))
    return V,R,O,Dreq
c=dict(V_in_O=0,R_in_V=0,R_in_V_given=0,given=0,R_not_in_V=0,R_not_in_V_given=0)
N=200000
for s in range(N):
    V,R,O,D=run(s)
    c['V_in_O']+= V<=O
    c['R_in_V']+= R<=V
    if R<=D:
        c['given']+=1; c['R_in_V_given']+= R<=V
        if not R<=V: c['R_not_in_V_given']+=1
    if not R<=V: c['R_not_in_V']+=1
print(N,c)

def stages(seed):
    r=random.Random(seed)
    nX=r.randint(2,7); nU=r.randint(1,3); nE=r.randint(1,3)
    X=range(nX); U=range(nU); E=range(nE)
    f={(x,u,e):r.randrange(nX) for x in X for u in U for e in E}
    K={x for x in X if r.random()<0.7}
    eta=[{(x,e):int(r.random()<0.7) for x in X for e in E} for _ in range(r.randint(1,2))]
    Ereq={x:{e for e in E if all(h[(x,e)] for h in eta)} for x in X}
    Kreq={x for x in K if Ereq[x]}
    V=gfp(Kreq, lambda x,S: any(all(f[(x,u,e)] in S for e in Ereq[x]) for u in U))
    S=set(Kreq); seq=[S]
    for _ in range(nX+2):
        S={x for x in Kreq if any(all(f[(x,u,e)] in seq[-1] for e in Ereq[x]) for u in U)}
        seq.append(S)
    inter=set(Kreq)
    for s in seq: inter&=s
    nested=all(seq[i+1]<=seq[i] for i in range(len(seq)-1))
    stab=next(i for i in range(len(seq)-1) if seq[i]==seq[i+1])
    return V==inter, nested, stab<=len(Kreq)
ok=[0,0,0]; M=100000
for s in range(M):
    a,b,c2=stages(s); ok[0]+=a; ok[1]+=b; ok[2]+=c2
print('stage check',M,'Viab==intersection',ok[0],'nested',ok[1],'stabilizes within |K_req| steps',ok[2])
