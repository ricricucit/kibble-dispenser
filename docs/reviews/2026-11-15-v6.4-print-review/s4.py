import json,numpy as np,sys
xf=json.load(open('xf.json'))
for f in sys.argv[1:]:
    rows=json.load(open(f))
    for fn,rs in rows.items():
        n=fn.replace('_print.stl','')
        if n not in xf: continue
        R=np.array(xf[n]['R']);t=np.array(xf[n]['t'])
        print('==',fn)
        for r in rs:
            a=(R.T@(np.array([r['cx'],r['cy'],r['z']])-t)).round(1)
            print(f"  printz {r['z']:6.1f} area {r['area']:6.1f} span {r['span']:5.1f} len {r['length']:6.1f} w {r['w']:4.2f} anch {r['anch']:.2f} isl {r['island']} asm {a}")
