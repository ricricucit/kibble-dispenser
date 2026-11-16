"""3MF writers: plain 3MF core (any slicer) and Bambu Studio project 3MF (plates, filaments, settings).

The Bambu layout follows src/libslic3r/Format/bbs_3mf.cpp of BambuStudio (master, 2026):
  3D/3dmodel.model                 build items + composite objects (components with p:path)
  3D/Objects/object_<k>.model      one mesh object per volume (colour part)
  3D/_rels/3dmodel.model.rels      relationships to the object files
  Metadata/model_settings.config   objects/parts (names, extruder = filament slot, per-object settings), plates
  Metadata/project_settings.config full print/filament/printer config (JSON)
  Metadata/plate_<n>.png           plate thumbnails
Plates are laid out like PartPlateList::compute_shape_position: stride = 1.2 x bed size, columns = ceil-ish sqrt(n).
"""
import io
import json
import math
import zipfile
import numpy as np

CT_XML = ('<?xml version="1.0" encoding="UTF-8"?>\n'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
          ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
          ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
          ' <Default Extension="png" ContentType="image/png"/>\n'
          ' <Default Extension="gcode" ContentType="text/x.gcode"/>\n'
          '</Types>')

OBJECT_UUID_SUFFIX = '-61cb-4c03-9d28-80fed5dfa1dc'
SUB_OBJECT_UUID_SUFFIX = '-81cb-4c03-9d28-80fed5dfa1dc'
COMPONENT_UUID_SUFFIX = '-b206-40ff-9872-83e8017abed1'
BUILD_UUID = '2c7c17d8-22b5-4d84-8835-1976022ea369'
BUILD_UUID_SUFFIX = '-b1ec-4553-aec9-835e5b724bb4'


def _esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'))


def _f(v):
    return '%.9g' % v


def _mesh_xml(m, indent='   '):
    """<mesh> with vertices/triangles; m is a trimesh."""
    out = io.StringIO()
    out.write(f'{indent}<mesh>\n{indent} <vertices>\n')
    for x, y, z in np.asarray(m.vertices, dtype=np.float64):
        out.write(f'{indent}  <vertex x="{_f(x)}" y="{_f(y)}" z="{_f(z)}"/>\n')
    out.write(f'{indent} </vertices>\n{indent} <triangles>\n')
    for a, b, c in np.asarray(m.faces):
        out.write(f'{indent}  <triangle v1="{a}" v2="{b}" v3="{c}"/>\n')
    out.write(f'{indent} </triangles>\n{indent}</mesh>\n')
    return out.getvalue()


def _transform_3mf(T):
    """4x4 -> 3MF 12-number transform (column-major 3x4)."""
    return ' '.join(_f(T[r, c]) for c in range(4) for r in range(3))


# --------------------------------------------------------------------------------------------
# plain 3MF (core spec + base materials as display colours), one composite object per part
# --------------------------------------------------------------------------------------------
def write_plain_3mf(path, objects, materials, title=''):
    """objects: [dict(name, volumes=[dict(name, material (key), mesh (world coords))])]
    materials: {key: (display name, '#RRGGBB')}"""
    mkeys = list(materials)
    out = io.StringIO()
    out.write('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
              'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n')
    out.write(f' <metadata name="Title">{_esc(title)}</metadata>\n')
    out.write(' <metadata name="Application">kibble-dispenser print_v6 generator</metadata>\n')
    out.write(' <resources>\n  <basematerials id="1">\n')
    for k in mkeys:
        n, hx = materials[k]
        out.write(f'   <base name="{_esc(n)}" displaycolor="{hx.upper()}FF"/>\n')
    out.write('  </basematerials>\n')
    nid = 2
    build = []
    for ob in objects:
        comp_ids = []
        for v in ob['volumes']:
            out.write(f'  <object id="{nid}" name="{_esc(v["name"])}" type="model" pid="1" pindex="{mkeys.index(v["material"])}">\n')
            out.write(_mesh_xml(v['mesh']))
            out.write('  </object>\n')
            comp_ids.append(nid)
            nid += 1
        if len(comp_ids) == 1:
            build.append(comp_ids[0])
        else:
            out.write(f'  <object id="{nid}" name="{_esc(ob["name"])}" type="model">\n   <components>\n')
            for cid in comp_ids:
                out.write(f'    <component objectid="{cid}"/>\n')
            out.write('   </components>\n  </object>\n')
            build.append(nid)
            nid += 1
    out.write(' </resources>\n <build>\n')
    for b in build:
        out.write(f'  <item objectid="{b}"/>\n')
    out.write(' </build>\n</model>\n')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
            '</Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CT_XML)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', out.getvalue())


