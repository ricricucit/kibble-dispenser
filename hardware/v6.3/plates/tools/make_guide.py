"""Write hardware/v6.3/plates/README.md (the print guide) from summary.json (numbers stay in sync with the slicer run)."""
import json
import os

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # hardware/v6.3/plates
S = json.load(open(os.path.join(OUT, 'summary.json')))
P = {p['key']: p for p in S['plates']}
V6 = None
_v6 = os.path.join(OUT, '..', '..', 'v6.2', 'plates', 'summary.json')   # the committed v6.2 package
if os.path.exists(_v6):
    V6 = json.load(open(_v6))


def g(v):
    return f'{v:.0f} g' if v >= 10 else f'{v:.1f} g'


lines = []
A = lines.append
T = S['totals']

A('# Kibble Dispenser Outdoor v6.3 - print guide (Bambu Lab A1 + AMS lite)')
A('')
A('Everything you need to print the v6.3 dispenser on a Bambu Lab A1 with the AMS lite: two ready Bambu Studio projects, '
  'plain 3MF files for any slicer, single STL files in print orientation, the recommended settings and a check list of every printed part.')
A('')
A('**Design v6.3 (hardware 6.3.0): designed and checked in CAD, not printed or tested yet.** Print the test pieces first. '
  'The firmware for the one-button control panel is still to come (issue #2). Website version, in English, Italian and German: '
  '<https://ricricucit.github.io/kibble-dispenser/print/>')
A('')
A('Kit note (v63.json kit_split): the kit ships the dispenser unit pre-assembled (bowl, drive tower, chute, electronics box, shell, cap '
  'with the control panel, plates, disc) plus a separate flange assembly. DIY builders print every part, so this package includes '
  'them all. The parts marked "kit module" are the factory modules inside the unit (drive tower, electronics box).')
A('')
A('## Files')
A('')
A('- `Kibble_Dispenser_v63_PETG.bambu.3mf`: Bambu Studio project with all PETG plates (1 test plate and 6 part plates). The parts '
  'are placed and oriented. Multicolour parts are single objects with their colour parts assigned to AMS slots. Per-part settings '
  '(walls, infill, supports, brim, layer height, IP66 settings for the box and the cap) are stored on each object, and '
  'the A1 printer, process and filament presets are set.')
A('- `Kibble_Dispenser_v63_TPU.bambu.3mf`: Bambu Studio project with the TPU plates (1 test plate and all seals), for the external spool.')
A('- `plates/*.3mf`: one plain 3MF per plate (same layout) for OrcaSlicer, PrusaSlicer and others. Colour parts are named '
  '`<part>_<colour>` and carry a display colour. Assign the filaments and the per-part settings below yourself: a plain 3MF '
  'carries no settings or modifiers.')
A('- `stl/*_print.stl`: every printed part on its own, in print orientation. Multicolour parts also come as colour bodies '
  '(`*_print_black.stl`, `*_print_orange.stl`, `*_print_green.stl`) in the same frame: load them together as one object with parts.')
A('- `preview/<plate>_top.png` and `<plate>_iso.png`: plate previews. `summary.json`: all numbers as data. `slice_check/`: slicer '
  'statistics. `layout.json`: part positions.')
A('- `tools/`: the generator scripts. `tools/run_all.sh` rebuilds everything, slices both projects with the OrcaSlicer command line, '
  'and writes summary.json and this guide again.')
A('')
A('## Printer, plate and filament slots')
A('')
A('- Printer: Bambu Lab A1, 0.4 mm nozzle, Textured PEI plate. Bed 256 x 256 x 256 mm. Parts keep at least 5 mm from each '
  'other and stay clear of the A1 calibration line (front edge, X 108 to 160).')
A('- Colour language: black is structure, orange is a touch point ("act here"), green is the food path, and yellow TPU is a seal '
  'or a soft part. Inlays are 0.6 mm (3 layers of 0.2 mm) in the first or the last layers of a part.')
A('- AMS lite:')
A('  - slot 1: PETG black')
A('  - slot 2: PETG orange')
A('  - slot 3: PETG green')
A('  - slot 4: optional second spool of PETG black as an automatic backup (enable "Filament backup/auto refill"). Black is about '
  f"{T['grams_per_filament'].get('PETG black', 0) / max(T['grams_PETG'], 1) * 100:.0f} % of all PETG. Without a second spool, leave slot 4 empty.")
A('- External spool holder: TPU 95A yellow. TPU cannot go through the AMS lite. In the print dialog, map the filament to "External spool".')
A('- Profiles: "Generic PETG @BBL A1" and "Generic TPU @BBL A1". If you use a branded filament, pick its own profile.')
A('')
A('## Plates')
A('')
A('Print the test plates first, then plates 01 to 06, then the TPU plate. Times and grams are slicer estimates that include '
  'supports, the prime tower and filament flushing.')
