# Kibble Dispenser Outdoor v6 - print guide (Bambu Lab A1 + AMS lite)

**Preview of v6: don't print the whole unit yet.** v6.1 is in design and will replace these files. They are here to look at the plates, set up the printer and print the test pieces. Website version, in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/v6/print/>

Everything you need to print the v6 dispenser on a Bambu Lab A1 with the AMS lite: two ready Bambu Studio projects, plain 3MF files for any slicer, single STL files in print orientation, the recommended settings and a check list of every printed part.

## Files

- `Kibble_Dispenser_v6_PETG.bambu.3mf`: Bambu Studio project with all PETG plates (1 test plate and 4 part plates). Parts are placed and oriented, multicolour parts are single objects with their colour parts assigned to AMS slots, the per-part settings (walls, infill, supports, brim, layer height) are stored on each object, and the A1 printer, process and filament presets are preset.
- `Kibble_Dispenser_v6_TPU.bambu.3mf`: Bambu Studio project with the TPU plates (1 test strip and all seals), for the external spool.
- `plates/*.3mf`: one plain 3MF per plate (same layout) for OrcaSlicer, PrusaSlicer and others. The colour parts are named `<part>_<colour>` and carry a display colour; assign the filaments yourself.
- `stl/*_print.stl`: every printed part on its own, in print orientation. Multicolour parts also come as colour bodies (`*_print_black.stl`, `*_print_orange.stl`, `*_print_green.stl`) in the same frame: load them together as one object with parts. The plain `*_print.stl` of a multicolour part is the whole part in one body, for single-colour printing.
- `preview/<plate>_top.png` and `<plate>_iso.png`: plate previews with labels and colours.
- `summary.json`: plates, parts, filament slots, grams per filament, times and colour swaps, as machine-readable data.
- `slice_check/`: the slicer statistics behind the numbers in this guide. `layout.json`: part positions on each plate.
- `tools/`: the scripts that generate all of the above (Python, trimesh and manifold3d). `tools/run_all.sh` rebuilds everything, slices both projects with the OrcaSlicer command line, and writes summary.json and this guide again.

## Printer, plate and filament slots

- Printer: Bambu Lab A1, 0.4 mm nozzle, Textured PEI plate (the plate the A1 comes with). Bed 256 x 256 x 256 mm; parts stay at least 12 mm from the front edge (the A1 draws its calibration line there) and 8 mm from the other edges.
- Colour language: black is structure, orange is a touch point ("act here"), green is the food path, and yellow TPU is a seal or a soft part. Text and arrow inlays are 0.6 mm deep (3 layers of 0.2 mm) in the first or the last layers of a part.
- AMS lite:
  - slot 1: PETG black
  - slot 2: PETG orange
  - slot 3: PETG green
  - slot 4: optional second spool of PETG black as an automatic backup (enable "Filament backup/auto refill" on the printer). Black is about 84 % of all PETG, and plate 01 alone uses over 300 g. If you have no second spool, leave slot 4 empty.
- External spool holder: TPU 95A yellow. TPU cannot go through the AMS lite. In the print dialog, map the filament to "External spool".
- The projects use the generic Bambu profiles "Generic PETG @BBL A1" and "Generic TPU @BBL A1". If you use a branded filament (for example Bambu PETG HF), pick its profile in the filament list. The part settings stay on the objects.

## Plates

Print the test plates first (see "Print these test pieces first"), then plates 01 to 04, then the TPU plate. Times and grams are slicer estimates that include supports, the prime tower and filament flushing.

### PETG-0: 00 TEST - spline + cover groove

Project `Kibble_Dispenser_v6_PETG.bambu.3mf`, plate 1. Plain file `plates/PETG-0_spline__cover_groove.3mf`. Preview `preview/PETG-0_top.png` and `preview/PETG-0_iso.png`.

