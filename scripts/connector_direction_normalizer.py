import argparse, json

def normalize(connectors):
    out = []
    for c in connectors:
        item = dict(c)
        if item.get('semantic') in ('query_response', 'bidirectional', 'request_response'):
            item['direction'] = 'both'
            item['arrow_head_start'] = True
            item['arrow_head_end'] = True
            item['object_count'] = 1
            item['parallel_companion'] = None
            if 'render_mode' not in item:
                item['render_mode'] = 'single_path_bidirectional'
        out.append(item)
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('scene_json')
    args = ap.parse_args()
    data = json.load(open(args.scene_json, 'r', encoding='utf-8'))
    data['connectors'] = normalize(data.get('connectors', []))
    print(json.dumps(data, ensure_ascii=False, indent=2))
