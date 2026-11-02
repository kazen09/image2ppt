import argparse, json

def inspect_styles(data):
    report = []
    for idx, shape in enumerate(data.get('shapes', []), 1):
        report.append({
            'index': idx,
            'name': shape.get('name', ''),
            'fill': shape.get('fill', None),
            'gradient': bool(shape.get('gradient_stops')),
            'line_color': shape.get('line_color', None),
            'line_width': shape.get('line_width', None),
            'shadow': bool(shape.get('shadow')),
            'corner_radius': shape.get('corner_radius', None),
        })
    return report

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('scene_json')
    args = ap.parse_args()
    data = json.load(open(args.scene_json, 'r', encoding='utf-8'))
    print(json.dumps({'shapes': inspect_styles(data)}, ensure_ascii=False, indent=2))
