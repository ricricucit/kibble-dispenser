"""Layer-by-layer support analysis in print orientation (0.2 mm layers).
For every layer: region not supported by the layer below (grown by 0.25 mm => anything flatter than ~51 deg from vertical),
split into components; reports islands (start in mid-air) and spans (short side of the min. rotated rectangle)."""
import sys,json,os,numpy as np,trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import make_valid
P='/home/claude/asm/parts'
LH=0.2; GROW=0.25
def polys_at(m,zs):
    secs=m.section_multiplane(plane_origin=[0,0,0],plane_normal=[0,0,1],heights=zs)
    out=[]
    for s in secs:
        if s is None: out.append(Polygon()); continue
        try:
            pf=s.polygons_full
            g=unary_union([make_valid(p) for p in pf if p is not None])
        except Exception as e:
            g=Polygon()
        out.append(g)
    return out
def analyse(f,minarea=4.0,minspan=2.0):
    m=trimesh.load(os.path.join(P,f),process=True)
    H=m.bounds[1][2]
    zs=np.arange(LH/2,H,LH)
    A=polys_at(m,zs)
    rows=[]
    for i in range(1,len(A)):
        if A[i].is_empty: continue
        sup=A[i-1].buffer(GROW)
        U=A[i].difference(sup)
        if U.is_empty: continue
        for c in (U.geoms if hasattr(U,'geoms') else [U]):
            if c.geom_type!='Polygon' or c.area<minarea: continue
            mr=c.minimum_rotated_rectangle
            xs=np.asarray(mr.exterior.coords); e1=np.linalg.norm(xs[0]-xs[1]); e2=np.linalg.norm(xs[1]-xs[2])
            span=min(e1,e2); length=max(e1,e2)
            # inscribed-ish width: 2*area/perimeter
            w=2*c.area/c.length
            if span<minspan: continue
            # island: the whole connected piece of this layer containing c has no overlap with layer below
            comp=[g for g in (A[i].geoms if hasattr(A[i],'geoms') else [A[i]]) if g.intersects(c)]
            island=all(not g.intersects(A[i-1]) for g in comp)
            # how much of boundary of c touches supported area (anchoring)
            anch=c.boundary.intersection(sup.buffer(0.02)).length/c.length
            rows.append(dict(z=round(float(zs[i]-LH/2),2),area=round(c.area,1),span=round(float(span),1),length=round(float(length),1),w=round(w,2),
                             island=bool(island),anch=round(float(anch),2),cx=round(c.centroid.x,1),cy=round(c.centroid.y,1)))
    return rows,A,zs
if __name__=='__main__':
    res={}
    for f in sys.argv[1:]:
        rows,_,_=analyse(f)
        res[f]=rows
        # group by z
        print('==',f,len(rows),'unsupported regions; islands',sum(r['island'] for r in rows))
        rows2=sorted(rows,key=lambda r:-r['area'])[:14]
        for r in rows2: print('   ',r)
        isl=[r for r in rows if r['island']]
        for r in isl[:8]: print('   ISLAND',r)
    json.dump(res,open('layers_'+os.path.basename(sys.argv[1])+'.json','w'))
