import argparse,json,sys
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--required-icons',required=True);a=p.parse_args()
d=json.loads(Path(a.scene).read_text(encoding='utf-8'));required=json.loads(Path(a.required_icons).read_text(encoding='utf-8'))
problems=[]
for pg_idx,p in enumerate(d['pages'],1):
 for ident in required.get(str(pg_idx),[]):
  matches=[e for e in p.get('elements',[]) if e.get('icon_id')==ident]
  if len(matches)!=1 or matches[0]['type']!='image' or matches[0].get('asset_origin')!='source_crop':
   problems.append(f'page {pg_idx} icon {ident}: missing source-cropped image')
  elif not Path(matches[0]['src']).is_file():problems.append(f'page {pg_idx} icon {ident}: cropped asset missing')
print(json.dumps({'passed':not problems,'issues':problems},ensure_ascii=False,indent=2));sys.exit(bool(problems))
