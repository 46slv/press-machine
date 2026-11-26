"""Offline same-body fixed profile matching SC34 DWG Linear -> AP1 DI Comp Bypass."""
from pathlib import Path
import json,re,sys
from fixtures import sha
src=Path('materials/PR19_769a014c_CANDIDATE.dctl'); dst=Path('goal-diagnostics/ZZ_S19_769a014c_AlphaAP1DI_r1.dctl'); p=dst.with_suffix('.json')
assert sha(src)=='fbee7172303d8f498f0ff3f6ad0161c2bd6baf376867dc724932cf5371133c35'
raw=src.read_bytes(); r=re.compile(rb'^DEFINE_UI_PARAMS\((\w+),[^\r\n]*\)',re.M)
a=list(r.finditer(raw)); expected=['pm_threshold','pm_compression','pm_softness','pm_comp_bypass','pmi_ig','pmi_it','pmi_og','pmi_ot']; assert [m[1].decode() for m in a]==expected
v=dict(zip(expected,('25.0f','100.0f','20.0f','1','0','4','4','1'),strict=True)); b=lambda m:f'#define {m[1].decode()} {v[m[1].decode()]}'.encode()
z=r.sub(b,raw); back=z
for m in a:
    assert back.count(b(m))==1; back=back.replace(b(m),m[0])
assert back==raw
check='--check' in sys.argv
if not check:
    with dst.open('xb') as f:f.write(z)
assert dst.read_bytes()==z
q={'profile':dst.as_posix(),'sha256':sha(dst),'candidate_sha256':sha(src),'only_ui_constants':v,'scope':'diagnostic direct comparison against prior SC34 associated-alpha native FX; not a fix'}
if check: assert json.loads(p.read_text(encoding='utf8'))==q
else:
    with p.open('x',encoding='utf8') as f:json.dump(q,f,indent=2)
print(q)
