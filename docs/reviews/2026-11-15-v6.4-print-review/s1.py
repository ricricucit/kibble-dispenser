from lib import *
import json
xf=json.load(open('xf.json'))
def toasm(n,p):
    R=np.array(xf[n]['R']);t=np.array(xf[n]['t']); return (R.T@(np.array(p)-t)).round(2)
print('scatola z18 region ->',toasm('scatola_v64',[20.7,43.4,18.0]),toasm('scatola_v64',[-6.8,39.7,39.0]))
print('fondello 29.2 ->',toasm('fondello_v64',[-18.1,-0.2,29.2]), toasm('fondello_v64',[-28.1,26.8,5.4]))
print('vasca 52.4 ->',toasm('modulo_vasca_v64',[17.4,-0.8,52.4]))
print('coperchio 12.2 ->',toasm('modulo_coperchio_v64',[6.6,-21.1,12.2]))
C=[('scatola_v64','#3a5'),('fondello_v64','#444'),('guscio_v64','#777'),('modulo_vasca_v64','#f80'),('modulo_coperchio_v64','#fb4'),
   ('modulo_guarnizione_v64','#ee2'),('guarnizione_fondello_v64','#ee2'),('modulo_anello_speaker_v64','#28f'),('chiocciola_v63','#bbb'),('colonna_v63','#999'),
   ('v64_asm/bought_inserts_holder','#c33'),('v64_asm/bought_m3x16_module_lock','#36c'),('v64_asm/bought_pt_k30x12_cap','#36c'),('v64_asm/bought_pt_k30x8_lid','#36c'),
   ('v64_asm/bought_socket_m8_5p','#9ac'),('v64_asm/bought_plug_m8_5p_angled','#9ac'),('v64_asm/bought_servo','#ccd'),('scivolo_v611','#4b6'),('labbro_scivolo_v611','#ee2')]
plot(C,'y',45.5,(0,60),(-106,-28),'sec_y45.5_post.png','Y=45.5 (x,z): holder post, socket, lock screw')
plot(C,'y',0,(-30,70),(-106,-28),'sec_y0.png','Y=0 (x,z)')
plot(C,'x',24,(-60,60),(-106,-28),'sec_x24.png','X=24 (y,z): posts, module back region')
plot(C,'z',-60,(-30,70),(-60,60),'sec_z-60.png','Z=-60 plan')
plot(C,'z',-80,(-30,70),(-60,60),'sec_z-80.png','Z=-80 plan')
plot(C,'z',-49,(-30,70),(-60,60),'sec_z-49.png','Z=-49 plan')
