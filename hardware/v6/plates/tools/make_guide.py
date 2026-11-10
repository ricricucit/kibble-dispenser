"""Write hardware/v6/plates/README.md (the print guide) from summary.json (numbers stay in sync with the slicer run)."""
import json
import os

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # hardware/v6/plates
S = json.load(open(os.path.join(OUT, 'summary.json')))
P = {p['key']: p for p in S['plates']}


def g(v):
    return f'{v:.0f} g' if v >= 10 else f'{v:.1f} g'


lines = []
A = lines.append

A('# Kibble Dispenser Outdoor v6 - print guide (Bambu Lab A1 + AMS lite)')
A('')
A('**Archived: print package of design v6 (hardware 6.0.0).** Design v6.2 replaced it: print '
  '[`../../v6.2/plates/`](../../v6.2/plates/README.md) instead. Archived website version, in English, Italian and German: '
  '<https://ricricucit.github.io/kibble-dispenser/v6/print/>')
A('')
A('Everything you need to print the v6 dispenser on a Bambu Lab A1 with the AMS lite: two ready Bambu Studio '
  'projects, plain 3MF files for any slicer, single STL files in print orientation, the recommended settings '
  'and a check list of every printed part.')
A('')
A('## Files')
A('')
A('- `Kibble_Dispenser_v6_PETG.bambu.3mf`: Bambu Studio project with all PETG plates (1 test plate and 4 part plates). Parts are '
  'placed and oriented, multicolour parts are single objects with their colour parts assigned to AMS slots, the per-part settings '
  '(walls, infill, supports, brim, layer height) are stored on each object, and the A1 printer, process and filament presets '
  'are preset.')
A('- `Kibble_Dispenser_v6_TPU.bambu.3mf`: Bambu Studio project with the TPU plates (1 test strip and all seals), for the external spool.')
A('- `plates/*.3mf`: one plain 3MF per plate (same layout) for OrcaSlicer, PrusaSlicer and others. The colour parts are named '
  '`<part>_<colour>` and carry a display colour; assign the filaments yourself.')
A('- `stl/*_print.stl`: every printed part on its own, in print orientation. Multicolour parts also come as colour bodies '
  '(`*_print_black.stl`, `*_print_orange.stl`, `*_print_green.stl`) in the same frame: load them together as one object with parts. '
  'The plain `*_print.stl` of a multicolour part is the whole part in one body, for single-colour printing.')
A('- `preview/<plate>_top.png` and `<plate>_iso.png`: plate previews with labels and colours.')
A('- `summary.json`: plates, parts, filament slots, grams per filament, times and colour swaps, as machine-readable data.')
A('- `slice_check/`: the slicer statistics behind the numbers in this guide. `layout.json`: part positions on each plate.')
A('- `tools/`: the scripts that generate all of the above (Python, trimesh and manifold3d). `tools/run_all.sh` rebuilds '
  'everything, slices both projects with the OrcaSlicer command line, and writes summary.json and this guide again.')
A('')
A('## Printer, plate and filament slots')
A('')
A('- Printer: Bambu Lab A1, 0.4 mm nozzle, Textured PEI plate (the plate the A1 comes with). Bed 256 x 256 x 256 mm; '
  'parts stay at least 12 mm from the front edge (the A1 draws its calibration line there) and 8 mm from the other edges.')
A('- Colour language: black is structure, orange is a touch point ("act here"), green is the food path, and yellow TPU is a seal or a soft part. '
  'Text and arrow inlays are 0.6 mm deep (3 layers of 0.2 mm) in the first or the last layers of a part.')
A('- AMS lite:')
A('  - slot 1: PETG black')
A('  - slot 2: PETG orange')
A('  - slot 3: PETG green')
A('  - slot 4: optional second spool of PETG black as an automatic backup (enable "Filament backup/auto refill" on the printer). '
  f"Black is about {S['totals']['grams_per_filament'].get('PETG black', 0) / max(S['totals']['grams_PETG'], 1) * 100:.0f} % "
  'of all PETG, and plate 01 alone uses over 300 g. If you have no second spool, leave slot 4 empty.')
