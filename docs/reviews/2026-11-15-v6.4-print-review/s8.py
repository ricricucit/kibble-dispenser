from lib import *
import pickle; C=pickle.load(open('C.pkl','rb'))
C=C+[('v64_asm/bought_oring_3x1','#111'),('v64_asm/bought_gland_m12','#c9a'),('v64_asm/bought_inserts_servo','#c33'),('v64_asm/bought_m3x8_servo','#36c'),('v64_asm/bought_vent_patch_eptfe','#f0f'),('v64_asm/bought_oring_face_24x2','#111')]
import pickle; pickle.dump(C,open('C2.pkl','wb'))
plot(C,'y',47,(0,22),(-106,-28),'sec_y47_bossC.png','Y=47 (x,z): cap boss C, PT K30x12, O-ring, counterbore',size=5)
plot(C,'y',47,(4,18),(-106,-86),'zoom_y47_bossC.png','Y=47 zoom: cap screw C head/O-ring/pilot',size=9)
plot(C,'y',33,(-32,-8),(-106,-28),'sec_y33_bossA.png','Y=33 (x,z): cap boss A',size=5)
plot(C,'y',0,(8,22),(-78,-64),'zoom_y0_caplip.png','Y=0 zoom: cap TPU lip, groove, bay rim',size=9)
plot(C,'x',0,(34,48),(-78,-64),'zoom_x0_caplip.png','X=0 zoom (y,z): cap TPU lip on the straight side',size=9)
plot(C,'y',0,(56,66),(-44,-36),'zoom_y0_lidlip.png','Y=0 zoom: lid TPU lip, groove, tub land',size=10)
plot(C,'x',-3,(-62,-34),(-62,-34),'sec_x-3_gland.png','X=-3 (y,z): M12 gland through bay south wall',size=8)
plot(C,'z',-48,(-30,30),(-62,-30),'sec_z-48_gland.png','Z=-48 plan: gland, boss D, post',size=9)
plot(C,'y',-45.5,(14,34),(-106,-80),'zoom_y-45.5_lock.png','Y=-45.5 zoom: lock screw, insert, post tip, socket',size=10)
plot(C,'x',33,(-30,10),(-106,-90),'zoom_x33_speaker.png','X=33 (y,z): speaker collar, ring, grille holes',size=11)
