"""Usage: python fetch_bbl_profiles.py "Bambu Lab A1 0.4 nozzle" "0.20mm Standard @BBL A1" "Generic PETG @BBL A1" "Generic TPU @BBL A1" ...
Fetch Bambu Studio system profiles (BBL vendor) needed for the A1 project and resolve 'inherits' chains."""
import json, os, sys, urllib.parse, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.environ.get('BBL_CACHE', os.path.join(HERE, 'bbl_cache'))
BASE = 'https://raw.githubusercontent.com/bambulab/BambuStudio/master/resources/profiles/BBL/'
os.makedirs(REF, exist_ok=True)
if not os.path.exists(os.path.join(REF, 'BBL.json')):
    subprocess.run(['curl', '-sS', '-f', '-o', os.path.join(REF, 'BBL.json'), BASE[:-1] + '.json'], check=True)
idx = json.load(open(os.path.join(REF, 'BBL.json')))
SUB = {}
for sect in ('machine_list', 'process_list', 'filament_list', 'machine_model_list'):
    for x in idx[sect]:
        SUB[x['name']] = x['sub_path']
CACHE = os.path.join(REF, 'profiles')
os.makedirs(CACHE, exist_ok=True)


def fetch(name):
    sp = SUB[name]
    local = os.path.join(CACHE, sp)
    if not os.path.exists(local):
        os.makedirs(os.path.dirname(local), exist_ok=True)
        url = BASE + urllib.parse.quote(sp)
        subprocess.run(['curl', '-sS', '-f', '-o', local, url], check=True)
    return json.load(open(local))


def resolve(name):
    d = fetch(name)
    chain = [d]
    while d.get('inherits'):
        d = fetch(d['inherits'])
        chain.append(d)
    out = {}
    for d in reversed(chain):
        out.update(d)
        # 'include' lists template presets (e.g. the A1 start/end G-code) merged at this level
        for inc in d.get('include', []) or []:
            t = fetch(inc)
            for k, v in t.items():
                if k not in ('name', 'type', 'from', 'instantiation', 'inherits', 'setting_id'):
                    out[k] = v
    out['name'] = name
    out['inherits_chain'] = [c.get('name') for c in chain]
    return out


if __name__ == '__main__':
    names = sys.argv[1:]
    res = {n: resolve(n) for n in names}
    json.dump(res, open(os.path.join(HERE, 'bbl_profiles_resolved.json'), 'w'), indent=1)
    for n, d in res.items():
        print(n, len(d), d['inherits_chain'])
