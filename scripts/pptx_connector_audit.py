"""Report duplicate connector objects on slides; does not silently remove objects."""
import argparse,json,math
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

def main():
 p=argparse.ArgumentParser();p.add_argument('pptx');p.add_argument('--out',required=True);p.add_argument('--tolerance-emu',type=int,default=20000);a=p.parse_args()
 prs=Presentation(a.pptx);issues=[];count=0
 for page,sl in enumerate(prs.slides):
  candidates=[]
  for i,sh in enumerate(sl.shapes):
   if sh.shape_type != MSO_SHAPE_TYPE.LINE:continue
   count+=1
   line=sh._element.spPr.find(qn('a:ln'))
   stroke=line.xml if line is not None else ''
   dims=(sh.left,sh.top,sh.width,sh.height)
   for j,prev,style in candidates:
    if all(abs(v-w)<=a.tolerance_emu for v,w in zip(dims,prev)) and stroke==style:
     issues.append({'slide':page+1,'shapes':[j,i],'reason':'same connector bounding geometry and XML stroke'})
   candidates.append((i,dims,stroke))
 report={'connectors':count,'duplicate_pairs':issues}
 Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
 if issues:raise SystemExit(2)
if __name__=='__main__':main()
