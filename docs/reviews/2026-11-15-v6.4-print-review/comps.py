import sys,os,numpy as np,trimesh,manifold3d as mf
P='/home/claude/asm/parts'
for f in sys.argv[1:]:
    m=trimesh.load(os.path.join(P,f),process=True)
    print('==',f,'wt',m.is_watertight,'euler',m.euler_number,'faces',len(m.faces))
    # open edges
    e=m.edges_sorted; u,c=np.unique(e,axis=0,return_counts=True)
    print('  edges count!=2:',dict(zip(*np.unique(c,return_counts=True))))
    bad=u[c!=2]
    if len(bad): 
        pts=m.vertices[bad].reshape(-1,3); print('  bad edge bbox',pts.min(0).round(2),pts.max(0).round(2))
    for c_ in m.split(only_watertight=False):
        print('  body faces',len(c_.faces),'wt',c_.is_watertight,'vol',round(c_.volume,2),'bounds',c_.bounds.round(2).tolist())
    M=mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices,np.float32),tri_verts=np.asarray(m.faces,np.uint32)))
    print('  manifold status',M.status(),'vol',round(M.volume(),1) if M.status()==mf.Error.NoError else None, 'genus',M.genus() if M.status()==mf.Error.NoError else None)
