"""Build DCTL and CPU/CUDA core from the same math and pipeline sources.
Never overwrites the immutable accepted DCTL under baseline/.
"""
from pathlib import Path
import json,re,hashlib
r=Path(__file__).resolve().parent
schema=json.loads((r.parents[1]/'parameters/press_machine_v2.json').read_text())
prefix=(r.parents[1]/'core/press_machine/PlatformPrefix.hpp.in').read_text()
math=(r.parents[1]/'core/press_machine/PixelMath.dctlh').read_text()
pipeline=(r.parents[1]/'core/press_machine/PixelPipeline.dctlh').read_text()
alpha=(r.parents[1]/'core/press_machine/AlphaAndIdentity.hpp.in').read_text()
core=prefix+math+pipeline+alpha
(r/'generated/PixelCore.hpp').write_text(core,newline='\n')
baseline=(r.parents[1]/'adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl').read_text()
ui='\n'.join(line for line in baseline.splitlines() if line.startswith(('DEFINE_UI_PARAMS','DEFINE_UI_TOOLTIP')))+'\n'
dctl_pipeline=pipeline.replace('transform(const Parameters& p,','transform(')
for p in schema:dctl_pipeline=re.sub(r'\bp\.'+p['id']+r'\b',p['id'],dctl_pipeline)
ui=ui.replace('Angle zero targets BT2020 red.','Angle zero targets the existing skin-tone chart reference.')
dctl=ui+math+dctl_pipeline
(r/'generated/PressMachine_Full_SkinAxis_TEST.dctl').write_text(dctl,newline='\n')
# Static token equality to the baseline excludes comments and UI declarations only.
def tokens(s):
 s=re.sub(r'//[^\n]*','',s)
 s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
 s='\n'.join(line for line in s.splitlines() if not line.startswith(('DEFINE_UI_PARAMS','DEFINE_UI_TOOLTIP')))
 return re.findall(r'[A-Za-z_]\w*|\d+(?:\.\d*)?(?:[eE][+-]?\d+)?[fF]?|[^\s]',s)
approved_old='__DEVICE__ float2 pmcf_phase(){return make_float2(2.72323161363601685e-01f,6.31167917930497424e-09f);}'
approved_new='__DEVICE__ float2 pmcf_phase(){return make_float2(7.28219926357269287e-01f,-1.02679500457725226e-08f);}'
assert dctl.count(approved_new)==1
assert tokens(baseline)==tokens(dctl.replace(approved_new,approved_old)),'unapproved math/pipeline difference from1938'
result=dict(status='PASS',baseline_sha256=hashlib.sha256((r.parents[1]/'adapters/dctl/PressMachine_Full_Color_19382145_TEST.dctl').read_bytes()).hexdigest(),shared_core_sha256=hashlib.sha256(core.encode()).hexdigest(),generated_dctl_sha256=hashlib.sha256(dctl.encode()).hexdigest(),math_pipeline_tokens_exact=False,math_pipeline_tokens_exact_except_skin_phase=True,skin_phase_radians=0.72821991608931957,legacy_angle_shift_degrees=26.120959577861925,scope='SkinAxis candidate: only approved active CF2 phase differs from1938; not Host tested')
(r/'results/SHARED_SOURCE_PARITY.json').write_text(json.dumps(result,indent=2)+'\n')
manifest=json.loads((r/'SOURCE_MANIFEST.json').read_text());manifest['core_sha256']=result['shared_core_sha256'];manifest['generated_dctl_sha256']=result['generated_dctl_sha256'];manifest['adapter_revision']='skin-axis-zero/logging-revision2/retained1938-equations-except-approved-phase';(r/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(result,indent=2))
