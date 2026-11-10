# Kibble Dispenser Outdoor v6.2 - print guide (Bambu Lab A1 + AMS lite)

Everything you need to print the v6.2 dispenser on a Bambu Lab A1 with the AMS lite: two ready Bambu Studio projects, plain 3MF files for any slicer, single STL files in print orientation, the recommended settings and a check list of every printed part.

**Design v6.2: designed and checked in CAD, not printed or tested yet.** These files are the authoritative print set of v6.2: they correct several CAD print orientations and replace the printed pivot pin of the lower flange with a 4 x 6 stainless dowel (see Deviations). Print the test pieces first. Website version, in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/print/>

Kit note (v62.json kit_split): the kit ships the dispenser unit pre-assembled (bowl, drive tower, chute, electronics box, shell, cap, plates, disc) plus a separate flange assembly and the cable channel. DIY builders print every part, so this package includes them all. The parts marked "kit module" are the factory modules inside the unit (drive tower, electronics box).

## Files

- `Kibble_Dispenser_v62_PETG.bambu.3mf`: Bambu Studio project with all PETG plates (1 test plate and 6 part plates). The parts are placed and oriented. Multicolour parts are single objects with their colour parts assigned to AMS slots. Per-part settings (walls, infill, supports, brim, layer height, IP66 settings for the box and the cap, support enforcers under the box C cup and the ring window) are stored on each object, and the A1 printer, process and filament presets are set.
- `Kibble_Dispenser_v62_TPU.bambu.3mf`: Bambu Studio project with the TPU plates (1 test plate and all seals), for the external spool.
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
  - slot 4: optional second spool of PETG black as an automatic backup (enable "Filament backup/auto refill"). Black is about 81 % of all PETG. Without a second spool, leave slot 4 empty.
- External spool holder: TPU 95A yellow. TPU cannot go through the AMS lite. In the print dialog, map the filament to "External spool".
- Profiles: "Generic PETG @BBL A1" and "Generic TPU @BBL A1". If you use a branded filament, pick its own profile.

## Plates

Print the test plates first, then plates 01 to 06, then the TPU plate. Times and grams are slicer estimates that include supports, the prime tower and filament flushing.

### PETG-0: 00 TEST - spline + rim, cap and skirt grooves

Project `Kibble_Dispenser_v62_PETG.bambu.3mf`, plate 1. Plain file `plates/PETG-0_spline__rim_cap_and_skirt_grooves.3mf`. Preview `preview/PETG-0_top.png` and `preview/PETG-0_iso.png`.

