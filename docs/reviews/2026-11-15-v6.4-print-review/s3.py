from lib import *
import pickle; C=pickle.load(open('C.pkl','rb'))
plot(C,'z',-87,(14,70),(-58,58),'sec_z-87.png','Z=-87 plan: panel band',size=9)
plot(C,'z',-92,(14,70),(-58,0),'sec_z-92_south.png','Z=-92 plan south half',size=11)
plot(C,'x',36,(-56,-30),(-104,-76),'zoom_x36_spike.png','X=36 zoom (y,z) south lobe',size=10)
plot(C,'x',40,(-56,-30),(-104,-76),'zoom_x40_spike.png','X=40 zoom (y,z) south lobe',size=10)
