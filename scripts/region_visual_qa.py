"""Grid-based rendered image comparison; reports worst visual regions, not repairs."""
import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageEnhance,ImageDraw

def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',required=True);p.add_argument('--rendered',required=True);p.add_argument('--out',required=True);p.add_argument('--grid',default='4x3');a=p.parse_args()
    cols,rows=map(int,a.grid.lower().split('x'));assert 1<=cols<=16 and 1<=rows<=16
    ref=Image.open(a.reference).convert('RGB');cur=Image.open(a.rendered).convert('RGB')
    resized=cur.size!=ref.size
    if resized:cur=cur.resize(ref.size,Image.Resampling.LANCZOS)
    A=np.asarray(ref,dtype=np.int16);B=np.asarray(cur,dtype=np.int16);d=np.abs(A-B)
    W,H=ref.size;segments=[]
    for row in range(rows):
        for col in range(cols):
            x0=W*col//cols;x1=W*(col+1)//cols;y0=H*row//rows;y1=H*(row+1)//rows
            tile=d[y0:y1,x0:x1];segments.append({'region':[x0,y0,x1,y1],'mae':round(float(tile.mean()),3),'fraction_delta_gt_20':round(float(np.any(tile>20,axis=2).mean()),4)})
    ordered=sorted(enumerate(segments),key=lambda item:item[1]['mae'],reverse=True)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    overlay=Image.blend(ref,cur,0.5);draw=ImageDraw.Draw(overlay)
    for rank,(index,r) in enumerate(ordered[:min(6,len(ordered))],1):
        x0,y0,x1,y1=r['region'];draw.rectangle((x0,y0,x1-1,y1-1),outline='red',width=3);draw.text((x0+4,y0+4),str(rank),fill='red')
    overlay.save(out/'regions-overlay.png')
    ImageEnhance.Contrast(ImageChops.difference(ref,cur)).enhance(3).save(out/'difference.png')
    result={'reference':a.reference,'rendered':a.rendered,'reference_size':[W,H],'rendered_resized':resized,'overall_mae':round(float(d.mean()),3),'regions':[{'rank':i+1,**r} for i,(_,r) in enumerate(ordered)]}
    (out/'region-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'overall_mae':result['overall_mae'],'worst_regions':result['regions'][:3]},ensure_ascii=False))
if __name__=='__main__':main()
