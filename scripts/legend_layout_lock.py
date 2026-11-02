import argparse, json

def validate_legend(items):
    issues = []
    for idx, item in enumerate(items, 1):
        if item.get('arrow_length', 0) < 20:
            issues.append({'index': idx, 'reason': 'arrow_too_short'})
        if item.get('label_w', 0) <= 0 or item.get('label_h', 0) <= 0:
            issues.append({'index': idx, 'reason': 'invalid_label_box'})
        if item.get('gap', 0) < 4:
            issues.append({'index': idx, 'reason': 'gap_too_small'})
    return issues

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('scene_json')
    args = ap.parse_args()
    data = json.load(open(args.scene_json, 'r', encoding='utf-8'))
    items = data.get('legend_items', [])
    issues = validate_legend(items)
    print(json.dumps({'ok': len(issues) == 0, 'issues': issues}, ensure_ascii=False, indent=2))
