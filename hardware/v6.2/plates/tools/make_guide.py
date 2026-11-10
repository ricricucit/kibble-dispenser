"""Write hardware/v6.2/plates/README.md (the print guide) from summary.json (numbers stay in sync with the slicer run)."""
import json
import os

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # hardware/v6.2/plates
S = json.load(open(os.path.join(OUT, 'summary.json')))
P = {p['key']: p for p in S['plates']}
# totals of the v6.1.1 print package (OrcaSlicer 2.5.0, 2026-11-09), for the "Changes" section; v6.1.1 was not published
V6 = {'totals': {'grams_PETG': 813.7, 'grams_TPU': 9.2, 'time_hm': '33 h 42 min', 'plates': 8, 'colour_swaps': 18}}


def g(v):
    return f'{v:.0f} g' if v >= 10 else f'{v:.1f} g'


lines = []
A = lines.append
T = S['totals']

A('# Kibble Dispenser Outdoor v6.2 - print guide (Bambu Lab A1 + AMS lite)')
A('')
A('Everything you need to print the v6.2 dispenser on a Bambu Lab A1 with the AMS lite: two ready Bambu Studio projects, '
  'plain 3MF files for any slicer, single STL files in print orientation, the recommended settings and a check list of every printed part.')
A('')
A('**Design v6.2: designed and checked in CAD, not printed or tested yet.** These files are the authoritative print set of '
  'v6.2: they correct several CAD print orientations and replace the printed pivot pin of the lower flange with a 4 x 6 '
  'stainless dowel (see Deviations). Print the test pieces first. Website version, in English, Italian and German: '
  '<https://ricricucit.github.io/kibble-dispenser/print/>')
A('')
A('Kit note (v62.json kit_split): the kit ships the dispenser unit pre-assembled (bowl, drive tower, chute, electronics box, shell, cap, '
  'plates, disc) plus a separate flange assembly and the cable channel. DIY builders print every part, so this package includes '
  'them all. The parts marked "kit module" are the factory modules inside the unit (drive tower, electronics box).')
A('')
A('## Files')
A('')
A('- `Kibble_Dispenser_v62_PETG.bambu.3mf`: Bambu Studio project with all PETG plates (1 test plate and 6 part plates). The parts '
  'are placed and oriented. Multicolour parts are single objects with their colour parts assigned to AMS slots. Per-part settings '
  '(walls, infill, supports, brim, layer height, IP66 settings for the box and the cap, support enforcers under the box C cup and the ring window) are stored on each object, and '
  'the A1 printer, process and filament presets are set.')
A('- `Kibble_Dispenser_v62_TPU.bambu.3mf`: Bambu Studio project with the TPU plates (1 test plate and all seals), for the external spool.')
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
A('- Black needs four plates: the shell (164 mm), the cap (143), both flange plates (180) and the box (81 x 96) do not pair up. '
  'Pairs that fit are shell + box and bowl + cap (both diagonal, about 6 mm apart, with relaxed 4 mm bed margins), lower flange + '
  'cable channel, and upper flange + tower/shaft/hub.')
A('- Plate 04 has a single colour and no prime tower, so the shaft (albero_v6) can use its own 0.15 mm layers there.')
A('- Plate 05 puts the two 3 mm plates (black with green bands) on the green plate.')
A('- Plate 06: the disc prints inside the 176 mm interlock ring. The gate blade (saracinesca_v62) is green with an orange arm '
  'through all 15 layers: two colours on every layer wherever it goes, so it sits with the other orange parts.')
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
A('  - fondello_v62 (cap) and scatola_v62 (box): IP66 settings, see below.')
A('  - chiocciola_v62 (bowl): 3 walls, 15 %. Supports: tree, on build plate only (3 bayonet lugs).')
A('  - flangia_piano_v62 (lower flange plate): 3 walls, 25 %, shelf-side face on the bed, no supports. The pivot pin is printed as '
  'a 4.0 mm hole for a steel dowel (see Deviations).')
