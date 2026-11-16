from lib import *
import pickle; C=pickle.load(open('C.pkl','rb'))
C2=C+[('guarnizione_baionetta_v61','#ee2'),('labbro_ombra_v611','#ee2')]
plot(C2,'z',-70,(-12,12),(56,76),'zoom_fondello_edge_z-70.png','Z=-70 plan zoom at cap zero-thickness edges (-2.0,66.6)/(1.2,66.1)',size=10)
plot(C2,'z',-70,(-90,70),(-80,80),'sec_z-70.png','Z=-70 plan',size=12)
plot(C2,'x',-0.4,(60,76),(-80,-60),'zoom_fondello_edge_x-0.4.png','X=-0.4 (y,z) zoom',size=9)
plot(C2,'y',52.35,(10,60),(-106,-30),'sec_y52.35_seam.png','Y=52.35 (x,z): in the side seam plane',size=9)
plot(C2,'z',-100,(10,45),(-60,-40),'zoom_z-100_corner.png','Z=-100 plan zoom south corner: module / cap rib',size=10)
plot(C2,'x',17.2,(-60,60),(-106,-60),'sec_x17.2.png','X=17.2 (y,z) in the back seam plane (between cap edge 17.05 and module 17.4)',size=12)