A('- External spool holder: TPU 95A yellow. TPU cannot go through the AMS lite. In the print dialog, map the filament to "External spool".')
A('- The projects use the generic Bambu profiles "Generic PETG @BBL A1" and "Generic TPU @BBL A1". If you use a branded filament '
  '(for example Bambu PETG HF), pick its profile in the filament list. The part settings stay on the objects.')
A('')
A('## Plates')
A('')
A('Print the test plates first (see "Print these test pieces first"), then plates 01 to 04, then the TPU plate. Times and grams are '
  'slicer estimates that include supports, the prime tower and filament flushing.')
A('')
for key in ['PETG-0', 'PETG-1', 'PETG-2', 'PETG-3', 'PETG-4', 'TPU-0', 'TPU-1']:
    p = P[key]
    A(f"### {key}: {p['name']}")
    A('')
    A(f"Project `{p['bambu_project']}`, plate {p['plate_in_project']}. Plain file `{p['plain_3mf']}`. "
      f"Preview `{p['preview_top']}` and `{p['preview_iso']}`.")
    A('')
    A(f"- Purpose: {p['purpose']}.")
    A('- Parts:')
    for pp in p['parts']:
        cols = ' + '.join(pp['colours'])
        A(f"  - {pp['id']} x{pp['qty']} ({pp['label']}; {pp['material']} {cols})")
    A(f"- Filament: {'; '.join(p['filament_slots'])}.")
    def extra(v):
        parts_ = [f"{lab} {v[k]} g" for k, lab in (('support', 'support'), ('prime_tower', 'prime tower'), ('flush', 'flush')) if v[k] > 0.05]
        return f" (of which {', '.join(parts_)})" if parts_ else ''
    fil = '; '.join(f"{k} {g(v['grams'])}{extra(v)}" for k, v in p['est_grams_per_filament'].items())
    A(f"- Estimate: {p['est_time_hm']}, {fil}; colour swaps: {p['colour_swaps']}.")
    if p['prime_tower_xy_mm']:
        A(f"- Prime tower at X {p['prime_tower_xy_mm'][0]:.0f}, Y {p['prime_tower_xy_mm'][1]:.0f} (stored in the project).")
    A('')

T = S['totals']
A('### Totals')
A('')
for k, v in T['grams_per_filament'].items():
    A(f'- {k}: {g(v)}')
A(f"- All PETG: {g(T['grams_PETG'])}. All TPU 95A: {g(T['grams_TPU'])}.")
A(f"- Print time: {T['time_hm']} over {T['plates']} plates (test plates included). Colour swaps: {T['colour_swaps']} in total.")
A('')
A('### Why the plates are grouped like this')
A('')
A('- A part has one body colour through its whole height. Two body colours on one plate would cost a swap on every layer, so the '
  'plates follow the body colour: black (01, 02), green (03) and orange (04).')
A('- The multicolour parts only add swaps in their 3 inlay layers: the fondello inlays (plate 02), the green bands of the gate and '
  'window plates (plate 03, top and bottom layers) and the black disc label (plate 04).')
A('- Plate 01 has only one colour and no prime tower, so the shaft (albero_v6) can use its own 0.15 mm layers there.')
A('- Plate 03 puts the two 3 mm plates (black with green bands) on the green plate. This costs 16 swaps but saves a plate. '
  'An alternative split into 03a (scivolo + colletto, green only) and 03b (gate + window plates) was sliced as well: it '
  'uses 6 swaps and about 4 g less filament, and comes out at about the same total time once the extra plate start '
  '(about 6 to 7 min of heating, levelling and cleaning) is counted.')
A('- Purge per swap on the A1, from the Bambu colour model with the 92 mm3 nozzle volume (these values are in the project):')
for k, v in S['purge_per_swap_A1']['volumes'].items():
    A(f"  - {k}: {v['mm3']} mm3 ({v['grams']} g)")
