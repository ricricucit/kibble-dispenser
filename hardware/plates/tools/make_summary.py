"""Collect layout, slicer results (OrcaSlicer CLI statistics) and the parts cross-check into summary.json.

Usage: python make_summary.py <work_dir>      (work_dir/<project id>/ holds the OrcaSlicer output of each project)
Copies a trimmed copy of each plate_N.statistics.json into slice_check/.
Per plate: product (chassis/module), parts, slicer estimates; plus products, totals, review_checks, parts_checklist,
bought_parts and the cross-check against v64.json.
"""
import datetime
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parts_v64 as pv          # noqa: E402
import plates_v64 as pl         # noqa: E402
import write_3mf as w3         # noqa: E402
import build_print_v64 as b     # noqa: E402

OUT = b.OUT
PARTS_DIR = pv.PARTS_DIR
SLOT_OF = {'black': 'AMS lite slot 1', 'orange': 'AMS lite slot 2', 'green': 'AMS lite slot 3', 'yellow': 'external spool'}


def load_stats(d, n):
    res = []
    for i in range(1, n + 1):
        f = os.path.join(d, f'plate_{i}.statistics.json')
        res.append(json.load(open(f)) if os.path.exists(f) else None)
    rj = json.load(open(os.path.join(d, 'result.json')))
    return res, rj


def trimmed(s):
    return dict(generator=s.get('generator'), summary=s['summary'], objects=s.get('objects'))


def cross_check():
    v64 = json.load(open(os.path.join(PARTS_DIR, 'v64.json')))
    ours = {}
    for plate in pl.ALL_PLATES:
        if plate.get('duplicate_of'):
            continue
        for pid, q in plate['parts']:
            if pv.PART[pid]['kind'] == 'part':
                ours[pid] = ours.get(pid, 0) + q
    expected = {k: v['qty'] for k, v in v64['grams']['per_part_chassis'].items()}
    expected.update({k: v['qty'] for k, v in v64['grams']['per_part_module'].items()})
    missing = {k: q for k, q in expected.items() if ours.get(k, 0) < q}
    extra = {k: q for k, q in ours.items() if k not in expected}
    qty_mismatch = {k: (q, ours.get(k)) for k, q in expected.items() if ours.get(k, 0) not in (0, q)}
    hashed = v64['parts']['safe_to_print_now (byte-identical to 6.3.0)']   # v64.json key name; print files with a stored hash
    hashes = {}
    for k, v in hashed.items():
        h = hashlib.sha256(open(os.path.join(PARTS_DIR, v['print_file']), 'rb').read()).hexdigest()[:16]
        hashes[k] = (h == v['print_sha256_16'])

    def cnt(prod):
        ids = [k for k in ours if pv.PART[k]['product'] == prod]
        return dict(PETG_parts=sum(1 for k in ids if pv.PART[k]['material'] == 'PETG'),
                    PETG_pieces=sum(ours[k] for k in ids if pv.PART[k]['material'] == 'PETG'),
                    TPU_pieces=sum(ours[k] for k in ids if pv.PART[k]['material'] == 'TPU'))
    return dict(expected_from_v64_json=expected, missing=missing, extra=extra, qty_mismatch=qty_mismatch,
                count_v64_json=dict(chassis=v64['grams']['chassis_v64'], module=v64['grams']['module_case_1_0']),
                count_print_v64=dict(chassis=cnt('chassis'), module=cnt('module'),
                                     test_pieces=sum(1 for p in pv.PARTS if p['kind'] == 'test')),
                print_files_match_v64_json_hashes=all(hashes.values()), hash_mismatch=[k for k, ok in hashes.items() if not ok])


