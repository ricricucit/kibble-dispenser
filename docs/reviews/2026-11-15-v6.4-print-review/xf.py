import json,numpy as np,trimesh,os
P='/home/claude/asm/parts'
d=json.load(open(P+'/v64.json'))
names=list(d['parts']['changed_chassis_parts'])+d['parts']['new_module_parts']+list(d['parts']['safe_to_print_now (byte-identical to 6.3.0)'])
out={}
for n in names:
    a=trimesh.load(f'{P}/{n}.stl',process=False); b=trimesh.load(f'{P}/{n}_print.stl',process=False)
    if len(a.vertices)!=len(b.vertices): print(n,'DIFFERENT vertex count',len(a.faces),len(b.faces)); continue
    A=np.asarray(a.vertices,float);B=np.asarray(b.vertices,float)
    ca=A.mean(0);cb=B.mean(0)
    H=(A-ca).T@(B-cb);U,S,Vt=np.linalg.svd(H);R=Vt.T@U.T
    if np.linalg.det(R)<0: Vt[-1]*=-1;R=Vt.T@U.T
    t=cb-R@ca; err=np.abs((A@R.T+t)-B).max()
    out[n]=dict(R=R.round(4).tolist(),t=t.round(3).tolist(),err=float(err))
    up=R.T@[0,0,1]  # print +Z expressed in asm frame
    print(f'{n:32s} err {err:.3f} print-up in asm = {up.round(3)} t={t.round(2)} vol a/b {a.volume/1000:.2f}/{b.volume/1000:.2f}')
json.dump(out,open('xf.json','w'))
