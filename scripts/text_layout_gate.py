import argparse, json

def check_textboxes(data):
    issues = []
    for idx, tb in enumerate(data.get('text_boxes', []), 1):
        w = tb.get('w', 0)
        h = tb.get('h', 0)
        fs = tb.get('font_size', 0)
        text = tb.get('text', '')
        lines = max(1, int(tb.get('line_count', 1)))
        if w <= 0 or h <= 0:
            issues.append({'index': idx, 'reason': 'invalid_size', 'text': text[:30]})
        if fs and h and lines and fs * lines * 1.0 > h * 1.15:
            issues.append({'index': idx, 'reason': 'possible_overflow', 'text': text[:30]})
        if tb.get('auto_shrink'):
            issues.append({'index': idx, 'reason': 'auto_shrink_enabled', 'text': text[:30]})
    return issues

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('scene_json')
    args = ap.parse_args()
    data = json.load(open(args.scene_json, 'r', encoding='utf-8'))
    issues = check_textboxes(data)
    print(json.dumps({'ok': len(issues) == 0, 'issues': issues}, ensure_ascii=False, indent=2))
