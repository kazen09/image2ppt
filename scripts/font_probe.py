"""Inspect installed fonts and produce text length measurements; no unsupported claims of exact font identification."""
import argparse,json
from pathlib import Path
from PIL import ImageFont

FONTS=[Path('C:/Windows/Fonts'),Path('/usr/share/fonts'),Path.home()/'.fonts',Path.home()/'.local/share/fonts']

def main():
    p=argparse.ArgumentParser();p.add_argument('--text',required=True);p.add_argument('--size',type=int,default=24);p.add_argument('--out',required=True);p.add_argument('--font-dir',action='append');a=p.parse_args()
    dirs=[Path(x) for x in a.font_dir] if a.font_dir else FONTS
    entries=[]
    for directory in dirs:
        if not directory.is_dir():continue
        for f in sorted(directory.rglob('*')):
            if f.suffix.lower() not in ('.ttf','.otf','.ttc'):continue
            try:
                font=ImageFont.truetype(str(f),a.size)
                box=font.getbbox(a.text)
                entries.append({'font_file':str(f),'font_index':0,'bbox_px':list(box),'advance_px':round(font.getlength(a.text),2)})
            except Exception:continue
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({'text':a.text,'size_px':a.size,'candidates':entries,'note':'Dimensions only. Does not identify source font without image comparison.'},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Candidates={len(entries)} -> {out}')
if __name__=='__main__':main()
