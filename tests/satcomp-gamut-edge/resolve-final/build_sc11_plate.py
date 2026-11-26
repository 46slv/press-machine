"""Create two identical and independently decoded opaque background frames for SC11."""
from array import array
from pathlib import Path
import json,sys
from fixtures import BG,N,RGBA,encode_exr,bytes_of,sha
from native_checkpoint_metrics import load

ROOT=Path('sc11-media')
if __name__=='__main__':
    check=sys.argv[1:]==['--check']; assert check or not sys.argv[1:]
    if not check: ROOT.mkdir(exist_ok=False)
    z={c:array('f',[v])*N for c,v in zip(RGBA,(*BG,1.),strict=True)}
    files={}
    for i in (0,1):
        p=ROOT/f'background.{i:06d}.exr'
        if not check: encode_exr(p,z)
        assert bytes_of(z,RGBA)==bytes_of(load(p),RGBA)
        files[p.name]=sha(p)
    assert len(set(files.values()))==1
    record={'scope':'opaque DWG Relative Linear background matching the SC34 linear composite', 'files':files}
    m=ROOT/'manifest.json'
    if check: assert record==json.loads(m.read_text(encoding='utf8'))
    else:
        with m.open('x',encoding='utf8') as f: json.dump(record,f,indent=2)
    print(record)
