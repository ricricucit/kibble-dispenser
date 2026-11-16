"""Build review-only Bambu projects for the 8 new v6.4 parts (one part per plate, settings as stated in v64.json 'print')
with the 6.3 package writer; outputs only under review_v64/slice."""
import sys,os,json,numpy as np,trimesh
sys.path.insert(0,'/home/claude/asm/print_v63/tools')
import write_3mf as w3, parts_v63 as pv
P='/home/claude/asm/parts'; OUT='/home/claude/asm/review_v64/slice'
R=json.load(open('/home/claude/asm/print_v63/tools/bbl_profiles_resolved.json'))
APP='02.05.00.00'
IP=dict(pv.S_IP66)
def obj(name,settings,xy=(128,128)):
    m=pv._manifold_clean(trimesh.load(f'{P}/{name}_print.stl'))
    c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]])
    return dict(name=name,settings=settings,volumes=[dict(name=name,extruder=1,mesh=m,source_file=name+'_print.stl')],instances=[xy])
variant=sys.argv[1]
SUP=dict(pv.SUP_BED_SNUG,support_threshold_angle='45') if variant=='sup' else {}
petg=[('scatola_v64',{**IP,'ironing_type':'top',**SUP}),
      ('fondello_v64',{**IP,**SUP}),
      ('guscio_v64',{'wall_loops':'5','sparse_infill_density':'15%','brim_type':'outer_only','brim_width':'6'}),
      ('modulo_vasca_v64',{**IP,**SUP}),
      ('modulo_coperchio_v64',{**IP,**SUP}),
      ('modulo_anello_speaker_v64',dict(pv.S_SOLID))]
tpu=[('guarnizione_fondello_v64',{**pv.S_TPU,'outer_wall_speed':'20','inner_wall_speed':'20'}),
     ('modulo_guarnizione_v64',{**pv.S_TPU,'outer_wall_speed':'20','inner_wall_speed':'20'}),
     ('modulo_guarnizione_v64',dict(pv.S_TPU_LIP))]
for mat,lst,fil,col in (('PETG',petg,'Generic PETG @BBL A1','#1A1A1A'),('TPU',tpu,'Generic TPU @BBL A1','#F2C81E')):
    if variant=='sup' and mat=='TPU': continue
    plates=[dict(name=n,objects=[obj(n,s)]) for n,s in lst]
    cfg=w3.build_project_config(R['Bambu Lab A1 0.4 nozzle'],R['0.20mm Standard @BBL A1'],[R[fil]],[col],APP,len(plates),[(15.0,220.0)]*len(plates))
    w3.write_bambu_project(f'{OUT}/review_v64_{mat}_{variant}.bambu.3mf',plates,cfg,APP,title='review v64 '+mat)
    print('wrote',mat,variant,[p['name'] for p in plates])
