"""Collect layout, slicer results (OrcaSlicer CLI statistics) and the parts cross-check into summary.json.

Usage: python make_summary.py <orca_out_PETG_dir> <orca_out_TPU_dir>
Copies a trimmed copy of each plate_N.statistics.json into hardware/v6.3/plates/slice_check/.
"""
import json
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_v63 as pv          # noqa: E402
import plates_v63 as pl         # noqa: E402
import write_3mf as w3         # noqa: E402
import build_print_v63 as b     # noqa: E402

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
    v63 = json.load(open(os.path.join(PARTS_DIR, 'v63.json')))
    viewer = json.load(open(os.path.join(PARTS_DIR, 'v63_viewer.json')))
    ours = {}
    for plate in pl.PLATES_PETG + pl.PLATES_TPU:
        for pid, q in plate['parts']:
            if pv.PART[pid]['kind'] == 'part':
                ours[pid] = ours.get(pid, 0) + q
    per = v63['grams']['per_part_v63']
    expected = {k: v['qty'] for k, v in per.items()}
    listed = set(v63['changed_parts']) | {r.split(' ')[0] for r in v63['reused_unchanged']}
    missing = {k: q for k, q in expected.items() if ours.get(k, 0) < q}
    extra = {k: q for k, q in ours.items() if k not in expected}
    qty_mismatch = {k: (q, ours.get(k)) for k, q in expected.items() if ours.get(k, 0) not in (0, q)}
    viewer_ids = [p['id'] for p in viewer['parts'] if not p['bought']]
    vmap = {'guarnizione_piano': ['guarnizione_piano_v5'], 'piastra_finestra_nero': ['piastra_finestra_v62'], 'piastra_finestra_verde': ['piastra_finestra_v62'],
            'labbri': ['labbro_pettine_v62'], 'disco_v61_arancio': ['disco_v61'], 'disco_v61_nero': ['disco_v61'],
            'piastra_gate_nero': ['piastra_gate_v62'], 'piastra_gate_verde': ['piastra_gate_v62'], 'linguetta_sicura': ['linguetta_sicura_v63'],
            'guscio_v611_basso': ['guscio_v611'], 'guscio_v611_alto': ['guscio_v611']}
    for k in ['fondello_v63_fondo', 'fondello_v63_fianco', 'fondello_v63_bordo', 'fondello_v63_pannello', 'fondello_v63_pannello_2',
              'fondello_v63_pannello_3', 'fondello_v63_pannello_4', 'fondello_v63_pannello_5']:
        vmap[k] = ['fondello_v63']
    viewer_unmatched = [vid for vid in viewer_ids if not all(t in ours for t in vmap.get(vid, [vid]))]
    asm_files = sorted(f for f in os.listdir(os.path.join(PARTS_DIR, 'v63_asm')) if f.endswith('.stl') and not f.startswith('bought_'))
    petg = {k: q for k, q in ours.items() if pv.PART[k]['material'] == 'PETG'}
    tpu = {k: q for k, q in ours.items() if pv.PART[k]['material'] == 'TPU'}
    return dict(expected_from_v63_json=expected, missing=missing, extra=extra, qty_mismatch=qty_mismatch,
                listed_in_changed_or_reused_not_in_grams=sorted(listed - set(expected)),
                v63_viewer_printed_ids=viewer_ids, v63_viewer_unmatched=viewer_unmatched, v63_asm_printed_files=asm_files,
                count_v63_json=v63['grams']['v63'],
                count_print_v63=dict(PETG_parts=len(petg), PETG_pieces=sum(petg.values()), TPU_pieces=sum(tpu.values()),
                                     test_pieces=sum(1 for p in pv.PARTS if p['kind'] == 'test')),
                changed_in_v63=sorted(v63['changed_parts']),
                removed_in_v63=['canalina_base_v62 x2', 'canalina_coperchio_v62 x2', 'canalina_tappo_v62', 'nottolino_v611 x3'],
                cad_print_orientations_verified=['flangia_piano_v63: shelf-side face down, no pin, d4.0 x 2.7 dowel hole (22371 mm2 on the bed, 847 mm2 overhang)',
                                                 'linguetta_sicura_v63: on its back (56.5 x 12 x 4.8)', 'passacavo_v63: lip on the bed (74.5 mm2 base, 8.9 mm2 overhang)',
                                                 'anello_saracinesca_v63: teardrop window, no flat bridge', 'saracinesca_v63: one body, flat',
                                                 'flangia_alta_v63: shelf face down, pins up', 'scatola_v63: no region needing support'],
                cad_findings=['6.3.0 fixes verified: dowel seat in flangia_piano_v63 closed 360 deg (wall 100 % at r 2.05..4.0, section z 68.75)',
                              '6.3.0 fixes verified: fondello_v63 spigot ring unioned with the cap (one watertight body after cleaning; the raw '
                              'STL carries 4 zero-area slivers that the manifold clean drops); the 1051 mm2 flat ledge at z 31.4 is gone, '
                              '84 mm2 of flat bits remain at z 30.8; the O-ring groove ceiling (627 mm2 at z 35.3, 1.5 mm deep) is unchanged',
                              'fondello_v611 / fondello_v62 keep the separate spigot ring (older packages not regenerated)'])


