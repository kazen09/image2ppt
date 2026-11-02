"""Verify each multi-bend route is stored as exactly one PPTX DrawingML shape."""
import argparse,json,sys
from collections import Counter
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

def run(pptx,expected=None):
 p=Presentation(pptx);report=[];bad=[]
 for n,slide in enumerate(p.slides,1):
  routes=[s for s in slide.shapes if s.name.startswith('route:')]
  names=Counter(s.name for s in routes)
  for name,c in names.items():
   if c!=1:bad.append(f'page {n} {name}: {c} objects')
  for s in routes:
   cust=s._element.spPr.find(qn('a:custGeom'))
   path=cust.find('.//'+qn('a:path')) if cust is not None else None
   line_count=len(path.findall(qn('a:lnTo'))) if path is not None else 0
   end=s._element.spPr.find(qn('a:ln'))
   tail=end.find(qn('a:tailEnd')) if end is not None else None
   if path is None or line_count<1:bad.append(f'page {n} {s.name}: no continuous path')
   report.append({'page':n,'name':s.name,'line_segments_inside_one_shape':line_count,'has_end_arrow':tail is not None})
 if expected is not None and len(report)!=expected:bad.append(f'expected {expected} route shapes, found {len(report)}')
 return {'ok':not bad,'routes':report,'issues':bad}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('pptx');ap.add_argument('--expected',type=int);args=ap.parse_args()
 r=run(args.pptx,args.expected);print(json.dumps(r,ensure_ascii=False,indent=2));sys.exit(0 if r['ok'] else 1)
