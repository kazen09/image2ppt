import argparse,json
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
p=argparse.ArgumentParser();p.add_argument('--pptx',required=True);p.add_argument('--out',required=True);a=p.parse_args()
prs=Presentation(a.pptx);report={'slide_inches':[prs.slide_width/914400,prs.slide_height/914400],'slides':[]}
for index,s in enumerate(prs.slides,1):
 d={'index':index,'shapes':len(s.shapes),'text_boxes':0,'pictures':0,'text':[],'out_of_bounds':[],'near_full_slide_images':[]}
 for sh in s.shapes:
  if sh.has_text_frame and sh.text.strip():d['text_boxes']+=1;d['text'].append(sh.text[:150])
  if sh.shape_type==MSO_SHAPE_TYPE.PICTURE:
   d['pictures']+=1
   if sh.width*sh.height>prs.slide_width*prs.slide_height*.85:d['near_full_slide_images'].append(sh.name)
  if sh.left<0 or sh.top<0 or sh.left+sh.width>prs.slide_width+10000 or sh.top+sh.height>prs.slide_height+10000:d['out_of_bounds'].append(sh.name)
 report['slides'].append(d)
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False,indent=2))
