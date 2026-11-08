#!/usr/bin/env python3
"""
Chute v1 (scivolo_v1) generator, plus the legacy disc v2 (tappo_v2, superseded by disco_v3).

Run from anywhere:  python hardware/cad/build_disc_v2_chute.py
Outputs (paths relative to this script's folder):
  ../stl/scivolo_v1.stl      print orientation (as used for prototype 1)
  ../3mf/scivolo_v1.3mf      chute local frame (flange plane at x = -4..0)
  build/scivolo_v1.stl       chute local frame (not committed)
  build/tappo_v2.stl/.3mf    legacy disc v2, kept for reference (not committed)

The servo-mount/spacer and old-layout sections of the original script were removed:
they depended on a third-party model that is not part of this repository.
The current assembly frame and positions live in layout_v3.json.
"""
from pathlib import Path
import numpy as np, trimesh
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
STL_DIR, MF_DIR, BUILD = HERE.parent / 'stl', HERE.parent / '3mf', HERE / 'build'
for _d in (STL_DIR, MF_DIR, BUILD):
    _d.mkdir(parents=True, exist_ok=True)

def frustum_pts(r1,z1,r2,z2,n=96):
    a=np.linspace(0,2*np.pi,n,endpoint=False)
    P=np.vstack([np.c_[r1*np.cos(a),r1*np.sin(a),np.full(n,z1)],np.c_[r2*np.cos(a),r2*np.sin(a),np.full(n,z2)]])
    return trimesh.convex.convex_hull(P)
U=lambda ms: trimesh.boolean.union(ms,engine='manifold')
D=lambda a,b: trimesh.boolean.difference([a,b],engine='manifold')

# ============ 1. DISCO v2 (come .scad: 4mm, foro smussato, tubo + piede Ø30) ============
T=4.0
nom=Polygon([(-8,8),(8,8),(17.5,43),(-17.5,43)]).buffer(-3,join_style=1,resolution=24).buffer(3,join_style=1,resolution=24)
def ring(p): return np.array(p.exterior.coords)[:-1]
def hullp(pl,zl,ph,zh):
    a=ring(pl);b=ring(ph)
    return trimesh.convex.convex_hull(np.vstack([np.c_[a,np.full(len(a),zl)],np.c_[b,np.full(len(b),zh)]]))
ct,cb=1.5,0.7
disc=trimesh.creation.cylinder(radius=51.5,height=T,sections=256); disc.apply_translation([0,0,T/2])
st=trimesh.creation.extrude_polygon(nom,height=T+2); st.apply_translation([0,0,-1])
cut=U([st,hullp(nom,T-ct,nom.buffer(ct,join_style=1,resolution=24),T),hullp(nom.buffer(cb,join_style=1,resolution=24),0,nom,cb)])
disc=D(disc,cut)
tube=trimesh.creation.cylinder(radius=8,height=22,sections=128); tube.apply_translation([0,0,-11])
flare=frustum_pts(15,-25,8,-22)
boss=trimesh.creation.cylinder(radius=15,height=15,sections=128); boss.apply_translation([0,0,-32.5])
tappo=U([disc,tube,flare,boss]); tappo.process(validate=True)
tappo.export(BUILD/'tappo_v2.stl'); tappo.export(BUILD/'tappo_v2.3mf')
print('tappo_v2 watertight',tappo.is_watertight,'bounds z',np.round(tappo.bounds[:,2],1))

# ============ 2. SCIVOLO v1 (condotto curvo cavo + flangia d'attacco) ============
N,M,W=44,64,2.6
aw0,aw1,bh0,bh1=23.0,17.0,13.0,16.0
P=[np.array(p,float) for p in [(0,0),(55,0),(85,-18),(92,-62)]]
ts=np.linspace(0,1,N)
C=((1-ts)**3)[:,None]*P[0]+(3*(1-ts)**2*ts)[:,None]*P[1]+(3*(1-ts)*ts**2)[:,None]*P[2]+(ts**3)[:,None]*P[3]
Dd=(3*(1-ts)**2)[:,None]*(P[1]-P[0])+(6*(1-ts)*ts)[:,None]*(P[2]-P[1])+(3*ts**2)[:,None]*(P[3]-P[2])
th=np.linspace(0,2*np.pi,M,endpoint=False)
def sec(i,inner,ext=0.0):
    cx,cz=C[i]; tx,tz=Dd[i]/np.linalg.norm(Dd[i]); Hx,Hz=tz,-tx
    aw=aw0+(aw1-aw0)*ts[i]; bh=bh0+(bh1-bh0)*ts[i]
    if inner: aw-=W; bh-=W
    # estende i capi leggermente lungo la tangente per booleane pulite
    cx+=tx*ext; cz+=tz*ext
    return np.c_[cx+np.sin(th)*bh*Hx, np.cos(th)*aw, cz+np.sin(th)*bh*Hz]
def loft(inner,ext0=0,ext1=0):
    V=[];F=[]
    R=[sec(i,inner,ext0 if i==0 else (ext1 if i==N-1 else 0)) for i in range(N)]
    for r in R: V.extend(r.tolist())
    for i in range(N-1):
        for k in range(M):
            a=i*M+k;b=i*M+(k+1)%M;c=(i+1)*M+(k+1)%M;d=(i+1)*M+k
            F+= [[a,b,c],[a,c,d]]
    c0=len(V); V.append(R[0].mean(0).tolist()); c1=len(V); V.append(R[-1].mean(0).tolist())
    for k in range(M):
        F.append([c0,(k+1)%M,k]); F.append([c1,(N-1)*M+k,(N-1)*M+(k+1)%M])
    m=trimesh.Trimesh(np.array(V),np.array(F),process=True); m.fix_normals(); return m
outer=loft(False); inner=loft(True,ext0=-3,ext1=3)
duct=D(outer,inner)
# flangia: piastra 4mm sul piano d'ingresso (x da -4 a 0), foro passante, 4 fori Ø3.4
fw,fh=2*aw0+18,2*bh0+18
fl=trimesh.creation.box(extents=[4,fw,fh]); fl.apply_translation([-2,0,0])
ell=trimesh.creation.cylinder(radius=1.0,height=12,sections=96)
ell.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
ell.apply_scale([1,aw0-W,bh0-W]); ell.apply_translation([-2,0,0])
fl=D(fl,ell)
for sy in (-1,1):
    for sz in (-1,1):
        h=trimesh.creation.cylinder(radius=1.7,height=12,sections=32)
        h.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
        h.apply_translation([-2,sy*(aw0+4.5),sz*(bh0+4.5)]); fl=D(fl,h)
scivolo=U([duct,fl]); scivolo.process(validate=True)
scivolo.export(BUILD/'scivolo_v1.stl'); scivolo.export(MF_DIR/'scivolo_v1.3mf')
# print orientation used for prototype 1: +90 deg about Y (flange plate on top), min corner at the origin
sp=scivolo.copy(); sp.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[0,1,0]))
sp.apply_translation(-sp.bounds[0]); sp.export(STL_DIR/'scivolo_v1.stl')
print('scivolo watertight',scivolo.is_watertight,'ext',np.round(scivolo.extents,1).tolist(),'vol cm3',round(scivolo.volume/1000,1))
