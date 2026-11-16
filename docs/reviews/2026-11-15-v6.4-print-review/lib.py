import os, numpy as np, trimesh, manifold3d as mf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.ops import unary_union
P='/home/claude/asm/parts'
def L(f):
    if not f.endswith('.stl'): f+='.stl'
    return trimesh.load(os.path.join(P,f),process=True)
def M(m):
    if isinstance(m,str): m=L(m)
    return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices,np.float32),tri_verts=np.asarray(m.faces,np.uint32)))
def T(Mm):
    o=Mm.to_mesh(); return trimesh.Trimesh(np.asarray(o.vert_properties)[:,:3],np.asarray(o.tri_verts),process=True)
AX={'x':0,'y':1,'z':2}
def sec(m,axis,val):
    """return shapely geometry of section; coords = the two remaining axes in order"""
    if isinstance(m,str): m=L(m)
    n=[0,0,0]; n[AX[axis]]=1; o=[0,0,0]; o[AX[axis]]=val
    s=m.section(plane_origin=o,plane_normal=n)
    if s is None: return None
    keep=[i for i in range(3) if i!=AX[axis]]
    polys=[]
    for ent in s.discrete:
        p=np.asarray(ent)[:,keep]
        if len(p)>=4:
            try:
                pg=Polygon(p)
                if not pg.is_valid: pg=pg.buffer(0)
                polys.append(pg)
            except Exception: pass
    # even-odd
    polys.sort(key=lambda p:-p.area)
    out=None
    for p in polys:
        out=p if out is None else out.symmetric_difference(p)
    return out
def plot(parts,axis,val,xlim,ylim,fn,title='',dpi=130,size=10):
    """parts: list of (name_or_mesh,color)"""
    fig,ax=plt.subplots(figsize=(size,size*(ylim[1]-ylim[0])/(xlim[1]-xlim[0])))
    for nm,col in parts:
        g=sec(nm,axis,val)
        if g is None or g.is_empty: continue
        for pg in (g.geoms if hasattr(g,'geoms') else [g]):
            if pg.geom_type!='Polygon': continue
            from matplotlib.path import Path; from matplotlib.patches import PathPatch
            verts=[];codes=[]
            for ring in [pg.exterior]+list(pg.interiors):
                c=np.asarray(ring.coords); verts+=c.tolist(); codes+=[Path.MOVETO]+[Path.LINETO]*(len(c)-2)+[Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts,codes),fc=col,ec='k',lw=0.3,alpha=0.85))
    ax.set_xlim(xlim);ax.set_ylim(ylim);ax.set_aspect('equal');ax.grid(alpha=0.3);ax.set_title(title,fontsize=9)
    import matplotlib.ticker as tk
    fig.savefig(fn,dpi=dpi,bbox_inches='tight');plt.close(fig)
