"""Create uncompressed scanline FLOAT RGBA OpenEXR fixtures without host access."""
import csv
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reference import oracle as o
from tools.vectors import colors, STATES

ROOT=Path(__file__).resolve().parents[1]

def write_exr(path,width,height,rgba):
    def attr(name,kind,data):
        return name.encode()+b'\0'+kind.encode()+b'\0'+struct.pack('<I',len(data))+data
    box=struct.pack('<4i',0,0,width-1,height-1)
    channels=b''.join(n.encode()+b'\0'+struct.pack('<iB3xii',2,0,1,1) for n in 'ABGR')+b'\0'
    header=struct.pack('<II',20000630,2)
    header+=attr('channels','chlist',channels)+attr('compression','compression',b'\0')
    header+=attr('dataWindow','box2i',box)+attr('displayWindow','box2i',box)
    header+=attr('lineOrder','lineOrder',b'\0')+attr('pixelAspectRatio','float',struct.pack('<f',1))
    header+=attr('screenWindowCenter','v2f',struct.pack('<ff',0,0))
    header+=attr('screenWindowWidth','float',struct.pack('<f',1))+b'\0'
    row_size=width*16
    offsets=[len(header)+8*height+y*(8+row_size) for y in range(height)]
    with path.open('wb') as stream:
        stream.write(header); stream.write(struct.pack('<'+'Q'*height,*offsets))
        for y in range(height):
            row=rgba[y*width:(y+1)*width]
            stream.write(struct.pack('<ii',y,row_size))
            for channel in (3,2,1,0): stream.write(struct.pack('<'+'f'*width,*(pixel[channel] for pixel in row)))

def generate():
    dest=ROOT/'fixtures/host'; dest.mkdir(parents=True,exist_ok=True)
    # Exclude only the deliberately unrepresentable decode and bit stress.
    patches=[(name,rgb) for name,rgb in colors() if name not in ('decode_overflow','huge_negative','subnormal')]
    width=64; height=((len(patches)+7)//8)*8
    inputs=[]; linear=[]; expected={state:[] for state in STATES}
    records=[]
    for i,(name,rgb) in enumerate(patches):
        alpha=(0.,.25,.5,1.)[i%4]
        results={state:o.apply(rgb,*params) for state,params in STATES.items()}
        records.append({'index':i,'id':name,'sample_x':(i%8)*8+4,'sample_y':(i//8)*8+4,
                        'rgba':[*rgb,alpha], 'states':{k:v.__dict__ for k,v in results.items()}})
    for y in range(height):
        for x in range(width):
            i=(y//8)*8+x//8
            if i>=len(records):
                rgba=(0.,0.,0.,1.); results={state:rgba for state in STATES}
            else:
                record=records[i]; rgba=tuple(record['rgba'])
                results={state:(*record['states'][state]['rgb'],rgba[3]) for state in STATES}
            inputs.append(rgba)
            linear.append((*map(o.decode,rgba[:3]),rgba[3]))
            for state in STATES: expected[state].append(results[state])
    write_exr(dest/'input_dwg_di.exr',width,height,inputs)
    write_exr(dest/'input_linear_dwg.exr',width,height,linear)
    for state in STATES: write_exr(dest/f'expected_dwg_di_{state}.exr',width,height,expected[state])
    manifest={'format':'OpenEXR v2 uncompressed scanline FLOAT RGBA; little endian; 8x8 patches',
              'width':width,'height':height,'patches':records,'states':STATES,
              'input_dwg_di':'Topology B: actual encoded DWG/DI, no duplicate input CST',
              'input_linear_dwg':'Topology A: CST In DWG/Linear -> DWG/DI, tone/gamut mapping None',
              'alpha':'Authored fixture and expected alpha only; actual host behavior NOT_RUN',
              'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.glob('*.exr'))}}
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    with (dest/'patches.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f,lineterminator='\n'); writer.writerow(['id','x','y','alpha','state','T','Compression','Softness','Bypass','R','G','B','path','S_in','S_out'])
        for record in records:
            for state,params in STATES.items():
                r=record['states'][state]
                writer.writerow([record['id'],record['sample_x'],record['sample_y'],record['rgba'][3],state,*params,*r['rgb'],r['path'],r['s_in'],r['s_out']])
    print(f'{len(patches)} patches, {width}x{height}, {len(manifest["files"])} EXRs: {dest}')

if __name__=='__main__': generate()
