"""Static semantic scene checks for editable source-aligned layouts."""
import argparse, json
from pathlib import Path

def check(data):
    issues=[]; W=float(data['slide']['width_px']);H=float(data['slide']['height_px'])
    for pi,page in enumerate(data.get('pages',[]),1):
        seen=set();elements=page.get('elements',[])
        for i,o in enumerate(elements):
            ident=o.get('id')
            if ident and ident in seen:issues.append({'page':pi,'item':i,'issue':'duplicate object id'})
            if ident:seen.add(ident)
            typ=o.get('type'); x=float(o.get('x',0));y=float(o.get('y',0));w=float(o.get('w',0));h=float(o.get('h',0))
            if typ not in ('text','shape','connector','image'):issues.append({'page':pi,'item':i,'issue':'unknown type'})
            if typ!='connector' and (w<=0 or h<=0):issues.append({'page':pi,'item':i,'issue':'nonpositive box'})
            if typ!='connector' and (x < -2 or y < -2 or x+w>W+2 or y+h>H+2):issues.append({'page':pi,'item':i,'issue':'object outside canvas'})
            if typ=='connector' and not o.get('border'):issues.append({'page':pi,'item':i,'issue':'connector missing stroke'})
            if typ=='image':issues.append({'page':pi,'item':i,'issue':'image item is not fully editable'})
            if typ=='text' and not (o.get('text') or o.get('runs')):issues.append({'page':pi,'item':i,'issue':'empty text'})
        if page.get('background',{}).get('image'):issues.append({'page':pi,'issue':'raster background not fully editable'})
    return {'pass':not issues,'issues':issues,'pages':len(data.get('pages',[]))}

def main():
    p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    result=check(json.loads(Path(a.scene).read_text(encoding='utf-8')))
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False));raise SystemExit(0 if result['pass'] else 2)
if __name__=='__main__':main()
