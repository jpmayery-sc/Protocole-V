"""Validate Electron-2.txt assertions via numeric tests (T1-T5).

Produces outputs in results/: per-test JSON and a summary report.
"""
import json
import time
from pathlib import Path
import runpy
import csv
import math

ts = time.strftime('%Y%m%d-%H%M%SZ')
outdir = Path('results')
outdir.mkdir(exist_ok=True)

# Load run_with_params helper
ns = runpy.run_path('scripts/run_triangles_with_params.py')
run_with_params = ns.get('run_with_params')

results = {'timestamp': ts, 'tests': {}}

def save_json(name, data):
    p = outdir / f'{name}_{ts}.json'
    p.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False), encoding='utf-8')
    return str(p)

# Test T1: Presence of electrons for N=60
def test_T1():
    r1 = run_with_params(N=60, MIN_NEUTRON=25, MIN_GLOBAL=-1)
    r2 = run_with_params(N=60, MIN_NEUTRON=29, MIN_GLOBAL=-1)
    ok1 = r1.get('|Ce|',0) > 0
    ok2 = r2.get('|Ce|',0) > 0
    data = {'r_MIN25': r1, 'r_MIN29': r2, 'ok_MIN25_Ce_pos': ok1, 'ok_MIN29_Ce_pos': ok2}
    path = save_json('T1_presence_Ce_N60', data)
    return path, data

# Test T2: Sensitivity to MIN_GLOBAL
def test_T2():
    a = run_with_params(N=60, MIN_NEUTRON=29, MIN_GLOBAL=29)
    b = run_with_params(N=60, MIN_NEUTRON=29, MIN_GLOBAL=-1)
    data = {'with_MIN_GLOBAL_29': a, 'without_MIN_GLOBAL': b}
    data['delta_Cp'] = b.get('|Cp|',0) - a.get('|Cp|',0)
    data['delta_Ce'] = b.get('|Ce|',0) - a.get('|Ce|',0)
    path = save_json('T2_sensitivity_MIN_GLOBAL', data)
    return path, data

# Test T3: Relation annihilation/libération (compare Mp/Me)
def test_T3():
    a = run_with_params(N=100, MIN_NEUTRON=29, MIN_GLOBAL=29)
    b = run_with_params(N=100, MIN_NEUTRON=29, MIN_GLOBAL=-1)
    data = {'with_MIN_GLOBAL_29': a, 'without_MIN_GLOBAL': b}
    if b.get('Me') and a.get('Me'):
        data['ratio_Me'] = b.get('Me') / a.get('Me') if a.get('Me') else None
    path = save_json('T3_annihilation_relation_N100', data)
    return path, data

# Test T4: Evolution of Ce with N
def test_T4():
    Ns = [60,100,200]
    out = {}
    for N in Ns:
        r = run_with_params(N=N, MIN_NEUTRON=29, MIN_GLOBAL=-1)
        out[N] = r
    path = save_json('T4_Ce_vs_N', out)
    return path, out

# Test T5: Correlation |Ce| vs Cint_n from sweep CSV
def pearson(xs, ys):
    n = len(xs)
    if n==0: return float('nan')
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den = math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return num/den if den!=0 else float('nan')

def test_T5():
    # Prefer sweep_all JSON (contains |Ce|). Fallback to CSV if needed.
    jsonp = list(outdir.glob('sweep_all_*.json'))
    rows = []
    if jsonp:
        path = str(jsonp[-1])
        j = json.loads(Path(path).read_text(encoding='utf-8'))
        for r0 in j.get('runs',[]):
            rows.append({'N':int(r0.get('N')),'MIN_NEUTRON':int(r0.get('MIN_NEUTRON')),'Cint_n':r0.get('Cint_n'),'|Ce|':r0.get('|Ce|'),'eps':r0.get('eps')})
    else:
        csvp = list(outdir.glob('sweep_summary_*.csv'))
        if not csvp:
            return None, {'error':'sweep CSV/json not found'}
        path = str(csvp[-1])
        with open(path,newline='',encoding='utf-8') as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append({'N':int(row['N']),'MIN_NEUTRON':int(row['MIN_NEUTRON']),'Cint_n':float(row['Cint_n']),'|Ce|':int(row.get('|Ce|',0)) if row.get('|Ce|') else None,'eps':float(row['eps'])})
    # group by MIN_NEUTRON
    mn_values = sorted({r['MIN_NEUTRON'] for r in rows})
    corrs = {}
    for mn in mn_values:
        sub = [r for r in rows if r['MIN_NEUTRON']==mn]
        xs = [r['|Ce|'] for r in sub if r['|Ce|'] is not None]
        ys = [r['Cint_n'] for r in sub if r['|Ce|'] is not None]
        corrs[mn] = pearson(xs, ys)
    data = {'sweep_csv': path, 'pearson_by_MIN_NEUTRON': corrs}
    outp = save_json('T5_corr_Ce_Cint', data)
    return outp, data

