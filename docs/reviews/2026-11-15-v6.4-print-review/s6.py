from lib import *
import pickle; C=pickle.load(open('C.pkl','rb'))
C3=C+[('v64_asm/bought_board_70x50_A','#2a2'),('v64_asm/bought_esp32_wrover_stack','#9bd')]
plot(C3,'y',34.6,(15,40),(-95,-35),'sec_y34.6_slot.png','Y=34.6 (x,z): board slot A/B in the guide wall, board top vs lid',size=7)
plot(C3,'z',-60,(15,40),(28,54),'zoom_z-60_slots.png','Z=-60 plan zoom: slots A/B, post socket region',size=10)
v=L('modulo_vasca_v64')
g=sec(v,'z',-60)
# measure slot features: intersect with strip y in [34.0,35.4]
from shapely.geometry import box
s=g.intersection(box(15,33.9,40,35.5))
for p in (s.geoms if hasattr(s,'geoms') else [s]): print('piece',np.round(p.bounds,2),round(p.area,2))
g=sec(v,'y',34.7); s=g.intersection(box(21,-95,24.5,-85))
for p in (s.geoms if hasattr(s,'geoms') else [s]): print('yz piece',np.round(p.bounds,2))
g=sec(v,'x',23.2); print('x=23.2 section bounds near slot bottom:')
s=g.intersection(box(33,-93,36,-88)); 
for p in (s.geoms if hasattr(s,'geoms') else [s]): print('  ',np.round(p.bounds,2))
