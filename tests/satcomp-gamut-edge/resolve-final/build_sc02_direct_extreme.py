"""Create fixed direct comparators for the exact saved range3 source. No host operations."""
from pathlib import Path
import difflib,json,re,sys
from fixtures import sha

ROOT=Path('goal-diagnostics'); C=Path('materials/PR19_769a014c_CANDIDATE.dctl'); H='fbee7172303d8f498f0ff3f6ad0161c2bd6baf376867dc724932cf5371133c35'
PROFILES={'LogC3':2,'DIExtreme':1}
UI=re.compile(rb'^DEFINE_UI_PARAMS\((\w+),[^\r\n]*\)',re.M)
assert sha(C)==H
src=C.read_bytes(); ordered=['pm_threshold','pm_compression','pm_softness','pm_comp_bypass','pmi_ig','pmi_it','pmi_og','pmi_ot']; lines=list(UI.finditer(src))
assert [x[1].decode() for x in lines]==ordered
assert b'{ Same as Input, DaVinci Intermediate, LogC3 EI800 Exposure, LogC4 Scene' in src
r={}; check='--check' in sys.argv
for name,out in PROFILES.items():
    values=dict(zip(ordered,('25.0f','100.0f','20.0f','1','0','4','0',str(out)),strict=True)); o=ROOT/f'ZZ_S19_769a014c_Direct_{name}_r2.dctl'; p=o.with_suffix('.patch')
    rep=lambda m:f'#define {m[1].decode()} {values[m[1].decode()]}'.encode()
    data=UI.sub(rep,src); back=data
    for m in lines:
        assert back.count(rep(m))==1; back=back.replace(rep(m),m[0])
    assert back==src
    d=''.join(difflib.unified_diff(src.decode().splitlines(keepends=True),data.decode().splitlines(keepends=True),fromfile=C.name,tofile=o.name,n=0))
    if not check:
        with o.open('xb') as f:f.write(data)
        with p.open('x',encoding='utf8',newline='') as f:f.write(d)
    assert o.read_bytes()==data and p.read_bytes()==d.encode()
    r[name]={'DCTL':o.as_posix(),'sha256':sha(o),'candidate':H,'ui_to_constants_only':values,'native':False}
report=ROOT/'sc02-direct-extreme-profiles.json'
if check: assert json.loads(report.read_text(encoding='utf8'))==r
else:
    with report.open('x',encoding='utf8') as f:json.dump(r,f,indent=2)
print(json.dumps(r,indent=2))
