"""Scene manifest to PPTX. Non-trivial alpha gradients/shadows via DrawingML, visual verification required."""
import argparse,json,math,re
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN,MSO_ANCHOR,MSO_AUTO_SIZE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn

def col(s):
 s=(s or '#000000').lstrip('#');return RGBColor.from_string(s.upper())
def alpha(x): return max(0,min(100000,int(float(x)*100000)))
def child(tag, parent, attrs={}):
 e=OxmlElement(tag)
 for k,v in attrs.items(): e.set(k,str(v))
 parent.append(e);return e

def add_gradient(shape,grad):
 spPr=shape._element.spPr
 for elt in list(spPr):
  if elt.tag in (qn('a:solidFill'),qn('a:noFill'),qn('a:gradFill'),qn('a:pattFill')):spPr.remove(elt)
 root=child('a:gradFill',spPr,{'rotWithShape':'1'});stops=child('a:gsLst',root)
 for stop in grad.get('stops',[]):
  e=child('a:gs',stops,{'pos':int(float(stop['pos'])*100000)}); c=child('a:srgbClr',e,{'val':stop['color'].lstrip('#').upper()})
  if float(stop.get('opacity',1))<1:child('a:alpha',c,{'val':alpha(stop['opacity'])})
 child('a:lin',root,{'ang':int(float(grad.get('angle',0))*60000),'scaled':'1'})

def add_shadow(shape,spec):
 spPr=shape._element.spPr; effect=spPr.find(qn('a:effectLst'))
 if effect is None:effect=child('a:effectLst',spPr)
 blur=int(float(spec.get('blur_pt',4))*12700)
 distance=int(float(spec.get('distance_pt',2))*12700)
 angle=int(float(spec.get('angle',45))*60000)
 outer=child('a:outerShdw',effect,{'blurRad':blur,'dist':distance,'dir':angle,'algn':'ctr','rotWithShape':'0'})
 color=child('a:srgbClr',outer,{'val':spec.get('color','#000000').lstrip('#').upper()})
 child('a:alpha',color,{'val':alpha(spec.get('opacity',0.25))})

def fill_shape(shape,obj):
 spec=obj.get('fill')
 if not spec:shape.fill.background();return
 if 'gradient' in spec: add_gradient(shape,spec['gradient'])
 else:
  shape.fill.solid();shape.fill.fore_color.rgb=col(spec.get('color','#FFFFFF'))
  if 'opacity' in spec:
   sr=shape._element.spPr.find('.//'+qn('a:srgbClr'))
   if sr is not None:child('a:alpha',sr,{'val':alpha(spec['opacity'])})

def stroke(shape,spec):
 if not spec:shape.line.fill.background();return
 shape.line.color.rgb=col(spec.get('color','#000000'));shape.line.width=Pt(float(spec.get('width_pt',1)))
 if 'opacity' in spec:
  sr=shape._element.spPr.find('.//'+qn('a:ln')+'/'+qn('a:solidFill')+'/'+qn('a:srgbClr'))
  if sr is not None:child('a:alpha',sr,{'val':alpha(spec['opacity'])})

