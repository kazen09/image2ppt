"""Validate *scene* text against transcribed source segments; not OCR itself."""
import argparse, json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--scene',required=True);p.add_argument('--ledger',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    scene=json.loads(Path(a.scene).read_text(encoding='utf-8')); ledger=json.loads(Path(a.ledger).read_text(encoding='utf-8'))
    contents=[o.get('text','') for page in scene.get('pages',[]) for o in page.get('elements',[]) if o.get('type')=='text']
    contents += [str(run.get('text','')) for page in scene.get('pages',[]) for o in page.get('elements',[]) if o.get('type')=='text' for run in o.get('runs',[])]
    combined='\n'.join(contents); missing=[]
    for item in ledger.get('required',[]):
        value=item if isinstance(item,str) else item['text']
        if value not in combined:missing.append(value)
    chars=sum(len(c) for c in contents)
    issues=[]
    if chars<int(ledger.get('minimum_characters',0)):issues.append('Scene has fewer text characters than ledger minimum')
    report={'pass':not missing and not issues,'missing':missing,'scene_characters':chars,'issues':issues}
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False));raise SystemExit(0 if report['pass'] else 2)
if __name__=='__main__':main()
