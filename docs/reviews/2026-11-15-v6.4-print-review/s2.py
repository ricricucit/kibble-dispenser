from lib import *
exec(open('s1.py').read().split("plot(C")[0].split("C=[")[0])
C=[('scatola_v64','#3a5'),('fondello_v64','#444'),('guscio_v64','#777'),('modulo_vasca_v64','#f80'),('modulo_coperchio_v64','#fb4'),
   ('modulo_guarnizione_v64','#ee2'),('guarnizione_fondello_v64','#ee2'),('modulo_anello_speaker_v64','#28f'),('chiocciola_v63','#bbb'),('colonna_v63','#999'),
   ('v64_asm/bought_inserts_holder','#c33'),('v64_asm/bought_m3x16_module_lock','#36c'),('v64_asm/bought_pt_k30x12_cap','#36c'),('v64_asm/bought_pt_k30x8_lid','#36c'),
   ('v64_asm/bought_socket_m8_5p','#9ac'),('v64_asm/bought_plug_m8_5p_angled','#9ac'),('v64_asm/bought_servo','#ccd'),('scivolo_v611','#4b6'),('labbro_scivolo_v611','#ee2'),
   ('v64_asm/bought_switch_12mm_ip67','#aaf'),('v64_asm/bought_lightpipes_5mm','#aaf'),('v64_asm/bought_oring_3x1_lid','#111'),('v64_asm/bought_oring_3x1_cap','#111')]
import pickle; pickle.dump(C,open('C.pkl','wb'))
plot(C,'x',36,(-60,60),(-106,-28),'sec_x36.png','X=36 (y,z)',size=12)
plot(C,'z',-38.5,(10,70),(-60,60),'sec_z-38.5_lid.png','Z=-38.5 plan: lid mid-thickness')
plot(C,'z',-41.2,(10,70),(-60,60),'sec_z-41.2_land.png','Z=-41.2 plan: tub land just under the lid, gasket lip')
plot(C,'z',-36,(10,70),(-60,60),'sec_z-36.png','Z=-36 plan: above the lid (what stands above lid top -37)')
plot(C,'y',-24,(10,72),(-60,-20),'sec_y-24_J1.png','Y=-24 J1 turret',size=12)
plot(C,'y',0,(44,70),(-56,-30),'zoom_rim_y0.png','Y=0 zoom rim/lip/gasket/skin top',size=11)
plot(C,'y',0,(14,24),(-44,-32),'zoom_back_y0.png','Y=0 zoom back edge lid/gasket',size=10)
