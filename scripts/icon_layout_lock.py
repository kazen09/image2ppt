import argparse,json
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--icons',required=True);p.add_argument('--scene',required=True);p.add_argument('--tolerance-px',type=float,default=2.0);p.add_argument('--report');a=p.parse_args()
 icons=json.loads(Path(a.icons).read_text(encoding='utf-8'))['icons'];data=json.loads(Path(a.scene).read_text(encoding='utf-8'))
 pages=data.get('pages',[]);fails=[];checked=0
 for i in icons:
  page=i.get('page',1)-1
  elements=pages[page].get('elements',[]) if 0<=page<len(pages) else []
  e=next((e for e in elements if e.get('id')==i.get('scene_id',i['id'])),None)
  if e is None:fails.append({'id':i['id'],'reason':'missing_scene_object'});continue
  reference=i['bbox'];actual=[e.get(k) for k in ('x','y','w','h')];checked+=1
  if any(not isinstance(n,(float,int)) or abs(float(n)-float(m))>a.tolerance_px for n,m in zip(actual,reference)):
   fails.append({'id':i['id'],'reason':'bbox_drift','expected':reference,'actual':actual})
 report={'pass':not fails,'checked':checked,'failures':fails}
 if a.report:Path(a.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False));raise SystemExit(0 if not fails else 2)
if __name__=='__main__':main()
