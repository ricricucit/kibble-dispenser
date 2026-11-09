"""Collect layout, slicer results (OrcaSlicer CLI statistics) and the parts cross-check into summary.json.

Usage: python make_summary.py <orca_out_PETG_dir> <orca_out_TPU_dir>
Copies a trimmed copy of each plate_N.statistics.json into print_v6/slice_check/.
"""
import json
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_v6 as pv          # noqa: E402
import plates_v6 as pl         # noqa: E402
import write_3mf as w3         # noqa: E402
import build_print_v6 as b     # noqa: E402

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
    v6 = json.load(open(os.path.join(PARTS_DIR, 'v6.json')))
    viewer = json.load(open(os.path.join(PARTS_DIR, 'v6_viewer.json')))
    ours = {}
    for plate in pl.PLATES_PETG + pl.PLATES_TPU:
        for pid, q in plate['parts']:
            pid = pv.resolve(pid)
            ours[pid] = ours.get(pid, 0) + q
    expected = {}
    for k in v6['parts_printed_PETG']:
        expected[k] = 4 if k == 'nottolino_v6' else 1
    for k in v6['parts_TPU_95A']:
        if k.startswith('labbro_'):
            for n in ('labbro_uscita_1', 'labbro_uscita_2', 'labbro_finestra_1', 'labbro_finestra_2'):
                expected[pv.resolve(n)] = 1
        else:
            expected[pv.resolve(k)] = 1
    missing = {k: q for k, q in expected.items() if ours.get(k, 0) < q}
    viewer_ids = [p['id'] for p in viewer['parts'] if not p['bought']]
    vmap = {'guarnizione_piano': 'guarnizione_piano_v5', 'piastra_finestra_nero': 'piastra_finestra_v4b', 'piastra_finestra_verde': 'piastra_finestra_v4b',
            'labbri': 'labbro_*', 'disco_v6_arancio': 'disco_v6', 'disco_v6_nero': 'disco_v6', 'piastra_gate_nero': 'piastra_gate_v4b',
            'piastra_gate_verde': 'piastra_gate_v4b', 'fondello_v6_nero': 'fondello_v6', 'fondello_v6_arancio': 'fondello_v6', 'nottolini_v6': 'nottolino_v6'}
    viewer_unmatched = []
    for vid in viewer_ids:
        t = vmap.get(vid, vid)
        if t == 'labbro_*':
            ok = all(pv.resolve(n) in ours for n in ('labbro_uscita_1', 'labbro_uscita_2', 'labbro_finestra_1', 'labbro_finestra_2'))
        else:
            ok = pv.resolve(t) in ours
        if not ok:
            viewer_unmatched.append(vid)
    asm_files = sorted(f for f in os.listdir(os.path.join(PARTS_DIR, 'v6_asm')) if not f.startswith('bought_'))
    petg_pieces = sum(q for k, q in ours.items() if pv.PART[k]['material'] == 'PETG' and pv.PART[k]['kind'] == 'part')
    tpu_pieces = sum(q for k, q in ours.items() if pv.PART[k]['material'] == 'TPU' and pv.PART[k]['kind'] == 'part')
    return dict(expected_from_v6_json=expected, missing=missing, v6_viewer_printed_ids=viewer_ids,
                v6_viewer_unmatched=viewer_unmatched, v6_asm_printed_files=asm_files,
                count_v6_json=dict(PETG_parts=v6['count']['v6']['printed_PETG_parts'], PETG_pieces=v6['count']['v6']['printed_PETG_pieces'],
                                   TPU_pieces=v6['count']['v6']['printed_TPU_parts']),
                count_print_v6=dict(PETG_parts=sum(1 for k in ours if pv.PART[k]['material'] == 'PETG' and pv.PART[k]['kind'] == 'part'),
                                    PETG_pieces=petg_pieces, TPU_pieces=tpu_pieces,
                                    test_pieces=sum(q for k, q in ours.items() if pv.PART[k]['kind'] == 'test')),
                tpu_v6_redesign_used=dict(pv.ALIAS),
                tpu_v6_redesign_pending=[v for k, v in pv.TPU_V6_REDESIGN.items() if k not in pv.ALIAS])


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
    for material, plates, d, proj in (('PETG', pl.PLATES_PETG, d_petg, 'Kibble_Dispenser_v6_PETG.bambu.3mf'),
                                      ('TPU', pl.PLATES_TPU, d_tpu, 'Kibble_Dispenser_v6_TPU.bambu.3mf')):
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
                              source=p['source']))
    summary = dict(
        project='Kibble Dispenser Outdoor v6', generated=datetime.date.today().isoformat(),
        printer=dict(model='Bambu Lab A1', bed_mm=[256, 256, 256], plate='Textured PEI', nozzle_mm=0.4, ams='AMS lite (4 slots)',
                     machine_profile=b.MACHINE, process_profile=b.PROCESS),
        filament_slots={'AMS lite slot 1': 'PETG black (structure) - Generic PETG @BBL A1, #1A1A1A',
                        'AMS lite slot 2': 'PETG orange (touch points) - Generic PETG @BBL A1, #F07A1A',
                        'AMS lite slot 3': 'PETG green (food path) - Generic PETG @BBL A1, #2E9D4F',
                        'AMS lite slot 4': 'suggested: a second PETG black spool as auto-refill backup (black is ~85 % of all PETG); otherwise leave empty',
                        'external spool': 'TPU 95A yellow (seals) - Generic TPU @BBL A1, #F2C81E; TPU cannot go through the AMS lite'},
        files=dict(bambu_projects=['Kibble_Dispenser_v6_PETG.bambu.3mf', 'Kibble_Dispenser_v6_TPU.bambu.3mf'],
                   plain_3mf_per_plate='plates/', stl_print_orientation='stl/', previews='preview/', layout='layout.json',
                   slicer_statistics='slice_check/', guide='README.md', generator='tools/build_print_v6.py, tools/make_summary.py'),
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
        cross_check=cross_check())
    json.dump(summary, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)
    print('summary.json written; totals', summary['totals'])
    return summary


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
