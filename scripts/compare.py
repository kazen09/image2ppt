import argparse,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageChops,ImageEnhance
try:
 from skimage.metrics import structural_similarity as ssim
except ImportError:ssim=None
p=argparse.ArgumentParser();p.add_argument('--reference',required=True);p.add_argument('--rendered',required=True);p.add_argument('--out',required=True);a=p.parse_args()
def images(path):
 path=Path(path)
 if path.is_file():return [path]
 return sorted([f for f in path.iterdir() if f.suffix.lower() in ('.png','.jpg','.jpeg','.webp')])
refs=images(a.reference);renders=images(a.rendered)
if len(refs)!=len(renders):raise SystemExit(f'Page count differs: reference {len(refs)} vs render {len(renders)}')
out=Path(a.out);out.mkdir(parents=True,exist_ok=True);result=[]
for i,(r,png) in enumerate(zip(refs,renders),1):
 ref=Image.open(r).convert('RGB');cur=Image.open(png).convert('RGB')
 if cur.size!=ref.size:cur=cur.resize(ref.size,Image.Resampling.LANCZOS)
 A=np.asarray(ref,dtype=np.float32);B=np.asarray(cur,dtype=np.float32);absdiff=np.abs(A-B)
 mae=float(absdiff.mean());p95=float(np.percentile(absdiff,95));error=float((absdiff>20).any(axis=2).mean())
 item={'slide':i,'reference':r.name,'rendered':png.name,'mae_0_255':round(mae,3),'p95_error':round(p95,3),'fraction_pixels_any_channel_delta_gt20':round(error,5)}
 if ssim is not None:item['ssim']=round(float(ssim(A.astype('uint8'),B.astype('uint8'),channel_axis=2,data_range=255)),5)
 Image.blend(ref,cur,0.5).save(out/f'page-{i:02}-overlay.png')
 ImageEnhance.Contrast(ImageChops.difference(ref,cur)).enhance(3).save(out/f'page-{i:02}-difference.png')
 result.append(item)
(out/'metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
