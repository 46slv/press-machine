from pathlib import Path
import ctypes as c
import hashlib,json,sys

R=Path(__file__).resolve().parents[1]
bundle=Path(sys.argv[1]) if len(sys.argv)>1 else R/'build/PressMachineV2SkinAxis.ofx.bundle'
suffix='.ofx.bundle'
assert bundle.name.endswith(suffix), 'Expected an OFX bundle directory'
stem=bundle.name[:-len(suffix)]
relative=Path('Contents/Win64')/(stem+'.ofx')
binary=bundle/relative
assert binary.is_file(), 'Bundle stem and binary stem must match: '+relative.as_posix()
notice=bundle/'Contents/Resources/THIRD_PARTY_NOTICES.txt'
assert notice.is_file(), 'Missing dependency license notice'
assert notice.read_text()==(R/'THIRD_PARTY_NOTICES.txt').read_text(), 'Dependency notice differs'

class Plugin(c.Structure):
    _fields_=[('api',c.c_char_p),('api_version',c.c_int),
              ('identifier',c.c_char_p),('major',c.c_uint),('minor',c.c_uint),
              ('set_host',c.c_void_p),('entry',c.c_void_p)]
dll=c.CDLL(str(binary.resolve()))
dll.OfxGetNumberOfPlugins.restype=c.c_int
dll.OfxGetPlugin.argtypes=[c.c_int]
dll.OfxGetPlugin.restype=c.POINTER(Plugin)
assert dll.OfxGetNumberOfPlugins()==1
plugin=dll.OfxGetPlugin(0).contents
assert plugin.api==b'OfxImageEffectPluginAPI' and plugin.api_version==1
assert plugin.identifier==b'com.46slv.PressMachine.v2.skinaxis'
assert (plugin.major,plugin.minor)==(2,0) and plugin.set_host and plugin.entry
report={'status':'PASS','bundle_name':bundle.name,'binary_relative_path':relative.as_posix(),
        'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
        'plugin_count':1,'identifier':plugin.identifier.decode(),
        'api':plugin.api.decode(),'api_version':plugin.api_version,
        'plugin_version':[plugin.major,plugin.minor],
        'dependency_notice_text_exact':True,'host_acceptance':False}
(R/'results').mkdir(exist_ok=True)
(R/'results/PACKAGE_LAYOUT.json').write_text(json.dumps(report,indent=2),newline='\n')
print(json.dumps(report,indent=2))
