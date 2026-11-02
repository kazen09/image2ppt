"""Report native text, images, connectors, and suspicious shape explosions."""
import argparse,json
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
p=argparse.ArgumentParser();p.add_argument('pptx');p.add_argument('--out');a=p.parse_args()
prs=Presentation(a.pptx);slides=[]
for i,s in enumerate(prs.slides,1):
 counts={'text':0,'images':0,'connectors':0,'other_shapes':0,'text_chars':0}
 for shp in s.shapes:
  if shp.shape_type==MSO_SHAPE_TYPE.PICTURE:counts['images']+=1
  elif shp.shape_type==MSO_SHAPE_TYPE.LINE:counts['connectors']+=1
  elif shp.has_text_frame and shp.text.strip():counts['text']+=1;counts['text_chars']+=len(shp.text)
  else:counts['other_shapes']+=1
 counts['slide']=i;slides.append(counts)
report={'slides':slides,'total_text_chars':sum(s['text_chars'] for s in slides)}
if a.out:Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
