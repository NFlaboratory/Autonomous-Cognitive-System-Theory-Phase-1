"""工程5-2〜5-4 用：§2〜§8 の環境の外の地の文を文に分け、分類して数える（候補抽出であり、意味の判定ではない）。
使い方：python3 -I tools/prose_extract.py [-o 出力.json] paper/section2_definition.tex ...
  -o を指定すると結果の JSON をそのファイルに書き、件数を標準エラーに出す。
  -o を省くと JSON を標準出力に書き、件数を標準エラーに出す。"""
import re,sys,json,hashlib
ENV_SKIP={'definition','assumption','assumptioninner','proposition','lemma','theorem','proof','observation','problem','remark','figure','table','equation','equation*','align','align*','tikzpicture'}
ASSERT=re.compile(r'ならば|したがって|よって|ゆえに|から従う|導かれ|成り立つ|成立する|含意|同値|帰結|一致する|に等しい|である。$')
IMPLICIT=re.compile(r'前述|上述|既述|先に述べ|前節|前項|前小節|以上の|上記|同様に|同じく|この(?:条件|性質|規約|区別|定義|量|集合)')
def strip_comments(s): return re.sub(r'(?<!\\)%.*','',s)
def outside_envs(s):
    out=[];depth=[];i=0
    tok=re.compile(r'\\(begin|end)\{([^}]+)\}|\\\[|\\\]')
    pos=0;skip=0;mstack=0
    for m in tok.finditer(s):
        seg=s[pos:m.start()]
        if not skip and not mstack: out.append((pos,seg))
        pos=m.end()
        if m.group(0)=='\\[': mstack+=1; out.append((m.start(),' [式] ')) if not skip else None; continue
        if m.group(0)=='\\]': mstack=max(0,mstack-1); continue
        kind,name=m.group(1),m.group(2)
        if name in ENV_SKIP:
            skip+= 1 if kind=='begin' else -1
            skip=max(skip,0)
    if not skip: out.append((pos,s[pos:]))
    return out
def main(paths):
    res=[]
    for p in paths:
        s=strip_comments(open(p).read())
        for off,seg in outside_envs(s):
            seg=re.sub(r'\\(sub)*section\*?\{[^}]*\}|\\label\{[^}]*\}','',seg)
            for m in re.finditer(r'[^。]+。',seg):
                t=' '.join(m.group(0).split())
                if len(t)<6: continue
                line=s[:off+m.start()].count('\n')+1
                has_ref='\\ref{' in t
                cls=[]
                if IMPLICIT.search(t): cls.append('5-4')
                if has_ref and ASSERT.search(t): cls.append('5-3')
                if not has_ref and ASSERT.search(t): cls.append('5-2')
                res.append({'file':p,'line':line,'id':hashlib.md5(t.encode()).hexdigest()[:8],'cls':cls,'text':t})
    for n,x in enumerate(res):
        x['key']=f"{x['file']}:{x['line']}:{n}"  # 一意キー。内容ハッシュ id は同じ文で重複しうるので、照合のキーには key を用いる
    return res
if __name__=='__main__':
    args=sys.argv[1:]
    out=None
    if len(args)>=2 and args[0]=='-o':
        out,args=args[1],args[2:]
    if not args:
        sys.exit('usage: prose_extract.py [-o out.json] file.tex ...')
    r=main(args)
    if out:
        with open(out,'w',encoding='utf-8') as fh:
            json.dump(r,fh,ensure_ascii=False,indent=0)
    else:
        json.dump(r,sys.stdout,ensure_ascii=False,indent=0)
        sys.stdout.write('\n')
    from collections import Counter
    c=Counter()
    for x in r:
        for k in x['cls']: c[k]+=1
    print('sentences',len(r),dict(c),'any',sum(1 for x in r if x['cls']),file=sys.stderr)
