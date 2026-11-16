"""Mesh audit of every printed part of v6.4 (print orientation). Read-only on parts/."""
import json, os, sys, numpy as np, trimesh
P='/home/claude/asm/parts'
d=json.load(open(P+'/v64.json'))
reused=[v['print_file'] for v in d['parts']['safe_to_print_now (byte-identical to 6.3.0)'].values()]
new=[k+'_print.stl' for k in list(d['parts']['changed_chassis_parts'])+d['parts']['new_module_parts']]
out={}
for f in new+reused:
    m=trimesh.load(os.path.join(P,f),process=True)
    b=m.bounds; ext=b[1]-b[0]
    n=m.face_normals; a=m.area_faces
    cz=m.triangles_center[:,2]
    down=n[:,2]<-1e-6
    onbed=down&(cz<b[0][2]+0.05)
    ang=np.degrees(np.arccos(np.clip(-n[:,2],-1,1)))  # 0 = facing straight down
    # overhang angle from vertical = 90-ang ; >50deg overhang  <=> ang<40
    ov45=down&~onbed&(ang<45)
    ov35=down&~onbed&(ang<35)
    flat=down&~onbed&(ang<5)
    comps=m.split(only_watertight=False)
    r=dict(file=f,watertight=bool(m.is_watertight),winding=bool(m.is_winding_consistent),volume_cm3=round(m.volume/1000,2),
      bodies=len(comps),ext=[round(x,2) for x in ext],zmin=round(b[0][2],3),
      bed_contact_mm2=round(a[onbed].sum(),1),overhang_gt45_mm2=round(a[ov45].sum(),1),overhang_gt55_mm2=round(a[ov35].sum(),1),
      flat_down_mm2=round(a[flat].sum(),1),
      slender=round(ext[2]/max(1e-6,np.sqrt(max(a[onbed].sum(),1e-6))),2))
    out[f]=r
    print(json.dumps(r))
json.dump(out,open('audit.json','w'),indent=1)
