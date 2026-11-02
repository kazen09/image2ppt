"""Apply image-backed icon assets to a scene with stable IDs. Does not guess icon boxes.

Input icons.json: {"icons":[{"id":"kafka","bbox":[200,200,64,64],"page":0}]}
In scene, icon primitives MUST have icon_id equal to id OR stable id == id.
"""
import argparse, json
from pathlib import Path
from PIL import Image

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--scene',required=True);ap.add_argument('--icons',required=True)
    ap.add_argument('--sources',nargs='+',required=True,help='one source image per page')
    ap.add_argument('--out',required=True);ap.add_argument('--assets-dir',required=True)
    a=ap.parse_args()
    data=json.loads(Path(a.scene).read_text(encoding='utf-8'))
    cfg=json.loads(Path(a.icons).read_text(encoding='utf-8'))
    out=Path(a.out).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    dst=Path(a.assets_dir).resolve();dst.mkdir(parents=True,exist_ok=True)
    originals=[Image.open(f).convert('RGBA') for f in a.sources]
    problems=[];done=[]
    for item in cfg.get('icons',[]):
        page=int(item.get('page',0));id=str(item['id']);bbox=item['bbox']
        if not (0 <= page < len(data['pages']) and page<len(originals)):raise ValueError(f'{id}: invalid page')
        x,y,w,h=map(float,bbox)
        im=originals[page];W,H=im.size
        if min(w,h)<=0 or x<0 or y<0 or x+w>W or y+h>H:raise ValueError(f'{id}: crop out of image')
        matches=[];kept=[]
        for e in data['pages'][page]['elements']:
            if e.get('icon_id')==id or (e.get('role')=='icon' and e.get('id')==id):matches.append(e)
            else:kept.append(e)
        if not matches:
            problems.append(f'{id}: no labeled icon object(s) in scene; refusing to auto-overlay crop')
            continue
        # Capture z from the original icon group; preserve bbox from source, avoid redrawing primitives.
        z=min(float(e.get('z',0)) for e in matches)
        pix=(round(x),round(y),round(x+w),round(y+h))
        fname=f'page-{page+1:02d}-{id}.png'
        (dst/fname).parent.mkdir(parents=True,exist_ok=True)
        im.crop(pix).save(dst/fname)
        rel=str((dst/fname).relative_to(out.parent)) if (dst/fname).is_relative_to(out.parent) else str(dst/fname)
        kept.append({'type':'image','id':id,'role':'icon','icon_id':id,'src':rel,'x':x,'y':y,'w':w,'h':h,'z':z,'editability':'raster_icon'})
        data['pages'][page]['elements']=kept
        done.append({'id':id,'page':page,'replaced_primitives':len(matches),'asset':rel,'bbox':bbox})
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    rep={'replacements':done,'errors':problems,'warning':'Raster icon assets are not fully editable; recorded as exceptions.'}
    (out.parent/'icon-replacement-report.json').write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(rep,ensure_ascii=False,indent=2))
    if problems:raise SystemExit(2)
if __name__=='__main__':main()
