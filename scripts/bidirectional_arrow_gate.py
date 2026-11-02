import argparse, json

def check(connectors):
    issues = []
    for i, c in enumerate(connectors, 1):
        if c.get('direction') == 'both':
            if c.get('object_count', 1) != 1:
                issues.append({'index': i, 'reason': 'bidirectional_not_single_object'})
            if c.get('parallel_companion'):
                issues.append({'index': i, 'reason': 'bidirectional_split_parallel_lines'})
            if not c.get('arrow_head_start', False):
                issues.append({'index': i, 'reason': 'missing_start_arrow'})
            if not c.get('arrow_head_end', False):
                issues.append({'index': i, 'reason': 'missing_end_arrow'})
    return issues

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('scene_json')
    args = ap.parse_args()
    data = json.load(open(args.scene_json, 'r', encoding='utf-8'))
    issues = check(data.get('connectors', []))
    print(json.dumps({'ok': len(issues) == 0, 'issues': issues}, ensure_ascii=False, indent=2))