def bought_parts():
    S = 'v63_viewer.json / v63.json'
    rows = [
        dict(qty=1, item='dowel pin ISO 2338 4 m6 x 6, stainless', use='gate blade pivot, pressed into the lower flange plate'),
        dict(qty=4, item='wood screw 5x35 pan head (5x30 for an 18 mm shelf)', use='flange set -> shelf (they also clamp the cable jacket)'),
        dict(qty=7, item='M3 heat-set insert RX-M3x5.7', use='3 in the bowl (stack screws P1..P3), 4 in the box (servo)'),
        dict(qty=3, item='M3x40 DIN912 A2', use='box + tower + bowl stack, from below'),
        dict(qty=2, item='O-ring NBR70 3x1', use='under the P2/P3 stack-screw heads in the roof countersinks'),
        dict(qty=3, item='EJOT PT K30x12 thread-forming screw, Torx T10', use='cap -> box bosses (replace the thumb-turns), from below'),
        dict(qty=3, item='O-ring NBR70 3x1', use='under the three cap screw heads'),
        dict(qty=3, item='EJOT PT K30x12 thread-forming screw', use='shell tabs -> bowl (d2.5 pilots, no inserts)'),
        dict(qty=2, item='EJOT PT K30x10 thread-forming screw', use='chute ears -> bowl (d2.5 pilots, no inserts)'),
        dict(qty=4, item='M3x8 DIN912 A2 + washer', use='servo -> cradle inserts'),
        dict(qty=1, item='M3x8 DIN912 A2', use='hub -> servo spline'),
        dict(qty=2, item='O-ring NBR70 9x2', use='shaft (tower module)'),
        dict(qty=1, item='O-ring NBR70 24x2', use='tower <-> box face seal'),
        dict(qty=1, item='O-ring NBR70 14x1.5', use='latch push-button, in the shell bore groove'),
        dict(qty=1, item='O-ring NBR70 132x2', use='shell | cap seam, in the cap spigot groove'),
        dict(qty=1, item='M12x1.5 cable gland IP68 + locknut', use='box wall'),
        dict(qty=1, item='M12x1.5 ePTFE membrane vent IP68 + locknut', use='box roof'),
        dict(qty=1, item='M8 A-coded 4-pin IP67 inline connector pair', use='unit pigtail <-> supply cable, in the pod top'),
        dict(qty=1, item='12 V cable, unit side (pigtail) + supply cable PUR 4x0.34 d5', use='supply cable runs through the flange tunnel'),
        dict(qty=1, item='cable tie 3.6 x 140, UV-stable PA66', use='strain relief, cinched in the upper plate window'),
        dict(qty=1, item='IP67 12 mm momentary push-button, flush flat head, M12x1 front mount, short body (<= 14 mm behind the panel, d13), front gasket',
             use='control panel; check the depth on the datasheet (14 mm free behind the mount wall)'),
        dict(qty=2, item='panel light pipe d5 x 9-10 mm, flat flush lens, flange d8 (clear PC) + O-ring NBR70 5x1 each', use='status and Wi-Fi LEDs'),
        dict(qty=2, item='LED 3 mm (status green, Wi-Fi blue) + series resistors on the board', use='behind the light pipes'),
        dict(qty=1, item='IP67 adhesive acoustic vent, ePTFE, d15 disc with d8 active area', use='speaker opening in the cap'),
        dict(qty=1, item='mylar speaker d20 x 4.5, 8 ohm 0.5 W + foam ring d20/12 x 1', use='meow / sounds'),
        dict(qty=1, item='harness JST-XH 2.54 8-pin', use='panel (button, LEDs, speaker, 1 spare) -> board; unplug before pulling the cap off'),
        dict(qty=1, item='standard servo (25T spline)', use='drive'),
        dict(qty=1, item='70 x 50 perfboard + ESP32-WROVER dev board + Pololu D36V50F6 12 V regulator + 5 V logic regulator + 1000 uF capacitor', use='electronics'),
        dict(qty=1, item='food-grade silicone grease NSF H1', use='factory: O-rings'),
    ]
    for r in rows:
        r['source'] = S
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
    for material, plates, d, proj in (('PETG', pl.PLATES_PETG, d_petg, 'Kibble_Dispenser_v63_PETG.bambu.3mf'),
                                      ('TPU', pl.PLATES_TPU, d_tpu, 'Kibble_Dispenser_v63_TPU.bambu.3mf')):
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
        project='Kibble Dispenser Outdoor v6.3', generated=datetime.date.today().isoformat(),
        printer=dict(model='Bambu Lab A1', bed_mm=[256, 256, 256], plate='Textured PEI', nozzle_mm=0.4, ams='AMS lite (4 slots)',
                     machine_profile=b.MACHINE, process_profile=b.PROCESS),
        filament_slots={'AMS lite slot 1': 'PETG black (structure) - Generic PETG @BBL A1, #1A1A1A',
                        'AMS lite slot 2': 'PETG orange (touch points) - Generic PETG @BBL A1, #F07A1A',
                        'AMS lite slot 3': 'PETG green (food path) - Generic PETG @BBL A1, #2E9D4F',
                        'AMS lite slot 4': 'suggested: a second PETG black spool as auto-refill backup (black is most of the PETG); otherwise leave empty',
                        'external spool': 'TPU 95A yellow (seals) - Generic TPU @BBL A1, #F2C81E; TPU cannot go through the AMS lite'},
        files=dict(bambu_projects=['Kibble_Dispenser_v63_PETG.bambu.3mf', 'Kibble_Dispenser_v63_TPU.bambu.3mf'],
                   plain_3mf_per_plate='plates/', stl_print_orientation='stl/', previews='preview/', layout='layout.json',
                   slicer_statistics='slice_check/', guide='README.md', generator='tools/build_print_v63.py, tools/make_summary.py, tools/make_guide.py, tools/run_all.sh'),
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
