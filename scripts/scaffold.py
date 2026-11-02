import argparse,json
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser(); p.add_argument('--images', nargs='+',required=True); p.add_argument('--out',required=True); a=p.parse_args()
files=[Path(f).resolve() for f in a.images]
sizes=[Image.open(f).size for f in files]
if len(set(round(w/h,6) for w,h in sizes))>1: raise SystemExit('Different page aspect ratios: split decks or specify normalization')
w,h=sizes[0]; scene={'slide':{'width_px':w,'height_px':h,'width_in':13.333333},'pages':[]}
for f,(iw,ih) in zip(files,sizes):
    if (iw,ih)!=(w,h): raise SystemExit('All pages should use the same px size for this manifest')
    scene['pages'].append({'name':f.stem,'background':{'color':'#FFFFFF'},'elements':[], '_reference':str(f)})
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Created {out}; populate actual elements from image analysis; references are NOT embedded as slide images.')
