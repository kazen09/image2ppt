"""Convert icon manifest rectangles into source-cropped image elements within scene JSON.
Icon coordinates are pixel coordinates in the original source image.
"""
import argparse, json, re
from pathlib import Path
from PIL import Image

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--scene',required=True);ap.add_argument('--manifest',required=True)
 ap.add_argument('--out-scene',required=True);ap.add_argument('--asset-dir',required=True)
 args=ap.parse_args()
 scene_path=Path(args.scene).resolve(); manifest_path=Path(args.manifest).resolve()
 scene=json.loads(scene_path.read_text(encoding='utf-8'))
 manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
 target=Path(args.out_scene).resolve(); target.parent.mkdir(parents=True,exist_ok=True)
 out=Path(args.asset_dir).resolve();out.mkdir(parents=True,exist_ok=True)
 audit=[]
 for item in manifest['icons']:
  page=int(item.get('page',1))-1
  page_elements=scene['pages'][page].setdefault('elements',[])
  image=Path(item.get('source_image',manifest.get('source_image','')))
  if not image.is_absolute():image=(manifest_path.parent/image).resolve()
  if not image.is_file():raise FileNotFoundError(image)
  x,y,w,h=(int(item[k]) for k in ('x','y','w','h'))
  im=Image.open(image).convert('RGBA')
  if w<1 or h<1 or x<0 or y<0 or x+w>im.width or y+h>im.height:raise ValueError(f'Invalid crop for {item}')
  ident=item['id']; filename=re.sub(r'[^a-zA-Z0-9_-]','_',ident)+'.png'
  asset=out/filename;im.crop((x,y,x+w,y+h)).save(asset)
  found=[(i,e) for i,e in enumerate(page_elements) if e.get('icon_id')==ident or e.get('id')==ident]
  if len(found)!=1:raise ValueError(f'Icon {ident}: expected exactly one placeholder, found {len(found)}')
  idx,e=found[0]
  # preserve placement/z rather than move anything around
  page_elements[idx]={'type':'image','id':ident,'icon_id':ident,'role':'icon','asset_origin':'source_crop',
   'src':str(asset),'x':e['x'],'y':e['y'],'w':e['w'],'h':e['h'],'z':e.get('z',idx)}
  audit.append({'id':ident,'page':page+1,'asset':str(asset)})
 target.write_text(json.dumps(scene,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'icons_replaced':len(audit),'audit':audit},ensure_ascii=False,indent=2))
if __name__=='__main__': main()
