import sys,re
W=["完全","決定的","革命的","究極","絶対的","必然","自明","明らか","よく知られている","常に","ほとんどの場合","通常は","我々は達成した","極めて","非常に","初めて示した","保証","四層","原理層","三層対応","構造的存続要件","構造的崩壊","機能的崩壊"]
for f in sys.argv[1:]:
    s=open(f,encoding='utf-8').read()
    c={w:s.count(w) for w in W}
    print(f, {k:v for k,v in c.items() if v})
