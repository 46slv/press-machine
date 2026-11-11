from pathlib import Path
import json
r=Path(__file__).resolve().parent
params=json.loads((r.parents[1]/'parameters/press_machine_v3_curve.json').read_text())
decl=['#pragma once\n#include "ofxsImageEffect.h"\n#include <array>\nstruct Parameters{\n']
kind={'double':'Double','bool':'Boolean','choice':'Choice'}
for p in params:decl.append(' OFX::'+kind[p['kind']]+'Param* '+p['id']+';\n')
decl.append(' explicit Parameters(OFX::ImageEffect&e){\n')
for p in params:decl.append('  '+p['id']+'=e.fetch'+kind[p['kind']]+'Param("'+p['id']+'");\n')
decl.append(' }\n void read(double time,double*v){\n')
for i,p in enumerate(params):
 if p['kind']=='choice':decl.append(' {int choice=0;'+p['id']+'->getValueAtTime(time,choice);v['+str(i)+']=choice;}\n')
 else:decl.append('  v['+str(i)+']='+p['id']+'->getValueAtTime(time);\n')
decl.append(' }\n template<class Visitor> void forEach(Visitor visitor){\n')
for p in params:decl.append('  visitor('+p['id']+');\n')
decl.append(' }\n};\ninline void defineParameters(OFX::ImageEffectDescriptor&d){\n auto*page=d.definePageParam("Controls");\n')
groups=[]
for p in params:
 if p['group'] not in groups:
  groups.append(p['group']);name='group'+str(len(groups))
  decl.append(' auto*'+name+'=d.defineGroupParam("'+name+'");'+name+'->setLabels("'+p['group']+'","'+p['group']+'","'+p['group']+'");\n')
 p['groupid']='group'+str(groups.index(p['group'])+1)
for i,p in enumerate(params):
 v='p'+str(i);decl.append(' auto*'+v+'=d.define'+kind[p['kind']]+'Param("'+p['id']+'");\n')
 decl.append(v+'->setLabels("'+p['label']+'","'+p['label']+'","'+p['label']+'");'+v+'->setScriptName("'+p['id']+'");'+v+'->setDefault('+str(p['default']).lower()+');\n')
 if p['kind']=='double':
  decl.append(v+'->setRange('+str(p['min'])+','+str(p['max'])+');'+v+'->setDisplayRange('+str(p['min'])+','+str(p['max'])+');'+v+'->setIncrement('+str(p['step'])+');\n')
 if p['kind']=='choice':
  for option in p['options']:decl.append(v+'->appendOption("'+option+'");\n')
 if p['id']=='pm_hue_angle':decl.append(v+'->setHint("0 degrees: skin-tone reference axis.");\n')
 if p['id']=='pm_hue_pattern':decl.append(v+'->setHint("Six anchor families. Bias and Split remain active at Strength zero. No v2 state migration.");\n')
 if p['id']=='pm_db':decl.append(v+'->setHint("Bypass Density only, preserving its settings. Other stages remain active.");\n')
 decl.append(v+'->setParent(*'+p['groupid']+');page->addChild(*'+v+');\n')
decl.append(' auto*graph=d.defineBooleanParam("pm_graph");graph->setLabels("Graph","Graph","Graph");graph->setScriptName("pm_graph");graph->setDefault(false);graph->setAnimates(false);graph->setEvaluateOnChange(false);graph->setHint("Read-only viewer HUD. Hue swatches are Pattern direction keys, not output colors. Q is luminance response; Drive is signed Angle/opposite attraction, not final hue angle. Density: fixed Skin/Red/Blue probes, input EV -6 to +6, protected Hue to protected Look. Brightness EV and relative Oklab C/L percent; neutral denominators are omitted. Not footage measurement. Requires OpenFX overlays; never rendered into pixels.");page->addChild(*graph);\n')
decl.append('}\n');(r/'generated/Descriptors.hpp').write_text(''.join(decl))
print(f'Generated {len(params)} processing parameter descriptors + OFX-only Graph flag.')

values=['#pragma once\n#include "PixelCore.hpp"\ninline constexpr int kParameterCount = '+str(len(params))+';\ninline pm::Parameters fromValues(const double* v){pm::Parameters p{};']
for i,p in enumerate(params):
 values.append('p.'+p['id']+'=('+('float' if p['kind']=='double' else 'int')+')v['+str(i)+'];')
values.append('return p;}\n')
(r/'generated/ParameterValues.hpp').write_text(''.join(values))
