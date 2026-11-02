"""Optional local PaddleOCR 3.x adapter. No fabricated OCR on failure."""
import argparse
import json
import sys
from pathlib import Path


def extract(path):
    try:
        from paddleocr import PaddleOCR
    except ImportError as e:
        raise RuntimeError('PaddleOCR missing; run uv sync --extra ocr and install matching paddlepaddle inference runtime') from e
    try:
        engine = PaddleOCR(use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False)
        result = engine.predict(str(path))
    except Exception as e:
        raise RuntimeError(f'OCR initialization/inference failed: {e}') from e
    lines = []
    for page in result:
        payload = getattr(page, 'json', None)
        if callable(payload):
            payload = payload()
        if not isinstance(payload, dict):
            raise RuntimeError('Unexpected PaddleOCR result layout: cannot safely parse; update adapter')
        data = payload.get('res', payload)
        texts = data.get('rec_texts', [])
        scores = data.get('rec_scores', [])
        polys = data.get('rec_polys', data.get('dt_polys', []))
        if len(texts) != len(polys):
            raise RuntimeError('OCR texts and polygons are inconsistent')
        for i, (text, polygon) in enumerate(zip(texts, polys)):
            points = polygon.tolist() if hasattr(polygon,'tolist') else polygon
            xs = [float(p[0]) for p in points]
            ys = [float(p[1]) for p in points]
            lines.append({'text': str(text), 'confidence': float(scores[i]) if i < len(scores) else None,
                          'bbox': [min(xs), min(ys), max(xs), max(ys)], 'polygon': points})
    return {'source': str(path), 'engine':'PaddleOCR 3.x', 'lines':lines, 'review_required':[
        i for i,x in enumerate(lines) if x['confidence'] is None or x['confidence'] < 0.9]}


def main():
    p=argparse.ArgumentParser();p.add_argument('image');p.add_argument('--out',required=True);a=p.parse_args()
    data=extract(Path(a.image));out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'OCR lines={len(data["lines"])} review={len(data["review_required"])} -> {out}')

if __name__=='__main__':
    try: main()
    except Exception as ex: print(f'ERROR: {ex}',file=sys.stderr);sys.exit(2)
