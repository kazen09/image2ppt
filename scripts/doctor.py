"""Environment diagnostics. Exit 0 on a working core pipeline, report optional failures."""
import importlib,json,shutil,sys
from pathlib import Path
mods={'pptx':'python-pptx','PIL':'Pillow','cv2':'opencv','fontTools':'fonttools','lxml':'lxml','fitz':'PyMuPDF','skimage':'scikit-image','rapidfuzz':'rapidfuzz'}
optional={'paddleocr':'PaddleOCR (optional)','paddle':'PaddlePaddle runtime (optional)','cairosvg':'CairoSVG (optional)'}
res={'python':sys.version.split()[0], 'required':{},'optional':{},'executables':{}}
for k,v in mods.items():
 try:importlib.import_module(k);res['required'][v]='ok'
 except Exception as e:res['required'][v]=str(e)
for k,v in optional.items():
 try:importlib.import_module(k);res['optional'][v]='ok'
 except Exception as e:res['optional'][v]=type(e).__name__
for x in ('uv','soffice','libreoffice'):
 res['executables'][x]=shutil.which(x)
print(json.dumps(res,indent=2,ensure_ascii=False))
sys.exit(0 if all(v=='ok' for v in res['required'].values()) else 2)
