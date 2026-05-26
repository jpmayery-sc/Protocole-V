import csv, math
from collections import defaultdict
path='results/sweep_summary_20260505-114937Z.csv'
rows= []
with open(path,newline='',encoding='utf-8') as f:
    r=csv.DictReader(f)
    for row in r:
        row['N']=int(row['N'])
        row['MIN_NEUTRON']=int(row['MIN_NEUTRON'])
        row['Cint_n']=float(row['Cint_n']) if row['Cint_n']!='' else float('nan')
        row['lambda_pred']=float(row['lambda_pred']) if row['lambda_pred']!='' else float('nan')
        row['|Cn|']=int(row['|Cn|'])
        row['eps']=float(row['eps']) if row['eps']!='' else float('nan')
        rows.append(row)

by_mn=defaultdict(list)
for r in rows:
    by_mn[r['MIN_NEUTRON']].append(r)

summary=[]
for mn in sorted(by_mn.keys()):
    vals=[abs(x['eps']) for x in by_mn[mn] if not math.isnan(x['eps'])]
    mean=sum(vals)/len(vals)
    sd=(sum((v-mean)**2 for v in vals)/len(vals))**0.5
    mx=max(vals)
    summary.append((mn, mean, sd, mx, len(vals)))

print('MIN_NEUTRON | mean_abs_eps | std_abs_eps | max_abs_eps | samples')
for mn,mean,sd,mx,n in summary:
    print(f'{mn:11d} | {mean:12.6f} | {sd:10.6f} | {mx:11.6f} | {n:7d}')

best= min(summary, key=lambda t: t[1])
print('\nBest MIN_NEUTRON by mean|eps|:', best[0], 'mean_abs_eps=', best[1])

# also find min of max_abs_eps
best_max=min(summary, key=lambda t: t[3])
print('Best MIN_NEUTRON by max|eps|:', best_max[0], 'max_abs_eps=', best_max[3])

# compute average Cint_n per mn
print('\nMIN_NEUTRON average C_int^(n):')
for mn in sorted(by_mn.keys()):
    cints=[x['Cint_n'] for x in by_mn[mn]]
    print(f'{mn:2d} avg Cint = {sum(cints)/len(cints):.6f}')

# write a small report file
report='results/robust_min_neutron_report.txt'
with open(report,'w',encoding='utf-8') as f:
    f.write('Robust MIN_NEUTRON analysis\n')
    f.write('Best by mean_abs_eps: %d (mean_abs_eps=%.6f)\n' % (best[0], best[1]))
    f.write('Best by max_abs_eps: %d (max_abs_eps=%.6f)\n' % (best_max[0], best_max[3]))
    f.write('\nSummary per MIN_NEUTRON:\n')
    for mn,mean,sd,mx,n in summary:
        f.write(f'{mn}\t{mean:.6f}\t{sd:.6f}\t{mx:.6f}\t{n}\n')

print('\nReport written to', report)
