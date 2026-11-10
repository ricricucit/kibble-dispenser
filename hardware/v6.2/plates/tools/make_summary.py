"""Collect layout, slicer results (OrcaSlicer CLI statistics) and the parts cross-check into summary.json.

Usage: python make_summary.py <orca_out_PETG_dir> <orca_out_TPU_dir>
Copies a trimmed copy of each plate_N.statistics.json into hardware/v6.2/plates/slice_check/.
"""
import json
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_v62 as pv          # noqa: E402
import plates_v62 as pl         # noqa: E402
import write_3mf as w3         # noqa: E402
import build_print_v62 as b     # noqa: E402

OUT = b.OUT
PARTS_DIR = pv.PARTS_DIR
SLOT_OF = {'black': 'AMS lite slot 1', 'orange': 'AMS lite slot 2', 'green': 'AMS lite slot 3', 'yellow': 'external spool'}


def load_stats(d, n):
    res = []
    for i in range(1, n + 1):
        f = os.path.join(d, f'plate_{i}.statistics.json')
        if not os.path.exists(f):
            res.append(None)
            continue
        s = json.load(open(f))
        res.append(s)
    rj = json.load(open(os.path.join(d, 'result.json')))
    return res, rj


def trimmed(s):
    return dict(generator=s.get('generator'), summary=s['summary'], objects=s.get('objects'))


def cross_check():
    v62 = json.load(open(os.path.join(PARTS_DIR, 'v62.json')))
    viewer = json.load(open(os.path.join(PARTS_DIR, 'v62_viewer.json')))
    ours = {}
    for plate in pl.PLATES_PETG + pl.PLATES_TPU:
        for pid, q in plate['parts']:
            if pv.PART[pid]['kind'] == 'part':
                ours[pid] = ours.get(pid, 0) + q
    gq = {k: v['qty'] for k, v in v62['grams']['v62_changed_and_new_parts'].items()}
    expected = {k: gq.get(k, 1) for k in list(v62['changed_parts']) + list(v62['new_parts'])}
    for r in v62['reused_unchanged']:
        base = r.split(' ')[0]
        expected[base] = 3 if base == 'nottolino_v611' else 1
    missing = {k: q for k, q in expected.items() if ours.get(k, 0) < q}
    extra = {k: q for k, q in ours.items() if k not in expected}
    qty_mismatch = {k: (q, ours.get(k)) for k, q in expected.items() if ours.get(k, 0) not in (0, q)}
    viewer_ids = [p['id'] for p in viewer['parts'] if not p['bought']]
    vmap = {'guarnizione_piano': ['guarnizione_piano_v5'], 'saracinesca_lama': ['saracinesca_v62'], 'saracinesca_braccio': ['saracinesca_v62'],
            'anello_saracinesca': ['anello_saracinesca_v62'], 'piastra_finestra_nero': ['piastra_finestra_v62'], 'piastra_finestra_verde': ['piastra_finestra_v62'],
            'labbri': ['labbro_pettine_v62'], 'disco_v61_arancio': ['disco_v61'], 'disco_v61_nero': ['disco_v61'],
            'piastra_gate_nero': ['piastra_gate_v62'], 'piastra_gate_verde': ['piastra_gate_v62'],
            'guscio_v611_basso': ['guscio_v611'], 'guscio_v611_alto': ['guscio_v611'],
            'fondello_v62_fondo': ['fondello_v62'], 'fondello_v62_fianco': ['fondello_v62'], 'fondello_v62_bordo': ['fondello_v62'],
            'nottolino_v611_A': ['nottolino_v611'], 'nottolino_v611_B': ['nottolino_v611'], 'nottolino_v611_C': ['nottolino_v611'],
            'canalina_base_1': ['canalina_base_v62'], 'canalina_base_2': ['canalina_base_v62'], 'canalina_coperchio_1': ['canalina_coperchio_v62'],
            'canalina_coperchio_2': ['canalina_coperchio_v62'], 'canalina_tappo': ['canalina_tappo_v62']}
    viewer_unmatched = [vid for vid in viewer_ids if not all(t in ours for t in vmap.get(vid, [vid]))]
    asm_files = sorted(f for f in os.listdir(os.path.join(PARTS_DIR, 'v62_asm')) if f.endswith('.stl') and not f.startswith('bought_'))
    petg = {k: q for k, q in ours.items() if pv.PART[k]['material'] == 'PETG'}
    tpu = {k: q for k, q in ours.items() if pv.PART[k]['material'] == 'TPU'}
    return dict(expected_from_v62_json=expected, missing=missing, extra=extra, qty_mismatch=qty_mismatch,
                v62_viewer_printed_ids=viewer_ids, v62_viewer_unmatched=viewer_unmatched, v62_asm_printed_files=asm_files,
                count_print_v62=dict(PETG_parts=len(petg), PETG_pieces=sum(petg.values()), TPU_pieces=sum(tpu.values()),
                                     test_pieces=sum(1 for p in pv.PARTS if p['kind'] == 'test')),
                changed_in_v62=sorted(list(v62['changed_parts']) + list(v62['new_parts'])),
                colour_bodies='saracinesca_v62, piastra_gate_v62, piastra_finestra_v62 colour bodies: inside their *_print.stl (0 mm3 '
                              'outside) and the bodies add up to the print volume exactly; disco_v61 uses the v6.1.1 bodies',
                print_orientation_fixes=['flangia_piano_v62 (pivot pin -> dowel, shelf face down)', 'canalina_base_v62 (flipped)',
                                         'canalina_coperchio_v62 (open side up)', 'canalina_tappo_v62 (-90 deg about X)',
                                         'passacavo_v62 (lip on the bed)'])


