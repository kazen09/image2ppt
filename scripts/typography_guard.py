"""Flag likely text overflow/too-small fonts; heuristic gate, not visual proof."""
import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--out',required=True);p.add_argument('--min-font-pt',type=float,default=7);a=p.parse_args()
 d=json.loads(Path(a.scene).read_text(encoding='utf-8'));errors=[];warnings=[]
 for pageno,page in enumerate(d['pages'],1):
  for e in page.get('elements',[]):
   if e.get('type')!='text':continue
   font=float(e.get('font_size_pt',18)); text=e.get('text','')
   if font<a.min_font_pt:errors.append({'page':pageno,'id':e.get('id'),'reason':'font too small','font_pt':font})
   if not str(text).strip():warnings.append({'page':pageno,'id':e.get('id'),'reason':'empty textbox'})
   if float(e.get('h',0))<font*.65:warnings.append({'page':pageno,'id':e.get('id'),'reason':'potential vertical clipping'})
 report={'errors':errors,'warnings':warnings}
 Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'errors':len(errors),'warnings':len(warnings)}))
 if errors:raise SystemExit(2)
if __name__=='__main__':main()
