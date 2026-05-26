"""Run a denser sweep over N and MIN_NEUTRON, plus targeted dense replicates.

This script reuses `sweep` and `save_outputs` from `scripts/sweep_min_neutron.py`.
Usage example:
  python scripts/run_dense_and_replicates.py --N-min 40 --N-max 300 --N-step 10 --mn-min 20 --mn-max 35 --mn-step 1 --extra-mns 26,29,33 --extra-N-step 5
"""
import runpy
import argparse
from pathlib import Path
import time
import json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--N-min', type=int, default=40)
    parser.add_argument('--N-max', type=int, default=300)
    parser.add_argument('--N-step', type=int, default=10)
    parser.add_argument('--mn-min', type=int, default=20)
    parser.add_argument('--mn-max', type=int, default=35)
    parser.add_argument('--mn-step', type=int, default=1)
    parser.add_argument('--extra-mns', type=str, default='26,29,33', help='Comma list')
    parser.add_argument('--extra-N-step', type=int, default=5)
    args = parser.parse_args()

    ns = list(range(args.N_min, args.N_max + 1, args.N_step))
    mn_range = range(args.mn_min, args.mn_max + 1, args.mn_step)

    ns_module = runpy.run_path('scripts/sweep_min_neutron.py')
    sweep = ns_module.get('sweep')
    save_outputs = ns_module.get('save_outputs')

    print('Running base dense sweep: N values:', ns)
    out = sweep(N_values=ns, mn_range=mn_range, min_global=-1)

    # targeted extra dense runs for selected MIN_NEUTRON values
    extra_mns = [int(x) for x in args.extra_mns.split(',') if x]
    for emn in extra_mns:
        dense_ns = list(range(args.N_min, args.N_max + 1, args.extra_N_step))
        print(f'Running extra dense for MIN_NEUTRON={emn}, Ns step {args.extra_N_step} -> {len(dense_ns)} runs per N')
        out_extra = sweep(N_values=dense_ns, mn_range=[emn], min_global=-1)
        # append runs and summary entries
        out['runs'].extend(out_extra.get('runs', []))
        out['summary'].extend(out_extra.get('summary', []))

    # deduplicate summary by (N, MIN_NEUTRON) keeping last
    seen = {}
    new_summary = []
    for s in out['summary']:
        key = (s['N'], s['MIN_NEUTRON'])
        seen[key] = s
    for k, v in sorted(seen.items()):
        new_summary.append(v)
    out['summary'] = new_summary

    ts = time.strftime('%Y%m%d-%H%M%SZ')
    p = Path('results')
    p.mkdir(exist_ok=True)
    json_path = p / f'sweep_all_dense_{ts}.json'
    json_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')

    paths = save_outputs(out, mn_range, ns)
    print('Saved dense sweep outputs:', json_path, paths)


if __name__ == '__main__':
    main()