def bought_parts():
    v61 = json.load(open(os.path.join(PARTS_DIR, 'v61.json')))
    v611 = json.load(open(os.path.join(PARTS_DIR, 'v611.json')))
    rows = []
    for h in v61['hardware']:
        it = h['item']
        if it.startswith('wood screw 5x25'):
            rows.append(dict(qty=4, item='wood screw 5x35 pan head (5x30 for an 18 mm shelf)', use='flange -> shelf (flange 8 mm thicker in v6.2)', source='v62.json'))
        elif it.startswith('M3x12') and 'tower' in h['use']:
            continue                                   # replaced by the M3x40 stack
        elif it.startswith('M3x10') and 'tower' in h['use']:
            continue
        elif it.startswith('M3 heat-set insert'):
            rows.append(dict(qty=12, item=it, use='8 in the bowl (3 at P1..P3 for the stack, 2 chute, 3 shell tabs), 4 servo in the box (no plateau inserts)', source='v62.json'))
        elif it.startswith('O-ring NBR70 8x1.5'):
            rows.append(dict(qty=3, item=it, use='one per thumb-turn', source='v611.json'))
        elif it.startswith('inline IP67 2-pin connector'):
            rows.append(dict(qty=1, item='M8 A-coded 4-pin IP67 inline pair + PUR 4x0.34 d5 cable', use='replaces the generic inline connector + d6 cable', source='v62.json'))
        else:
            rows.append(dict(qty=h['qty'], item=it, use=h['use'], source='v61.json'))
    for h in v611['hardware_added']:
        if h['item'].startswith('O-ring NBR70 8x1.5') or h['item'].startswith('food-grade'):
            continue
        rows.append(dict(qty=h['qty'], item=h['item'], use=h['use'], source='v611.json'))
    rows += [dict(qty=3, item='M3x40 DIN912 A2', use='box + tower + bowl stack, from below (P1 ear, P2/P3 through the roof)', source='v62.json'),
             dict(qty=2, item='O-ring NBR70 3x1', use='under the P2/P3 stack-screw heads in the roof countersinks', source='v62.json'),
             dict(qty=3, item='ST2.9x9.5 DIN 7982 countersunk', use='join the two flange plates from the shelf face', source='v62.json'),
             dict(qty=4, item='wood screw 3.5x16 countersunk', use='cable channel bases', source='v62.json'),
             dict(qty=1, item='dowel pin ISO 2338 4 m6 x 6, stainless', use='blade pivot in the lower flange plate (replaces the printed pin: print_v62 deviation, designer to confirm)', source='print_v62')]
    return rows