A('')
A('## Recommended settings')
A('')
A('These settings are already set in the Bambu projects, as process presets and per-object settings. Use them in other slicers too.')
A('')
A('### PETG (all PETG parts)')
A('')
A('- Profile: Generic PETG @BBL A1 (or your brand profile). Nozzle 255 C (range 220 to 270), bed 80 C on Textured PEI '
  '(70 C on Engineering Plate). On smooth PEI, use glue stick as a release agent: PETG bonds too strongly to bare smooth PEI.')
A('- Cooling: fan 40 to 90 %, no fan for the first 3 layers. Max volumetric speed 8 mm3/s for generic PETG.')
A('- Dry the PETG before printing if it has been open (65 C for 6 to 8 h). Wet PETG strings, and stringing spoils the inlays.')
A('- Layer height 0.20 mm and first layer 0.20 mm (process 0.20mm Standard @BBL A1). Keep 0.20 mm on the plates with inlays: '
  'the inlays are exactly 3 layers (0.6 mm). The only exception is albero_v6 at 0.15 mm, for its O-ring grooves.')
A('- Seam: aligned (the default). Line width 0.42 mm.')
A('- Prime tower: on (the A1 default) for the multicolour plates, at the position stored in each plate.')
A('- Support filament is left on "Default", so the slicer may print a few supports with the filament that is already loaded '
  '(for example black under the green chute). This saves swaps and does not show on the parts.')
A('- Per part (walls / infill / other):')
A('  - chiocciola_v6 (bowl): 3 walls, 15 % infill. Supports: tree (auto), on build plate only, for the 3 bayonet lugs.')
A('  - scatola_v6 (box): 5 walls (solid 2.4 mm walls for the IP65 box), 15 % infill, 5 top and 5 bottom layers. Supports: normal (auto), '
  'on build plate only: this is the thin wedge under the 2.5 deg roof slopes.')
A('  - flangia_piano_v6 (flange): 3 walls, 25 % infill (it carries the whole unit). No supports needed; supports under the 4 mm hook ledges are optional.')
A('  - disco_v6, piastra_gate_v4b, piastra_finestra_v4b, colletto_v6: 3 walls, 15 % infill, no supports.')
A('  - fondello_v6 (cover): 4 walls, 15 % infill, 5 top and 5 bottom layers, no supports.')
A('  - colonna_v6 (tower): 4 walls, 40 % infill, no supports. The O-ring groove is a 2.7 mm bridge; the top lobes sit on 45 deg wedges.')
A('  - scivolo_v6 (chute): 4 walls, 15 % infill. Supports: tree (auto), allowed on the model (see "Deviations").')
A('  - albero_v6 (shaft): 100 % infill, 4 walls, 0.15 mm layers, 5 mm brim (it is 63 mm tall and only 12 mm wide).')
A('  - mozzo_v6 (hub), nottolino_v6 x4 (buttons), linguetta_sicura (latch), test_scanalato: 100 % infill, 4 walls.')
A('  - linguetta_sicura (latch): lying on its back with the nub up. Supports: normal (auto), on build plate only, under the spring tab (1.6 mm gap).')
A('')
A('### TPU 95A (seals)')
A('')
A('- Profile: Generic TPU @BBL A1 (or Bambu TPU 95A HF). Nozzle 240 C, bed 45 C on Textured PEI (35 to 45 C), fan 100 %.')
A('- Max volumetric speed 3.2 mm3/s (the profile limits the speed), retraction 0.4 mm. Feed from the external spool with a short, free path.')
A('- 100 % infill and 2 walls on every TPU part; 0.20 mm layers. The cover lip seal (guarnizione_fondello_v6) runs its walls at 20 mm/s.')
A('- Dry the TPU (65 C for 6 h) right before printing; wet TPU strings and bubbles.')
A('')
A('## Print these test pieces first')
A('')
A('1. PETG-0 (25 min, black): `test_scanalato` and `test_groove_fondello`.')
A('   - test_scanalato has 3 spline coupons, marked with 1, 2 or 3 notches for 0.05, 0.10 or 0.20 mm radial clearance on the 25T servo spline. '
  'Push each one onto the servo by hand. The right one slides on with light pressure and does not wobble. mozzo_v6 is built with '
  '0.10 mm (2 notches). If another coupon fits better, change SPL_CLEAR in parts/build_drivetrain.py, run build_v6.py again, '
  'and then run tools/build_print_v6.py again before printing plate 01.')