# --------------------------------------------------------------------------------------------
# Bambu Studio project
# --------------------------------------------------------------------------------------------
def plate_columns(n):
    v = math.sqrt(n)
    r = round(v)
    return int(r + 1 if v > r else r)


def plate_origin(i, n, bed=(256.0, 256.0)):
    cols = plate_columns(n)
    row, col = i // cols, i % cols
    return col * bed[0] * 1.2, -row * bed[1] * 1.2


def write_bambu_project(path, plates, project_config, app_version, title='', designer='', description='',
                        thumbnails=None, bed=(256.0, 256.0)):
    """plates: [dict(name, objects=[dict(name, settings{key: str}, volumes=[dict(name, extruder int, mesh local)],
                                          instances=[(x_bed, y_bed)])])]
    Meshes are in object-local coordinates (rotation already applied, z from 0); instances give the bed position
    of the object origin on that plate. thumbnails: {plate_index: png bytes}."""
    n_plates = len(plates)
    model_head = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                  '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
                  'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
                  'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n')
    files = {}
    main = io.StringIO()
    main.write(model_head)
    meta = {'Application': f'BambuStudio-{app_version}', 'BambuStudio:3mfVersion': '1', 'Copyright': '', 'CreationDate': '',
            'Description': description, 'Designer': designer, 'DesignerCover': '', 'DesignerUserId': '', 'License': '',
            'ModificationDate': '', 'Origin': '', 'Title': title}
    import datetime
    today = datetime.date.today().isoformat()
    meta['CreationDate'] = meta['ModificationDate'] = today
    for k in sorted(meta):
        main.write(f' <metadata name="{k}">{_esc(meta[k])}</metadata>\n')
    main.write(' <resources>\n')
    build_items = []
    cfg = io.StringIO()
    cfg.write('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n')
    plate_instances = [[] for _ in plates]
    object_paths = []
    next_id = 1
    backup_id = 0
    identify = 1000
    comp_xml = io.StringIO()
    for pi, plate in enumerate(plates):
        ox, oy = plate_origin(pi, n_plates, bed)
        for ob in plate['objects']:
            backup_id += 1
            sub = io.StringIO()
            sub.write(model_head)
            sub.write(' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n')
            vol_ids = []
            for vi, v in enumerate(ob['volumes']):
                vid = next_id
                next_id += 1
                vol_ids.append(vid)
                otype = 'other' if v.get('modifier') else 'model'   # modifier, support enforcer/blocker volumes
                sub.write(f'  <object id="{vid}" p:UUID="{(vi + (backup_id << 16)):08x}{SUB_OBJECT_UUID_SUFFIX}" type="{otype}">\n')
                sub.write(_mesh_xml(v['mesh']))
                sub.write('  </object>\n')
            sub.write(' </resources>\n <build/>\n</model>\n')
            opath = f'3D/Objects/object_{backup_id}.model'
            files[opath] = sub.getvalue()
            object_paths.append(opath)
            oid = next_id
            next_id += 1
            comp_xml.write(f'  <object id="{oid}" p:UUID="{backup_id:08x}{OBJECT_UUID_SUFFIX}" type="model">\n   <components>\n')
            for vi, vid in enumerate(vol_ids):
                comp_xml.write(f'    <component p:path="/{opath}" objectid="{vid}" '
                               f'p:UUID="{(vi + (backup_id << 16)):08x}{COMPONENT_UUID_SUFFIX}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n')
            comp_xml.write('   </components>\n  </object>\n')
            # model_settings: object + parts
            faces = sum(len(v['mesh'].faces) for v in ob['volumes'] if not v.get('modifier'))
            cfg.write(f'  <object id="{oid}">\n')
            cfg.write(f'    <metadata key="name" value="{_esc(ob["name"])}"/>\n')
            cfg.write(f'    <metadata key="extruder" value="{ob["volumes"][0]["extruder"]}"/>\n')
            for k, val in ob.get('settings', {}).items():
                cfg.write(f'    <metadata key="{_esc(k)}" value="{_esc(val)}"/>\n')
            cfg.write(f'    <metadata face_count="{faces}"/>\n')
            for vi, (vid, v) in enumerate(zip(vol_ids, ob['volumes'])):
                sub_t = v.get('subtype', 'modifier_part') if v.get('modifier') else 'normal_part'
                cfg.write(f'    <part id="{vid}" subtype="{sub_t}">\n')
                cfg.write(f'      <metadata key="name" value="{_esc(v["name"])}"/>\n')
                cfg.write('      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n')
                cfg.write(f'      <metadata key="source_file" value="{_esc(v.get("source_file", ""))}"/>\n')
                cfg.write(f'      <metadata key="source_object_id" value="0"/>\n')
                cfg.write(f'      <metadata key="source_volume_id" value="{vi}"/>\n')
                if not v.get('modifier'):
                    cfg.write(f'      <metadata key="extruder" value="{v["extruder"]}"/>\n')
                for k, val in v.get('settings', {}).items():
                    cfg.write(f'      <metadata key="{_esc(k)}" value="{_esc(val)}"/>\n')
                cfg.write(f'      <mesh_stat face_count="{len(v["mesh"].faces)}" edges_fixed="0" degenerate_facets="0" '
                          f'facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n')
                cfg.write('    </part>\n')
            cfg.write('  </object>\n')
            for ii, (x, y) in enumerate(ob['instances']):
                T = np.eye(4)
                T[0, 3], T[1, 3] = ox + x, oy + y
                build_items.append((oid, T))
                identify += 1
                plate_instances[pi].append((oid, ii, identify))
    main.write(comp_xml.getvalue())
    main.write(' </resources>\n')
    main.write(f' <build p:UUID="{BUILD_UUID}">\n')
    for oid, T in build_items:
        main.write(f'  <item objectid="{oid}" p:UUID="{oid:08x}{BUILD_UUID_SUFFIX}" transform="{_transform_3mf(T)}" printable="1"/>\n')
    main.write(' </build>\n</model>\n')
    for pi, plate in enumerate(plates):
        cfg.write('  <plate>\n')
        cfg.write(f'    <metadata key="plater_id" value="{pi + 1}"/>\n')
        cfg.write(f'    <metadata key="plater_name" value="{_esc(plate["name"])}"/>\n')
        cfg.write('    <metadata key="locked" value="false"/>\n')
        cfg.write('    <metadata key="filament_map_mode" value="Auto For Flush"/>\n')
        if thumbnails and pi in thumbnails:
            cfg.write(f'    <metadata key="thumbnail_file" value="Metadata/plate_{pi + 1}.png"/>\n')
        for oid, ii, ident in plate_instances[pi]:
            cfg.write('    <model_instance>\n')
            cfg.write(f'      <metadata key="object_id" value="{oid}"/>\n')
            cfg.write(f'      <metadata key="instance_id" value="{ii}"/>\n')
            cfg.write(f'      <metadata key="identify_id" value="{ident}"/>\n')
            cfg.write('    </model_instance>\n')
        cfg.write('  </plate>\n')
    cfg.write('  <assemble>\n')
    cfg.write('  </assemble>\n')
    cfg.write('</config>\n')
    rels_main = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                 ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
                 ' <Relationship Target="/Metadata/plate_1.png" Id="rel-2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/thumbnail"/>\n'
                 ' <Relationship Target="/Metadata/plate_1.png" Id="rel-4" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-middle"/>\n'
                 ' <Relationship Target="/Metadata/plate_1_small.png" Id="rel-5" Type="http://schemas.bambulab.com/package/2021/cover-thumbnail-small"/>\n'
                 '</Relationships>')
    rels_model = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                  + ''.join(f' <Relationship Target="/{p}" Id="rel-{i + 1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
                            for i, p in enumerate(object_paths)) + '</Relationships>')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CT_XML)
        z.writestr('_rels/.rels', rels_main)
        z.writestr('3D/3dmodel.model', main.getvalue())
        z.writestr('3D/_rels/3dmodel.model.rels', rels_model)
        for p, s in files.items():
            z.writestr(p, s)
        z.writestr('Metadata/model_settings.config', cfg.getvalue())
        z.writestr('Metadata/project_settings.config', json.dumps(project_config, indent=4, ensure_ascii=False))
        if thumbnails:
            for pi, png in thumbnails.items():
                z.writestr(f'Metadata/plate_{pi + 1}.png', png['big'])
                z.writestr(f'Metadata/plate_{pi + 1}_small.png', png['small'])