def main(d_petg, d_tpu):
    layout = json.load(open(os.path.join(OUT, 'layout.json')))
    files = json.load(open(os.path.join(OUT, 'tools', 'build_files.json')))
    os.makedirs(os.path.join(OUT, 'slice_check'), exist_ok=True)
    plates_out = []
    totals = {}
    total_time = 0.0
    total_swaps = 0
    slicer = None
    validation = {}
    colours_hex = {f['colour']: f['hex'] for f in pv.PETG_FILAMENTS}
    for material, plates, d, proj in (('PETG', pl.PLATES_PETG, d_petg, 'Kibble_Dispenser_v62_PETG.bambu.3mf'),
                                      ('TPU', pl.PLATES_TPU, d_tpu, 'Kibble_Dispenser_v62_TPU.bambu.3mf')):
        stats, rj = load_stats(d, len(plates))
        validation[proj] = dict(return_code=rj.get('return_code'), error_string=rj.get('error_string'),
                                plates=[dict(id=p['id'], warning=p.get('warning_message', '')) for p in rj.get('sliced_plates', [])],
                                warnings=rj.get('warnings', []))
        slot_colour = ({f['slot']: f['colour'] for f in pv.PETG_FILAMENTS} if material == 'PETG' else {1: 'yellow'})
        for i, plate in enumerate(plates):
            s = stats[i]
            L = layout[plate['key']]
            if s:
                slicer = s.get('generator')
                json.dump(trimmed(s), open(os.path.join(OUT, 'slice_check', f"{plate['key']}.statistics.json"), 'w'), indent=1)
            parts = []
            agg = {}
            for it in L['items']:
                agg[it['part']] = agg.get(it['part'], 0) + 1
            for pid, q in agg.items():
                p = pv.PART[pid]
                cols = [c for c, _ in p['bodies']]
                parts.append(dict(id=pid, label=p['label'], qty=q, material=p['material'] + (' 95A' if p['material'] == 'TPU' else ''),
                                  colours=cols, slots=[SLOT_OF[c] for c in cols], settings=p['settings'], print_note=p['note']))
            fil = {}
            if s:
                for f in s['summary']['filaments']:
                    c = slot_colour[f['id']]
                    key = f"{material} {c}"
                    fil[key] = dict(slot=SLOT_OF[c], grams=round(f['weight'], 1), model=round(f['model']['weight'], 1),
                                    support=round(f['support']['weight'], 1), prime_tower=round(f['prime_tower']['weight'], 1),
                                    flush=round(f['flush']['weight'], 1))
                    totals[key] = round(totals.get(key, 0) + f['weight'], 1)
                tmin = s['summary']['time'] / 60.0
                swaps = s['summary'].get('filament_changes', 0)
                total_time += tmin
                total_swaps += swaps
            used = sorted({c for pp in parts for c in pp['colours']}, key=lambda c: ['black', 'orange', 'green', 'yellow'].index(c))
            plates_out.append(dict(
                key=plate['key'], name=plate['name'], purpose=plate['purpose'], material=material,
                bambu_project=proj, plate_in_project=i + 1,
                plain_3mf=files['plain'][plate['key']],
                preview_top=f"preview/{plate['key']}_top.png", preview_iso=f"preview/{plate['key']}_iso.png",
                parts=parts, filament_slots=[SLOT_OF[c] + f' = {material} {c}' for c in used],
                colour_swaps=(s['summary'].get('filament_changes') if s else None),
                est_grams_per_filament=fil,
                est_grams_total=round(s['summary']['weight'], 1) if s else None,
                est_time_min=round(s['summary']['time'] / 60.0, 1) if s else None,
                est_time_hm=(f"{int(s['summary']['time'] // 3600)} h {int(s['summary']['time'] % 3600 // 60):02d} min" if s else None),
                layers=s['summary']['layer_count'] if s else None,
                prime_tower_xy_mm=L['tower_xy'], min_part_gap_mm=L['min_gap_mm']))
    flush = {}
    for a, ha in colours_hex.items():
        for c, hc in colours_hex.items():
            if a != c:
                v = w3.flush_volume(ha, hc)
                flush[f'{a}->{c}'] = dict(mm3=v, grams=round(v / 1000 * pv.DENSITY['PETG'], 2))
    checklist = []
    where = {}
    for plate in pl.PLATES_PETG + pl.PLATES_TPU:
        for pid, q in plate['parts']:
            pid = pv.resolve(pid)
            where.setdefault(pid, []).append(plate['key'])
    for p in pv.PARTS:
        checklist.append(dict(id=p['id'], label=p['label'], kind=p['kind'], material=p['material'] + (' 95A' if p['material'] == 'TPU' else ''),
                              qty=p['qty'], colours=[c for c, _ in p['bodies']], plates=where.get(p['id'], []),
                              stl=[f'stl/{f}' for f in next(r['files'] for r in files['stl'] if r['id'] == p['id'])],
                              source=p['source'], kit_module=p.get('module')))
    summary = dict(
        project='Kibble Dispenser Outdoor v6.2', generated=datetime.date.today().isoformat(),
        printer=dict(model='Bambu Lab A1', bed_mm=[256, 256, 256], plate='Textured PEI', nozzle_mm=0.4, ams='AMS lite (4 slots)',
                     machine_profile=b.MACHINE, process_profile=b.PROCESS),
        filament_slots={'AMS lite slot 1': 'PETG black (structure) - Generic PETG @BBL A1, #1A1A1A',
                        'AMS lite slot 2': 'PETG orange (touch points) - Generic PETG @BBL A1, #F07A1A',
                        'AMS lite slot 3': 'PETG green (food path) - Generic PETG @BBL A1, #2E9D4F',
                        'AMS lite slot 4': 'suggested: a second PETG black spool as auto-refill backup (black is most of the PETG); otherwise leave empty',
                        'external spool': 'TPU 95A yellow (seals) - Generic TPU @BBL A1, #F2C81E; TPU cannot go through the AMS lite'},
        files=dict(bambu_projects=['Kibble_Dispenser_v62_PETG.bambu.3mf', 'Kibble_Dispenser_v62_TPU.bambu.3mf'],
                   plain_3mf_per_plate='plates/', stl_print_orientation='stl/', previews='preview/', layout='layout.json',
                   slicer_statistics='slice_check/', guide='README.md', generator='tools/build_print_v62.py, tools/make_summary.py, tools/make_guide.py, tools/run_all.sh'),
        validation=dict(slicer=slicer, method='OrcaSlicer 2.5.0 Linux CLI (AppImage) opened each Bambu project 3MF and sliced all plates '
                                               'with the settings embedded in the project (--slice 0 --export-statistics); no Bambu Studio '
                                               'binary was available here, so the files were not opened in Bambu Studio itself',
                        results=validation, bambu_profiles=b.PROFILE_SOURCE, application_tag=f'BambuStudio-{b.APP_VERSION}'),
        plates=plates_out,
        totals=dict(grams_per_filament=totals,
                    grams_PETG=round(sum(v for k, v in totals.items() if k.startswith('PETG')), 1),
                    grams_TPU=round(sum(v for k, v in totals.items() if k.startswith('TPU')), 1),
                    time_min=round(total_time, 1), time_hm=f'{int(total_time // 60)} h {int(total_time % 60):02d} min',
                    colour_swaps=total_swaps, plates=len(plates_out),
                    note='slicer estimates (OrcaSlicer 2.5.0 with the Bambu A1 system profiles); include supports, prime tower and flush; '
                         'test plates included'),
        purge_per_swap_A1=dict(model='Bambu Studio colour flush model (FlushVolCalc) + A1 nozzle volume 92 mm3, multiplier 1.0; '
                                     'these values are written into flush_volumes_matrix of the PETG project', volumes=flush),
        parts_checklist=checklist,
        bought_parts=bought_parts(),
        cross_check=cross_check())
    json.dump(summary, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)
    print('summary.json written; totals', summary['totals'])
    return summary


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
