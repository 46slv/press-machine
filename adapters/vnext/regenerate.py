"""Generate the vNext shared C++ core, DCTL candidate, and OFX parameter glue."""
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
 if p['kind']=='double': return f"DEFINE_UI_PARAMS({p['id']}, {p['label']}, DCTLUI_SLIDER_FLOAT, {p['default']}, {p['min']}, {p['max']}, {p['step']})"
 if p['kind']=='bool': return f"DEFINE_UI_PARAMS({p['id']}, {p['label']}, DCTLUI_CHECK_BOX, {p['default']})"
 ids=', '.join(token(p['id'],i) for i,_ in enumerate(p['options']))
 labels=', '.join(p['options'])
 return f"DEFINE_UI_PARAMS({p['id']}, {p['label']}, DCTLUI_COMBO_BOX, {p['default']}, {{ {ids} }}, {{ {labels} }})"
ui_text='\n'.join(ui(p) for p in schema)+'\n'
dctl_pipeline=pipeline.replace('transform(const Parameters& p,','transform(')
for p in schema:dctl_pipeline=re.sub(r'\bp\.'+re.escape(p['id'])+r'\b',p['id'],dctl_pipeline)
dctl=ui_text+math+vnext+dctl_pipeline
(GEN/'PressMachine_vNext_TEST.dctl').write_text(dctl,newline='\n')
lines=['#pragma once\n#include "PixelCore.hpp"\ninline constexpr int kParameterCount='+str(len(schema))+';\ninline pm::Parameters fromValues(const double* v){pm::Parameters p{};']
for i,p in enumerate(schema):
 cast='(int)' if p['kind']!='double' else '(float)'
 lines.append(f"p.{p['id']}={cast}v[{i}];")
lines.append('return p;}\n')
(GEN/'ParameterValues.hpp').write_text(''.join(lines),newline='\n')
kind={'double':'Double','bool':'Boolean','choice':'Choice'}
decl=['#pragma once\n#include "ofxsImageEffect.h"\nstruct ParameterHandles{\n']
for p in schema:decl.append(' OFX::'+kind[p['kind']]+'Param* '+p['id']+';\n')
decl.append(' explicit ParameterHandles(OFX::ImageEffect&e){\n')
for p in schema:decl.append('  '+p['id']+'=e.fetch'+kind[p['kind']]+'Param("'+p['id']+'");\n')
decl.append(' }\n void read(double time,double*v){\n')
for i,p in enumerate(schema):
 if p['kind']=='choice':decl.append(' {int choice=0;'+p['id']+'->getValueAtTime(time,choice);v['+str(i)+']=choice;}\n')
 else:decl.append(' v['+str(i)+']='+p['id']+'->getValueAtTime(time);\n')
decl.append(' }\n};\ninline void defineParameters(OFX::ImageEffectDescriptor&d){\n auto*page=d.definePageParam("Controls");\n')
groups=[]
for p in schema:
 if p['group'] not in groups:
  groups.append(p['group']);g='group'+str(len(groups))
  decl.append(' auto*'+g+'=d.defineGroupParam("'+g+'");'+g+'->setLabels("'+p['group']+'","'+p['group']+'","'+p['group']+'");\n')
 p['_gid']='group'+str(groups.index(p['group'])+1)
for i,p in enumerate(schema):
 v='p'+str(i);decl.append(' auto*'+v+'=d.define'+kind[p['kind']]+'Param("'+p['id']+'");\n')
 label=p['label'].replace('"','\\\"')
 decl.append(v+'->setLabels("'+label+'","'+label+'","'+label+'");'+v+'->setScriptName("'+p['id']+'");'+v+'->setDefault('+str(p['default']).lower()+');\n')
 if p['kind']=='double':decl.append(v+'->setRange('+str(p['min'])+','+str(p['max'])+');'+v+'->setDisplayRange('+str(p['min'])+','+str(p['max'])+');'+v+'->setIncrement('+str(p['step'])+');\n')
 if p['kind']=='choice':
  for option in p['options']:decl.append(v+'->appendOption("'+option.replace('"','\\\"')+'");\n')
 if p['id']=='pm_hue_angle':decl.append(v+'->setHint("Primary Hue shared by Pattern, Hue Bias and Luma Split.");\n')
 if p['id']=='pm_hue_pattern':decl.append(v+'->setHint("Mono, Analogous, Complementary, Split Complementary, Triadic or Tetradic.");\n')
 if p['id']=='pm_luma_split':decl.append(v+'->setHint("Fixed-luminance split-tone drive with extreme headroom; it does not create contrast.");\n')
 if p['id']=='pm_db':decl.append(v+'->setHint("Bypass Density only. Hue remains active.");\n')
 decl.append(v+'->setParent(*'+p['_gid']+');page->addChild(*'+v+');\n')
decl.append('}\n')
(GEN/'Descriptors.hpp').write_text(''.join(decl),newline='\n')
receipt={'status':'GENERATED','parameter_count':len(schema),'core_sha256':hashlib.sha256(core.encode()).hexdigest(),'dctl_sha256':hashlib.sha256(dctl.encode()).hexdigest(),'pipeline':'PreSat -> SatComp -> Pattern/Bias/Split -> Density -> FinalDesat'}
(GEN/'GENERATION.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
