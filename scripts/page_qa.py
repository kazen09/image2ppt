"""Page-level native-object and layout QA (heuristics, not proof of visual fidelity)."""
import argparse, json
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

def audit(path):
    prs=Presentation(path)
    slides=[]
    for index,slide in enumerate(prs.slides,1):
        counts={"texts":0,"chars":0,"pictures":0,"connectors":0,"freeforms":0,"other":0}
        flags=[]
        W,H=prs.slide_width,prs.slide_height
        for pos,sh in enumerate(slide.shapes):
            name=sh.name
            if sh.shape_type==MSO_SHAPE_TYPE.PICTURE:
                counts['pictures']+=1
                if sh.left<=0 and sh.top<=0 and sh.width>=W*.98 and sh.height>=H*.98:
                    flags.append({"severity":"error","object":name,"issue":"near-full-slide image: not fully editable"})
            elif sh.shape_type==MSO_SHAPE_TYPE.LINE:counts['connectors']+=1
            elif sh.shape_type==MSO_SHAPE_TYPE.FREEFORM:counts['freeforms']+=1
            elif sh.has_text_frame and sh.text.strip():
                counts['texts']+=1; counts['chars']+=len(sh.text)
                if sh.width<=0 or sh.height<=0: flags.append({"severity":"error","object":name,"issue":"zero-area text box"})
            else:counts['other']+=1
            if sh.left < -W*.003 or sh.top < -H*.003 or sh.left+sh.width > W*1.003 or sh.top+sh.height>H*1.003:
                flags.append({"severity":"warning","object":name,"issue":"outside slide bounds"})
        if counts['freeforms']>100:
            flags.append({"severity":"error","issue":"excessive Freeform objects; possible contour explosion"})
        slides.append({"page":index,"counts":counts,"issues":flags,"passed_structure":not any(f['severity']=='error' for f in flags)})
    return {"pptx":str(path),"slides":slides,"structure_pass":all(s['passed_structure'] for s in slides)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('pptx');p.add_argument('--out');a=p.parse_args()
    data=audit(a.pptx)
    if a.out:Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(data,ensure_ascii=False,indent=2))
    raise SystemExit(0 if data['structure_pass'] else 2)
