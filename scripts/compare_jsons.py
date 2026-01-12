#!/usr/bin/env python3
import json
from pathlib import Path

def load(p):
    return json.loads(Path(p).read_text())


def flatten(d, prefix=''):
    out={}
    if isinstance(d, dict):
        for k,v in d.items():
            path = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                if v == {}:
                    out[path] = v
                else:
                    # consider _locked flag as leaf
                    if '_locked' in v and len(v)==1:
                        out[path] = v
                    else:
                        out.update(flatten(v,prefix=path))
            elif isinstance(v, list):
                out[path] = v
            else:
                out[path] = v
    elif isinstance(d, list):
        for i,v in enumerate(d):
            path = f"{prefix}[{i}]"
            if isinstance(v,(dict,list)):
                out.update(flatten(v,prefix=path))
            else:
                out[path]=v
    else:
        out[prefix]=d
    return out


def classify(a_val,b_val):
    if b_val is None:
        return 'null'
    if b_val == {}:
        return 'empty_obj'
    if isinstance(b_val, dict) and b_val.get('_locked'):
        return 'locked'
    if a_val==b_val:
        return 'same'
    return 'different'


def diff(a,b):
    fa=flatten(a)
    fb=flatten(b)
    a_keys=set(fa.keys())
    b_keys=set(fb.keys())
    missing_in_b = sorted(list(a_keys - b_keys))
    missing_in_a = sorted(list(b_keys - a_keys))
    differing=[]
    nulls=[]
    locked=[]
    same=[]
    for k in sorted(a_keys & b_keys):
        cls = classify(fa[k], fb[k])
        if cls=='same': same.append(k)
        elif cls=='different': differing.append(k)
        elif cls=='null': nulls.append(k)
        elif cls=='empty_obj': nulls.append(k)
        elif cls=='locked': locked.append(k)
    return {
        'count_a_keys': len(a_keys),
        'count_b_keys': len(b_keys),
        'missing_in_b_count': len(missing_in_b),
        'missing_in_a_count': len(missing_in_a),
        'differing_count': len(differing),
        'null_or_empty_count': len(nulls),
        'locked_count': len(locked),
        'samples': {
            'missing_in_b': missing_in_b[:30],
            'missing_in_a': missing_in_a[:30],
            'differing': differing[:30],
            'null_or_empty': nulls[:30],
            'locked': locked[:30]
        }
    }

if __name__=='__main__':
    base = Path('tests/debug_outputs')
    files = {
     'device_free': base / 'backend_device_free.json',
     'paid': base / 'backend_paid.json',
     'paid_general': base / 'backend_paid_general.json'
    }
    objs = {k: json.loads(p.read_text()) for k,p in files.items()}
    pairs = [('device_free','paid'),('device_free','paid_general'),('paid','paid_general')]
    for a,b in pairs:
        res = diff(objs[a], objs[b])
        print(f"\nCOMPARE {a} -> {b}")
        for k,v in res.items():
            if k!='samples':
                print(f"  {k}: {v}")
        print('  samples:')
        for sname,arr in res['samples'].items():
            print(f"    {sname} (count {len(arr)}):")
            for p in arr:
                print(f"      - {p}")
