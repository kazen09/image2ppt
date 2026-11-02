"""Create a deterministic one-reference-per-slide manifest; avoids accidental montage inputs."""
import argparse,json
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('inputs',nargs='+');p.add_argument('--out',required=True);a=p.parse_args()
files=[]
for i,item in enumerate(a.inputs,1):
    path=Path(item)
    if not path.is_file():p.error(f'not found: {path}')
    with Image.open(path) as im:w,h=im.size
    if w<100 or h<100:p.error(f'reference too small: {path}')
    files.append({'page':i,'source':str(path.resolve()),'width_px':w,'height_px':h,'aspect_ratio':round(w/h,7),'status':'pending','scene':f'pages/page-{i:02}/scene.json','preview':f'pages/page-{i:02}/render.png'})
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'mode':'full_editable','reference_images':files},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Created {out} with {len(files)} page references')
