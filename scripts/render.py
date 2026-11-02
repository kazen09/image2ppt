import argparse,subprocess,tempfile,shutil
from pathlib import Path
import fitz
p=argparse.ArgumentParser();p.add_argument('--pptx',required=True);p.add_argument('--out',required=True);p.add_argument('--dpi',type=int,default=144);a=p.parse_args()
out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
libre=shutil.which('soffice') or shutil.which('libreoffice')
if not libre:raise SystemExit('LibreOffice not available. Export slides to PNG from PowerPoint manually instead.')
with tempfile.TemporaryDirectory() as d:
 cmd=[libre,'-env:UserInstallation=file://'+str(Path(d,'lo_profile')),'--headless','--convert-to','pdf','--outdir',d,str(Path(a.pptx).resolve())]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
 pdf=Path(d,Path(a.pptx).stem+'.pdf')
 if r.returncode or not pdf.exists():raise SystemExit(f'LibreOffice failed: {r.stdout} {r.stderr}')
 doc=fitz.open(pdf)
 for i,page in enumerate(doc,1):
  pix=page.get_pixmap(matrix=fitz.Matrix(a.dpi/72,a.dpi/72),alpha=False)
  pix.save(str(out/f'page-{i:02}.png'))
print('Rendered',len(doc),'slides into',out)
