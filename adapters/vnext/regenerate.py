"""Generate the vNext shared C++ core and a DCTL candidate without touching v2 artifacts."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
GEN=HERE/'generated';GEN.mkdir(parents=True,exist_ok=True)
schema=json.loads((ROOT/'parameters/press_machine_vnext.json').read_text())
prefix=(ROOT/'core/press_machine/PlatformPrefixVNext.hpp.in').read_text()
math=(ROOT/'core/press_machine/PixelMath.dctlh').read_text()
vnext=(ROOT/'core/press_machine/PixelVNext.dctlh').read_text()
pipeline=(ROOT/'core/press_machine/PixelPipelineVNext.dctlh').read_text()
alpha=(ROOT/'core/press_machine/AlphaAndIdentityVNext.hpp.in').read_text()
core=prefix+math+vnext+pipeline+alpha
(GEN/'PixelCore.hpp').write_text(core,newline='\n')
def token(id_,i):return ('PMVN_'+id_+'_'+str(i)).upper()
def ui(p):
 if p['kind']=='double':
  return f"DEFINE_UI_PARAMS({p['id']}, {p['label']}, DCTLUI_SLIDER_FLOAT, {p['default']}, {p['min']}, {p['max']}, {p['step']})"
 if p['kind']=='bool':
  return f"DEFINE_UI_PARAMS({p['id']}, {p['label']}, DCTLUI_CHECK_BOX, {p['default']})"
 ids=', '.join(token(p['id'],i) for i,_ in enumerate(p['options']))
 labels=', '.join(p['options'])
 return f"DEFINE_UI_PARAMS({p['id']}, {p['label']}, DCTLUI_COMBO_BOX, {p['default']}, {{ {ids} }}, {{ {labels} }})"
ui_text='\n'.join(ui(p) for p in schema)+'\n'
dctl_pipeline=pipeline.replace('transform(const Parameters& p,','transform(')
for p in schema:dctl_pipeline=re.sub(r'\bp\.'+re.escape(p['id'])+r'\b',p['id'],dctl_pipeline)
dctl=ui_text+math+vnext+dctl_pipeline
(GEN/'PressMachine_vNext_TEST.dctl').write_text(dctl,newline='\n')
kind={'double':'float','choice':'int','bool':'int'}
lines=['#pragma once\n#include "PixelCore.hpp"\ninline pm::Parameters fromValues(const double* v){pm::Parameters p{};']
for i,p in enumerate(schema):
 cast='(int)' if p['kind']!='double' else '(float)'
 lines.append(f"p.{p['id']}={cast}v[{i}];")
lines.append('return p;}\n')
(GEN/'ParameterValues.hpp').write_text(''.join(lines),newline='\n')
receipt={
 'status':'GENERATED','parameter_count':len(schema),
 'core_sha256':hashlib.sha256(core.encode()).hexdigest(),
 'dctl_sha256':hashlib.sha256(dctl.encode()).hexdigest(),
 'pipeline':'PreSat -> SatComp -> Pattern/Bias/Split -> Density -> FinalDesat'
}
(GEN/'GENERATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
