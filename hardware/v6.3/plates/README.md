# Kibble Dispenser Outdoor v6.3 - print guide (Bambu Lab A1 + AMS lite)

Everything you need to print the v6.3 dispenser on a Bambu Lab A1 with the AMS lite: two ready Bambu Studio projects, plain 3MF files for any slicer, single STL files in print orientation, the recommended settings and a check list of every printed part.

**Design v6.3 (hardware 6.3.0): designed and checked in CAD, not printed or tested yet.** Print the test pieces first. The firmware for the one-button control panel is still to come (issue #2). Website version, in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/print/>

Kit note (v63.json kit_split): the kit ships the dispenser unit pre-assembled (bowl, drive tower, chute, electronics box, shell, cap with the control panel, plates, disc) plus a separate flange assembly. DIY builders print every part, so this package includes them all. The parts marked "kit module" are the factory modules inside the unit (drive tower, electronics box).

## Files

- `Kibble_Dispenser_v63_PETG.bambu.3mf`: Bambu Studio project with all PETG plates (1 test plate and 6 part plates). The parts are placed and oriented. Multicolour parts are single objects with their colour parts assigned to AMS slots. Per-part settings (walls, infill, supports, brim, layer height, IP66 settings for the box and the cap) are stored on each object, and the A1 printer, process and filament presets are set.
- `Kibble_Dispenser_v63_TPU.bambu.3mf`: Bambu Studio project with the TPU plates (1 test plate and all seals), for the external spool.
- `plates/*.3mf`: one plain 3MF per plate (same layout) for OrcaSlicer, PrusaSlicer and others. Colour parts are named `<part>_<colour>` and carry a display colour. Assign the filaments and the per-part settings below yourself: a plain 3MF carries no settings or modifiers.
- `stl/*_print.stl`: every printed part on its own, in print orientation. Multicolour parts also come as colour bodies (`*_print_black.stl`, `*_print_orange.stl`, `*_print_green.stl`) in the same frame: load them together as one object with parts.
- `preview/<plate>_top.png` and `<plate>_iso.png`: plate previews. `summary.json`: all numbers as data. `slice_check/`: slicer statistics. `layout.json`: part positions.
- `tools/`: the generator scripts. `tools/run_all.sh` rebuilds everything, slices both projects with the OrcaSlicer command line, and writes summary.json and this guide again.

## Printer, plate and filament slots

- Printer: Bambu Lab A1, 0.4 mm nozzle, Textured PEI plate. Bed 256 x 256 x 256 mm. Parts keep at least 5 mm from each other and stay clear of the A1 calibration line (front edge, X 108 to 160).
- Colour language: black is structure, orange is a touch point ("act here"), green is the food path, and yellow TPU is a seal or a soft part. Inlays are 0.6 mm (3 layers of 0.2 mm) in the first or the last layers of a part.
- AMS lite:
  - slot 1: PETG black
  - slot 2: PETG orange
  - slot 3: PETG green
  - slot 4: optional second spool of PETG black as an automatic backup (enable "Filament backup/auto refill"). Black is about 82 % of all PETG. Without a second spool, leave slot 4 empty.
- External spool holder: TPU 95A yellow. TPU cannot go through the AMS lite. In the print dialog, map the filament to "External spool".
- Profiles: "Generic PETG @BBL A1" and "Generic TPU @BBL A1". If you use a branded filament, pick its own profile.

## Plates

Print the test plates first, then plates 01 to 06, then the TPU plate. Times and grams are slicer estimates that include supports, the prime tower and filament flushing.

### PETG-0: 00 TEST - spline + rim, cap and skirt grooves

Project `Kibble_Dispenser_v63_PETG.bambu.3mf`, plate 1. Plain file `plates/PETG-0_spline__rim_cap_and_skirt_grooves.3mf`. Preview `preview/PETG-0_top.png` and `preview/PETG-0_iso.png`.

- Purpose: print first: spline clearance for mozzo_v6; groove coupons for the TPU test strips.
- Parts:
  - test_scanalato x1 (Spline fit test (3 coupons); PETG black)
  - test_groove_rim x1 (Bowl rim groove coupon (30 mm cut of chiocciola_v63); PETG black)
  - test_groove_cap x1 (Cap upstand groove coupon (20 mm cut of fondello_v63); PETG black)
  - test_groove_skirt x1 (Flange skirt groove coupon (30 mm cut of flangia_piano_v63); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 0 h 31 min, PETG black 6.9 g; colour swaps: 0.

### PETG-1: 01 BLACK - pod shell + electronics box

Project `Kibble_Dispenser_v63_PETG.bambu.3mf`, plate 2. Plain file `plates/PETG-1_pod_shell__electronics_box.3mf`. Preview `preview/PETG-1_top.png` and `preview/PETG-1_iso.png`.

- Purpose: single colour (black); shell with brim; box with the IP66 settings (no support any more).
- Parts:
  - guscio_v611 x1 (Pod shell; PETG black)
  - scatola_v63 x1 (Electronics box (PT bosses); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 9 h 07 min, PETG black 248 g; colour swaps: 0.

### PETG-2: 02 BLACK - bowl + pod cap

Project `Kibble_Dispenser_v63_PETG.bambu.3mf`, plate 3. Plain file `plates/PETG-2_bowl__pod_cap.3mf`. Preview `preview/PETG-2_top.png` and `preview/PETG-2_iso.png`.

- Purpose: single colour (black); bowl lugs and cap bottom edge on bed-only supports.
- Parts:
  - chiocciola_v63 x1 (Bowl (PT pilots, P3 insert moved); PETG black)
  - fondello_v63 x1 (Pod cap (control panel, PT screw bosses); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 11 h 06 min, PETG black 304 g (of which support 13.2 g); colour swaps: 0.

### PETG-3: 03 BLACK - lower flange + tower + shaft + hub

Project `Kibble_Dispenser_v63_PETG.bambu.3mf`, plate 4. Plain file `plates/PETG-3_lower_flange__tower__shaft__hub.3mf`. Preview `preview/PETG-3_top.png` and `preview/PETG-3_iso.png`.

- Purpose: single colour (black); the shaft at 0.15 mm layers needs a plate without prime tower.
- Parts:
  - flangia_piano_v63 x1 (Lower flange plate (dowel hole); PETG black)
  - colonna_v63 x1 (Tower (3 pillars, P3 moved); PETG black)
  - albero_v6 x1 (Shaft; PETG black)
  - mozzo_v6 x1 (Servo hub; PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 5 h 52 min, PETG black 128 g; colour swaps: 0.

### PETG-4: 04 BLACK - upper flange

Project `Kibble_Dispenser_v63_PETG.bambu.3mf`, plate 5. Plain file `plates/PETG-4_upper_flange.3mf`. Preview `preview/PETG-4_top.png` and `preview/PETG-4_iso.png`.

- Purpose: single colour (black); the second d180 plate cannot share a plate with another big part.
- Parts:
  - flangia_alta_v63 x1 (Upper flange plate (3 press-fit pins, tie window); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 3 h 01 min, PETG black 90 g; colour swaps: 0.

### PETG-5: 05 GREEN+black - chute + collar + gate blade + gate + window plates

Project `Kibble_Dispenser_v63_PETG.bambu.3mf`, plate 6. Plain file `plates/PETG-5_chute__collar__gate_blade__gate__window_plates.3mf`. Preview `preview/PETG-5_top.png` and `preview/PETG-5_iso.png`.

- Purpose: food path and gate: green parts + the two 3 mm plates (black body, green bands).
- Parts:
  - scivolo_v611 x1 (Chute; PETG green)
  - colletto_v6 x1 (Funnel collar; PETG green)
  - saracinesca_v63 x1 (Gate blade (one colour); PETG green)
  - piastra_finestra_v62 x1 (Window plate; PETG black + green)
  - piastra_gate_v62 x1 (Gate plate; PETG black + green)
- Filament: AMS lite slot 1 = PETG black; AMS lite slot 3 = PETG green.
- Estimate: 4 h 21 min, PETG black 37 g (of which prime tower 0.8 g, flush 1.3 g); PETG green 64 g (of which prime tower 0.5 g, flush 3.7 g); colour swaps: 15.
- Prime tower at X 204, Y 77 (stored in the project).

### PETG-6: 06 ORANGE+black - interlock ring + disc + latch + button

Project `Kibble_Dispenser_v63_PETG.bambu.3mf`, plate 7. Plain file `plates/PETG-6_interlock_ring__disc__latch__button.3mf`. Preview `preview/PETG-6_top.png` and `preview/PETG-6_iso.png`.

- Purpose: orange parts; the disc prints inside the ring; black disc label only in the first 3 layers.
- Parts:
  - anello_saracinesca_v63 x1 (Interlock ring (teardrop window); PETG orange)
  - disco_v61 x1 (Dosing disc (self-cleaning); PETG orange + black)
  - linguetta_sicura_v63 x1 (Safety latch; PETG orange)
  - pulsante_v611 x1 (Latch push-button; PETG orange)
- Filament: AMS lite slot 1 = PETG black; AMS lite slot 2 = PETG orange.
- Estimate: 4 h 09 min, PETG black 2.2 g (of which prime tower 0.2 g, flush 0.3 g); PETG orange 120 g (of which support 0.1 g, prime tower 0.2 g, flush 1.1 g); colour swaps: 3.
- Prime tower at X 193, Y 195 (stored in the project).

### TPU-0: 00 TEST - rim, cap, skirt and comb lips

Project `Kibble_Dispenser_v63_TPU.bambu.3mf`, plate 1. Plain file `plates/TPU-0_rim_cap_skirt_and_comb_lips.3mf`. Preview `preview/TPU-0_top.png` and `preview/TPU-0_iso.png`.

- Purpose: print first: the thin TPU flaps (0.5 rim, 0.5 skirt, comb slits, cap lip).
- Parts:
  - test_rim_lip x1 (TPU rim lip seal test arc (30 mm); TPU 95A yellow)
  - test_cap_lip x1 (TPU cap lip seal test strip (20 mm); TPU 95A yellow)
  - test_skirt_lip x1 (TPU skirt lip test arc (30 mm); TPU 95A yellow)
  - test_comb_lip x1 (TPU comb lip test (spare labbro_pettine_v62); TPU 95A yellow)
- Filament: external spool = TPU yellow.
- Estimate: 0 h 12 min, TPU yellow 0.5 g; colour swaps: 0.

### TPU-1: 01 TPU 95A - all seals

Project `Kibble_Dispenser_v63_TPU.bambu.3mf`, plate 2. Plain file `plates/TPU-1_all_seals.3mf`. Preview `preview/TPU-1_top.png` and `preview/TPU-1_iso.png`.

- Purpose: all 10 TPU pieces, external spool.
- Parts:
  - labbro_ombra_v611 x1 (Skirt lip ring; TPU 95A yellow)
  - guarnizione_baionetta_v61 x1 (Rim lip seal; TPU 95A yellow)
  - guarnizione_piano_v5 x1 (Flange-shelf gasket ring; TPU 95A yellow)
  - labbro_scivolo_v611 x1 (Chute lip ring; TPU 95A yellow)
  - guarnizione_fondello_v61 x1 (Cap lip seal (D outline); TPU 95A yellow)
  - labbro_pettine_v62 x4 (Comb lip (common, x4); TPU 95A yellow)
  - passacavo_v63 x1 (Cable tunnel grommet (raised tunnel); TPU 95A yellow)
- Filament: external spool = TPU yellow.
- Estimate: 1 h 08 min, TPU yellow 7.5 g; colour swaps: 0.

### Totals

- PETG black: 816 g
- PETG green: 64 g
- PETG orange: 120 g
- TPU yellow: 8.0 g
- All PETG: 1000 g. All TPU 95A: 8.0 g.
- Print time: 39 h 30 min over 9 plates (test plates included). Colour swaps: 18 in total.

### Why the plates are grouped like this

- A part has one body colour through its whole height, so the plates follow the body colour: black (01, 02, 03), green (04) and orange (05). The multicolour parts add swaps only in their 3 inlay layers.
- Black needs four plates: the shell (164 mm), the cap (143), both flange plates (180) and the box do not pair up. The pairs that fit are shell + box and bowl + cap (diagonal, 6 mm apart, relaxed 4 mm bed margins), and lower flange + tower/shaft/hub. The upper flange plate prints alone.
- Plate 03 has a single colour and no prime tower, so the shaft (albero_v6) can use its own 0.15 mm layers there.
- Plate 05: the gate blade is green only in v6.3. Its 15 layers coincide with the black/green layers of the gate and window plates, so it adds no swaps there.
- Plate 06: the disc prints inside the 176 mm interlock ring; only the disc label adds swaps (first 3 layers).
- Purge per swap on the A1 (Bambu colour model, 92 mm3 nozzle volume, stored in the project):
  - black->orange: 551 mm3 (0.7 g)
  - black->green: 421 mm3 (0.53 g)
  - orange->black: 203 mm3 (0.26 g)
  - orange->green: 263 mm3 (0.33 g)
  - green->black: 172 mm3 (0.22 g)
  - green->orange: 423 mm3 (0.54 g)

## Recommended settings

These settings are already in the Bambu projects, as process presets and per-object settings. Use them in other slicers too.

### PETG

- Profile Generic PETG @BBL A1: nozzle 255 C, bed 80 C on Textured PEI (70 C on Engineering Plate). On smooth PEI, use glue stick as a release agent.
- Fan 40 to 90 % (off for the first 3 layers). Max volumetric speed 8 mm3/s (generic). Dry open spools at 65 C for 6 to 8 h.
- Layer height 0.20 mm and first layer 0.20 mm (0.20mm Standard @BBL A1); keep 0.20 mm where there are inlays. Only albero_v6 uses 0.15 mm. Seam aligned. Prime tower on for the multicolour plates.
- Support filament stays on "Default", so a few supports may print in the filament that is already loaded. This saves swaps.
- Per part:
  - guscio_v611 (shell): 5 walls, 15 % infill, 6 mm outer brim, no supports.
  - fondello_v63 (cap) and scatola_v63 (box): IP66 settings, see below.
  - chiocciola_v63 (bowl): 3 walls, 15 %. Supports: tree, on build plate only (3 bayonet lugs). The chute-ear and shell-tab holes are d2.5 pilots for the PT screws: do not drill them out.
  - flangia_piano_v63 (lower flange plate): shelf-side face on the bed, 3 walls, 25 %, no supports. Press the 4 x 6 dowel in after printing.
  - flangia_alta_v63 (upper flange plate): shelf face on the bed, 3 walls, 25 %, no supports. The 3 press-fit pins grow up (they are printed, not bought).
  - anello_saracinesca_v63 (interlock ring, orange): on its bottom edge, 4 walls, 15 %, 5 mm outer brim, no support (teardrop window).
  - saracinesca_v63 (gate blade, green): flat, 3 walls, 100 % infill.
  - colonna_v63 (tower): upright, 4 walls, 100 % infill (pillars under the M3x40 preload).
  - scivolo_v611 (chute): 5 walls, 15 %, no supports. disco_v61, piastra_gate_v62, piastra_finestra_v62, colletto_v6: 3 walls, 15 %, no supports.
  - albero_v6 (shaft): 100 %, 0.15 mm layers, 5 mm brim. mozzo_v6, pulsante_v611, linguetta_sicura_v63: 100 % infill, 4 walls (the latch lies on its back with a small bed-only support under the spring tab).

### IP66 settings: box and cap (as v6.1.1; v63.json print notes)

- 5 walls at 0.42 mm line width (at least 4 walls fill a 2.0 mm wall solid), 100 % infill, 5 top and 5 bottom layers, seam at the back.
- Object flow ratio 1.03 (+3 %, inside the +2 to 5 % range), stored as print_flow_ratio on the two objects.
- Box: top surfaces ironed (the rim face prints as a top surface and carries the cap lip).
- Box: no support at all in v6.3 (the C boss overhangs its column by 2.5 mm). Top surfaces ironed (rim face).
- Cap: the control-panel knock-out skins (2.0 mm) print solid inside the 5 walls, the 0.3 mm engravings face sideways, and the dry-pocket roof bridges at most 18 mm between the bosses. None of these needs support.
- Cap: a bed-only support ring (normal supports, threshold 45 deg) under the lowest ~5 mm of the R15 bottom edge, as in v6.1.
- Filament settings for these two plates (set them by hand in the filament profile): nozzle 245 to 250 C, part fan 40 % or less, for layer bonding.
- After printing:
  - clear the drain holes (d 0.8 mm, two labyrinth drains in v6.3) in the cap with a 0.8 mm drill; first-layer squish can close them;
  - hold the empty box against a bright light in a dark room: pinholes glow;
  - the gland pad is a vertical face and cannot be ironed: check it is flat where the gland O-ring seats.

### TPU 95A

- Profile Generic TPU @BBL A1: nozzle 240 C, bed 45 C on Textured PEI, fan 100 %, max volumetric speed 3.2 mm3/s, retraction 0.4 mm. Dry the TPU (65 C, 6 h) right before printing.
- All TPU parts use 100 % infill and 2 walls, 0.20 mm layers.
- Thin flaps use the Arachne wall generator at 15 mm/s so that each flap prints as one clean line: guarnizione_baionetta_v61 (0.5 mm), labbro_ombra_v611 (skirt, 0.5 mm, 20 deg cone), labbro_scivolo_v611 (chute, 0.6 mm) and the 4 comb lips (0.8 mm, 0.7 mm slits). guarnizione_fondello_v61 prints its walls at 20 mm/s.

## Print these test pieces first

1. PETG-0 (black): `test_scanalato`, `test_groove_rim`, `test_groove_cap` and `test_groove_skirt`.
   - test_scanalato: 3 spline coupons (1, 2 or 3 notches for 0.05, 0.10 or 0.20 mm). mozzo_v6 is built with 0.10 mm. If another coupon fits better, change SPL_CLEAR in parts/build_drivetrain.py, rebuild mozzo_v6 and run tools/run_all.sh.
   - The groove coupons are cuts of the bowl rim (chiocciola_v63), the cap D upstand (fondello_v63) and the lower flange edge (flangia_piano_v63, skirt-lip groove).
2. TPU-0 (external spool): `test_rim_lip`, `test_cap_lip`, `test_skirt_lip` and `test_comb_lip` (a spare labbro_pettine_v62).
   - Press each strip into its groove coupon. The anchor should seat fully, and the flap should be one clean, closed line that springs back.
   - On the comb lip, the slits must be open.
3. After printing:
   - check the seam O-ring 132x2 squeeze (light drag over the last 2 mm) and look at the cap spigot ring (see Deviations);
   - drive the PT K30 screws by hand (about 0.6 N m), at most about 5 times per hole;
   - tighten the M3x40 stack screws to 0.4 N m and re-check after a week.
4. Hose-test the closed pod before you put electronics inside.

## Bought parts (not printed)

Not on any plate. Changes in v6.3:
- New: the panel parts: an IP67 12 mm short-body push-button, 2 light pipes with LEDs, an IP67 acoustic membrane, a d20 speaker and a JST harness.
- New: 3 PT K30x12 cap screws (T10) with O-rings 3x1 instead of the thumb-turns, keys and their O-rings.
- New: PT K30 screws straight into pilots for the chute and the shell tabs, instead of 5 heat-set inserts.
- New: a UV cable tie for strain relief. The 4 x 6 dowel is now part of the design.
- Gone: the 3 flange join screws (now 3 press-fit pins printed on the upper plate) and the 4 cable-channel screws.

- 1 x dowel pin ISO 2338 4 m6 x 6, stainless: gate blade pivot, pressed into the lower flange plate (v63_viewer.json / v63.json)
- 4 x wood screw 5x35 pan head (5x30 for an 18 mm shelf): flange set -> shelf (they also clamp the cable jacket) (v63_viewer.json / v63.json)
- 7 x M3 heat-set insert RX-M3x5.7: 3 in the bowl (stack screws P1..P3), 4 in the box (servo) (v63_viewer.json / v63.json)
- 3 x M3x40 DIN912 A2: box + tower + bowl stack, from below (v63_viewer.json / v63.json)
- 2 x O-ring NBR70 3x1: under the P2/P3 stack-screw heads in the roof countersinks (v63_viewer.json / v63.json)
- 3 x EJOT PT K30x12 thread-forming screw, Torx T10: cap -> box bosses (replace the thumb-turns), from below (v63_viewer.json / v63.json)
- 3 x O-ring NBR70 3x1: under the three cap screw heads (v63_viewer.json / v63.json)
- 3 x EJOT PT K30x12 thread-forming screw: shell tabs -> bowl (d2.5 pilots, no inserts) (v63_viewer.json / v63.json)
- 2 x EJOT PT K30x10 thread-forming screw: chute ears -> bowl (d2.5 pilots, no inserts) (v63_viewer.json / v63.json)
- 4 x M3x8 DIN912 A2 + washer: servo -> cradle inserts (v63_viewer.json / v63.json)
- 1 x M3x8 DIN912 A2: hub -> servo spline (v63_viewer.json / v63.json)
- 2 x O-ring NBR70 9x2: shaft (tower module) (v63_viewer.json / v63.json)
- 1 x O-ring NBR70 24x2: tower <-> box face seal (v63_viewer.json / v63.json)
- 1 x O-ring NBR70 14x1.5: latch push-button, in the shell bore groove (v63_viewer.json / v63.json)
- 1 x O-ring NBR70 132x2: shell | cap seam, in the cap spigot groove (v63_viewer.json / v63.json)
- 1 x M12x1.5 cable gland IP68 + locknut: box wall (v63_viewer.json / v63.json)
- 1 x M12x1.5 ePTFE membrane vent IP68 + locknut: box roof (v63_viewer.json / v63.json)
- 1 x M8 A-coded 4-pin IP67 inline connector pair: unit pigtail <-> supply cable, in the pod top (v63_viewer.json / v63.json)
- 1 x 12 V cable, unit side (pigtail) + supply cable PUR 4x0.34 d5: supply cable runs through the flange tunnel (v63_viewer.json / v63.json)
- 1 x cable tie 3.6 x 140, UV-stable PA66: strain relief, cinched in the upper plate window (v63_viewer.json / v63.json)
- 1 x IP67 12 mm momentary push-button, flush flat head, M12x1 front mount, short body (<= 14 mm behind the panel, d13), front gasket: control panel; check the depth on the datasheet (14 mm free behind the mount wall) (v63_viewer.json / v63.json)
- 2 x panel light pipe d5 x 9-10 mm, flat flush lens, flange d8 (clear PC) + O-ring NBR70 5x1 each: status and Wi-Fi LEDs (v63_viewer.json / v63.json)
- 2 x LED 3 mm (status green, Wi-Fi blue) + series resistors on the board: behind the light pipes (v63_viewer.json / v63.json)
- 1 x IP67 adhesive acoustic vent, ePTFE, d15 disc with d8 active area: speaker opening in the cap (v63_viewer.json / v63.json)
- 1 x mylar speaker d20 x 4.5, 8 ohm 0.5 W + foam ring d20/12 x 1: meow / sounds (v63_viewer.json / v63.json)
- 1 x harness JST-XH 2.54 8-pin: panel (button, LEDs, speaker, 1 spare) -> board; unplug before pulling the cap off (v63_viewer.json / v63.json)
- 1 x standard servo (25T spline): drive (v63_viewer.json / v63.json)
- 1 x 70 x 50 perfboard + ESP32-WROVER dev board + Pololu D36V50F6 12 V regulator + 5 V logic regulator + 1000 uF capacitor: electronics (v63_viewer.json / v63.json)
- 1 x food-grade silicone grease NSF H1: factory: O-rings (v63_viewer.json / v63.json)

## Check list: all printed parts

v6.3 has 18 PETG parts (18 pieces) and 10 TPU pieces, plus 8 test pieces.

- [ ] guscio_v611 x1: Pod shell; PETG black; plate PETG-1; `stl/guscio_v611_print.stl`
- [ ] fondello_v63 x1: Pod cap (control panel, PT screw bosses); PETG black; plate PETG-2; `stl/fondello_v63_print.stl`
- [ ] chiocciola_v63 x1: Bowl (PT pilots, P3 insert moved); PETG black; plate PETG-2; `stl/chiocciola_v63_print.stl`
- [ ] flangia_piano_v63 x1: Lower flange plate (dowel hole); PETG black; plate PETG-3; `stl/flangia_piano_v63_print.stl`
- [ ] flangia_alta_v63 x1: Upper flange plate (3 press-fit pins, tie window); PETG black; plate PETG-4; `stl/flangia_alta_v63_print.stl`
- [ ] colonna_v63 x1: Tower (3 pillars, P3 moved); PETG black; plate PETG-3; `stl/colonna_v63_print.stl` - kit module: drive tower
- [ ] albero_v6 x1: Shaft; PETG black; plate PETG-3; `stl/albero_v6_print.stl` - kit module: drive tower
- [ ] mozzo_v6 x1: Servo hub; PETG black; plate PETG-3; `stl/mozzo_v6_print.stl` - kit module: electronics box (hub on the servo)
- [ ] scatola_v63 x1: Electronics box (PT bosses); PETG black; plate PETG-1; `stl/scatola_v63_print.stl` - kit module: electronics box
- [ ] piastra_gate_v62 x1: Gate plate; PETG black + green; plate PETG-5; `stl/piastra_gate_v62_print.stl`
- [ ] piastra_finestra_v62 x1: Window plate; PETG black + green; plate PETG-5; `stl/piastra_finestra_v62_print.stl`
- [ ] saracinesca_v63 x1: Gate blade (one colour); PETG green; plate PETG-5; `stl/saracinesca_v63_print.stl`
- [ ] scivolo_v611 x1: Chute; PETG green; plate PETG-5; `stl/scivolo_v611_print.stl`
- [ ] colletto_v6 x1: Funnel collar; PETG green; plate PETG-5; `stl/colletto_v6_print.stl`
- [ ] disco_v61 x1: Dosing disc (self-cleaning); PETG orange + black; plate PETG-6; `stl/disco_v61_print.stl`
- [ ] anello_saracinesca_v63 x1: Interlock ring (teardrop window); PETG orange; plate PETG-6; `stl/anello_saracinesca_v63_print.stl`
- [ ] linguetta_sicura_v63 x1: Safety latch; PETG orange; plate PETG-6; `stl/linguetta_sicura_v63_print.stl`
- [ ] pulsante_v611 x1: Latch push-button; PETG orange; plate PETG-6; `stl/pulsante_v611_print.stl`
- [ ] labbro_pettine_v62 x4: Comb lip (common, x4); TPU 95A yellow; plate TPU-1; `stl/labbro_pettine_v62_print.stl`
- [ ] guarnizione_baionetta_v61 x1: Rim lip seal; TPU 95A yellow; plate TPU-1; `stl/guarnizione_baionetta_v61_print.stl`
- [ ] guarnizione_fondello_v61 x1: Cap lip seal (D outline); TPU 95A yellow; plate TPU-1; `stl/guarnizione_fondello_v61_print.stl`
- [ ] guarnizione_piano_v5 x1: Flange-shelf gasket ring; TPU 95A yellow; plate TPU-1; `stl/guarnizione_piano_v5_print.stl`
- [ ] labbro_ombra_v611 x1: Skirt lip ring; TPU 95A yellow; plate TPU-1; `stl/labbro_ombra_v611_print.stl`
- [ ] labbro_scivolo_v611 x1: Chute lip ring; TPU 95A yellow; plate TPU-1; `stl/labbro_scivolo_v611_print.stl`
- [ ] passacavo_v63 x1: Cable tunnel grommet (raised tunnel); TPU 95A yellow; plate TPU-1; `stl/passacavo_v63_print.stl`
- [ ] test_scanalato x1: Spline fit test (3 coupons); PETG black; plate PETG-0; `stl/test_scanalato_print.stl`
- [ ] test_groove_rim x1: Bowl rim groove coupon (30 mm cut of chiocciola_v63); PETG black; plate PETG-0; `stl/test_groove_rim_print.stl`
- [ ] test_groove_cap x1: Cap upstand groove coupon (20 mm cut of fondello_v63); PETG black; plate PETG-0; `stl/test_groove_cap_print.stl`
- [ ] test_groove_skirt x1: Flange skirt groove coupon (30 mm cut of flangia_piano_v63); PETG black; plate PETG-0; `stl/test_groove_skirt_print.stl`
- [ ] test_rim_lip x1: TPU rim lip seal test arc (30 mm); TPU 95A yellow; plate TPU-0; `stl/test_rim_lip_print.stl`
- [ ] test_cap_lip x1: TPU cap lip seal test strip (20 mm); TPU 95A yellow; plate TPU-0; `stl/test_cap_lip_print.stl`
- [ ] test_skirt_lip x1: TPU skirt lip test arc (30 mm); TPU 95A yellow; plate TPU-0; `stl/test_skirt_lip_print.stl`
- [ ] test_comb_lip x1: TPU comb lip test (spare labbro_pettine_v62); TPU 95A yellow; plate TPU-0; `stl/test_comb_lip_print.stl`

## Changes from the v6.2 package

- Totals: PETG 1047 g -> 1000 g, TPU 8.0 g -> 8.0 g, time 41 h 14 min -> 39 h 30 min, plates 9 -> 9, colour swaps 33 -> 18.
- Removed: the cable channel (2 bases, 2 covers, 1 end cap) and the 3 thumb-turns.
- Gate blade: now green only, and it moved to the green plate.
- Changed parts: the bowl (PT pilots, P3 insert moved), the tower (P3 pillar moved), the box (PT bosses instead of cups), the cap (PT counterbores, control panel, second drain), both flange plates (dowel hole, press-fit pins, tie window, raised tunnel), the ring (teardrop window), the grommet and the latch (print orientation).
- Print orientations: the v6.3 CAD print files now carry the corrections made in print_v62 (no pin and a dowel hole on the lower plate, the latch on its back, the grommet lip down). They were verified here and used as they are. No support enforcers are needed any more: the box needs no support, and the ring window is a teardrop.

## Deviations and notes

- **6.3.0 CAD fixes, checked here**:
  - Lower flange dowel seat: closed all round (wall at 100 % around the d4 hole), so it is a normal press fit now.
  - Cap seam ring: joined to the cap, with a 45 deg chamfer underneath. The old 2.5 mm flat ledge is gone; about 84 mm2 of small flat bits remain. The slicer reports no warning.
  - LED light pipe seats: squared to the panel face.
  - The raw cap STL has 4 zero-area slivers. The package's mesh clean removes them, so the cap is one watertight solid in all files.
- **linguetta_sicura_v63** now comes on its back from the CAD (geometry unchanged).
- **Plain 3MF files** carry no settings. Use the Bambu projects, or apply the settings above by hand.
- The Bambu projects are generated by a script in the Bambu Studio project format (metadata `BambuStudio-02.05.00.00`). The settings come from the Bambu system profiles (BambuStudio master, resources/profiles/BBL, profile version 02.09.00.74, fetched 2026-11-09). Every plate was opened and sliced with the OrcaSlicer 2.5.0 command line, but not in Bambu Studio itself. After opening in Bambu Studio, check the plate list and the filament mapping, and slice once.
- Times and grams come from the OrcaSlicer estimator with the A1 profiles. Bambu Studio may differ by 5 to 10 %.