A('')
for key in [p['key'] for p in S['plates']]:
    p = P[key]
    A(f"### {key}: {p['name']}")
    A('')
    A(f"Project `{p['bambu_project']}`, plate {p['plate_in_project']}. Plain file `{p['plain_3mf']}`. "
      f"Preview `{p['preview_top']}` and `{p['preview_iso']}`.")
    A('')
    A(f"- Purpose: {p['purpose']}.")
    A('- Parts:')
    for pp in p['parts']:
        A(f"  - {pp['id']} x{pp['qty']} ({pp['label']}; {pp['material']} {' + '.join(pp['colours'])})")
    A(f"- Filament: {'; '.join(p['filament_slots'])}.")

    def extra(v):
        parts_ = [f"{lab} {v[k]} g" for k, lab in (('support', 'support'), ('prime_tower', 'prime tower'), ('flush', 'flush')) if v[k] > 0.05]
        return f" (of which {', '.join(parts_)})" if parts_ else ''
    fil = '; '.join(f"{k} {g(v['grams'])}{extra(v)}" for k, v in p['est_grams_per_filament'].items())
    A(f"- Estimate: {p['est_time_hm']}, {fil}; colour swaps: {p['colour_swaps']}.")
    if p['prime_tower_xy_mm']:
        A(f"- Prime tower at X {p['prime_tower_xy_mm'][0]:.0f}, Y {p['prime_tower_xy_mm'][1]:.0f} (stored in the project).")
    A('')

A('### Totals')
A('')
for k, v in T['grams_per_filament'].items():
    A(f'- {k}: {g(v)}')
A(f"- All PETG: {g(T['grams_PETG'])}. All TPU 95A: {g(T['grams_TPU'])}.")
A(f"- Print time: {T['time_hm']} over {T['plates']} plates (test plates included). Colour swaps: {T['colour_swaps']} in total.")
A('')
A('### Why the plates are grouped like this')
A('')
A('- A part has one body colour through its whole height, so the plates follow the body colour: black (01, 02, 03), green (04) '
  'and orange (05). The multicolour parts add swaps only in their 3 inlay layers.')
A('- Black needs four plates: the shell (164 mm), the cap (143), both flange plates (180) and the box do not pair up. '
  'The pairs that fit are shell + box and bowl + cap (diagonal, 6 mm apart, relaxed 4 mm bed margins), and lower flange + '
  'tower/shaft/hub. The upper flange plate prints alone.')
A('- Plate 03 has a single colour and no prime tower, so the shaft (albero_v6) can use its own 0.15 mm layers there.')
A('- Plate 05: the gate blade is green only in v6.3. Its 15 layers coincide with the black/green layers of the gate and window '
  'plates, so it adds no swaps there.')
A('- Plate 06: the disc prints inside the 176 mm interlock ring; only the disc label adds swaps (first 3 layers).')
A('- Purge per swap on the A1 (Bambu colour model, 92 mm3 nozzle volume, stored in the project):')
for k, v in S['purge_per_swap_A1']['volumes'].items():
    A(f"  - {k}: {v['mm3']} mm3 ({v['grams']} g)")
A('')
A('## Recommended settings')
A('')
A('These settings are already in the Bambu projects, as process presets and per-object settings. Use them in other slicers too.')
A('')
A('### PETG')
A('')
A('- Profile Generic PETG @BBL A1: nozzle 255 C, bed 80 C on Textured PEI (70 C on Engineering Plate). On smooth PEI, use glue stick as a release agent.')
A('- Fan 40 to 90 % (off for the first 3 layers). Max volumetric speed 8 mm3/s (generic). Dry open spools at 65 C for 6 to 8 h.')
A('- Layer height 0.20 mm and first layer 0.20 mm (0.20mm Standard @BBL A1); keep 0.20 mm where there are inlays. Only albero_v6 uses 0.15 mm. Seam aligned. Prime tower on for the multicolour plates.')
A('- Support filament stays on "Default", so a few supports may print in the filament that is already loaded. This saves swaps.')
A('- Per part:')
A('  - guscio_v611 (shell): 5 walls, 15 % infill, 6 mm outer brim, no supports.')
A('  - fondello_v63 (cap) and scatola_v63 (box): IP66 settings, see below.')
A('  - chiocciola_v63 (bowl): 3 walls, 15 %. Supports: tree, on build plate only (3 bayonet lugs). The chute-ear and shell-tab holes are d2.5 '
  'pilots for the PT screws: do not drill them out.')
A('  - flangia_piano_v63 (lower flange plate): shelf-side face on the bed, 3 walls, 25 %, no supports. Press the 4 x 6 dowel in after printing.')
A('  - flangia_alta_v63 (upper flange plate): shelf face on the bed, 3 walls, 25 %, no supports. The 3 press-fit pins grow up '
  '(they are printed, not bought).')