def bought_parts():
    S = 'v64.json hardware / v64_viewer.json'
    C, M = 'chassis', 'module'
    rows = [
        (C, 1, 'dowel pin ISO 2338 4 m6 x 6, stainless', 'gate blade pivot, pressed into the lower flange plate'),
        (C, 4, 'wood screw 5x35 pan head (5x30 for an 18 mm shelf)', 'flange set -> shelf (they also clamp the cable jacket)'),
        (C, 9, 'M3 heat-set insert RX-M3x5.7', '3 in the bowl (stack screws P1..P3), 4 in the servo cradle of the bay, 2 in the lower ends of the holder posts (module lock)'),
        (C, 3, 'M3x40 DIN912 A2', 'servo bay + tower + bowl stack, from below'),
        (C, 1, 'O-ring NBR70 3x1', 'under the P2 stack-screw head (the only stack screw inside the bay)'),
        (C, 4, 'EJOT PT K30x12 thread-forming screw, Torx T10', 'cap -> bay bosses, from below'),
        (C, 4, 'O-ring NBR70 3x1', 'under the four cap screw heads'),
        (C, 3, 'EJOT PT K30x12 thread-forming screw', 'shell tabs -> bowl (d2.5 pilots, no inserts)'),
        (C, 2, 'EJOT PT K30x10 thread-forming screw', 'chute ears -> bowl (d2.5 pilots, no inserts)'),
        (C, 4, 'M3x8 DIN912 A2 + washer', 'servo -> cradle inserts'),
        (C, 1, 'M3x8 DIN912 A2', 'hub -> servo spline'),
        (C, 2, 'O-ring NBR70 9x2', 'shaft (tower module)'),
        (C, 1, 'O-ring NBR70 24x2', 'tower <-> bay face seal'),
        (C, 1, 'O-ring NBR70 14x1.5', 'latch push-button, in the shell bore groove'),
        (C, 1, 'M12x1.5 cable gland IP68, cable range 3 to 6.5 mm, + locknut', 'bay south wall; seals on the round servo branch of the harness (dome nut 2.5 N m)'),
        (C, 1, 'adhesive ePTFE vent patch d12', 'servo bay vent (d2 hole)'),
        (C, 1, 'M8 A-coded 4-pin IP67 inline connector pair', 'unit pigtail <-> supply cable, in the pod top'),
        (C, 1, 'M8 5-pin A-coded MALE cordset, angled, PUR d4.5, ready-made 0.5 m (cut to a 190 mm tail, plug body to splice centre)',
         'harness tail: plugs into J1 on the module lid; service loop parked on the lid; lets the module down 120 mm'),
        (C, 1, 'round 3-core PUR cable 3 x 0.25 mm2, d4.0, 100 mm', 'harness servo branch: splice -> M12 gland -> 12 mm inside the bay (40 mm spare)'),
        (C, 1, 'JR/Futaba 3-pin servo housing, female, 2.54 mm + 3 female crimp terminals for 22-26 AWG', 'crimped on the servo branch inside the bay after it passes the gland (signal, +6 V, GND); the servo plugs into it'),
        (C, 1, '2-core PUR cable 90 mm (or the pigtail of an M8 4-pin A-coded male field connector)', 'harness 12 V branch: splice -> pod-top M8 IP67 pair'),
        (C, 1, 'adhesive-lined heat shrink d8 x 20 mm', 'over the soldered Y splice (tail 1 -> 12 V +, 3 -> GND both, 2 -> servo signal, 4 -> servo +6 V, 5 not connected)'),
        (C, 1, 'cable tie 2.5 x 100', 'harness tail anchored round the lug bar of the servo bay'),
        (C, 1, '12 V supply cable PUR 4x0.34 d5', 'runs through the flange tunnel'),
        (C, 1, 'cable tie 3.6 x 140, UV-stable PA66', 'strain relief, cinched in the upper plate window'),
        (C, 1, 'standard servo (25T spline)', 'drive, in the servo bay'),
        (C, 1, 'food-grade silicone grease NSF H1', 'O-rings'),
        (M, 2, 'M3x16 ISO 4762 A2 (hex 2.5)', 'module lock, from below into the post inserts, 0.5 N m; they stay with the module'),
        (M, 5, 'EJOT PT K30x10 thread-forming screw', 'lid -> tub bosses (or melt M3 inserts into the 5 bosses for a development module)'),
        (M, 5, 'O-ring NBR70 3x1', 'under the five lid screw heads'),
        (M, 1, 'M8 5-pin A-coded panel socket (female), front mount', 'J1 in the lid turret; thread and nut size (10 to 13 mm AF assumed) TO VERIFY before printing or drilling the lid'),
        (M, 1, 'IP67 12 mm momentary push-button, short body', 'control panel, d17 recess'),
        (M, 2, 'panel light pipe d5 (clear PC) + O-ring NBR70 5x1 each', 'status and Wi-Fi LEDs'),
        (M, 2, 'LED 3 mm (status green, Wi-Fi blue) + series resistors on the board', 'behind the light pipes'),
        (M, 1, 'IP67 adhesive acoustic membrane, ePTFE, d15', 'inside, over the 7 x d1.5 speaker grille in the tub floor'),
        (M, 1, 'speaker d23 (d20 to d24 with a matching ring)', 'in the printed speaker ring on the tub floor'),
        (M, 1, '50 x 70 perfboard + ESP32-WROVER dev board on socket strips + 6 V servo regulator + 5 V logic regulator + 1000 uF capacitor',
         'electronics (demo layout of v64.json; the case is generic)'),
    ]
    return [dict(product=p, qty=q, item=i, use=u, source=S) for p, q, i, u in rows]