def main():
    results['tests']['T1'] = {}
    p, d = test_T1(); results['tests']['T1']['path']=p; results['tests']['T1']['data']=d
    results['tests']['T2'] = {}
    p, d = test_T2(); results['tests']['T2']['path']=p; results['tests']['T2']['data']=d
    results['tests']['T3'] = {}
    p, d = test_T3(); results['tests']['T3']['path']=p; results['tests']['T3']['data']=d
    results['tests']['T4'] = {}
    p, d = test_T4(); results['tests']['T4']['path']=p; results['tests']['T4']['data']=d
    results['tests']['T5'] = {}
    p, d = test_T5(); results['tests']['T5'] = {'path':p, 'data':d}

    # summary judgement
    summary = []
    t1 = results['tests']['T1']['data']
    verdict_T1 = 'supported' if t1['ok_MIN25_Ce_pos'] and t1['ok_MIN29_Ce_pos'] else 'contradicted'
    summary.append(('T1_presence_electron', verdict_T1))
    t2 = results['tests']['T2']['data']
    verdict_T2 = 'supported' if t2.get('delta_Cp') == 64 and t2.get('delta_Ce') == 286 else 'contradicted'
    summary.append(('T2_MIN_GLOBAL_effect', verdict_T2))

    t3 = results['tests']['T3']['data']
    with_min_global = t3['with_MIN_GLOBAL_29']
    without_min_global = t3['without_MIN_GLOBAL']
    verdict_T3 = 'supported' if with_min_global.get('|Cp|') == 0 and with_min_global.get('|Ce|') == 0 and without_min_global.get('|Cp|') == 64 and without_min_global.get('|Ce|') == 909 else 'contradicted'
    summary.append(('T3_annihilation_relation', verdict_T3))

    t4 = results['tests']['T4']['data']
    ce_values = [t4[k]['|Ce|'] for k in sorted(t4.keys())]
    verdict_T4 = 'supported' if ce_values == sorted(ce_values) and len(set(ce_values)) == len(ce_values) else 'contradicted'
    summary.append(('T4_Ce_vs_N', verdict_T4))

    t5 = results['tests']['T5']['data']
    pearsons = list(t5.get('pearson_by_MIN_NEUTRON', {}).values())
    verdict_T5 = 'supported' if pearsons and all(v > 0 for v in pearsons if not math.isnan(v)) else 'contradicted'
    summary.append(('T5_corr_Ce_Cint', verdict_T5))

    results['summary'] = summary
    # write overall JSON and report
    overall = outdir / f'electron_validation_results_{ts}.json'
    overall.write_text(json.dumps(results, indent=2, default=str, ensure_ascii=False), encoding='utf-8')
    # human report
    rpt = outdir / f'electron_validation_report_{ts}.txt'
    with rpt.open('w',encoding='utf-8') as f:
        f.write('Electron validation report\n')
        f.write('timestamp: '+ts+'\n')
        f.write('\nSummary verdicts:\n')
        for k,v in summary:
            f.write(f'{k}: {v}\n')
        f.write('\nDetailed test paths:\n')
        for k in results['tests']:
            f.write(f"{k}: {results['tests'][k].get('path')}\n")
    print('Wrote overall results to', overall)
    print('Report:', rpt)


if __name__ == '__main__':
    main()
