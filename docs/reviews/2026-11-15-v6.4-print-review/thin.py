"""Per-layer thin-feature finder (print orientation, every 0.2 mm): regions of a layer narrower than W (morphological opening)."""
import sys,json,os,numpy as np,trimesh
from layers import polys_at,P,LH
xf=json.load(open('xf.json'))
def thin(A,W):
    r=W/2-0.01
    o=A.buffer(-r,join_style=2).buffer(r*1.05,join_style=1)
    d=A.difference(o)
    out=[]
    for c in (d.geoms if hasattr(d,'geoms') else [d]):
        if c.geom_type!='Polygon' or c.is_empty: continue
        mr=c.minimum_rotated_rectangle; xs=np.asarray(mr.exterior.coords)
        L=max(np.linalg.norm(xs[0]-xs[1]),np.linalg.norm(xs[1]-xs[2]))
        if c.area>0.25 and L>1.5: out.append((c,L))
    return out
res={}
for f in sys.argv[1:]:
    n=f.replace('_print.stl','')
    m=trimesh.load(os.path.join(P,f),process=True)
    zs=np.arange(LH/2,m.bounds[1][2],LH)
    A=polys_at(m,zs)
    R=np.array(xf[n]['R']);t=np.array(xf[n]['t'])
    for W in (0.8,0.42):
        hits=[]
        for z,a in zip(zs,A):
            if a.is_empty: continue
            for c,L in thin(a,W):
                p=(R.T@(np.array([c.centroid.x,c.centroid.y,z])-t)).round(1).tolist()
                hits.append(dict(pz=round(float(z),1),area=round(c.area,2),L=round(float(L),1),wmean=round(2*c.area/c.length,2),asm=p,pxy=[round(c.centroid.x,1),round(c.centroid.y,1)]))
        res[f'{f}|{W}']=hits
        # cluster summary by xy (2mm grid)
        cl={}
        for h in hits:
            k=(round(h['pxy'][0]/3),round(h['pxy'][1]/3)); cl.setdefault(k,[]).append(h)
        print(f'== {f} narrower than {W}: {len(hits)} layer-regions, {len(cl)} clusters, total area-layers {sum(h["area"] for h in hits):.0f}')
        for k,v in sorted(cl.items(),key=lambda kv:-sum(h['area'] for h in kv[1]))[:8]:
            zz=[h['pz'] for h in v]
            print(f'     n={len(v):3d} printz {min(zz):.1f}..{max(zz):.1f} maxL {max(h["L"] for h in v):5.1f} wmean {np.mean([h["wmean"] for h in v]):.2f} asm~{v[len(v)//2]["asm"]}')
json.dump(res,open('thin_'+sys.argv[1]+'.json','w'))
