from lib import *
from holes import holes
print('gland hole (y=-41 plane; coords x,z):',holes('scatola_v64','y',-41,20))
print('vent hole?:',holes('scatola_v64','x',-14.2,20), holes('scatola_v64','x',14.2,20))
g=L('v64_asm/bought_gland_m12'); print('gland bounds',g.bounds.round(2).tolist())
# button/led holes: section the tub with a plane normal to radial dir at az 16 deg, r = 56
import trimesh
v=L('modulo_vasca_v64')
for nm,az,rr in (('btn',16,[52,54,57,60]),('led',31,[52,54,56,58,60]),('ko1',-3,[58])):
    a=np.radians(az); n=np.array([np.cos(a),np.sin(a),0])
    for r in rr:
        s=v.section(plane_origin=n*r,plane_normal=n)
        if s is None: continue
        p2,T=s.to_2D() if hasattr(s,'to_2D') else s.to_planar()
        hs=[]
        for pg in p2.polygons_full:
            for ring in pg.interiors:
                from shapely.geometry import Polygon
                q=Polygon(ring); d=2*np.sqrt(q.area/np.pi)
                if d<25: hs.append((round(d,2),round(4*np.pi*q.area/q.length**2,2)))
        print(nm,'az',az,'plane r',r,'holes(d,circularity):',hs)
