"""Replay sibling assertions unmodified except for loader/path and extended shim ABI."""
from harness import ROOT,CAND
src=(ROOT/'fixtures/test_original_cpu.py').read_text(encoding='utf-8')
start=src.index('ROOT = pathlib.Path(')
end=src.index('\nUI =',start)
src=src[:start] + '''from harness import CAND,load
SOURCE = CAND
launch = load('candidate')
''' + src[end:]
start=src.index('    inp=(C.c_float*3)')
end=src.index('\ncounts =',start)
src=src[:start] + '''    return launch(rgb, threshold=threshold, amount=amount, knee=knee, bypass=bypass,
                  ig=ig,it=it,og=og-1 if og else None,ot=ot-1 if ot else None)
''' + src[end:]
exec(compile(src,'fixtures/test_original_cpu.py [candidate loader]', 'exec'))
