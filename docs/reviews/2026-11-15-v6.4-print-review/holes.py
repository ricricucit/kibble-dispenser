from lib import *
from shapely.geometry import Polygon
def holes(name,axis,val,dmax=14):
    g=sec(name,axis,val); out=[]
    if g is None: return out
    for pg in (g.geoms if hasattr(g,'geoms') else [g]):
        if pg.geom_type!='Polygon': continue
        for r in pg.interiors:
            p=Polygon(r); d=2*np.sqrt(p.area/np.pi)
            circ=4*np.pi*p.area/p.length**2
            if d<dmax: out.append((round(p.centroid.x,2),round(p.centroid.y,2),round(d,2),round(circ,2)))
    return sorted(out)
for nm,ax,v in (('scatola_v64','z',-92),('scatola_v64','z',-86),('scatola_v64','z',-56),('scatola_v64','z',-31),('scatola_v64','z',-34),
                ('fondello_v64','z',-103.9),('fondello_v64','z',-102),('fondello_v64','z',-99),
                ('modulo_vasca_v64','z',-44),('modulo_vasca_v64','z',-103.9),('modulo_vasca_v64','z',-102.5),('modulo_vasca_v64','z',-95),('modulo_vasca_v64','z',-80),
                ('modulo_coperchio_v64','z',-38.5),('modulo_coperchio_v64','z',-26.5),('modulo_anello_speaker_v64','z',-98.2),('modulo_anello_speaker_v64','z',-96.5)):
    print(nm,ax,v,holes(nm,ax,v))
# outer dims
for nm in ('modulo_vasca_v64','modulo_coperchio_v64','modulo_guarnizione_v64','guarnizione_fondello_v64','fondello_v64','scatola_v64','modulo_anello_speaker_v64'):
    print(nm,L(nm).bounds.round(2).tolist())
# rim stairs: profile of the tub inner face at y=0, x>50, z in -56..-46
g=sec('modulo_vasca_v64','y',0.0)
from shapely.geometry import LineString
print('tub inner face x at Y=0 (first solid from x=45 going +x) by z:')
prev=None
for z in np.arange(-47.0,-54.6,-0.2):
    ln=LineString([(56.5,z),(70,z)]).intersection(g)
    xs=ln.bounds[0] if not ln.is_empty else None
    if prev is not None and xs is not None and abs(xs-prev)>0.3: print('   z %.1f: inner face jumps %.2f -> %.2f (ledge %.2f mm)'%(z,prev,xs,xs-prev))
    prev=xs
# module bottom edge / cap edge chamfer at z=-104
for nm in ('modulo_vasca_v64','fondello_v64'):
    g=sec(nm,'y',0.0)
    for z in (-103.95,-103.8,-103.5,-103.0):
        ln=LineString([(10,z),(25,z)]).intersection(g)
        print(nm,'Y=0 z',z,'solid x-range near seam',np.round(ln.bounds,2) if not ln.is_empty else None)