A('  - anello_saracinesca_v63 (interlock ring, orange): on its bottom edge, 4 walls, 15 %, 5 mm outer brim, no support (teardrop window).')
A('  - saracinesca_v63 (gate blade, green): flat, 3 walls, 100 % infill.')
A('  - colonna_v63 (tower): upright, 4 walls, 100 % infill (pillars under the M3x40 preload).')
A('  - scivolo_v611 (chute): 5 walls, 15 %, no supports. disco_v61, piastra_gate_v62, piastra_finestra_v62, colletto_v6: 3 walls, 15 %, no supports.')
A('  - albero_v6 (shaft): 100 %, 0.15 mm layers, 5 mm brim. mozzo_v6, pulsante_v611, linguetta_sicura_v63: 100 % infill, 4 walls '
  '(the latch lies on its back with a small bed-only support under the spring tab).')
A('')
A('### IP66 settings: box and cap (as v6.1.1; v63.json print notes)')
A('')
A('- 5 walls at 0.42 mm line width (at least 4 walls fill a 2.0 mm wall solid), 100 % infill, 5 top and 5 bottom layers, seam at the back.')
A('- Object flow ratio 1.03 (+3 %, inside the +2 to 5 % range), stored as print_flow_ratio on the two objects.')
A('- Box: top surfaces ironed (the rim face prints as a top surface and carries the cap lip).')
A('- Box: no support at all in v6.3 (the C boss overhangs its column by 2.5 mm). Top surfaces ironed (rim face).')
A('- Cap: the control-panel knock-out skins (2.0 mm) print solid inside the 5 walls, the 0.3 mm engravings face sideways, and '
  'the dry-pocket roof bridges at most 18 mm between the bosses. None of these needs support.')
A('- Cap: a bed-only support ring (normal supports, threshold 45 deg) under the lowest ~5 mm of the R15 bottom edge, as in v6.1.')
A('- Filament settings for these two plates (set them by hand in the filament profile): nozzle 245 to 250 C, part fan 40 % or less, for layer bonding.')
A('- After printing:')
A('  - clear the drain holes (d 0.8 mm, two labyrinth drains in v6.3) in the cap with a 0.8 mm drill; first-layer squish can close them;')
A('  - hold the empty box against a bright light in a dark room: pinholes glow;')
A('  - the gland pad is a vertical face and cannot be ironed: check it is flat where the gland O-ring seats.')
A('')
A('### TPU 95A')
A('')
A('- Profile Generic TPU @BBL A1: nozzle 240 C, bed 45 C on Textured PEI, fan 100 %, max volumetric speed 3.2 mm3/s, retraction 0.4 mm. Dry the TPU (65 C, 6 h) right before printing.')
A('- All TPU parts use 100 % infill and 2 walls, 0.20 mm layers.')
A('- Thin flaps use the Arachne wall generator at 15 mm/s so that each flap prints as one clean line: guarnizione_baionetta_v61 (0.5 mm), '
  'labbro_ombra_v611 (skirt, 0.5 mm, 20 deg cone), labbro_scivolo_v611 (chute, 0.6 mm) and the 4 comb lips (0.8 mm, 0.7 mm slits). '
  'guarnizione_fondello_v61 prints its walls at 20 mm/s.')
A('')
A('## Print these test pieces first')
A('')
A('1. PETG-0 (black): `test_scanalato`, `test_groove_rim`, `test_groove_cap` and `test_groove_skirt`.')
A('   - test_scanalato: 3 spline coupons (1, 2 or 3 notches for 0.05, 0.10 or 0.20 mm). mozzo_v6 is built with 0.10 mm. If another coupon '
  'fits better, change SPL_CLEAR in parts/build_drivetrain.py, rebuild mozzo_v6 and run tools/run_all.sh.')
A('   - The groove coupons are cuts of the bowl rim (chiocciola_v63), the cap D upstand (fondello_v63) and the lower flange edge '
  '(flangia_piano_v63, skirt-lip groove).')