A('   - test_groove_fondello is a 40 mm cut of the cover edge (skirt, groove and inner lip) to check the TPU strip below.')
A('2. TPU-0 (about 9 min, mostly the printer start routine; external spool): `test_lip_strip`, a 40 mm straight cut of the cover lip seal. Check these points:')
A('   - the base presses fully into the groove of test_groove_fondello;')
A('   - the lip stands about 30 deg inward, clean and without strings;')
A('   - the lip springs back after you bend it flat.')
A('   If the lip is ragged, dry the TPU, print slower, or try 0.16 mm layers.')
A('3. After assembly, hose-test the closed box before you put electronics inside.')
A('')
A('## Check list: all printed parts')
A('')
A('Tick each part off as you print it. v6 has 14 PETG parts (17 pieces) and 7 TPU pieces, plus 3 test pieces.')
A('')
for c in S['parts_checklist']:
    A(f"- [ ] {c['id']} x{c['qty']}: {c['label']}; {c['material']} {' + '.join(c['colours'])}; plate {', '.join(c['plates'])}; "
      f"`{c['stl'][0]}`")
A('')
A('## Deviations and notes')
A('')
A('- **linguetta_sicura**: `parts/linguetta_sicura_print.stl` is exported upright (56.5 mm tall on a 12 x 3 mm foot). Its print note says '
  '"lying on its back (T-foot face down)". This package lays it on its back, nub up. That orientation is steadier on the moving A1 bed, '
  'and the spring tab then flexes along its layers instead of across them. It needs a small bed-only support under the tab.')
A('- **scivolo_v6**: the v6 note says "no supports". The drip ring is square to the tube, which is tilted 35 deg, so on its low side '
  'the 45 deg chamfer ends up about 10 deg from horizontal (about 300 mm2 of overhang at z 1 to 11 mm). The slicer reported '
  'floating regions. Supports are switched on for this part and may also stand on the flange top (not a sealing face).')
A('- `piastra_finestra_v4b_print*.stl` and `piastra_gate_v4b_print.stl` in parts/ have non-manifold edges where bodies touch. All '
  'files in `stl/` and in the 3MFs went through manifold3d and are closed solids.')
A('- The Bambu projects are generated by a script in the Bambu Studio project format (3MF metadata `BambuStudio-02.05.00.00`, so '
  'Bambu Studio 2.5 or newer and OrcaSlicer 2.5 or newer open them as projects). The settings come from the Bambu system '
  f"profiles ({S['validation']['bambu_profiles']}). They were checked by opening and slicing every plate with the OrcaSlicer 2.5.0 command line, "
  'without errors or warnings. They were not opened in Bambu Studio itself. After opening them in Bambu Studio, check the plate '
  'list, the filament mapping (slots 1 to 3, or the external spool for TPU) and slice each plate once.')
A('- The times and grams come from the OrcaSlicer estimator with the A1 profiles. Bambu Studio may differ by roughly 5 to 10 %.')
if S['cross_check']['tpu_v6_redesign_pending']:
    A('- **TPU redesign pending**: the 4 plate lips (comb-slit) and the bayonet rim gasket (low-force lip seal) are being redesigned as '
      + ', '.join(f'`{x}`' for x in S['cross_check']['tpu_v6_redesign_pending'])
      + '. This package still uses the reused v4b versions. When the `*_v6_print.stl` files appear in parts/, run '
        '`tools/build_print_v6.py` and the slicer check again: the generator then uses them automatically, and the TPU plate is rebuilt.')
A('')
open(os.path.join(OUT, 'README.md'), 'w').write('\n'.join(lines) + '\n')
print('README.md written,', len(lines), 'lines')
