"""Reject obvious regressions between candidate and baseline PPTX; not a visual metric."""
import argparse,json
from pathlib import Path
from page_qa import audit
p=argparse.ArgumentParser();p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True);p.add_argument('--out');p.add_argument('--min-text-ratio',type=float,default=.97);a=p.parse_args()
base=audit(a.baseline);cand=audit(a.candidate); issues=[]
if len(base['slides'])!=len(cand['slides']):issues.append('Slide count changed')
for old,new in zip(base['slides'],cand['slides']):
    b=old['counts']['chars'];c=new['counts']['chars']
    if b>0 and c/b<a.min_text_ratio:issues.append(f"page {old['page']} characters dropped: {b} -> {c}")
    if new['counts']['freeforms']>max(old['counts']['freeforms']+100,100):issues.append(f"page {old['page']} freeform explosion")
    if not new['passed_structure']:issues.append(f"page {old['page']} structure errors")
report={'pass':not issues,'issues':issues,'baseline':a.baseline,'candidate':a.candidate}
if a.out:Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(0 if not issues else 2)