- Purpose: print first: pick the spline clearance for mozzo_v6 and check the TPU lip strip in the groove.
- Parts:
  - test_scanalato x1 (Spline fit test (3 coupons); PETG black)
  - test_groove_fondello x1 (Cover groove coupon (40 mm cut of fondello_v6); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 0 h 25 min, PETG black 5.4 g; colour swaps: 0.

### PETG-1: 01 BLACK - bowl + box + shaft + hub

Project `Kibble_Dispenser_v6_PETG.bambu.3mf`, plate 2. Plain file `plates/PETG-1_bowl__box__shaft__hub.3mf`. Preview `preview/PETG-1_top.png` and `preview/PETG-1_iso.png`.

- Purpose: single colour (black); the two big supported parts; shaft at 0.15 mm layers needs a plate without prime tower.
- Parts:
  - chiocciola_v6 x1 (Bowl (chiocciola); PETG black)
  - scatola_v6 x1 (Electronics box; PETG black)
  - albero_v6 x1 (Shaft; PETG black)
  - mozzo_v6 x1 (Servo hub; PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 12 h 49 min, PETG black 324 g (of which support 11.2 g); colour swaps: 0.

### PETG-2: 02 BLACK+orange - flange + cover + tower

Project `Kibble_Dispenser_v6_PETG.bambu.3mf`, plate 3. Plain file `plates/PETG-2_flange__cover__tower.3mf`. Preview `preview/PETG-2_top.png` and `preview/PETG-2_iso.png`.

- Purpose: black body; orange cover inlays only in the first 3 layers.
- Parts:
  - flangia_piano_v6 x1 (Shelf flange; PETG black)
  - fondello_v6 x1 (Box cover; PETG black + orange)
  - colonna_v6 x1 (Tower (shaft passage); PETG black)
- Filament: AMS lite slot 1 = PETG black; AMS lite slot 2 = PETG orange.
- Estimate: 4 h 36 min, PETG black 121 g (of which prime tower 0.4 g, flush 0.3 g); PETG orange 1.7 g (of which prime tower 0.1 g, flush 0.8 g); colour swaps: 3.
- Prime tower at X 119, Y 185 (stored in the project).

### PETG-3: 03 GREEN+black - chute + collar + gate + window plates

Project `Kibble_Dispenser_v6_PETG.bambu.3mf`, plate 4. Plain file `plates/PETG-3_chute__collar__gate__window_plates.3mf`. Preview `preview/PETG-3_top.png` and `preview/PETG-3_iso.png`.

- Purpose: food path: green parts + the two 3 mm plates (black body, green bands).
- Parts:
  - scivolo_v6 x1 (Chute; PETG green)
  - colletto_v6 x1 (Funnel collar; PETG green)
  - piastra_finestra_v4b x1 (Window plate; PETG black + green)
  - piastra_gate_v4b x1 (Gate plate; PETG black + green)
- Filament: AMS lite slot 1 = PETG black; AMS lite slot 3 = PETG green.
- Estimate: 3 h 40 min, PETG black 39 g (of which support 0.3 g, prime tower 1.2 g, flush 1.1 g); PETG green 41 g (of which support 1.3 g, prime tower 0.6 g, flush 3.7 g); colour swaps: 16.
- Prime tower at X 201, Y 202 (stored in the project).

### PETG-4: 04 ORANGE+black - disc + latch + 4 buttons

Project `Kibble_Dispenser_v6_PETG.bambu.3mf`, plate 5. Plain file `plates/PETG-4_disc__latch__4_buttons.3mf`. Preview `preview/PETG-4_top.png` and `preview/PETG-4_iso.png`.

- Purpose: orange parts; black disc label only in the first 3 layers.
- Parts:
  - disco_v6 x1 (Dosing disc; PETG orange + black)
  - linguetta_sicura x1 (Safety latch; PETG orange)
  - nottolino_v6 x4 (Quarter-turn button; PETG orange)
- Filament: AMS lite slot 1 = PETG black; AMS lite slot 2 = PETG orange.
- Estimate: 2 h 22 min, PETG black 2.2 g (of which prime tower 0.2 g, flush 0.3 g); PETG orange 50 g (of which support 0.1 g, prime tower 0.2 g, flush 1.1 g); colour swaps: 3.
- Prime tower at X 165, Y 79 (stored in the project).

### TPU-0: 00 TEST - TPU lip seal strip

Project `Kibble_Dispenser_v6_TPU.bambu.3mf`, plate 1. Plain file `plates/TPU-0_TPU_lip_seal_strip.3mf`. Preview `preview/TPU-0_top.png` and `preview/TPU-0_iso.png`.

- Purpose: print first: check lip shape, fit in the groove coupon, deflection.
- Parts:
  - test_lip_strip x1 (TPU lip seal test strip (40 mm cut of guarnizione_fondello_v6); TPU 95A yellow)
- Filament: external spool = TPU yellow.
- Estimate: 0 h 09 min, TPU yellow 0.2 g; colour swaps: 0.

### TPU-1: 01 TPU 95A - all seals

Project `Kibble_Dispenser_v6_TPU.bambu.3mf`, plate 2. Plain file `plates/TPU-1_all_seals.3mf`. Preview `preview/TPU-1_top.png` and `preview/TPU-1_iso.png`.

- Purpose: all 7 TPU pieces, external spool.
- Parts:
  - guarnizione_baionetta x1 (Rim gasket (bayonet); TPU 95A yellow)
  - guarnizione_piano_v5 x1 (Flange-shelf gasket ring; TPU 95A yellow)
  - guarnizione_fondello_v6 x1 (Cover lip seal; TPU 95A yellow)
  - labbro_uscita_1 x1 (Plate lip, outlet 1; TPU 95A yellow)
  - labbro_uscita_2 x1 (Plate lip, outlet 2; TPU 95A yellow)
  - labbro_finestra_1 x1 (Plate lip, window 1; TPU 95A yellow)
  - labbro_finestra_2 x1 (Plate lip, window 2; TPU 95A yellow)
- Filament: external spool = TPU yellow.
- Estimate: 0 h 44 min, TPU yellow 6.7 g; colour swaps: 0.

### Totals

- PETG black: 491 g
- PETG orange: 52 g
- PETG green: 41 g
- TPU yellow: 6.9 g
- All PETG: 584 g. All TPU 95A: 6.9 g.
- Print time: 24 h 47 min over 7 plates (test plates included). Colour swaps: 22 in total.

### Why the plates are grouped like this

- A part has one body colour through its whole height. Two body colours on one plate would cost a swap on every layer, so the plates follow the body colour: black (01, 02), green (03) and orange (04).
- The multicolour parts only add swaps in their 3 inlay layers: the fondello inlays (plate 02), the green bands of the gate and window plates (plate 03, top and bottom layers) and the black disc label (plate 04).
- Plate 01 has only one colour and no prime tower, so the shaft (albero_v6) can use its own 0.15 mm layers there.
- Plate 03 puts the two 3 mm plates (black with green bands) on the green plate. This costs 16 swaps but saves a plate. An alternative split into 03a (scivolo + colletto, green only) and 03b (gate + window plates) was sliced as well: it uses 6 swaps and about 4 g less filament, and comes out at about the same total time once the extra plate start (about 6 to 7 min of heating, levelling and cleaning) is counted.
- Purge per swap on the A1, from the Bambu colour model with the 92 mm3 nozzle volume (these values are in the project):
  - black->orange: 551 mm3 (0.7 g)
  - black->green: 421 mm3 (0.53 g)
  - orange->black: 203 mm3 (0.26 g)
  - orange->green: 263 mm3 (0.33 g)
  - green->black: 172 mm3 (0.22 g)
  - green->orange: 423 mm3 (0.54 g)

## Recommended settings

These settings are already set in the Bambu projects, as process presets and per-object settings. Use them in other slicers too.

### PETG (all PETG parts)

- Profile: Generic PETG @BBL A1 (or your brand profile). Nozzle 255 C (range 220 to 270), bed 80 C on Textured PEI (70 C on Engineering Plate). On smooth PEI, use glue stick as a release agent: PETG bonds too strongly to bare smooth PEI.
- Cooling: fan 40 to 90 %, no fan for the first 3 layers. Max volumetric speed 8 mm3/s for generic PETG.
- Dry the PETG before printing if it has been open (65 C for 6 to 8 h). Wet PETG strings, and stringing spoils the inlays.
- Layer height 0.20 mm and first layer 0.20 mm (process 0.20mm Standard @BBL A1). Keep 0.20 mm on the plates with inlays: the inlays are exactly 3 layers (0.6 mm). The only exception is albero_v6 at 0.15 mm, for its O-ring grooves.
- Seam: aligned (the default). Line width 0.42 mm.
- Prime tower: on (the A1 default) for the multicolour plates, at the position stored in each plate.
- Support filament is left on "Default", so the slicer may print a few supports with the filament that is already loaded (for example black under the green chute). This saves swaps and does not show on the parts.
- Per part (walls / infill / other):
  - chiocciola_v6 (bowl): 3 walls, 15 % infill. Supports: tree (auto), on build plate only, for the 3 bayonet lugs.
  - scatola_v6 (box): 5 walls (solid 2.4 mm walls for the IP65 box), 15 % infill, 5 top and 5 bottom layers. Supports: normal (auto), on build plate only: this is the thin wedge under the 2.5 deg roof slopes.
  - flangia_piano_v6 (flange): 3 walls, 25 % infill (it carries the whole unit). No supports needed; supports under the 4 mm hook ledges are optional.
  - disco_v6, piastra_gate_v4b, piastra_finestra_v4b, colletto_v6: 3 walls, 15 % infill, no supports.
  - fondello_v6 (cover): 4 walls, 15 % infill, 5 top and 5 bottom layers, no supports.
  - colonna_v6 (tower): 4 walls, 40 % infill, no supports. The O-ring groove is a 2.7 mm bridge; the top lobes sit on 45 deg wedges.
  - scivolo_v6 (chute): 4 walls, 15 % infill. Supports: tree (auto), allowed on the model (see "Deviations").
  - albero_v6 (shaft): 100 % infill, 4 walls, 0.15 mm layers, 5 mm brim (it is 63 mm tall and only 12 mm wide).
  - mozzo_v6 (hub), nottolino_v6 x4 (buttons), linguetta_sicura (latch), test_scanalato: 100 % infill, 4 walls.
  - linguetta_sicura (latch): lying on its back with the nub up. Supports: normal (auto), on build plate only, under the spring tab (1.6 mm gap).

### TPU 95A (seals)

- Profile: Generic TPU @BBL A1 (or Bambu TPU 95A HF). Nozzle 240 C, bed 45 C on Textured PEI (35 to 45 C), fan 100 %.
- Max volumetric speed 3.2 mm3/s (the profile limits the speed), retraction 0.4 mm. Feed from the external spool with a short, free path.
- 100 % infill and 2 walls on every TPU part; 0.20 mm layers. The cover lip seal (guarnizione_fondello_v6) runs its walls at 20 mm/s.
- Dry the TPU (65 C for 6 h) right before printing; wet TPU strings and bubbles.

## Print these test pieces first

1. PETG-0 (25 min, black): `test_scanalato` and `test_groove_fondello`.
   - test_scanalato has 3 spline coupons, marked with 1, 2 or 3 notches for 0.05, 0.10 or 0.20 mm radial clearance on the 25T servo spline. Push each one onto the servo by hand. The right one slides on with light pressure and does not wobble. mozzo_v6 is built with 0.10 mm (2 notches). If another coupon fits better, change SPL_CLEAR in parts/build_drivetrain.py, run build_v6.py again, and then run tools/build_print_v6.py again before printing plate 01.
   - test_groove_fondello is a 40 mm cut of the cover edge (skirt, groove and inner lip) to check the TPU strip below.
2. TPU-0 (about 9 min, mostly the printer start routine; external spool): `test_lip_strip`, a 40 mm straight cut of the cover lip seal. Check these points:
   - the base presses fully into the groove of test_groove_fondello;
   - the lip stands about 30 deg inward, clean and without strings;
   - the lip springs back after you bend it flat.
   If the lip is ragged, dry the TPU, print slower, or try 0.16 mm layers.
3. After assembly, hose-test the closed box before you put electronics inside.

## Check list: all printed parts

Tick each part off as you print it. v6 has 14 PETG parts (17 pieces) and 7 TPU pieces, plus 3 test pieces.

- [ ] chiocciola_v6 x1: Bowl (chiocciola); PETG black; plate PETG-1; `stl/chiocciola_v6_print.stl`
- [ ] scatola_v6 x1: Electronics box; PETG black; plate PETG-1; `stl/scatola_v6_print.stl`
- [ ] flangia_piano_v6 x1: Shelf flange; PETG black; plate PETG-2; `stl/flangia_piano_v6_print.stl`
- [ ] disco_v6 x1: Dosing disc; PETG orange + black; plate PETG-4; `stl/disco_v6_print.stl`
- [ ] piastra_gate_v4b x1: Gate plate; PETG black + green; plate PETG-3; `stl/piastra_gate_v4b_print.stl`
- [ ] piastra_finestra_v4b x1: Window plate; PETG black + green; plate PETG-3; `stl/piastra_finestra_v4b_print.stl`
- [ ] linguetta_sicura x1: Safety latch; PETG orange; plate PETG-4; `stl/linguetta_sicura_print.stl`
- [ ] fondello_v6 x1: Box cover; PETG black + orange; plate PETG-2; `stl/fondello_v6_print.stl`
- [ ] colonna_v6 x1: Tower (shaft passage); PETG black; plate PETG-2; `stl/colonna_v6_print.stl`
- [ ] albero_v6 x1: Shaft; PETG black; plate PETG-1; `stl/albero_v6_print.stl`
- [ ] mozzo_v6 x1: Servo hub; PETG black; plate PETG-1; `stl/mozzo_v6_print.stl`
- [ ] scivolo_v6 x1: Chute; PETG green; plate PETG-3; `stl/scivolo_v6_print.stl`
- [ ] colletto_v6 x1: Funnel collar; PETG green; plate PETG-3; `stl/colletto_v6_print.stl`
- [ ] nottolino_v6 x4: Quarter-turn button; PETG orange; plate PETG-4; `stl/nottolino_v6_print.stl`
- [ ] guarnizione_baionetta x1: Rim gasket (bayonet); TPU 95A yellow; plate TPU-1; `stl/guarnizione_baionetta_print.stl`
- [ ] guarnizione_piano_v5 x1: Flange-shelf gasket ring; TPU 95A yellow; plate TPU-1; `stl/guarnizione_piano_v5_print.stl`
- [ ] guarnizione_fondello_v6 x1: Cover lip seal; TPU 95A yellow; plate TPU-1; `stl/guarnizione_fondello_v6_print.stl`
- [ ] labbro_uscita_1 x1: Plate lip, outlet 1; TPU 95A yellow; plate TPU-1; `stl/labbro_uscita_1_print.stl`
- [ ] labbro_uscita_2 x1: Plate lip, outlet 2; TPU 95A yellow; plate TPU-1; `stl/labbro_uscita_2_print.stl`
- [ ] labbro_finestra_1 x1: Plate lip, window 1; TPU 95A yellow; plate TPU-1; `stl/labbro_finestra_1_print.stl`
- [ ] labbro_finestra_2 x1: Plate lip, window 2; TPU 95A yellow; plate TPU-1; `stl/labbro_finestra_2_print.stl`
- [ ] test_scanalato x1: Spline fit test (3 coupons); PETG black; plate PETG-0; `stl/test_scanalato_print.stl`
- [ ] test_groove_fondello x1: Cover groove coupon (40 mm cut of fondello_v6); PETG black; plate PETG-0; `stl/test_groove_fondello_print.stl`
- [ ] test_lip_strip x1: TPU lip seal test strip (40 mm cut of guarnizione_fondello_v6); TPU 95A yellow; plate TPU-0; `stl/test_lip_strip_print.stl`

## Deviations and notes

- **linguetta_sicura**: `parts/linguetta_sicura_print.stl` is exported upright (56.5 mm tall on a 12 x 3 mm foot). Its print note says "lying on its back (T-foot face down)". This package lays it on its back, nub up. That orientation is steadier on the moving A1 bed, and the spring tab then flexes along its layers instead of across them. It needs a small bed-only support under the tab.
- **scivolo_v6**: the v6 note says "no supports". The drip ring is square to the tube, which is tilted 35 deg, so on its low side the 45 deg chamfer ends up about 10 deg from horizontal (about 300 mm2 of overhang at z 1 to 11 mm). The slicer reported floating regions. Supports are switched on for this part and may also stand on the flange top (not a sealing face).
- `piastra_finestra_v4b_print*.stl` and `piastra_gate_v4b_print.stl` in parts/ have non-manifold edges where bodies touch. All files in `stl/` and in the 3MFs went through manifold3d and are closed solids.
- The Bambu projects are generated by a script in the Bambu Studio project format (3MF metadata `BambuStudio-02.05.00.00`, so Bambu Studio 2.5 or newer and OrcaSlicer 2.5 or newer open them as projects). The settings come from the Bambu system profiles (BambuStudio master, resources/profiles/BBL, profile version 02.09.00.74, fetched 2026-11-09). They were checked by opening and slicing every plate with the OrcaSlicer 2.5.0 command line, without errors or warnings. They were not opened in Bambu Studio itself. After opening them in Bambu Studio, check the plate list, the filament mapping (slots 1 to 3, or the external spool for TPU) and slice each plate once.
- The times and grams come from the OrcaSlicer estimator with the A1 profiles. Bambu Studio may differ by roughly 5 to 10 %.
- **TPU redesign pending**: the 4 plate lips (comb-slit) and the bayonet rim gasket (low-force lip seal) are being redesigned as `labbro_uscita_1_v6`, `labbro_uscita_2_v6`, `labbro_finestra_1_v6`, `labbro_finestra_2_v6`, `guarnizione_baionetta_v6`. This package still uses the reused v4b versions. When the `*_v6_print.stl` files appear in parts/, run `tools/build_print_v6.py` and the slicer check again: the generator then uses them automatically, and the TPU plate is rebuilt.

