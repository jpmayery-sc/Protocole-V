"""Bootstrap statistics for T5: Pearson correlation significance and CI.

Loads latest `results/sweep_all_*.json` and `results/electron_validation_results_*.json`.
For each `MIN_NEUTRON` present in the sweep, computes observed Pearson r between
`|Ce|` and `Cint_n`, performs bootstrap resampling to estimate a two-sided p-value
and a 95% percentile confidence interval. Results are appended to the validation
JSON and written to a new timestamped JSON and a short text report in `results/`.
"""
from pathlib import Path
import json, time
import numpy as np
import argparse
from datetime import datetime, timezone

def latest(glob_pattern):
    p = sorted(Path('.').glob(glob_pattern))
    return p[-1] if p else None

resdir = Path('results')
resdir.mkdir(exist_ok=True)

sweep_file = latest('results/sweep_all_*.json')
val_file = latest('results/electron_validation_results_*.json')
if not sweep_file or not val_file:
    raise SystemExit('Missing required results files')

with sweep_file.open('r', encoding='utf-8') as f:
    sweep = json.load(f)

with val_file.open('r', encoding='utf-8') as f:
    val = json.load(f)

# Aggregate pairs by MIN_NEUTRON
pairs = {}
for run in sweep.get('runs', []):
    try:
        mn = int(run.get('MIN_NEUTRON'))
        ce = float(run.get('|Ce|', 0))
        cint = float(run.get('Cint_n', 0))
        pairs.setdefault(mn, []).append((ce, cint))
    except Exception:
        continue

def pearson_r(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    if x.size < 2:
        return float('nan')
    return float(np.corrcoef(x, y)[0,1])

parser = argparse.ArgumentParser(description='Bootstrap T5 statistics')
parser.add_argument('--nsamples', type=int, default=3000, help='Number of bootstrap samples')
parser.add_argument('--seed', type=int, default=12345, help='RNG seed')
args = parser.parse_args()

rng = np.random.default_rng(args.seed)
res = {}
nsamples = int(args.nsamples)

for mn, arr in sorted(pairs.items()):
    arr = np.array(arr)
    if arr.shape[0] < 3:
        res[mn] = {'n': int(arr.shape[0]), 'error': 'too few samples'}
        continue
    x = arr[:,0]
    y = arr[:,1]
    r_obs = pearson_r(x, y)
    boots = []
    n = len(x)
    for _ in range(nsamples):
        idx = rng.integers(0, n, size=n)
        boots.append(pearson_r(x[idx], y[idx]))
    boots = np.array(boots)
    # two-sided p-value via bootstrap
    pval = float((np.sum(np.abs(boots) >= abs(r_obs)) + 1) / (len(boots) + 1))
    ci_low, ci_high = np.percentile(boots, [2.5, 97.5])
    res[mn] = {
        'n': int(n),
        'r_obs': float(r_obs),
        'p_value': float(pval),
        'ci_95': [float(ci_low), float(ci_high)],
        'nsamples': nsamples
    }

# Attach to validation JSON under tests.T5.bootstrap
val.setdefault('tests', {})
val['tests'].setdefault('T5', {})
val['tests']['T5'].setdefault('data', {})
val['tests']['T5']['data']['bootstrap'] = {str(k): v for k,v in res.items()}

ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%SZ')
out_json = resdir / f'electron_validation_results_with_bootstrap_{ts}.json'
with out_json.open('w', encoding='utf-8') as f:
    json.dump(val, f, indent=2, ensure_ascii=False)

report = resdir / f'electron_validation_bootstrap_report_{ts}.txt'
with report.open('w', encoding='utf-8') as f:
    f.write('Bootstrap T5 report\n')
    f.write(f'generated: {ts} UTC\n\n')
    for mn, d in sorted(res.items()):
        f.write(f'MIN_NEUTRON = {mn}\n')
        if 'error' in d:
            f.write(f"  n = {d.get('n')} -> {d.get('error')}\n\n")
            continue
        f.write(f"  n = {d['n']}\n")
        f.write(f"  r_obs = {d['r_obs']:.6f}\n")
        f.write(f"  p_value = {d['p_value']:.6e}\n")
        f.write(f"  95% CI = [{d['ci_95'][0]:.6f}, {d['ci_95'][1]:.6f}]\n")
        f.write(f"  bootstrap samples = {d['nsamples']}\n\n")

print('Wrote', out_json, report)

if __name__ == '__main__':
    pass