# --------------------------------------------------------------------------------------------
# project_settings.config from resolved Bambu system profiles
# --------------------------------------------------------------------------------------------
META_KEYS = {'type', 'name', 'from', 'instantiation', 'inherits', 'setting_id', 'include', 'inherits_chain', 'description',
             'compatible_printers', 'compatible_printers_condition', 'compatible_prints', 'compatible_prints_condition',
             'renamed_from', 'filament_id', 'base_id', 'version', 'is_custom_defined'}


def _rgb(hx):
    hx = hx.lstrip('#')
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def _rgb2hsv(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    d = mx - mn
    if d == 0:
        h = 0.0
    elif mx == r:
        h = 60.0 * (((g - b) / d) % 6)
    elif mx == g:
        h = 60.0 * (((b - r) / d) + 2)
    else:
        h = 60.0 * (((r - g) / d) + 4)
    s = 0.0 if mx == 0 else d / mx
    return h, s, mx


def flush_volume(src_hex, dst_hex, min_flush=92, max_flush=900):
    """Bambu Studio FlushVolCalculator::calc_flush_vol_rgb (colour model) + nozzle-volume minimum (A1: 92 mm3)."""
    sr, sg, sb = [c / 255.0 for c in _rgb(src_hex)]
    dr, dg, db = [c / 255.0 for c in _rgb(dst_hex)]
    h1, s1, v1 = _rgb2hsv(sr, sg, sb)
    h2, s2, v2 = _rgb2hsv(dr, dg, db)
    dx = math.cos(math.radians(h1)) * s1 * v1 - math.cos(math.radians(h2)) * s2 * v2
    dy = math.sin(math.radians(h1)) * s1 * v1 - math.sin(math.radians(h2)) * s2 * v2
    hs = min(1.2, math.hypot(dx, dy))
    lf = sr * 0.3 + sg * 0.59 + sb * 0.11
    lt = dr * 0.3 + dg * 0.59 + db * 0.11
    if lt >= lf:
        lumi = (lt - lf) ** 0.7 * 560.0
    else:
        lumi = (lf - lt) * 80.0
        hs = min(0.67 * v2 + 0.33 * v1, hs)
    hsf = 230.0 * hs
    fv = math.sqrt(hsf * hsf + lumi * lumi - 2 * hsf * lumi * math.cos(math.radians(120.0)))
    fv = max(fv, 60.0) + min_flush
    return int(min(fv, max_flush))


def build_project_config(machine, process, filaments, colours, app_version, plate_count, wipe_tower_xy, bed_type='Textured PEI Plate'):
    cfg = {}
    for src in (process, machine):
        for k, v in src.items():
            if k not in META_KEYS:
                cfg[k] = v
    fkeys = []
    for f in filaments:
        for k in f:
            if k not in META_KEYS and k not in fkeys:
                fkeys.append(k)
    for k in fkeys:
        vals = [f.get(k) for f in filaments]
        if all(isinstance(v, list) for v in vals if v is not None):
            out = []
            for v in vals:
                out += (v if v is not None else [''])
            cfg[k] = out
        else:
            cfg[k] = vals[0]
    n = len(filaments)
    cfg['filament_settings_id'] = [f['name'] for f in filaments]
    cfg['filament_ids'] = [f.get('filament_id', '') for f in filaments]
    cfg['filament_colour'] = list(colours)
    cfg['filament_multi_colour'] = list(colours)
    cfg['filament_colour_type'] = ['1'] * n
    cfg['filament_self_index'] = [str(i + 1) for i in range(n)]
    cfg['filament_map'] = ['1'] * n
    cfg['filament_map_mode'] = 'Auto For Flush'
    cfg['print_settings_id'] = process['name']
    cfg['printer_settings_id'] = machine['name']
    cfg['default_print_profile'] = process['name']
    cfg['curr_bed_type'] = bed_type
    cfg['nozzle_volume_type'] = ['Standard']
    mat = []
    for a in colours:
        for b in colours:
            mat.append('0' if a == b else str(flush_volume(a, b)))
    cfg['flush_volumes_matrix'] = mat
    cfg['flush_volumes_vector'] = ['140'] * (2 * n)
    cfg['flush_multiplier'] = ['1']
    cfg['wipe_tower_x'] = [_f(x) for x, _ in wipe_tower_xy]
    cfg['wipe_tower_y'] = [_f(y) for _, y in wipe_tower_xy]
    cfg['name'] = 'project_settings'
    cfg['from'] = 'project'
    cfg['version'] = app_version
    return dict(sorted(cfg.items()))
