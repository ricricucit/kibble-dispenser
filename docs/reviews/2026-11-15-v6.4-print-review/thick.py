"""Ray-cast wall thickness (surface point -> opposite surface along the inward normal). Lists places thinner than 1.2 mm."""
import sys,numpy as np,trimesh
P='/home/claude/asm/parts/'
for n in [a for a in sys.argv[1:] if not a.isdigit()]:
    m=trimesh.load(P+n+'.stl',process=True)
    pts,fi=trimesh.sample.sample_surface(m,int(sys.argv[-1]) if sys.argv[-1].isdigit() else 40000,seed=1)
    nrm=m.face_normals[fi]
    o=pts-nrm*1e-3
    loc,ri,_=m.ray.intersects_location(o,-nrm,multiple_hits=False)
    t=np.full(len(pts),np.nan); t[ri]=np.linalg.norm(loc-o[ri],axis=1)
    ok=~np.isnan(t)
    print(f'== {n}: sampled {ok.sum()}  thickness percentiles 0.1/1/5/50: {np.nanpercentile(t,[0.1,1,5,50]).round(2)}')
    thin=np.where(ok&(t<1.2)&(t>0.02))[0]
    # cluster on 4 mm grid
    cl={}
    for i in thin:
        k=tuple(np.round(pts[i]/4).astype(int)); cl.setdefault(k,[]).append(i)
    rows=sorted(cl.items(),key=lambda kv:-len(kv[1]))
    print('   points <1.2 mm:',len(thin),'clusters',len(rows))
    for k,v in rows[:14]:
        print('    n=%3d tmin %.2f tmed %.2f at asm %s normal %s'%(len(v),t[v].min(),np.median(t[v]),pts[v].mean(0).round(1),nrm[v].mean(0).round(1)))
