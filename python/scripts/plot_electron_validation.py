"""Generate summary plots for electron validation results.

Produces PNG files in `results/`:
- plot_Ce_vs_N_MIN29.png
- plot_Me_vs_N.png
- plot_Cint_vs_MIN_NEUTRON.png
- heatmap_T5_pearson.png
"""
from pathlib import Path
import json
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

base_dir = Path(__file__).resolve().parents[1]
resdir = base_dir / 'results'
resdir.mkdir(exist_ok=True)

def latest(path_glob):
    p = list(base_dir.glob(path_glob))
    return Path(sorted([str(x) for x in p])[-1]) if p else None

# Load sweep_all JSON for |Ce| per run
sweep_all = latest('results/sweep_all_*.json')
sweep_summary = latest('results/sweep_summary_*.csv')
val = latest('results/electron_validation_results_*.json')

if not sweep_all or not sweep_summary or not val:
    raise SystemExit('Missing results files: ensure sweep_all, sweep_summary and validation JSON exist')

with sweep_all.open('r', encoding='utf-8') as f:
    sweep = json.load(f)

with val.open('r', encoding='utf-8') as f:
    validation = json.load(f)


def get_test_data(name):
    test = validation.get('tests', {}).get(name, {})
    if isinstance(test, dict):
        if 'data' in test and isinstance(test['data'], dict):
            return test['data']
        return test
    return {}

# 1) |Ce| vs N for MIN_NEUTRON=29
mn = 29
Ns = [60,100,200]
Ce_by_N = {}
for run in sweep.get('runs',[]):
    if int(run.get('MIN_NEUTRON'))==mn and int(run.get('N')) in Ns:
        Ce_by_N[int(run.get('N'))] = int(run.get('|Ce|', 0))

xs = sorted(Ce_by_N.keys())
ys = [Ce_by_N[x] for x in xs]
plt.figure()
plt.bar([str(x) for x in xs], ys)
plt.xlabel('N')
plt.ylabel('|Ce|')
plt.title(f'|Ce| vs N (MIN_NEUTRON={mn})')
out1 = resdir / f'plot_Ce_vs_N_MIN{mn}.png'
plt.savefig(out1, dpi=150, bbox_inches='tight')
plt.close()

# 2) Me vs N using validation T4
Me_by_N = {}
for k, v in get_test_data('T4').items():
    try:
        N = int(k)
        Me_by_N[N] = v.get('Me')
    except Exception:
        pass
xs = sorted(Me_by_N.keys())
ys = [Me_by_N[x] for x in xs]
plt.figure()
plt.plot(xs, ys, marker='o')
plt.xlabel('N')
plt.ylabel('Me')
plt.title('Me vs N (from validation T4)')
out2 = resdir / 'plot_Me_vs_N.png'
plt.savefig(out2, dpi=150, bbox_inches='tight')
plt.close()

# 3) Cint_n vs MIN_NEUTRON for each N (from sweep_summary CSV)
data = {}
with open(sweep_summary, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        N = int(row['N']); mn = int(row['MIN_NEUTRON']); cint = float(row['Cint_n'])
        data.setdefault(N,[]).append((mn,cint))

plt.figure(figsize=(8,5))
for N,vals in sorted(data.items()):
    vals = sorted(vals)
    xs = [m for m,_ in vals]; ys = [c for _,c in vals]
    plt.plot(xs, ys, marker='o', label=f'N={N}')
plt.xlabel('MIN_NEUTRON')
plt.ylabel('C_int^(n)')
plt.title('C_int^(n) vs MIN_NEUTRON')
plt.legend()
out3 = resdir / 'plot_Cint_vs_MIN_NEUTRON.png'
plt.savefig(out3, dpi=150, bbox_inches='tight')
plt.close()

# 4) Heatmap of Pearson correlations from T5
test_t5 = get_test_data('T5')
pearson = test_t5.get('pearson_by_MIN_NEUTRON', {})
if not pearson:
    bootstrap = test_t5.get('bootstrap', {})
    pearson = {mn: details.get('r_obs') for mn, details in bootstrap.items() if isinstance(details, dict) and 'r_obs' in details}
mn_keys = sorted([int(k) for k in pearson.keys()])
vals = [pearson[str(k)] for k in mn_keys]
arr = np.array(vals, dtype=float).reshape(1, -1)
plt.figure(figsize=(10,2))
plt.imshow(arr, aspect='auto', cmap='viridis', vmin=-1, vmax=1)
plt.colorbar(label='Pearson r')
plt.yticks([])
plt.xticks(range(len(mn_keys)), mn_keys, rotation=45)
plt.title('Pearson(|Ce|, Cint_n) vs MIN_NEUTRON')
out4 = resdir / 'heatmap_T5_pearson.png'
plt.savefig(out4, dpi=150, bbox_inches='tight')
plt.close()

print('Saved plots:', out1, out2, out3, out4)

if __name__ == '__main__':
    pass
