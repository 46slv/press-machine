from pathlib import Path
import hashlib,json,re,subprocess
r=Path(__file__).resolve().parents[3]
o=r/'adapters/ofx'
base='02c57f0e93ae27b25b97ab6f1b5e1a51c8da2235'
def baseline(p):return subprocess.check_output(['git','show',base+':'+p],cwd=r)
frozen=['parameters/press_machine_v2.json','adapters/ofx/src/CudaRunner.cpp',
 'adapters/ofx/src/Kernel.cu','adapters/ofx/tests/Native.cpp']
frozen += [
 p.relative_to(r).as_posix() for p in (r/'core/press_machine').glob('*') if p.is_file()]
hashes={}
for p in frozen:
 a=baseline(p).replace(b'\r\n',b'\n');b=(r/p).read_bytes().replace(b'\r\n',b'\n')
 assert a==b,'Frozen source changed: '+p
 hashes[p]=hashlib.sha256(a).hexdigest()
old=baseline('adapters/ofx/src/Plugin.cpp').decode().replace('\r\n','\n')
new=(o/'src/Plugin.cpp').read_text()
for start,end in [('class Processor:','class PressMachine:'),('class PressMachine:','mDeclarePluginFactory')]:
 assert old.split(start,1)[1].split(end,1)[0]==new.split(start,1)[1].split(end,1)[0],start+' changed'
assert 'pm_graph' not in new, 'Graph leaked into processor/effect class'
schema=json.loads((r/'parameters/press_machine_v2.json').read_text());assert len(schema)==25
generated=(o/'generated/Descriptors.hpp').read_text()
assert 'graph->setDefault(false)' in generated and 'graph->setAnimates(false)' in generated
assert 'graph->setEvaluateOnChange(false)' in generated
for name in ['PixelCore.hpp','ParameterValues.hpp']:
 assert 'pm_graph' not in (o/'generated'/name).read_text(),name
overlay=(o/'src/HudOverlay.hpp').read_text()
assert 'setValue(' not in overlay and 'fetchImage(' not in overlay and 'pm::pixel(' not in overlay
assert 'kOfxImageEffectPluginPropOverlayInteractV1' in overlay
assert 'glClear(' not in overlay and 'swapBuffers(' not in overlay
report={'status':'PASS','qualified_base':base,'frozen_file_sha256':hashes,
 'processor_and_image_effect_class_byte_identical':True,'core_parameter_count':25,
 'graph_ofx_only_default_off':True,'graph_nonanimated_no_evaluate_hint':True,
 'host_export_pixel_test':False}
(o/'results/HUD_SOURCE_SEPARATION.json').write_text(json.dumps(report,indent=2),newline='\n')
print('HUD source separation PASS:',len(hashes),'frozen files; full Processor + PressMachine classes unchanged')