def add_arrow_ends(shape,obj):
 """Arrowhead is part of the line in DrawingML, not a separate triangle."""
 ln=shape._element.spPr.find(qn('a:ln'))
 if ln is None:
  ln=child('a:ln',shape._element.spPr)
 for tag in ('a:headEnd','a:tailEnd'):
  for old in list(ln):
   if old.tag==qn(tag):ln.remove(old)
 for key,tag in (('begin_arrow','a:headEnd'),('end_arrow','a:tailEnd')):
  val=obj.get(key)
  if not val or val=='none':continue
  if val not in ('triangle','stealth','diamond','oval','arrow'):
   raise ValueError(f'Unsupported arrow shape {val}')
  child(tag,ln,{'type':val,'w':obj.get('arrow_width','med'),'len':obj.get('arrow_length','med')})

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--scene',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
 source=Path(a.scene).resolve();data=json.loads(source.read_text(encoding='utf-8'));s=data['slide'];W=s['width_px'];H=s['height_px'];iw=float(s.get('width_in',13.333333)); scale=iw/W
 prs=Presentation();prs.slide_width=Inches(iw);prs.slide_height=Inches(H*scale)
 def u(v):return Inches(float(v)*scale)
 def image_path(s):
  p=Path(s);return p if p.is_absolute() else source.parent/p
 for pg in data['pages']:
  slide=prs.slides.add_slide(prs.slide_layouts[6]); bg=pg.get('background',{})
  if 'image' in bg:
   p=image_path(bg['image']); assert p.exists(),f'Missing {p}';slide.shapes.add_picture(str(p),0,0,width=prs.slide_width,height=prs.slide_height)
  else:slide.background.fill.solid();slide.background.fill.fore_color.rgb=col(bg.get('color','#FFFFFF'))
  items=sorted(enumerate(pg.get('elements',[])),key=lambda pair:(pair[1].get('z',pair[0]),pair[0]))
  for idx,o in items:
   kind=o['type'];x,y,w,h=map(lambda n:float(o[n]),('x','y','w','h'))
   if kind=='connector':
    variant=o.get('geometry','straight')
    ctype={'straight':MSO_CONNECTOR.STRAIGHT,'elbow':MSO_CONNECTOR.ELBOW,'curve':MSO_CONNECTOR.CURVE}.get(variant)
    if ctype is None:raise ValueError(f'Unsupported connector geometry {variant}')
    # End coordinates are x+w, y+h. Negative deltas supported.
    sh=slide.shapes.add_connector(ctype,u(x),u(y),u(x+w),u(y+h))
    stroke(sh,o.get('border',{'color':'#0066CC','width_pt':2}))
    add_arrow_ends(sh,o)
    continue
   if kind=='image':
    p=image_path(o['src']);assert p.exists(),f'Missing {p}'
    sh=slide.shapes.add_picture(str(p),u(x),u(y),width=u(w),height=u(h))
    if o.get('rotation'):sh.rotation=float(o['rotation'])
    continue
   if kind=='shape':
    geom=o.get('geometry','rect')
    if geom=='line': sh=slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,u(x),u(y),u(x+w),u(y+h))
    else:
     shape_type={'rect':MSO_SHAPE.RECTANGLE,'roundRect':MSO_SHAPE.ROUNDED_RECTANGLE,'ellipse':MSO_SHAPE.OVAL}.get(geom)
     if shape_type is None:raise ValueError(f'Unsupported shape {geom}')
     sh=slide.shapes.add_shape(shape_type,u(x),u(y),u(w),u(h));fill_shape(sh,o)
    stroke(sh,o.get('border'))
    if o.get('shadow'):add_shadow(sh,o['shadow'])
    if o.get('rotation'):sh.rotation=float(o['rotation'])
    continue
   if kind=='text':
    sh=slide.shapes.add_textbox(u(x),u(y),u(w),u(h));tf=sh.text_frame;tf.clear();tf.word_wrap=o.get('word_wrap',True);tf.auto_size=MSO_AUTO_SIZE.NONE
    mg=o.get('margin_px',0); mg=[mg]*4 if not isinstance(mg,list) else mg
    tf.margin_left=u(mg[0]);tf.margin_top=u(mg[1]);tf.margin_right=u(mg[2]);tf.margin_bottom=u(mg[3])
    tf.vertical_anchor={'top':MSO_ANCHOR.TOP,'middle':MSO_ANCHOR.MIDDLE,'bottom':MSO_ANCHOR.BOTTOM}.get(o.get('valign','top'),MSO_ANCHOR.TOP)
    lines=o.get('text','').split('\n') if 'runs' not in o else [None]
    for i,line in enumerate(lines):
     p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
     p.alignment={'left':PP_ALIGN.LEFT,'center':PP_ALIGN.CENTER,'right':PP_ALIGN.RIGHT}.get(o.get('align','left'),PP_ALIGN.LEFT)
     if 'line_spacing' in o:p.line_spacing=float(o['line_spacing'])
     runs=o.get('runs') if 'runs' in o else [{'text':line}]
     for rs in runs:
      r=p.add_run();r.text=rs.get('text','');f=r.font
      f.name=rs.get('font_family',o.get('font_family','Arial'))
      f.size=Pt(float(rs.get('font_size_pt',o.get('font_size_pt',18))))
      f.bold=bool(rs.get('bold',o.get('bold',False)));f.italic=bool(rs.get('italic',o.get('italic',False)))
      f.color.rgb=col(rs.get('color',o.get('color','#000000')))
    if o.get('fill'):fill_shape(sh,o)
    if o.get('border'):stroke(sh,o['border'])
    if o.get('shadow'):add_shadow(sh,o['shadow'])
    if o.get('rotation'):sh.rotation=float(o['rotation'])
    continue
   raise ValueError(f'Unknown type: {kind}')
 out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);prs.save(out);print('Saved',out,'slides',len(prs.slides))
if __name__=='__main__':main()