A('  - flangia_alta_v62 (upper flange plate): 3 walls, 25 %, shelf face on the bed, no supports. The 1.5 mm cable groove bridges about 7 mm.')
A('  - anello_saracinesca_v62 (interlock ring, orange): on its bottom edge, 4 walls, 15 %, 5 mm outer brim. The d28 window top is a '
  '28 mm bridge, so a small support stands on the window sill (support enforcer, manual normal support).')
A('  - saracinesca_v62 (gate blade): flat, 3 walls, 100 % infill (3 mm blade).')
A('  - colonna_v62 (tower): upright, 4 walls, 100 % infill: the three pillars carry the M3x40 preload.')
A('  - canalina_base_v62 x2 (wood face on the bed), canalina_coperchio_v62 x2 (open side up), canalina_tappo_v62 (on its side): 3 walls, 15 %.')
A('  - scivolo_v611 (chute): 5 walls, 15 %, no supports. disco_v61, piastra_gate_v62, piastra_finestra_v62, colletto_v6: 3 walls, 15 %, no supports.')
A('  - albero_v6 (shaft): 100 %, 0.15 mm layers, 5 mm brim. mozzo_v6, pulsante_v611, nottolino_v611 x3, linguetta_sicura: 100 % infill, '
  '4 walls (linguetta lies on its back with a small bed-only support under the spring tab).')
A('')
A('### IP66 settings: box and cap (as v6.1.1, v611.json ip_rating)')
A('')
A('- 5 walls at 0.42 mm line width (at least 4 walls fill a 2.0 mm wall solid), 100 % infill, 5 top and 5 bottom layers, seam at the back.')
A('- Object flow ratio 1.03 (+3 %, inside the +2 to 5 % range), stored as print_flow_ratio on the two objects.')
A('- Box: top surfaces ironed (the rim face prints as a top surface and carries the cap lip).')
A('- Box support: manual mode with one support enforcer, so support is generated only under the far half of the C cup ring (x > 21). '
  'It is normal (straight) support standing on the inside of the roof; in v6.1.1 tree support sent a trunk through the M12 vent hole down to the bed. '
  'The stack-screw ear prints on the bed, and the two roof countersinks (for the O-rings 3x1) face up.')
A('- Cap: a bed-only support ring (normal supports, threshold 45 deg) under the lowest ~5 mm of the R15 bottom edge, as in v6.1.')
A('- Filament settings for these two plates (set them by hand in the filament profile): nozzle 245 to 250 C, part fan 40 % or less, for layer bonding.')
A('- After printing:')
A('  - clear the 4 drain holes (d 0.8 mm) in the cap with a 0.8 mm drill; first-layer squish can close them;')
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
A('   - The groove coupons are cuts of the bowl rim (chiocciola_v62), the cap D upstand (fondello_v62) and the lower flange edge '
  '(flangia_piano_v62, skirt-lip groove).')
A('2. TPU-0 (external spool): `test_rim_lip`, `test_cap_lip`, `test_skirt_lip` and `test_comb_lip` (a spare labbro_pettine_v62).')
A('   - Press each strip into its groove coupon. The anchor should seat fully, and the flap should be one clean, closed line that springs back.')
A('   - On the comb lip, the slits must be open.')
A('3. After printing:')
A('   - check the seam O-ring 132x2 squeeze (light drag over the last 2 mm);')
A('   - check the P3 stack-screw head clearance to the cradle and the board (0.375 mm, open risk in v62.json);')
A('   - tighten the M3x40 to 0.4 N m and re-check after a week (PETG creep).')
A('4. Hose-test the closed pod before you put electronics inside.')
A('')
A('## Bought parts (not printed)')
A('')
A('Not on any plate. New in v6.2: 3 x M3x40 stack screws (they replace 3 x M3x12 and 3 x M3x10), 2 x O-ring 3x1 under the P2/P3 heads, '
  'the M8 IP67 connector pair with a 5 mm PUR cable, 3 x ST2.9x9.5 flange join screws, 4 x wood screw 3.5x16 for the cable channel, '
  'wood screws 5x35 instead of 5x25, and 12 heat-set inserts instead of 15. This package adds one 4 x 6 stainless dowel pin (see Deviations).')