- Purpose: print first: spline clearance for mozzo_v6; groove coupons for the TPU test strips.
- Parts:
  - test_scanalato x1 (Spline fit test (3 coupons); PETG black)
  - test_groove_rim x1 (Bowl rim groove coupon (30 mm cut of chiocciola_v62); PETG black)
  - test_groove_cap x1 (Cap upstand groove coupon (20 mm cut of fondello_v62); PETG black)
  - test_groove_skirt x1 (Flange skirt groove coupon (30 mm cut of flangia_piano_v62); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 0 h 31 min, PETG black 6.9 g; colour swaps: 0.

### PETG-1: 01 BLACK - pod shell + electronics box

Project `Kibble_Dispenser_v62_PETG.bambu.3mf`, plate 2. Plain file `plates/PETG-1_pod_shell__electronics_box.3mf`. Preview `preview/PETG-1_top.png` and `preview/PETG-1_iso.png`.

- Purpose: single colour (black); shell with brim; box with the IP66 settings and one support enforcer (C cup).
- Parts:
  - guscio_v611 x1 (Pod shell; PETG black)
  - scatola_v62 x1 (Electronics box (stack-screw ear + countersinks); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 9 h 35 min, PETG black 263 g (of which support 3.2 g); colour swaps: 0.

### PETG-2: 02 BLACK - bowl + pod cap

Project `Kibble_Dispenser_v62_PETG.bambu.3mf`, plate 3. Plain file `plates/PETG-2_bowl__pod_cap.3mf`. Preview `preview/PETG-2_top.png` and `preview/PETG-2_iso.png`.

- Purpose: single colour (black); bowl lugs and cap bottom edge on bed-only supports.
- Parts:
  - chiocciola_v62 x1 (Bowl (inserts at P1..P3); PETG black)
  - fondello_v62 x1 (Pod cap (dishes d24); PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 10 h 26 min, PETG black 296 g (of which support 12.7 g); colour swaps: 0.

### PETG-3: 03 BLACK - lower flange + cable channel

Project `Kibble_Dispenser_v62_PETG.bambu.3mf`, plate 4. Plain file `plates/PETG-3_lower_flange__cable_channel.3mf`. Preview `preview/PETG-3_top.png` and `preview/PETG-3_iso.png`.

- Purpose: single colour (black); the lower flange plate (pivot pin as a dowel) and all cable-channel parts.
- Parts:
  - flangia_piano_v62 x1 (Lower flange plate (pivot pin as dowel); PETG black)
  - canalina_base_v62 x2 (Cable channel base; PETG black)
  - canalina_coperchio_v62 x2 (Cable channel cover; PETG black)
  - canalina_tappo_v62 x1 (Cable channel end cap; PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 4 h 09 min, PETG black 116 g; colour swaps: 0.

### PETG-4: 04 BLACK - upper flange + tower + shaft + hub

Project `Kibble_Dispenser_v62_PETG.bambu.3mf`, plate 5. Plain file `plates/PETG-4_upper_flange__tower__shaft__hub.3mf`. Preview `preview/PETG-4_top.png` and `preview/PETG-4_iso.png`.

- Purpose: single colour (black); the shaft at 0.15 mm layers needs a plate without prime tower.
- Parts:
  - flangia_alta_v62 x1 (Upper flange plate; PETG black)
  - colonna_v62 x1 (Tower (3 pillars for the M3x40 stack); PETG black)
  - albero_v6 x1 (Shaft; PETG black)
  - mozzo_v6 x1 (Servo hub; PETG black)
- Filament: AMS lite slot 1 = PETG black.
- Estimate: 5 h 43 min, PETG black 126 g; colour swaps: 0.

### PETG-5: 05 GREEN+black - chute + collar + gate + window plates

Project `Kibble_Dispenser_v62_PETG.bambu.3mf`, plate 6. Plain file `plates/PETG-5_chute__collar__gate__window_plates.3mf`. Preview `preview/PETG-5_top.png` and `preview/PETG-5_iso.png`.

- Purpose: food path: green parts + the two 3 mm plates (black body, green bands).
- Parts:
  - scivolo_v611 x1 (Chute; PETG green)
  - colletto_v6 x1 (Funnel collar; PETG green)
  - piastra_finestra_v62 x1 (Window plate (common lip grooves); PETG black + green)
  - piastra_gate_v62 x1 (Gate plate (common lip grooves); PETG black + green)
- Filament: AMS lite slot 1 = PETG black; AMS lite slot 3 = PETG green.
- Estimate: 3 h 47 min, PETG black 37 g (of which prime tower 0.8 g, flush 1.3 g); PETG green 46 g (of which prime tower 0.5 g, flush 3.7 g); colour swaps: 15.
- Prime tower at X 158, Y 23 (stored in the project).

### PETG-6: 06 ORANGE+green+black - interlock ring + disc + gate blade + latch + button + 3 thumb-turns

Project `Kibble_Dispenser_v62_PETG.bambu.3mf`, plate 7. Plain file `plates/PETG-6_interlock_ring__disc__gate_blade__latch__button__3_thumb_turns.3mf`. Preview `preview/PETG-6_top.png` and `preview/PETG-6_iso.png`.

- Purpose: orange parts; the disc prints inside the ring; the gate blade (green, orange arm) adds swaps in its 15 layers.
- Parts:
  - anello_saracinesca_v62 x1 (Interlock ring; PETG orange)
  - disco_v61 x1 (Dosing disc (self-cleaning); PETG orange + black)
  - saracinesca_v62 x1 (Gate blade (sector); PETG green + orange)
  - linguetta_sicura x1 (Safety latch; PETG orange)
  - pulsante_v611 x1 (Latch push-button; PETG orange)
  - nottolino_v611 x3 (Flush thumb-turn (keyed); PETG orange)
- Filament: AMS lite slot 1 = PETG black; AMS lite slot 2 = PETG orange; AMS lite slot 3 = PETG green.
- Estimate: 5 h 39 min, PETG black 2.7 g (of which support 0.1 g, prime tower 0.1 g, flush 0.3 g); PETG orange 132 g (of which support 1.4 g, prime tower 1.0 g, flush 3.8 g); PETG green 21 g (of which support 0.1 g, prime tower 0.5 g, flush 2.4 g); colour swaps: 18.
- Prime tower at X 198, Y 20 (stored in the project).

### TPU-0: 00 TEST - rim, cap, skirt and comb lips

Project `Kibble_Dispenser_v62_TPU.bambu.3mf`, plate 1. Plain file `plates/TPU-0_rim_cap_skirt_and_comb_lips.3mf`. Preview `preview/TPU-0_top.png` and `preview/TPU-0_iso.png`.

- Purpose: print first: the thin TPU flaps (0.5 rim, 0.5 skirt, comb slits, cap lip).
- Parts:
  - test_rim_lip x1 (TPU rim lip seal test arc (30 mm); TPU 95A yellow)
  - test_cap_lip x1 (TPU cap lip seal test strip (20 mm); TPU 95A yellow)
  - test_skirt_lip x1 (TPU skirt lip test arc (30 mm); TPU 95A yellow)
  - test_comb_lip x1 (TPU comb lip test (spare labbro_pettine_v62); TPU 95A yellow)
- Filament: external spool = TPU yellow.
- Estimate: 0 h 12 min, TPU yellow 0.5 g; colour swaps: 0.

### TPU-1: 01 TPU 95A - all seals

Project `Kibble_Dispenser_v62_TPU.bambu.3mf`, plate 2. Plain file `plates/TPU-1_all_seals.3mf`. Preview `preview/TPU-1_top.png` and `preview/TPU-1_iso.png`.

- Purpose: all 10 TPU pieces, external spool.
- Parts:
  - labbro_ombra_v611 x1 (Skirt lip ring; TPU 95A yellow)
  - guarnizione_baionetta_v61 x1 (Rim lip seal; TPU 95A yellow)
  - guarnizione_piano_v5 x1 (Flange-shelf gasket ring; TPU 95A yellow)
  - labbro_scivolo_v611 x1 (Chute lip ring; TPU 95A yellow)
  - guarnizione_fondello_v61 x1 (Cap lip seal (D outline); TPU 95A yellow)
  - labbro_pettine_v62 x4 (Comb lip (common, x4); TPU 95A yellow)
  - passacavo_v62 x1 (Cable tunnel grommet; TPU 95A yellow)
- Filament: external spool = TPU yellow.
- Estimate: 1 h 08 min, TPU yellow 7.5 g; colour swaps: 0.

### Totals

- PETG black: 848 g
- PETG green: 66 g
- PETG orange: 132 g
- TPU yellow: 8.0 g
- All PETG: 1047 g. All TPU 95A: 8.0 g.
- Print time: 41 h 14 min over 9 plates (test plates included). Colour swaps: 33 in total.

### Why the plates are grouped like this

- A part has one body colour through its whole height, so the plates follow the body colour: black (01, 02, 03), green (04) and orange (05). The multicolour parts add swaps only in their 3 inlay layers.
- Black needs four plates: the shell (164 mm), the cap (143), both flange plates (180) and the box (81 x 96) do not pair up. Pairs that fit are shell + box and bowl + cap (both diagonal, about 6 mm apart, with relaxed 4 mm bed margins), lower flange + cable channel, and upper flange + tower/shaft/hub.
- Plate 04 has a single colour and no prime tower, so the shaft (albero_v6) can use its own 0.15 mm layers there.
- Plate 05 puts the two 3 mm plates (black with green bands) on the green plate.
- Plate 06: the disc prints inside the 176 mm interlock ring. The gate blade (saracinesca_v62) is green with an orange arm through all 15 layers: two colours on every layer wherever it goes, so it sits with the other orange parts.
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
  - fondello_v62 (cap) and scatola_v62 (box): IP66 settings, see below.
  - chiocciola_v62 (bowl): 3 walls, 15 %. Supports: tree, on build plate only (3 bayonet lugs).
  - flangia_piano_v62 (lower flange plate): 3 walls, 25 %, shelf-side face on the bed, no supports. The pivot pin is printed as a 4.0 mm hole for a steel dowel (see Deviations).
  - flangia_alta_v62 (upper flange plate): 3 walls, 25 %, shelf face on the bed, no supports. The 1.5 mm cable groove bridges about 7 mm.
  - anello_saracinesca_v62 (interlock ring, orange): on its bottom edge, 4 walls, 15 %, 5 mm outer brim. The d28 window top is a 28 mm bridge, so a small support stands on the window sill (support enforcer, manual normal support).
  - saracinesca_v62 (gate blade): flat, 3 walls, 100 % infill (3 mm blade).
  - colonna_v62 (tower): upright, 4 walls, 100 % infill: the three pillars carry the M3x40 preload.
  - canalina_base_v62 x2 (wood face on the bed), canalina_coperchio_v62 x2 (open side up), canalina_tappo_v62 (on its side): 3 walls, 15 %.
  - scivolo_v611 (chute): 5 walls, 15 %, no supports. disco_v61, piastra_gate_v62, piastra_finestra_v62, colletto_v6: 3 walls, 15 %, no supports.
  - albero_v6 (shaft): 100 %, 0.15 mm layers, 5 mm brim. mozzo_v6, pulsante_v611, nottolino_v611 x3, linguetta_sicura: 100 % infill, 4 walls (linguetta lies on its back with a small bed-only support under the spring tab).

### IP66 settings: box and cap (as v6.1.1, v611.json ip_rating)

- 5 walls at 0.42 mm line width (at least 4 walls fill a 2.0 mm wall solid), 100 % infill, 5 top and 5 bottom layers, seam at the back.
- Object flow ratio 1.03 (+3 %, inside the +2 to 5 % range), stored as print_flow_ratio on the two objects.
- Box: top surfaces ironed (the rim face prints as a top surface and carries the cap lip).
- Box support: manual mode with one support enforcer, so support is generated only under the far half of the C cup ring (x > 21). It is normal (straight) support standing on the inside of the roof; in v6.1.1 tree support sent a trunk through the M12 vent hole down to the bed. The stack-screw ear prints on the bed, and the two roof countersinks (for the O-rings 3x1) face up.
- Cap: a bed-only support ring (normal supports, threshold 45 deg) under the lowest ~5 mm of the R15 bottom edge, as in v6.1.
- Filament settings for these two plates (set them by hand in the filament profile): nozzle 245 to 250 C, part fan 40 % or less, for layer bonding.
- After printing:
  - clear the 4 drain holes (d 0.8 mm) in the cap with a 0.8 mm drill; first-layer squish can close them;
  - hold the empty box against a bright light in a dark room: pinholes glow;
  - the gland pad is a vertical face and cannot be ironed: check it is flat where the gland O-ring seats.

### TPU 95A

- Profile Generic TPU @BBL A1: nozzle 240 C, bed 45 C on Textured PEI, fan 100 %, max volumetric speed 3.2 mm3/s, retraction 0.4 mm. Dry the TPU (65 C, 6 h) right before printing.
- All TPU parts use 100 % infill and 2 walls, 0.20 mm layers.
- Thin flaps use the Arachne wall generator at 15 mm/s so that each flap prints as one clean line: guarnizione_baionetta_v61 (0.5 mm), labbro_ombra_v611 (skirt, 0.5 mm, 20 deg cone), labbro_scivolo_v611 (chute, 0.6 mm) and the 4 comb lips (0.8 mm, 0.7 mm slits). guarnizione_fondello_v61 prints its walls at 20 mm/s.

## Print these test pieces first

1. PETG-0 (black): `test_scanalato`, `test_groove_rim`, `test_groove_cap` and `test_groove_skirt`.
   - test_scanalato: 3 spline coupons (1, 2 or 3 notches for 0.05, 0.10 or 0.20 mm). mozzo_v6 is built with 0.10 mm. If another coupon fits better, change SPL_CLEAR in parts/build_drivetrain.py, rebuild mozzo_v6 and run tools/run_all.sh.
   - The groove coupons are cuts of the bowl rim (chiocciola_v62), the cap D upstand (fondello_v62) and the lower flange edge (flangia_piano_v62, skirt-lip groove).
2. TPU-0 (external spool): `test_rim_lip`, `test_cap_lip`, `test_skirt_lip` and `test_comb_lip` (a spare labbro_pettine_v62).
   - Press each strip into its groove coupon. The anchor should seat fully, and the flap should be one clean, closed line that springs back.
   - On the comb lip, the slits must be open.
3. After printing:
   - check the seam O-ring 132x2 squeeze (light drag over the last 2 mm);
   - check the P3 stack-screw head clearance to the cradle and the board (0.375 mm, open risk in v62.json);
   - tighten the M3x40 to 0.4 N m and re-check after a week (PETG creep).
4. Hose-test the closed pod before you put electronics inside.

## Bought parts (not printed)

Not on any plate. New in v6.2: 3 x M3x40 stack screws (they replace 3 x M3x12 and 3 x M3x10), 2 x O-ring 3x1 under the P2/P3 heads, the M8 IP67 connector pair with a 5 mm PUR cable, 3 x ST2.9x9.5 flange join screws, 4 x wood screw 3.5x16 for the cable channel, wood screws 5x35 instead of 5x25, and 12 heat-set inserts instead of 15. This package adds one 4 x 6 stainless dowel pin (see Deviations).

- 4 x wood screw 5x35 pan head (5x30 for an 18 mm shelf): flange -> shelf (flange 8 mm thicker in v6.2) (v62.json)
- 2 x M3x10 DIN912 A2: chute ears -> bowl nose inserts, from below (factory) (v61.json)
- 3 x M3x12 DIN912 A2: shell tabs -> bowl base inserts, from below (factory) (v61.json)
- 4 x M3x8 DIN912 A2 + washer: servo -> cradle inserts (factory) (v61.json)
- 1 x M3x8 DIN912 A2: hub -> servo spline (factory) (v61.json)
- 12 x M3 heat-set insert RX-M3x5.7: 8 in the bowl (3 at P1..P3 for the stack, 2 chute, 3 shell tabs), 4 servo in the box (no plateau inserts) (v62.json)
- 2 x O-ring NBR70 9x2: shaft (tower module, greased for life at the factory) (v61.json)
- 1 x O-ring NBR70 24x2: tower <-> box face seal (factory) (v61.json)
- 3 x O-ring NBR70 8x1.5: one per thumb-turn (v611.json)
- 1 x M12x1.5 cable gland IP68 (cable 4-7 mm) + locknut: box -Y wall, inside the pod (v61.json)
- 1 x M12x1.5 screw-in ePTFE membrane vent IP68 + locknut (e.g. GORE PolyVent / Amphenol LTW VENT-PS1 class): box roof, pointing up under the bowl (the highest, most sheltered point of the dry volume): pressure + humidity balance, replaces the silica bag (v61.json)
- 1 x M8 A-coded 4-pin IP67 inline pair + PUR 4x0.34 d5 cable: replaces the generic inline connector + d6 cable (v62.json)
- 1 x food-grade silicone grease NSF H1: FACTORY ONLY: shaft O-rings, face O-ring, thumb-turn O-ring; the user never greases anything (v61.json)
- 1 x 70 x 50 perfboard (ESP32 board on female headers, 2 regulators, 1000 uF, JST/screw terminals): replaces the 165 mm breadboard of the bench prototype (cannot fit a pod); slides up into slots, parts face the shell (v61.json)
- 3 x parallel key DIN 6885 B 3x3x18, stainless A4 (or 3x3 stainless square bar cut to 18): pressed through the thumb-turn shaft above the cap boss: captive + bears on the cup ledges (v611.json)
- 1 x O-ring NBR70 132x2: shell | cap seam, in the cap spigot groove (stretch 3.1 %, squeeze 15 %) (v611.json)
- 1 x O-ring NBR70 14x1.5: latch push-button, in the shell bore groove (v611.json)
- 3 x M3x40 DIN912 A2: box + tower + bowl stack, from below (P1 ear, P2/P3 through the roof) (v62.json)
- 2 x O-ring NBR70 3x1: under the P2/P3 stack-screw heads in the roof countersinks (v62.json)
- 3 x ST2.9x9.5 DIN 7982 countersunk: join the two flange plates from the shelf face (v62.json)
- 4 x wood screw 3.5x16 countersunk: cable channel bases (v62.json)
- 1 x dowel pin ISO 2338 4 m6 x 6, stainless: blade pivot in the lower flange plate (replaces the printed pin: print_v62 deviation, designer to confirm) (print_v62)

## Check list: all printed parts

v6.2 has 22 PETG parts (26 pieces) and 10 TPU pieces, plus 8 test pieces.

- [ ] guscio_v611 x1: Pod shell; PETG black; plate PETG-1; `stl/guscio_v611_print.stl`
- [ ] fondello_v62 x1: Pod cap (dishes d24); PETG black; plate PETG-2; `stl/fondello_v62_print.stl`
- [ ] chiocciola_v62 x1: Bowl (inserts at P1..P3); PETG black; plate PETG-2; `stl/chiocciola_v62_print.stl`
- [ ] flangia_piano_v62 x1: Lower flange plate (pivot pin as dowel); PETG black; plate PETG-3; `stl/flangia_piano_v62_print.stl`
- [ ] flangia_alta_v62 x1: Upper flange plate; PETG black; plate PETG-4; `stl/flangia_alta_v62_print.stl`
- [ ] canalina_base_v62 x2: Cable channel base; PETG black; plate PETG-3; `stl/canalina_base_v62_print.stl`
- [ ] canalina_coperchio_v62 x2: Cable channel cover; PETG black; plate PETG-3; `stl/canalina_coperchio_v62_print.stl`
- [ ] canalina_tappo_v62 x1: Cable channel end cap; PETG black; plate PETG-3; `stl/canalina_tappo_v62_print.stl`
- [ ] disco_v61 x1: Dosing disc (self-cleaning); PETG orange + black; plate PETG-6; `stl/disco_v61_print.stl`
- [ ] piastra_gate_v62 x1: Gate plate (common lip grooves); PETG black + green; plate PETG-5; `stl/piastra_gate_v62_print.stl`
- [ ] piastra_finestra_v62 x1: Window plate (common lip grooves); PETG black + green; plate PETG-5; `stl/piastra_finestra_v62_print.stl`
- [ ] saracinesca_v62 x1: Gate blade (sector); PETG green + orange; plate PETG-6; `stl/saracinesca_v62_print.stl`
- [ ] anello_saracinesca_v62 x1: Interlock ring; PETG orange; plate PETG-6; `stl/anello_saracinesca_v62_print.stl`
- [ ] scivolo_v611 x1: Chute; PETG green; plate PETG-5; `stl/scivolo_v611_print.stl`
- [ ] colletto_v6 x1: Funnel collar; PETG green; plate PETG-5; `stl/colletto_v6_print.stl`
- [ ] linguetta_sicura x1: Safety latch; PETG orange; plate PETG-6; `stl/linguetta_sicura_print.stl`
- [ ] pulsante_v611 x1: Latch push-button; PETG orange; plate PETG-6; `stl/pulsante_v611_print.stl`
- [ ] nottolino_v611 x3: Flush thumb-turn (keyed); PETG orange; plate PETG-6; `stl/nottolino_v611_print.stl`
- [ ] colonna_v62 x1: Tower (3 pillars for the M3x40 stack); PETG black; plate PETG-4; `stl/colonna_v62_print.stl` - kit module: drive tower
- [ ] albero_v6 x1: Shaft; PETG black; plate PETG-4; `stl/albero_v6_print.stl` - kit module: drive tower
- [ ] mozzo_v6 x1: Servo hub; PETG black; plate PETG-4; `stl/mozzo_v6_print.stl` - kit module: electronics box (hub on the servo)
- [ ] scatola_v62 x1: Electronics box (stack-screw ear + countersinks); PETG black; plate PETG-1; `stl/scatola_v62_print.stl` - kit module: electronics box
- [ ] labbro_pettine_v62 x4: Comb lip (common, x4); TPU 95A yellow; plate TPU-1; `stl/labbro_pettine_v62_print.stl`
- [ ] guarnizione_baionetta_v61 x1: Rim lip seal; TPU 95A yellow; plate TPU-1; `stl/guarnizione_baionetta_v61_print.stl`
- [ ] guarnizione_fondello_v61 x1: Cap lip seal (D outline); TPU 95A yellow; plate TPU-1; `stl/guarnizione_fondello_v61_print.stl`
- [ ] guarnizione_piano_v5 x1: Flange-shelf gasket ring; TPU 95A yellow; plate TPU-1; `stl/guarnizione_piano_v5_print.stl`
- [ ] labbro_ombra_v611 x1: Skirt lip ring; TPU 95A yellow; plate TPU-1; `stl/labbro_ombra_v611_print.stl`
- [ ] labbro_scivolo_v611 x1: Chute lip ring; TPU 95A yellow; plate TPU-1; `stl/labbro_scivolo_v611_print.stl`
- [ ] passacavo_v62 x1: Cable tunnel grommet; TPU 95A yellow; plate TPU-1; `stl/passacavo_v62_print.stl`
- [ ] test_scanalato x1: Spline fit test (3 coupons); PETG black; plate PETG-0; `stl/test_scanalato_print.stl`
- [ ] test_groove_rim x1: Bowl rim groove coupon (30 mm cut of chiocciola_v62); PETG black; plate PETG-0; `stl/test_groove_rim_print.stl`
- [ ] test_groove_cap x1: Cap upstand groove coupon (20 mm cut of fondello_v62); PETG black; plate PETG-0; `stl/test_groove_cap_print.stl`
- [ ] test_groove_skirt x1: Flange skirt groove coupon (30 mm cut of flangia_piano_v62); PETG black; plate PETG-0; `stl/test_groove_skirt_print.stl`
- [ ] test_rim_lip x1: TPU rim lip seal test arc (30 mm); TPU 95A yellow; plate TPU-0; `stl/test_rim_lip_print.stl`
- [ ] test_cap_lip x1: TPU cap lip seal test strip (20 mm); TPU 95A yellow; plate TPU-0; `stl/test_cap_lip_print.stl`
- [ ] test_skirt_lip x1: TPU skirt lip test arc (30 mm); TPU 95A yellow; plate TPU-0; `stl/test_skirt_lip_print.stl`
- [ ] test_comb_lip x1: TPU comb lip test (spare labbro_pettine_v62); TPU 95A yellow; plate TPU-0; `stl/test_comb_lip_print.stl`

## Changes from the v6.1.1 package

- Totals: PETG 814 g -> 1047 g, TPU 9.2 g -> 8.0 g, time 33 h 42 min -> 41 h 14 min, plates 8 -> 9, colour swaps 18 -> 33.
- New parts:
  - upper flange plate (flangia_alta_v62);
  - green gate blade with an orange arm (saracinesca_v62) and orange interlock ring (anello_saracinesca_v62);
  - cable channel: 2 bases, 2 covers and an end cap, black;
  - cable tunnel grommet (passacavo_v62, TPU);
  - one common comb lip printed 4 times (labbro_pettine_v62), replacing the 4 different v6.1 lips.
- Changed: the bowl (insert positions), the tower (3 pillars for the M3x40 stack), the box (stack-screw ear and countersinks, vent moved), the cap (dishes d24), the lower flange plate, and the gate and window plates (common lip grooves).
- Plates: one more black plate (the second flange plate). The orange plate carries the d176 ring with the disc inside it and the gate blade.

## Deviations and notes

- **flangia_piano_v62 pivot pin (designer to confirm)**: the CAD print file lays the plate shelf-side face down, but the d4 x 3.3 mm blade pivot pin stands on that face, so the whole plate would float 3.3 mm above the bed on the pin (22 400 mm2 of overhang). Printed the other way up, the skirt and the skirt-lip groove would need support instead. This package cuts the pin off and prints a d4.0 x 2.7 mm blind hole at the centre for a pressed-in ISO 2338 4 m6 x 6 stainless dowel. That leaves the same 3.3 mm stand-up, and the dowel is listed in the bought parts. The unmodified CAD file is in `stl/flangia_piano_v62_print_cad_original.stl`.
- **CAD print orientations corrected** to match the v62.json print notes, with less overhang in each case:
  - canalina_base_v62 flipped, wood face on the bed;
  - canalina_coperchio_v62 open side up;
  - canalina_tappo_v62 on its other side (1.9 instead of 115 mm2 of overhang);
  - passacavo_v62 lip on the bed.
- **Interlock ring window**: the 28 mm window bridge gets a small support from the window sill, through a support enforcer in manual mode. A chamfer on the window top in the CAD would remove the need for it.
- **Box support**: as in v6.1.1, support only under the far half of the C cup, normal instead of tree.
- **linguetta_sicura** lies on its back, as its print note says (the reused print STL is upright).
- **Plain 3MF files** carry no settings, modifiers or enforcers. Use the Bambu projects, or apply the settings above by hand.
- The Bambu projects are generated by a script in the Bambu Studio project format (metadata `BambuStudio-02.05.00.00`). The settings come from the Bambu system profiles (BambuStudio master, resources/profiles/BBL, profile version 02.09.00.74, fetched 2026-11-09). Every plate was opened and sliced with the OrcaSlicer 2.5.0 command line, but not in Bambu Studio itself. After opening in Bambu Studio, check the plate list and the filament mapping, and slice once.
- Times and grams come from the OrcaSlicer estimator with the A1 profiles. Bambu Studio may differ by 5 to 10 %.

