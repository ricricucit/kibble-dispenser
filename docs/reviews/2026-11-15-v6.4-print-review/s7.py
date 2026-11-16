from lib import *
import json,pickle; C=pickle.load(open('C.pkl','rb'))
xf=json.load(open('xf.json'))
def toasm(n,p):
    R=np.array(xf[n]['R']);t=np.array(xf[n]['t']); return (R.T@(np.array(p)-t)).round(2)
for p in ([-24.4,-55.2,64],[68.8,0.2,64],[46,-53.2,100.6],[13.7,-64.6,130],[25.6,-74.5,7.0]): print(p,'->',toasm('guscio_v64',p))
g=L('guscio_v64'); o=L('guscio_v611')
print('v64 bounds',g.bounds.round(2).tolist(),'v611',o.bounds.round(2).tolist())
# tab: radial section through tab at 0 deg (asm +x): plane y=0
plot([('guscio_v64','#777'),('chiocciola_v63','#bbb'),('modulo_vasca_v64','#f80'),('modulo_coperchio_v64','#fb4')],'y',0.2,(50,90),(-40,30),'guscio_tab_y0.png','Y=0.2 (x,z) shell tab at 0 deg (asm); printed upside-down',size=7)
plot([('guscio_v64','#777'),('chiocciola_v63','#bbb')],'z',-0.5,(-90,90),(-90,90),'guscio_tabs_z-0.5.png','Z=-0.5 plan: shell tabs',size=9)
plot([('guscio_v64','#777'),('modulo_vasca_v64','#f80'),('modulo_coperchio_v64','#fb4'),('fondello_v64','#444')],'z',-38,(25,60),(40,62),'guscio_rib_z-38.png','Z=-38 plan: shell return rib at the opening edge',size=9)