A('2. TPU-0 (external spool): `test_rim_lip`, `test_cap_lip`, `test_skirt_lip` and `test_comb_lip` (a spare labbro_pettine_v62).')
A('   - Press each strip into its groove coupon. The anchor should seat fully, and the flap should be one clean, closed line that springs back.')
A('   - On the comb lip, the slits must be open.')
A('3. After printing:')
A('   - check the seam O-ring 132x2 squeeze (light drag over the last 2 mm) and look at the cap spigot ring (see Deviations);')
A('   - drive the PT K30 screws by hand (about 0.6 N m), at most about 5 times per hole;')
A('   - tighten the M3x40 stack screws to 0.4 N m and re-check after a week.')
A('4. Hose-test the closed pod before you put electronics inside.')
A('')
A('## Bought parts (not printed)')
A('')
A('Not on any plate. Changes in v6.3:')
A('- New: the panel parts: an IP67 12 mm short-body push-button, 2 light pipes with LEDs, an IP67 acoustic membrane, a d20 speaker and a JST harness.')
A('- New: 3 PT K30x12 cap screws (T10) with O-rings 3x1 instead of the thumb-turns, keys and their O-rings.')
A('- New: PT K30 screws straight into pilots for the chute and the shell tabs, instead of 5 heat-set inserts.')
A('- New: a UV cable tie for strain relief. The 4 x 6 dowel is now part of the design.')
A('- Gone: the 3 flange join screws (now 3 press-fit pins printed on the upper plate) and the 4 cable-channel screws.')
A('')
for h in S['bought_parts']:
    A(f"- {h['qty']} x {h['item']}: {h['use']} ({h['source']})")
A('')
A('## Check list: all printed parts')
A('')
cc = S['cross_check']['count_print_v63']
A(f"v6.3 has {cc['PETG_parts']} PETG parts ({cc['PETG_pieces']} pieces) and {cc['TPU_pieces']} TPU pieces, plus {cc['test_pieces']} test pieces.")
A('')
for c in S['parts_checklist']:
    mod = f" - kit module: {c['kit_module']}" if c.get('kit_module') else ''
    A(f"- [ ] {c['id']} x{c['qty']}: {c['label']}; {c['material']} {' + '.join(c['colours'])}; plate {', '.join(c['plates'])}; "
      f"`{c['stl'][0]}`{mod}")
A('')
A('## Changes from the v6.2 package')
A('')
if V6:
    t6 = V6['totals']
    A(f"- Totals: PETG {g(t6['grams_PETG'])} -> {g(T['grams_PETG'])}, TPU {g(t6['grams_TPU'])} -> {g(T['grams_TPU'])}, time "
      f"{t6['time_hm']} -> {T['time_hm']}, plates {t6['plates']} -> {T['plates']}, colour swaps {t6['colour_swaps']} -> {T['colour_swaps']}.")
A('- Removed: the cable channel (2 bases, 2 covers, 1 end cap) and the 3 thumb-turns.')
A('- Gate blade: now green only, and it moved to the green plate.')
A('- Changed parts: the bowl (PT pilots, P3 insert moved), the tower (P3 pillar moved), the box (PT bosses instead of cups), the cap '
  '(PT counterbores, control panel, second drain), both flange plates (dowel hole, press-fit pins, tie window, raised tunnel), the ring '
  '(teardrop window), the grommet and the latch (print orientation).')
A('- Print orientations: the v6.3 CAD print files now carry the corrections made in print_v62 (no pin and a dowel hole on the lower plate, '
  'the latch on its back, the grommet lip down). They were verified here and used as they are. No support enforcers are needed any more: '
  'the box needs no support, and the ring window is a teardrop.')
A('')
A('## Deviations and notes')
A('')
A('- **6.3.0 CAD fixes, checked here**:')
A('  - Lower flange dowel seat: closed all round (wall at 100 % around the d4 hole), so it is a normal press fit now.')
A('  - Cap seam ring: joined to the cap, with a 45 deg chamfer underneath. The old 2.5 mm flat ledge is gone; about 84 mm2 of small flat '
  'bits remain. The slicer reports no warning.')
A('  - LED light pipe seats: squared to the panel face.')
A('  - The raw cap STL has 4 zero-area slivers. The package\'s mesh clean removes them, so the cap is one watertight solid in all files.')
A('- **linguetta_sicura_v63** now comes on its back from the CAD (geometry unchanged).')
A('- **Plain 3MF files** carry no settings. Use the Bambu projects, or apply the settings above by hand.')
A('- The Bambu projects are generated by a script in the Bambu Studio project format (metadata `BambuStudio-02.05.00.00`). The settings '
  f"come from the Bambu system profiles ({S['validation']['bambu_profiles']}). Every plate was opened and sliced with the OrcaSlicer 2.5.0 "
  'command line, but not in Bambu Studio itself. After opening in Bambu Studio, check the plate list and the filament mapping, and slice once.')
A('- Times and grams come from the OrcaSlicer estimator with the A1 profiles. Bambu Studio may differ by 5 to 10 %.')
warn = [(k, pl['id'], pl['warning']) for k, r in S['validation']['results'].items() for pl in r['plates'] if pl['warning']]
for k, i, w in warn:
    A(f'- Slicer warning ({k}, plate {i}): {w}')
A('')
open(os.path.join(OUT, 'README.md'), 'w').write('\n'.join(lines) + '\n')
print('README.md written,', len(lines), 'lines')