def main(work):
    layout = json.load(open(os.path.join(OUT, 'layout.json')))
    files = json.load(open(os.path.join(OUT, 'tools', 'build_files.json')))
    os.makedirs(os.path.join(OUT, 'slice_check'), exist_ok=True)
    plates_out, validation, slicer = [], {}, None
    colours_hex = {f['colour']: f['hex'] for f in pv.PETG_FILAMENTS}
    for pr in pl.PROJECTS:
        stats, rj = load_stats(os.path.join(work, pr['id']), len(pr['plates']))
        validation[pr['file']] = dict(return_code=rj.get('return_code'), error_string=rj.get('error_string'),
                                      plates=[dict(id=p['id'], warning=p.get('warning_message', '')) for p in rj.get('sliced_plates', [])],
                                      warnings=rj.get('warnings', []))
        material = pr['material']
        slot_colour = ({f['slot']: f['colour'] for f in pv.PETG_FILAMENTS} if pr['filaments'] == 'ams3'
                       else {1: 'black'} if material == 'PETG' else {1: 'yellow'})
        for i, plate in enumerate(pr['plates']):
            s = stats[i]
            L = layout[plate['key']]
            if s:
                slicer = s.get('generator')
                json.dump(trimmed(s), open(os.path.join(OUT, 'slice_check', f"{plate['key']}.statistics.json"), 'w'), indent=1)
            agg = {}
            for it in L['items']:
                agg[it['part']] = agg.get(it['part'], 0) + 1
            parts = []
            for pid, q in agg.items():
                p = pv.PART[pid]
                cols = [c for c, _ in p['bodies']]
                parts.append(dict(id=pid, label=p['label'], qty=q, material=p['material'] + (' 95A' if p['material'] == 'TPU' else ''),
                                  colours=cols, slots=[SLOT_OF[c] for c in cols], product=p['product'],
                                  settings=p['settings'], print_note=p['note'],
                                  helper_volumes=[m['name'] for m in pv.load_modifiers(pid, pv.load_bodies(pid))] if p['reorient'] in ('shell_tabs', 'tub_ears') else []))
            fil = {}
            if s:
                for f in s['summary']['filaments']:
                    c = slot_colour[f['id']]
                    key = f"{material} {c}"
                    fil[key] = dict(slot=SLOT_OF[c], grams=round(f['weight'], 1), model=round(f['model']['weight'], 1),
                                    support=round(f['support']['weight'], 1), prime_tower=round(f['prime_tower']['weight'], 1),
                                    flush=round(f['flush']['weight'], 1))
            used = sorted({c for pp in parts for c in pp['colours']}, key=lambda c: ['black', 'orange', 'green', 'yellow'].index(c))
            row = dict(
                key=plate['key'], name=plate['name'], purpose=plate['purpose'], material=material,
                product=plate['product'], duplicate_of=plate.get('duplicate_of'),
                bambu_project=pr['file'], plate_in_project=i + 1,
                plain_3mf=files['plain'][plate['key']],
                preview_top=f"preview/{plate['key']}_top.png", preview_iso=f"preview/{plate['key']}_iso.png",
                parts=parts, filament_slots=[SLOT_OF[c] + f' = {material} {c}' for c in used],
                colour_swaps=(s['summary'].get('filament_changes') if s else None),
                est_grams_per_filament=fil,
                est_grams_total=round(s['summary']['weight'], 1) if s else None,
                est_time_min=round(s['summary']['time'] / 60.0, 1) if s else None,
                est_time_hm=(f"{int(s['summary']['time'] // 3600)} h {int(s['summary']['time'] % 3600 // 60):02d} min" if s else None),
                layers=s['summary']['layer_count'] if s else None,
                prime_tower_xy_mm=L['tower_xy'], min_part_gap_mm=L['min_gap_mm'],
                slicer_warning=next((p.get('warning_message', '') for p in rj.get('sliced_plates', []) if p['id'] == i + 1), ''))
            plates_out.append(row)

    def tot(sel):
        t, time_, swaps, n = {}, 0.0, 0, 0
        for p in plates_out:
            if p['duplicate_of'] or not sel(p) or p['est_time_min'] is None:
                continue
            n += 1
            for k, v in p['est_grams_per_filament'].items():
                t[k] = round(t.get(k, 0) + v['grams'], 1)
            time_ += p['est_time_min']
            swaps += p['colour_swaps'] or 0
        return dict(grams_per_filament=t,
                    grams_PETG=round(sum(v for k, v in t.items() if k.startswith('PETG')), 1),
                    grams_TPU=round(sum(v for k, v in t.items() if k.startswith('TPU')), 1),
                    time_min=round(time_, 1), time_hm=f'{int(time_ // 60)} h {int(time_ % 60):02d} min', colour_swaps=swaps, plates=n)

    flush = {}
    for a, ha in colours_hex.items():
        for c, hc in colours_hex.items():
            if a != c:
                v = w3.flush_volume(ha, hc)
                flush[f'{a}->{c}'] = dict(mm3=v, grams=round(v / 1000 * pv.DENSITY['PETG'], 2))
    where = {}
    for plate in pl.ALL_PLATES:
        for pid, q in plate['parts']:
            where.setdefault(pid, []).append(plate['key'])
    checklist = []
    for p in pv.PARTS:
        checklist.append(dict(id=p['id'], label=p['label'], kind=p['kind'], product=p['product'],
                              material=p['material'] + (' 95A' if p['material'] == 'TPU' else ''),
                              qty=p['qty'], colours=[c for c, _ in p['bodies']], plates=where.get(p['id'], []),
                              stl=[f'stl/{f}' for f in next(r['files'] for r in files['stl'] if r['id'] == p['id'])],
                              source=p['source'], kit_module=p.get('module')))
    totals = tot(lambda p: True)
    totals['note'] = ('slicer estimates (OrcaSlicer 2.5.0 with the Bambu A1 system profiles); include supports, prime tower and flush; '
                      'test plates included; MOD-TPU-1 (duplicate of the gasket on TPU-2) not counted')
    warn_all = [(k, p_['id'], p_['warning']) for k, r in validation.items() for p_ in r['plates'] if p_['warning']]
    by_key = {p['key']: p for p in plates_out}
    review = dict(
        M1_scatola_v64_posts=dict(sliced_without_supports=True, plate='PETG-7', slicer_warning=by_key['PETG-7']['slicer_warning'],
                                  support_grams=sum(v['support'] for v in by_key['PETG-7']['est_grams_per_filament'].values())),
        M3_fondello_v64_bottom_edge=dict(sliced_without_supports=True, plate='PETG-7', slicer_warning=by_key['PETG-7']['slicer_warning']),
        M3_modulo_vasca_v64_bottom_edge=dict(
            bottom_edge_and_bosses_need_support=False, plate='MOD-1', slicer_warning=by_key['MOD-1']['slicer_warning'],
            note='bottom edge and the 5 lid-screw bosses need no support; with support off '
                 'the slicer flags the two upper corners of the button recess (print z 21.5): 2 enforcers there, see extra_checks',
            support_grams=sum(v['support'] for v in by_key['MOD-1']['est_grams_per_filament'].values())),
        M2_guscio_v64_tabs=dict(supports='tree(manual), build plate only, 45 deg, 3 support enforcers under the inner part of the tabs',
                                plate='PETG-1', slicer_warning=by_key['PETG-1']['slicer_warning'],
                                support_grams=sum(v['support'] for v in by_key['PETG-1']['est_grams_per_filament'].values())),
        m7_lid_skin=dict(plate='MOD-2', slicer_warning=by_key['MOD-2']['slicer_warning'],
                         note='0.2 mm skin at print z 12.2..12.4 = exactly one 0.2 mm layer; no supports'),
        all_slicer_warnings=[dict(project=k, plate=i, warning=w) for k, i, w in warn_all])
    extra_path = os.path.join(OUT, 'tools', 'review_checks_extra.json')
    if os.path.exists(extra_path):
        review['extra_checks'] = json.load(open(extra_path))
    summary = dict(
        project='Kibble Dispenser Outdoor hardware 6.4.0 (chassis 6.4 + electronics module case 1.0)',
        generated=datetime.date.today().isoformat(),
        printer=dict(model='Bambu Lab A1', bed_mm=[256, 256, 256], plate='Textured PEI', nozzle_mm=0.4, ams='AMS lite (4 slots)',
                     machine_profile=b.MACHINE, process_profile=b.PROCESS),
        filament_slots={'AMS lite slot 1': 'PETG black (structure) - Generic PETG @BBL A1, #1A1A1A',
                        'AMS lite slot 2': 'PETG orange (touch points) - Generic PETG @BBL A1, #F07A1A',
                        'AMS lite slot 3': 'PETG green (food path) - Generic PETG @BBL A1, #2E9D4F',
                        'AMS lite slot 4': 'spare PETG black (auto-refill backup for slot 1)',
                        'external spool': 'TPU 95A yellow (seals) - Generic TPU @BBL A1, #F2C81E; TPU cannot go through the AMS lite'},
        products=dict(
            chassis=dict(name='chassis 6.4 (mechanics + electronics-case holder)',
                         bambu_projects=[pr['file'] for pr in pl.PROJECTS if pr['product'] == 'chassis'],
                         plates=[p['key'] for p in plates_out if p['product'] == 'chassis'],
                         totals=tot(lambda p: p['product'] == 'chassis' and p['key'] != 'TPU-2'),
                         note='TPU-2 (cap lip seal + module gasket, shared plate) is counted separately in shared_plate_TPU_2'),
            module=dict(name='electronics module, case 1.0 (tub, lid, speaker ring, lid gasket)',
                        bambu_projects=[pr['file'] for pr in pl.PROJECTS if pr['product'] == 'module'],
                        plates=[p['key'] for p in plates_out if p['product'] == 'module'],
                        totals=tot(lambda p: p['product'] == 'module'),
                        totals_reprint_alone=dict(plates=['MOD-1', 'MOD-2', 'MOD-TPU-1'],
                                                  time_min=round(sum(by_key[k]['est_time_min'] or 0 for k in ('MOD-1', 'MOD-2', 'MOD-TPU-1')), 1),
                                                  grams=round(sum(by_key[k]['est_grams_total'] or 0 for k in ('MOD-1', 'MOD-2', 'MOD-TPU-1')), 1)),
                        note='the module gasket is printed once: on chassis plate TPU-2 now, or on MOD-TPU-1 when the module is reprinted alone'),
            shared_plate_TPU_2=tot(lambda p: p['key'] == 'TPU-2')),
        files=dict(bambu_projects=[pr['file'] for pr in pl.PROJECTS],
                   plain_3mf_per_plate='plates/', stl_print_orientation='stl/', previews='preview/', layout='layout.json',
                   slicer_statistics='slice_check/', guide='PRINT_GUIDE.md',
                   generator='tools/build_print_v64.py, tools/make_summary.py, tools/make_guide.py, tools/run_all.sh'),
        validation=dict(slicer=slicer, method='OrcaSlicer 2.5.0 Linux CLI (AppImage) opened each Bambu project 3MF and sliced all plates '
                                               'with the settings embedded in the project (--slice 0 --export-statistics); no Bambu Studio '
                                               'binary was available here, so the files were not opened in Bambu Studio itself',
                        results=validation, bambu_profiles=b.PROFILE_SOURCE, application_tag=f'BambuStudio-{b.APP_VERSION}',
                        ip66_filament_overrides=dict(projects=[pr['file'] for pr in pl.PROJECTS if pr['filaments'] == 'black_ip66'],
                                                     values=b.IP66_FILAMENT_OVERRIDES,
                                                     note='Generic PETG @BBL A1 with the part fan limited to 40 % (nozzle stays at the profile 255 C)')),
        review_checks=review,
        plates=plates_out,
        totals=totals,
        purge_per_swap_A1=dict(model='Bambu Studio colour flush model (FlushVolCalc) + A1 nozzle volume 92 mm3, multiplier 1.0; '
                                     'these values are written into flush_volumes_matrix of the chassis PETG project', volumes=flush),
        parts_checklist=checklist,
        bought_parts=bought_parts(),
        cross_check=cross_check())
    json.dump(summary, open(os.path.join(OUT, 'summary.json'), 'w'), indent=1)
    print('summary.json written; totals', {k: v for k, v in totals.items() if k != 'note'})
    for k, i, w in warn_all:
        print('WARNING', k, i, w)
    return summary


if __name__ == '__main__':
    main(sys.argv[1])
