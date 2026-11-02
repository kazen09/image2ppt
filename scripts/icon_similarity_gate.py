import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity

def compare(src,dst):
 a=np.asarray(Image.open(src).convert('RGB'),dtype=np.uint8)
 b=np.asarray(Image.open(dst).convert('RGB').resize((a.shape[1],a.shape[0]),Image.Resampling.LANCZOS),dtype=np.uint8)
 mae=float(np.abs(a.astype(np.float32)-b.astype(np.float32)).mean())
 # Small icons support SSIM by selecting legal odd window.
 win=min(7,a.shape[0],a.shape[1]);win-= (win+1)%2
 ssim=float(structural_similarity(a,b,channel_axis=2,data_range=255,win_size=win)) if win>=3 else None
 return {'mae':round(mae,3),'ssim':None if ssim is None else round(ssim,4)}
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',required=True);p.add_argument('--candidate',required=True)
 p.add_argument('--min-ssim',type=float,default=.90);p.add_argument('--max-mae',type=float,default=18)
 p.add_argument('--report');a=p.parse_args();r=compare(a.reference,a.candidate)
 r['pass']=r['ssim'] is not None and r['ssim']>=a.min_ssim and r['mae']<=a.max_mae
 r['note']='Thresholds are configurable heuristics, not proof of semantic/visual equivalence.'
 if a.report:Path(a.report).write_text(json.dumps(r,indent=2),encoding='utf-8')
 print(json.dumps(r));raise SystemExit(0 if r['pass'] else 2)
if __name__=='__main__':main()
