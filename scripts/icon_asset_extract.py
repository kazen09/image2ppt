import argparse,json
from pathlib import Path
from PIL import Image

def main():
 p=argparse.ArgumentParser(description='Crop source icon rectangles without inventing masks')
 p.add_argument('--source',required=True);p.add_argument('--icons',required=True);p.add_argument('--outdir',required=True);a=p.parse_args()
 manifest=json.loads(Path(a.icons).read_text(encoding='utf-8'))
 dst=Path(a.outdir);dst.mkdir(parents=True,exist_ok=True)
 im=Image.open(a.source).convert('RGBA');W,H=im.size;out=[]
 for item in manifest['icons']:
  x,y,w,h=map(int,item['bbox'])
  if w<=0 or h<=0 or x<0 or y<0 or x+w>W or y+h>H:raise ValueError(f"Invalid icon bbox: {item['id']}")
  name=''.join(c if c.isalnum() or c in '-_' else '_' for c in item['id'])+'.png'
  im.crop((x,y,x+w,y+h)).save(dst/name)
  out.append({'id':item['id'],'path':str(dst/name),'bbox':[x,y,w,h],'editable':False})
 (dst/'asset-report.json').write_text(json.dumps({'assets':out,'warning':'Raster crops are NOT full_editable'},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'count':len(out),'outdir':str(dst)},ensure_ascii=False))
if __name__=='__main__':main()
