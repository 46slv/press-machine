"""Independent FFmpeg EXR readback of authored float bits, including alpha.

Uses an existing ffmpeg on PATH; not a Resolve or display test.
"""
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference import oracle as o

ROOT=Path(__file__).resolve().parents[1]

def main():
    exe=shutil.which('ffmpeg')
    if not exe: raise RuntimeError('Existing ffmpeg required for optional independent EXR readback; do not install automatically')
    base=ROOT/'fixtures/host'; manifest=json.loads((base/'manifest.json').read_text())
    w,h=manifest['width'],manifest['height']; size=w*h
    checks=0
    for name,digest in manifest['files'].items():
        path=base/name
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest: raise AssertionError(('fixture hash',name))
        result=subprocess.run([exe,'-v','error','-i',str(path),'-f','rawvideo','-pix_fmt','gbrapf32le','pipe:1'],capture_output=True,check=True)
        if len(result.stdout)!=size*16: raise AssertionError(('decoded size',name,len(result.stdout)))
        words=struct.unpack('<'+'I'*(size*4),result.stdout)
        for y in range(h):
            for x in range(w):
                index=(y//8)*8+x//8
                if index>=len(manifest['patches']): rgba=(0.,0.,0.,1.)
                else:
                    record=manifest['patches'][index]
                    if name.startswith('expected_'):
                        state=name[len('expected_dwg_di_'):-len('.exr')]
                        rgba=(*record['states'][state]['rgb'],record['rgba'][3])
                    else: rgba=record['rgba']
                    if name=='input_linear_dwg.exr': rgba=(*map(o.decode,rgba[:3]),rgba[3])
                pos=y*w+x
                for plane,channel in enumerate((1,2,0,3)):
                    if words[plane*size+pos]!=o.bits(rgba[channel]):
                        raise AssertionError(('decoded float bits',name,x,y,channel))
                    checks+=1
    report={'stage':'EXR_INDEPENDENT_READBACK_PASS','files':len(manifest['files']),
            'float_words_exact':checks,'dimensions':[w,h],
            'decoder':subprocess.run([exe,'-version'],capture_output=True,text=True).stdout.splitlines()[0],
            'scope':'File serialization only; Resolve buffer/alpha/compile/visual are NOT_RUN'}
    (ROOT/'evidence/fixture_readback.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
