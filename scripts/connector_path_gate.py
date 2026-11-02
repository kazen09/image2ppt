"""Fail on duplicate same-direction routes; warn on near-overlaps.
No deletion: avoids damaging legitimate bidirectional flows. Stable x/y/w/h geometry.
"""
import argparse, json, math
from pathlib import Path

def pts(o):
    if o.get('path_points'):return [tuple(map(float,p)) for p in o['path_points']]
    return [(float(o['x']),float(o['y'])),(float(o['x'])+float(o['w']),float(o['y'])+float(o['h']))]

def close(a,b,tol):return len(a)==len(b) and all(math.dist(x,y)<=tol for x,y in zip(a,b))

def main():
    p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--out',required=True);p.add_argument('--tolerance-px',type=float,default=2.0);a=p.parse_args()
    scene=json.loads(Path(a.scene).read_text(encoding='utf-8'))
    report={'duplicates':[],'possible_overlaps':[],'connectors':0}
    for pi,page in enumerate(scene['pages']):
        seen=[]
        for i,e in enumerate(page['elements']):
            if e.get('type')!='connector':continue
            report['connectors']+=1;points=pts(e)
            if len(points)<2 or close([points[0]],[points[-1]],0.01):report.setdefault('invalid',[]).append({'page':pi,'index':i,'reason':'zero-length route'})
            for j,b,bpts in seen:
                same=close(points,bpts,a.tolerance_px)
                attrs=(e.get('begin_arrow'),e.get('end_arrow'),e.get('border',{}).get('color'),e.get('border',{}).get('width_pt'))
                battrs=(b.get('begin_arrow'),b.get('end_arrow'),b.get('border',{}).get('color'),b.get('border',{}).get('width_pt'))
                if same and attrs==battrs:report['duplicates'].append({'page':pi,'indices':[j,i],'reason':'same route and styling'})
                elif same:report['possible_overlaps'].append({'page':pi,'indices':[j,i],'reason':'same route, different styles or arrow direction'})
            seen.append((i,e,points))
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in report.items()},ensure_ascii=False))
    if report['duplicates'] or report.get('invalid'):raise SystemExit(2)
if __name__=='__main__':main()