A('')
for h in S['bought_parts']:
    A(f"- {h['qty']} x {h['item']}: {h['use']} ({h['source']})")
A('')
A('## Check list: all printed parts')
A('')
cc = S['cross_check']['count_print_v62']
A(f"v6.2 has {cc['PETG_parts']} PETG parts ({cc['PETG_pieces']} pieces) and {cc['TPU_pieces']} TPU pieces, plus {cc['test_pieces']} test pieces.")
A('')
for c in S['parts_checklist']:
    mod = f" - kit module: {c['kit_module']}" if c.get('kit_module') else ''
    A(f"- [ ] {c['id']} x{c['qty']}: {c['label']}; {c['material']} {' + '.join(c['colours'])}; plate {', '.join(c['plates'])}; "
      f"`{c['stl'][0]}`{mod}")
A('')
A('## Changes from the v6.1.1 package')
A('')
if V6:
    t6 = V6['totals']
    A(f"- Totals: PETG {g(t6['grams_PETG'])} -> {g(T['grams_PETG'])}, TPU {g(t6['grams_TPU'])} -> {g(T['grams_TPU'])}, time "
      f"{t6['time_hm']} -> {T['time_hm']}, plates {t6['plates']} -> {T['plates']}, colour swaps {t6['colour_swaps']} -> {T['colour_swaps']}.")
A('- New parts:')
A('  - upper flange plate (flangia_alta_v62);')
A('  - green gate blade with an orange arm (saracinesca_v62) and orange interlock ring (anello_saracinesca_v62);')
A('  - cable channel: 2 bases, 2 covers and an end cap, black;')
A('  - cable tunnel grommet (passacavo_v62, TPU);')
A('  - one common comb lip printed 4 times (labbro_pettine_v62), replacing the 4 different v6.1 lips.')
A('- Changed: the bowl (insert positions), the tower (3 pillars for the M3x40 stack), the box (stack-screw ear and countersinks, vent moved), '
  'the cap (dishes d24), the lower flange plate, and the gate and window plates (common lip grooves).')
A('- Plates: one more black plate (the second flange plate). The orange plate carries the d176 ring with the disc inside it and the gate blade.')
A('')
A('## Deviations and notes')
A('')
A('- **flangia_piano_v62 pivot pin (designer to confirm)**: the CAD print file lays the plate shelf-side face down, but the d4 x 3.3 mm '
  'blade pivot pin stands on that face, so the whole plate would float 3.3 mm above the bed on the pin (22 400 mm2 of overhang). Printed '
  'the other way up, the skirt and the skirt-lip groove would need support instead. This package cuts the pin off and prints a '
  'd4.0 x 2.7 mm blind hole at the centre for a pressed-in ISO 2338 4 m6 x 6 stainless dowel. That leaves the same 3.3 mm stand-up, '
  'and the dowel is listed in the bought parts. The unmodified CAD file is in `stl/flangia_piano_v62_print_cad_original.stl`.')
A('- **CAD print orientations corrected** to match the v62.json print notes, with less overhang in each case:')
A('  - canalina_base_v62 flipped, wood face on the bed;')
A('  - canalina_coperchio_v62 open side up;')
A('  - canalina_tappo_v62 on its other side (1.9 instead of 115 mm2 of overhang);')
A('  - passacavo_v62 lip on the bed.')
A('- **Interlock ring window**: the 28 mm window bridge gets a small support from the window sill, through a support enforcer in manual mode. '
  'A chamfer on the window top in the CAD would remove the need for it.')
A('- **Box support**: as in v6.1.1, support only under the far half of the C cup, normal instead of tree.')
A('- **linguetta_sicura** lies on its back, as its print note says (the reused print STL is upright).')
A('- **Plain 3MF files** carry no settings, modifiers or enforcers. Use the Bambu projects, or apply the settings above by hand.')
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
