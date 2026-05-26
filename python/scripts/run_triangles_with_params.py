"""Run scripts/run_triangles.py with overridden parameters and write JSON result.

Usage:
  python scripts/run_triangles_with_params.py --MIN_NEUTRON 25 --N 200 --output results/local_run_25.json
"""
import argparse
import json
from pathlib import Path
import time


def run_with_params(N=None, MIN_NEUTRON=None, MIN_GLOBAL=None):
    src = Path('scripts/run_triangles.py').read_text(encoding='utf-8')
    import re
    # replace assignments for N, MIN_NEUTRON, MIN_GLOBAL so the script uses our values
    if N is not None:
        src = re.sub(r'^N\s*=.*$', f'N = {int(N)}', src, flags=re.M)
    if MIN_NEUTRON is not None:
        src = re.sub(r'^MIN_NEUTRON\s*=.*$', f'MIN_NEUTRON = {int(MIN_NEUTRON)}', src, flags=re.M)
    if MIN_GLOBAL is not None:
        src = re.sub(r'^MIN_GLOBAL\s*=.*$', f'MIN_GLOBAL = {int(MIN_GLOBAL)}', src, flags=re.M)

    g = {}
    # Execute the modified script in its own globals dict
    exec(compile(src, 'scripts/run_triangles.py', 'exec'), g)

    # Collect results
    res = {}
    res['N'] = g.get('N')
    res['MIN_NEUTRON'] = g.get('MIN_NEUTRON')
    res['MIN_GLOBAL'] = g.get('MIN_GLOBAL')
    res['Mn'] = g.get('Mn')
    res['Mp'] = g.get('Mp')
    res['Me'] = g.get('Me')
    res['median_Mn'] = g.get('medMn')
    res['Cint_n'] = g.get('Cint_n')
    res['lambda_geo'] = g.get('lambda_geo')
    res['lambda_pred'] = g.get('lambda_pred')
    res['eps'] = g.get('eps')
    res['|Cn|'] = len(g.get('Cn', []))
    res['|Cp|'] = len(g.get('Cp', []))
    res['|Ce|'] = len(g.get('Ce', []))
    res['timestamp'] = time.strftime('%Y%m%d-%H%M%SZ')
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--N', type=int, default=None)
    parser.add_argument('--MIN_NEUTRON', type=int, default=None)
    parser.add_argument('--MIN_GLOBAL', type=int, default=None)
    parser.add_argument('--output', '-o', required=True)
    args = parser.parse_args()

    res = run_with_params(N=args.N, MIN_NEUTRON=args.MIN_NEUTRON, MIN_GLOBAL=args.MIN_GLOBAL)
    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, indent=2, default=str, ensure_ascii=False), encoding='utf-8')
    print('Wrote', outp)


if __name__ == '__main__':
    main()
