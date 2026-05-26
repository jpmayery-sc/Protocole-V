"""Sweep MIN_NEUTRON over a range for several N values, save JSON/CSV/LaTeX and plot.

Produces files in `results/`: `sweep_N<NN>.json`, `sweep_summary.csv`, `sweep_table.tex`, `sweep_plot.png`.
"""
import json
from pathlib import Path
import csv
import time
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import runpy

# load run_with_params from scripts/run_triangles_with_params.py
ns_wrapper = runpy.run_path('scripts/run_triangles_with_params.py')
run_with_params = ns_wrapper.get('run_with_params')


def sweep(N_values=(60,100,200), mn_range=range(20,36), min_global=-1):
    out = {'runs': [], 'summary': []}
    for N in N_values:
        row = []
        for mn in mn_range:
            params = {'N': N, 'MIN_NEUTRON': mn, 'MIN_GLOBAL': min_global}
            r = run_with_params(N=N, MIN_NEUTRON=mn, MIN_GLOBAL=min_global)
            r['N'] = N
            r['MIN_NEUTRON'] = mn
            out['runs'].append(r)
            row.append((mn, r.get('Cint_n'), r.get('lambda_pred'), r.get('|Cn|')))
            out['summary'].append({'N': N, 'MIN_NEUTRON': mn, 'Cint_n': r.get('Cint_n'), 'lambda_pred': r.get('lambda_pred'), '|Cn|': r.get('|Cn|'), 'eps': r.get('eps')})

    return out


def save_outputs(out, mn_range, N_values):
    ts = time.strftime('%Y%m%d-%H%M%SZ')
    p = Path('results')
    p.mkdir(exist_ok=True)

    json_path = p / f'sweep_all_{ts}.json'
    json_path.write_text(json.dumps(out, indent=2, default=str, ensure_ascii=False), encoding='utf-8')

    csv_path = p / f'sweep_summary_{ts}.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['N','MIN_NEUTRON','Cint_n','lambda_pred','|Cn|','eps'])
        writer.writeheader()
        for r in out['summary']:
            writer.writerow(r)

    # LaTeX table: one row per MIN_NEUTRON with columns for each N's Cint_n
    tex_lines = []
    header = 'MIN_NEUTRON & ' + ' & '.join([f'N={N}' for N in N_values]) + ' \\\\'
    tex_lines.append('\\begin{tabular}{r' + 'r'*len(N_values) + '}')
    tex_lines.append('\\toprule')
    tex_lines.append(header)
    tex_lines.append('\\midrule')
    for mn in mn_range:
        vals = []
        for N in N_values:
            # find entry
            entry = next((x for x in out['summary'] if x['N']==N and x['MIN_NEUTRON']==mn), None)
            vals.append(f"{entry['Cint_n']:.6f}" if entry and entry['Cint_n'] is not None and (not (isinstance(entry['Cint_n'], float) and math.isnan(entry['Cint_n']))) else 'nan')
        tex_lines.append(str(mn) + ' & ' + ' & '.join(vals) + ' \\\\')
    tex_lines.append('\\bottomrule')
    tex_lines.append('\\end{tabular}')

    tex_path = p / f'sweep_table_{ts}.tex'
    tex_path.write_text('\n'.join(tex_lines), encoding='utf-8')

    # plot
    plt.figure(figsize=(8,5))
    for N in N_values:
        xs = []
        ys = []
        for mn in mn_range:
            entry = next((x for x in out['summary'] if x['N']==N and x['MIN_NEUTRON']==mn), None)
            xs.append(mn)
            ys.append(entry['Cint_n'] if entry and entry['Cint_n'] is not None and not (isinstance(entry['Cint_n'], float) and math.isnan(entry['Cint_n'])) else float('nan'))
        plt.plot(xs, ys, marker='o', label=f'N={N}')
    plt.xlabel('MIN_NEUTRON')
    plt.ylabel('C_int^(n)')
    plt.title('Sweep MIN_NEUTRON')
    plt.legend()
    plt.grid(True)
    plot_path = p / f'sweep_plot_{ts}.png'
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()

    return {'json': str(json_path), 'csv': str(csv_path), 'tex': str(tex_path), 'png': str(plot_path)}


def main():
    mn_range = range(20,36)
    N_values = (60,100,200)
    out = sweep(N_values=N_values, mn_range=mn_range, min_global=-1)
    paths = save_outputs(out, mn_range, N_values)
    print('Saved:', paths)


if __name__ == '__main__':
    main()
