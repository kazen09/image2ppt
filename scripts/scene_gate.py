"""Refuse scenes known to create overlap, missing images, or Freeform fragments."""
import argparse,json,math
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--report');a=p.parse_args()
path=Path(a.scene).resolve();doc=json.loads(path.read_text(encoding='utf-8'));issues=[];warn=[]
w=float(doc['slide']['width_px']);h=float(doc['slide']['height_px'])
for n,page in enumerate(doc['pages'],1):
 bg=page.get('background',{})
 if 'image' in bg and page.get('elements'):issues.append(f'page {n}: full-slide bitmap under editable objects risks ghosting; use a cleaned background or remove overlay')
 texts=set()
 for j,e in enumerate(page.get('elements',[]),1):
  kind=e.get('type');tag=f'page {n} element {j}'
  if kind not in {'text','shape','image','connector'}:issues.append(f'{tag}: forbidden object type {kind!r}');continue
  x,y,ew,eh=[float(e.get(k,0)) for k in ('x','y','w','h')]
  if not all(math.isfinite(v) for v in (x,y,ew,eh)):issues.append(f'{tag}: nonfinite coordinate');continue
  if kind!='connector' and (ew<=0 or eh<=0):issues.append(f'{tag}: invalid bounds')
  if x< -2 or y< -2 or x+ew>w+2 or y+eh>h+2:warn.append(f'{tag}: outside canvas')
  if kind=='shape' and e.get('geometry') not in {'rect','roundRect','ellipse','line'}:issues.append(f'{tag}: unsupported geometry')
  if kind=='image':
   src=Path(e.get('src',''));src=src if src.is_absolute() else path.parent/src
   if not src.is_file():issues.append(f'{tag}: image not found: {src}')
  if kind=='text':
   value=e.get('text','');texts.add(value)
   if not str(value).strip():warn.append(f'{tag}: empty text')
   if float(e.get('font_size_pt',18))<7:warn.append(f'{tag}: suspicious font size')
  if kind=='connector' and abs(ew)+abs(eh)<0.5:issues.append(f'{tag}: zero-length connector')
result={'ok':not issues,'errors':issues,'warnings':warn,'slides':len(doc['pages']),'canvas':[w,h]}
if a.report:Path(a.report).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
if issues:raise SystemExit(2)
