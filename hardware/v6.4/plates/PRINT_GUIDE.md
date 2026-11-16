# Kibble Dispenser Outdoor 6.4 - print procedure (Bambu Lab A1 + AMS lite)

Follow the steps in order. Each step is one plate: what to load, what to check in the slicer, the supports, the time and the filament, what to look at on the finished parts, and the work to do on them before assembly.

Hardware 6.4 is two products:

- **Chassis 6.4**: the dispenser itself with the servo bay and the holder for the electronics module.
- **Electronics module, case 1.0**: a sealed case (tub, lid, speaker ring, lid gasket) that slides into the chassis from below. It has its own files, so you can print it again later without touching the chassis.

Every plate and every part is marked **UNCHANGED since 6.3.0**, **CHANGED in 6.4** or **NEW in 6.4**.

## If you already started with the 6.3 package (print_v63)

The 21 unchanged part files are byte-identical to 6.3.0, and their plates here have the same parts at the same positions with the same settings. Parts you already printed from print_v63 stay valid.

- Keep: everything from print_v63 plates PETG-3, PETG-4, PETG-5 and PETG-6, the bowl from PETG-2, the test pieces from PETG-0 and TPU-0, and all seals from TPU-1 except the cap lip seal.
- Throw away (obsolete 6.3 parts): the shell guscio_v611 and the electronics box scatola_v63 (print_v63 PETG-1), the cap fondello_v63 (print_v63 PETG-2) and the cap lip seal guarnizione_fondello_v61 (print_v63 TPU-1).
- Still to print: PETG-1, PETG-7, TPU-2, MOD-1, MOD-2. That is 19 h 18 min of printing, 470 g of PETG and 2.2 g of TPU.
- In the steps below, skip a plate marked UNCHANGED when you already have its parts.

Slicer check of "same as print_v63" (grams, time and layers of the sliced plate):
- PETG-0: identical to print_v63 PETG-0 (6.9 g, 32 min, 60 layers).
- PETG-2: same positions as print_v63 PETG-2, with the obsolete 6.3 part removed (304 g -> 158 g, 666 -> 348 min).
- PETG-3: identical to print_v63 PETG-3 (128 g, 352 min, 536 layers).
- PETG-4: identical to print_v63 PETG-4 (90 g, 182 min, 54 layers).
- PETG-5: identical to print_v63 PETG-5 (101 g, 262 min, 407 layers).
- PETG-6: identical to print_v63 PETG-6 (122 g, 250 min, 222 layers).
- TPU-0: identical to print_v63 TPU-0 (0.5 g, 12 min, 26 layers).
- TPU-1: same positions as print_v63 TPU-1, with the obsolete 6.3 part removed (7.5 g -> 6.3 g, 68 -> 59 min).

## Files

Chassis:
- `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`: plates PETG-0 to PETG-6 (plate numbers as in print_v63). Three colours from the AMS lite.
- `Kibble_Dispenser_v64_chassis_IP66_PETG.bambu.3mf`: plate PETG-7, the two sealed chassis parts (servo bay, cap), black, with low-fan filament settings stored in the project.
- `Kibble_Dispenser_v64_chassis_TPU.bambu.3mf`: TPU-0 (test), TPU-1 (unchanged seals), TPU-2 (the two 6.4 seals).

Electronics module, case 1.0:
- `Kibble_Module_case_1.0_PETG.bambu.3mf`: MOD-1 (tub and speaker ring), MOD-2 (lid), black, low-fan filament settings.
- `Kibble_Module_case_1.0_TPU.bambu.3mf`: MOD-TPU-1, the lid gasket alone. Use it only when you reprint the module later: the same gasket is already on chassis plate TPU-2.

Also in this folder:
- `plates/*.3mf`: one plain 3MF per plate for other slicers. They carry no settings, supports or enforcers: set them by hand from the steps below.
- `stl/*_print.stl`: every part alone in print orientation. Two-colour parts also come as colour bodies.
- `preview/<plate>_top.png` and `<plate>_iso.png`: pictures of each plate. `summary.json`: all numbers as data. `layout.json`: part positions. `slice_check/`: slicer statistics. `tools/`: the scripts that made all of this (`tools/run_all.sh`).

## Step 0: before the first print

1. Filament. You need about:
   - PETG black: 892 g
   - PETG green: 64 g
   - PETG orange: 120 g
   - TPU yellow: 9.0 g
   - That is 1076 g of PETG and 9.0 g of TPU for everything, test plates included. Black is 83 % of the PETG, so keep a second black spool ready.
2. Dry the filament. PETG from an open spool: 65 C for 6 to 8 hours. TPU: 65 to 70 C for 6 to 8 hours right before printing, every time. Wet TPU makes strings and bubbles and the thin sealing lips fail.
3. Load the AMS lite: slot 1 PETG black, slot 2 PETG orange, slot 3 PETG green, slot 4 the spare PETG black. In the AMS settings turn on "Filament backup" so slot 4 takes over when slot 1 runs out.
4. TPU does not go through the AMS lite. For the TPU plates, feed it from the external spool holder and choose "External spool" in the print dialog.
5. Build plate: Textured PEI. Wash it with dish soap and warm water, dry it, and do not touch the surface. Bed 80 C for PETG, 45 C for TPU (set by the profiles).
6. Open a project in Bambu Studio. Check: printer "Bambu Lab A1 0.4 nozzle", plate type "Textured PEI Plate", process "0.20mm Standard @BBL A1", and the filament colours in the right slots. Slice the plate once and look at the preview before you send it.
7. Keep "Bed levelling" and "Flow dynamics calibration" ticked in the print dialog.
8. Tools for the work after printing: flush cutters, long-nose pliers, a deburring knife, drills 1.5, 2.0, 5.1 and 8.2 mm (turned by hand), a soldering iron with an M3 insert tip, a small vice or hammer, a steel rule, calipers.

Colour language: black is structure, orange is a touch point, green is the food path, yellow TPU is a seal.

## Step 1: test coupons (PETG-0, then TPU-0)

### Step 1a - PETG-0: 00 TEST - spline + rim, cap and skirt grooves [UNCHANGED since 6.3.0]

- File: `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`, plate 1. Other slicers: `plates/PETG-0_spline__rim_cap_and_skirt_grooves.3mf`. Picture: `preview/PETG-0_top.png`.
- Parts on the plate:
  - test_scanalato x1: Spline fit test (3 coupons) (PETG black; unchanged since 6.3.0)
  - test_groove_rim x1: Bowl rim groove coupon (30 mm cut of chiocciola_v63) (PETG black; unchanged since 6.3.0)
  - test_groove_cap x1: Cap upstand groove coupon (20 mm cut of fondello_v64) (PETG black; unchanged since 6.3.0)
  - test_groove_skirt x1: Flange skirt groove coupon (30 mm cut of flangia_piano_v63) (PETG black; unchanged since 6.3.0)
- Time and filament: 0 h 31 min; PETG black 6.9 g; colour swaps: 0.
- Load: PETG black in AMS slot 1. Supports: none. Nothing to change in the settings.
- How to judge the spline test (test_scanalato, 3 coupons with 1, 2 or 3 notches = 0.05, 0.10, 0.20 mm clearance):
  - Push each coupon onto the servo output spline by hand.
  - The right one goes on with firm thumb pressure, has no play when you twist it, and comes off again by hand.
  - The hub (mozzo_v6) is built like the coupon with 2 notches. If 2 notches fits, go on.
  - If only the coupon with 1 or 3 notches fits, stop before PETG-3 and ask for a hub with that clearance (SPL_CLEAR in parts/build_drivetrain.py).
- How to judge the three groove coupons (bowl rim, cap upstand, flange skirt):
  - The grooves are open and clean down to the bottom, with no blobs.
  - Measure the cap coupon wall with calipers: it should be 4.4 mm thick. More than 4.6 mm means too much flow: run the flow calibration for this filament before the sealed parts.
  - Keep the coupons for step 1b.
- Status note: same coupons as print_v63 PETG-0 (the cap coupon is now cut from the 6.4 cap: same groove section, same size). If you printed and judged the 6.3 test plate, do not print it again.

### Step 1b - TPU-0: 00 TEST - rim, cap, skirt and comb lips [UNCHANGED since 6.3.0]

- File: `Kibble_Dispenser_v64_chassis_TPU.bambu.3mf`, plate 1. Other slicers: `plates/TPU-0_rim_cap_skirt_and_comb_lips.3mf`. Picture: `preview/TPU-0_top.png`.
- Parts on the plate:
  - test_rim_lip x1: TPU rim lip seal test arc (30 mm) (TPU 95A yellow; unchanged since 6.3.0)
  - test_cap_lip x1: TPU cap lip seal test strip (20 mm) (TPU 95A yellow; unchanged since 6.3.0)
  - test_skirt_lip x1: TPU skirt lip test arc (30 mm) (TPU 95A yellow; unchanged since 6.3.0)
  - test_comb_lip x1: TPU comb lip test (spare labbro_pettine_v62) (TPU 95A yellow; unchanged since 6.3.0)
- Time and filament: 0 h 12 min; TPU yellow 0.5 g; colour swaps: 0.
- Load: dried TPU 95A on the external spool. Supports: none.
- How to judge:
  - Each flap is one clean, continuous line: no gaps, no blobs, no hairs. It springs back when you bend it flat.
  - Press each strip into its groove coupon with your thumb (rim lip into the rim coupon, cap lip into the cap coupon, skirt lip into the skirt coupon). The foot seats fully and stays in when you turn the coupon upside down.
  - If a foot will not go in or falls out, do not print the big PETG parts yet: report which strip and which coupon.
  - Comb lip: all slits are open. A sheet of paper passes through each slit.
  - Strings between the parts or a rough, bubbly surface mean wet TPU. Dry it again and repeat this plate.
- Status note: same strips as print_v63 TPU-0 (the cap strip is cut from the 6.4 seal: same section, same size).

## Steps 2 to 13: the plates

### Step 2 - PETG-1: pod shell 6.4 [chassis; CHANGED in 6.4]

Status note: replaces print_v63 PETG-1 (shell 6.1.1 + electronics box 6.3): both of those parts are obsolete.

- File: `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`, plate 2. Other slicers: `plates/PETG-1_pod_shell_6_4.3mf`. Picture: `preview/PETG-1_top.png`.
- Parts on the plate:
  - guscio_v64 x1: Pod shell (module opening, return ribs) (PETG black; changed in 6.4)
- Time and filament: 5 h 50 min; PETG black 162 g (of which support 5.8 g); colour swaps: 0.
- Load: PETG black in AMS slot 1.
- Check in the slicer before printing:
  - Object guscio_v64: 5 walls, 15 % infill, outer brim 6 mm.
  - Support: enabled, type "tree (manual)", "On build plate only" ticked, threshold angle 45. The object holds three small "support enforcer" boxes, one under each bowl tab.
  - After slicing, the preview must show exactly three support trees. They stand on the plate inside the shell and end under the three tabs at Z 64 mm. Nothing else has support (the button boss and the ribs print without).
  - If your slicer shows no trees: set the support type to "tree (auto)", keep "On build plate only" and 45 degrees, and slice again.
- Supports: Tree, from the build plate only, 45 degrees, under the inner 12 mm of the three bowl tabs. The outer part of each tab rests on its own 45 degree corbel.
- Look at the finished parts:
  - The underside of the three tabs is flat and closed (this face sits on the bowl).
  - The module opening (the big notch in the wall): the cut edges are blunt, not feathered. A slightly rough start of the two return ribs is normal.
  - The round bore for the latch button and its O-ring groove are clean.
- Work after printing:
  - Break the three support trees out with pliers and scrape the tab faces flat.
  - Peel the brim off and deburr that edge with a knife (it is a visible edge).

### Step 3 - PETG-2: bowl [chassis; UNCHANGED since 6.3.0]

Status note: the bowl at its print_v63 position; print_v63 PETG-2 also held the 6.3 cap, which is obsolete: if you printed that plate, keep the bowl and do not print this plate.

- File: `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`, plate 3. Other slicers: `plates/PETG-2_bowl.3mf`. Picture: `preview/PETG-2_top.png`.
- Parts on the plate:
  - chiocciola_v63 x1: Bowl (PT pilots, P3 insert moved) (PETG black; unchanged since 6.3.0)
- Time and filament: 5 h 48 min; PETG black 158 g (of which support 5.8 g); colour swaps: 0.
- Load: PETG black in AMS slot 1.
- Check in the slicer before printing:
  - Object chiocciola_v63: 3 walls, 15 % infill.
  - Support: "tree (auto)", "On build plate only" ticked.
- Supports: Tree, from the build plate only, under the 3 bayonet lugs.
- Look at the finished parts:
  - The rim groove (3.0 x 2.2 mm) is clean all round: the rim lip seal goes there.
  - The three bayonet lugs are solid and their undersides are closed.
- Work after printing:
  - Remove the supports under the lugs.
  - Melt 3 M3 heat-set inserts into the three stack holes (P1, P2, P3). Soldering iron at 230 to 240 C, push straight, stop flush or 0.2 mm below the surface, let it cool before you touch it.
  - Do not drill the small 2.5 mm holes for the chute ears and the shell tabs: they are pilots for the PT screws.

### Step 4 - PETG-3: lower flange + tower + shaft + hub [chassis; UNCHANGED since 6.3.0]

- File: `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`, plate 4. Other slicers: `plates/PETG-3_lower_flange__tower__shaft__hub.3mf`. Picture: `preview/PETG-3_top.png`.
- Parts on the plate:
  - flangia_piano_v63 x1: Lower flange plate (dowel hole) (PETG black; unchanged since 6.3.0)
  - colonna_v63 x1: Tower (3 pillars) (PETG black; unchanged since 6.3.0)
  - albero_v6 x1: Shaft (PETG black; unchanged since 6.3.0)
  - mozzo_v6 x1: Servo hub (PETG black; unchanged since 6.3.0)
- Time and filament: 5 h 52 min; PETG black 128 g; colour swaps: 0.
- Load: PETG black in AMS slot 1.
- Check in the slicer before printing:
  - Lower flange plate: 3 walls, 25 % infill. Tower: 4 walls, 100 % infill. Hub: 4 walls, 100 % infill.
  - Shaft (albero_v6): layer height 0.15 mm, 100 % infill, 5 mm brim. This is why the plate has no prime tower.
- Supports: None.
- Look at the finished parts:
  - Lower flange plate: flat (lay it on a table), the skirt groove is clean, the 4.0 mm dowel hole is round.
  - Shaft: both O-ring grooves are clean, the hex and the spline are sharp.
  - Hub: it fits the servo spline like the coupon you chose in step 1.
- Work after printing:
  - Press the 4 x 6 mm steel dowel into the 4.0 x 2.7 mm hole of the lower flange plate. Use a vice or light hammer taps, keep it square. It must stand 3.3 mm proud.
  - Peel the brim off the shaft and deburr its foot.

### Step 5 - PETG-4: upper flange [chassis; UNCHANGED since 6.3.0]

- File: `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`, plate 5. Other slicers: `plates/PETG-4_upper_flange.3mf`. Picture: `preview/PETG-4_top.png`.
- Parts on the plate:
  - flangia_alta_v63 x1: Upper flange plate (3 press-fit pins, tie window) (PETG black; unchanged since 6.3.0)
- Time and filament: 3 h 01 min; PETG black 90 g; colour swaps: 0.
- Load: PETG black in AMS slot 1.
- Check in the slicer before printing:
  - Upper flange plate: 3 walls, 25 % infill.
- Supports: None.
- Look at the finished parts:
  - The plate is flat. The three press-fit pins are round and not stringy.
  - The cable-tie window is open.
- Work after printing:
  - Test the three pins in the holes of the lower plate: they must go in with firm hand pressure. Do not press them home yet.
  - If a corner of this 180 mm plate lifted, print it again with an outer brim of 5 mm on the object (it prints alone, so the brim fits).

### Step 6 - PETG-5: chute + collar + gate blade + gate + window plates [chassis; UNCHANGED since 6.3.0]

- File: `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`, plate 6. Other slicers: `plates/PETG-5_chute__collar__gate_blade__gate__window_plates.3mf`. Picture: `preview/PETG-5_top.png`.
- Parts on the plate:
  - scivolo_v611 x1: Chute (PETG green; unchanged since 6.3.0)
  - colletto_v6 x1: Funnel collar (PETG green; unchanged since 6.3.0)
  - saracinesca_v63 x1: Gate blade (one colour) (PETG green; unchanged since 6.3.0)
  - piastra_finestra_v62 x1: Window plate (PETG black + green; unchanged since 6.3.0)
  - piastra_gate_v62 x1: Gate plate (PETG black + green; unchanged since 6.3.0)
- Time and filament: 4 h 21 min; PETG black 37 g (of which prime tower 0.8 g, flush 1.3 g); PETG green 64 g (of which prime tower 0.5 g, flush 3.7 g); colour swaps: 15.
- Prime tower at X 204, Y 77.
- Load: PETG black in slot 1 and PETG green in slot 3.
- Check in the slicer before printing:
  - Prime tower enabled (position stored in the project).
  - Chute: 5 walls, 15 %. Gate blade: 100 % infill, green only. Collar and the two plates: 3 walls, 15 %.
- Supports: None.
- Look at the finished parts:
  - The green bands on the gate plate (OUT, top side) and the window plate (FOOD IN, bed side) are readable.
  - The gate blade is flat and slides freely on the gate plate.
  - Collar: the two small 3 x 3 mm pads are attached (in the model they sit 0.1 mm above the body). If one comes off, fix it with a drop of cyanoacrylate glue.
- Work after printing:
  - Throw the prime tower away. No drilling.

### Step 7 - PETG-6: interlock ring + disc + latch + button [chassis; UNCHANGED since 6.3.0]

- File: `Kibble_Dispenser_v64_chassis_PETG.bambu.3mf`, plate 7. Other slicers: `plates/PETG-6_interlock_ring__disc__latch__button.3mf`. Picture: `preview/PETG-6_top.png`.
- Parts on the plate:
  - anello_saracinesca_v63 x1: Interlock ring (teardrop window) (PETG orange; unchanged since 6.3.0)
  - disco_v61 x1: Dosing disc (self-cleaning) (PETG orange + black; unchanged since 6.3.0)
  - linguetta_sicura_v63 x1: Safety latch (PETG orange; unchanged since 6.3.0)
  - pulsante_v611 x1: Latch push-button (PETG orange; unchanged since 6.3.0)
- Time and filament: 4 h 09 min; PETG black 2.2 g (of which prime tower 0.2 g, flush 0.3 g); PETG orange 120 g (of which support 0.1 g, prime tower 0.2 g, flush 1.1 g); colour swaps: 3.
- Prime tower at X 193, Y 195.
- Load: PETG black in slot 1 and PETG orange in slot 2.
- Check in the slicer before printing:
  - Prime tower enabled. Interlock ring: 4 walls, 15 %, outer brim 5 mm. Disc: 3 walls, 15 %. Latch and button: 100 % infill.
  - Latch (linguetta_sicura_v63): support "normal (auto)", "On build plate only".
- Supports: A small bed-only support under the spring tab of the latch. Nothing else.
- Look at the finished parts:
  - The disc label (black, bed side) is readable. The disc pockets are clean.
  - The teardrop window of the ring is open and its top is closed without sagging strings.
  - The spring tab of the latch flexes and springs back.
- Work after printing:
  - Peel the brim off the ring. Remove the small support under the latch tab.

### Step 8 - PETG-7: servo bay + pod cap 6.4 [chassis; CHANGED in 6.4]

Status note: replaces the electronics box of print_v63 PETG-1 and the cap of print_v63 PETG-2.

- File: `Kibble_Dispenser_v64_chassis_IP66_PETG.bambu.3mf`, plate 1. Other slicers: `plates/PETG-7_servo_bay__pod_cap_6_4.3mf`. Picture: `preview/PETG-7_top.png`.
- Parts on the plate:
  - scatola_v64 x1: Servo bay + module holder posts (PETG black; changed in 6.4)
  - fondello_v64 x1: Pod cap (module opening, 4 PT screws) (PETG black; changed in 6.4)
- Time and filament: 7 h 59 min; PETG black 200 g; colour swaps: 0.
- Load: PETG black in AMS slot 1. This project has its own filament settings (see the first check).
- Check in the slicer before printing:
  - Filament: "Generic PETG @BBL A1" shown as modified. Part cooling fan: minimum 20 %, maximum 40 %; overhang fan threshold 25 %. Nozzle 255 C. Leave these as they are. With a branded PETG, pick its profile and set the same fan values.
  - Both objects: 5 walls, line width 0.42 mm, 100 % infill, 5 top and 5 bottom layers, seam "back", flow ratio 1.03.
  - Servo bay (scatola_v64): ironing "top surfaces". Cap (fondello_v64): elephant foot compensation 0.15 mm.
  - Support: off for both objects.
- Supports: None. The slicer gives no warning for this plate (the 6.4 CAD fixes for the bay posts, the harness lug, the C-hook and the cap bottom edge work).
- Look at the finished parts:
  - Servo bay: the two holder posts are straight and solid from the roof to their ends. They carry the electronics module.
  - Servo bay: the rim face (ironed, on top while printing) is smooth and closed all round. The cap lip seals on it.
  - Servo bay: hold it against a bright lamp in a dark room. No light may shine through the walls.
  - Servo bay: the pad around the 12 mm cable-gland hole is flat (lay a steel rule on it).
  - Servo bay: the small lug bar beside cap boss D (for the harness cable tie) and the C-hook on top of the south post (3.8 mm slit) are complete and not cracked.
  - Cap: the bottom edge (45 degree chamfer, then the radius) is smooth with no curled layers.
  - Cap: the lip-seal groove (2.2 x 1.15 mm) on the upstand is clean.
  - Cap: inside the round well, the 1.5 mm ring that holds the chute lip prints as a short overhang at Z 29.3 mm (its inner edge is now a 45 degree chamfer). A slightly rough underside there is normal; scrape off any loose strings so the lip seats.
- Work after printing:
  - Cap: push a 1.5 mm drill by hand through the 2 drain holes. Check the three 0.8 mm slits next to them with a blade.
  - Servo bay: melt 4 M3 inserts into the servo cradle and 2 into the ends of the two holder posts (4.0 x 6.5 mm holes; the post ends point up as printed). 230 to 240 C, straight, flush. Hold the post while it cools so it stays straight.
  - Servo bay: clear the 2 mm vent hole with a 2 mm drill and stick the ePTFE vent patch over it (clean, dry surface).
  - Servo bay: try the M12 gland in its hole and file the top of the hole if it is tight. Check that the harness tail (d4.5) snaps into the C-hook and that a 2.5 mm cable tie passes round the lug bar.
  - Do not drill the screw holes in the bay bosses: they are 2.5 mm pilots for the PT K30x12 cap screws.

### Step 9 - TPU-1: seals unchanged since 6.3.0 [chassis; UNCHANGED since 6.3.0]

Status note: print_v63 TPU-1 without the 6.1 cap lip seal (obsolete); all other pieces at their print_v63 positions. If you printed print_v63 TPU-1, do not print this plate.

- File: `Kibble_Dispenser_v64_chassis_TPU.bambu.3mf`, plate 2. Other slicers: `plates/TPU-1_seals_unchanged_since_6_3_0.3mf`. Picture: `preview/TPU-1_top.png`.
- Parts on the plate:
  - labbro_ombra_v611 x1: Skirt lip ring (TPU 95A yellow; unchanged since 6.3.0)
  - guarnizione_baionetta_v61 x1: Rim lip seal (TPU 95A yellow; unchanged since 6.3.0)
  - guarnizione_piano_v5 x1: Flange-shelf gasket ring (TPU 95A yellow; unchanged since 6.3.0)
  - labbro_scivolo_v611 x1: Chute lip ring (TPU 95A yellow; unchanged since 6.3.0)
  - labbro_pettine_v62 x4: Comb lip (common, x4) (TPU 95A yellow; unchanged since 6.3.0)
  - passacavo_v63 x1: Cable tunnel grommet (raised tunnel) (TPU 95A yellow; unchanged since 6.3.0)
- Time and filament: 0 h 58 min; TPU yellow 6.3 g; colour swaps: 0.
- Load: TPU 95A on the external spool holder. In the print dialog choose "External spool" (the AMS lite cannot feed TPU).
- Check in the slicer before printing:
  - Filament "Generic TPU @BBL A1". All parts: 2 walls, 100 % infill.
  - Thin lips (rim seal, skirt lip, chute lip, 4 comb lips): wall generator "Arachne", wall speed 15 mm/s.
- Supports: None.
- Look at the finished parts:
  - Every flap is one continuous line with no gaps or blobs, and it springs back when you bend it.
  - The slits of the 4 comb lips are open.
  - Strings and bubbles mean wet TPU: dry it again and reprint.
- Work after printing:
  - Trim strings with scissors. Do not pull on the flaps.

### Step 10 - TPU-2: 6.4 seals: cap lip seal + module gasket [chassis; CHANGED in 6.4]

- File: `Kibble_Dispenser_v64_chassis_TPU.bambu.3mf`, plate 3. Other slicers: `plates/TPU-2_6_4_seals.3mf`. Picture: `preview/TPU-2_top.png`.
- Parts on the plate:
  - guarnizione_fondello_v64 x1: Cap lip seal (smaller bay outline) (TPU 95A yellow; changed in 6.4)
  - modulo_guarnizione_v64 x1: Module lid lip gasket (TPU 95A yellow; new in 6.4)
- Time and filament: 0 h 26 min; TPU yellow 2.2 g; colour swaps: 0.
- Load: TPU 95A on the external spool holder ("External spool").
- Check in the slicer before printing:
  - Cap lip seal (guarnizione_fondello_v64): 2 walls, 100 %, wall speed 20 mm/s.
  - Module gasket (modulo_guarnizione_v64): wall generator "Arachne", wall speed 15 mm/s.
- Supports: None.
- Look at the finished parts:
  - Both rings are closed loops with a clean, continuous lip.
  - The cap lip seal presses into the groove of the cap upstand and stays there.
  - The module gasket presses into the groove on the underside of the module lid (a light press fit).
- Work after printing:
  - Trim strings with scissors.

The chassis is now complete. The next steps are the electronics module.

### Step 11 - MOD-1: module tub + speaker ring [module case 1.0; NEW in 6.4]

- File: `Kibble_Module_case_1.0_PETG.bambu.3mf`, plate 1. Other slicers: `plates/MOD-1_module_tub__speaker_ring.3mf`. Picture: `preview/MOD-1_top.png`.
- Parts on the plate:
  - modulo_vasca_v64 x1: Module tub (outer skin, control panel, board slots) (PETG black; new in 6.4)
  - modulo_anello_speaker_v64 x1: Speaker ring (for a d23 speaker) (PETG black; new in 6.4)
- Time and filament: 4 h 10 min; PETG black 91 g (of which support 0.5 g); colour swaps: 0.
- Load: PETG black in AMS slot 1. This project has the same low-fan filament settings as the sealed chassis parts.
- Check in the slicer before printing:
  - Filament: "Generic PETG @BBL A1" shown as modified. Fan minimum 20 %, maximum 40 %, overhang fan threshold 25 %, nozzle 255 C.
  - Tub (modulo_vasca_v64): 5 walls, line width 0.42 mm, 100 % infill, seam "back", flow ratio 1.03, elephant foot compensation 0.15 mm.
  - Tub support: enabled, type "normal (manual)", "On build plate only" not ticked, threshold 45. The object holds 2 small "support enforcer" boxes at the button recess and 2 mouse ears (thin discs, part of the object) at the back corners.
  - After slicing, the preview shows exactly two thin support columns. They stand on the plate just outside the panel face and end at Z 21.5 mm under the two upper corners of the 17 mm button recess. Nothing else has support.
  - Speaker ring: 3 walls, 100 % infill. It may be any colour (it sits inside the sealed module).
- Supports: Two thin columns (about 0.5 g) under the two upper corners of the button recess, where the recess rim meets the leaning skin and starts in free air. The bottom edge, the rim and the 5 lid-screw bosses need none (45 degree faces; the bosses grow on corbels from the wall).
- Look at the finished parts:
  - Lay a steel rule on the flat back wall (2 mm thick, 104 x 67 mm). A bow of more than about 0.3 mm will close the 0.35 mm seam to the cap: print again, drier filament and no draught.
  - The top face of the tub rim (the land) is smooth and unbroken all round. The lid gasket seals on it.
  - The 5 bosses and their corbels are solid and the 2.5 mm pilot holes are open.
  - Hold the tub against a bright lamp in a dark room: no light through the walls. The three knock-out marks stay closed.
  - Slide a 50 x 70 mm perfboard into slot A from the top. It must go down to the floor of the slot without force.
  - The two round sockets at the back corners (10 mm) slide onto the 9 mm posts of the servo bay.
- Work after printing:
  - Break the two support columns off the button recess and scrape both corners clean (the button gasket seats in the recess).
  - Cut the two mouse ears off flush and restore the small 0.4 mm chamfer on the bottom back edge with a knife.
  - Ream the two light-pipe holes with a 5.1 mm drill by hand (horizontal holes sag at the top).
  - Clear the 7 speaker grille holes in the floor with a 1.5 mm drill.
  - Check that the 12 mm push-button fits its 17 mm recess. Do not drill the 5 boss holes (PT K30x10 pilots).
  - Before electronics go in: close the module (gasket, lid, 5 screws with O-rings, button, light pipes, J1 socket) and hose it. About 105 mm of the gasket along the back edge has no screw, so this water test is required.

### Step 12 - MOD-2: module lid [module case 1.0; NEW in 6.4]

- File: `Kibble_Module_case_1.0_PETG.bambu.3mf`, plate 2. Other slicers: `plates/MOD-2_module_lid.3mf`. Picture: `preview/MOD-2_top.png`.
- Parts on the plate:
  - modulo_coperchio_v64 x1: Module lid (J1 turret, gasket groove) (PETG black; new in 6.4)
- Time and filament: 0 h 51 min; PETG black 17 g; colour swaps: 0.
- Load: PETG black in AMS slot 1 (same project, plate 2).
- Check in the slicer before printing:
  - Before you print: take the M8 5-pin panel socket you bought. Measure its thread and its nut. The lid is made for a hole of 8.2 mm and a nut up to 13 mm across flats (bore 16.5 mm). If your socket differs, stop and ask for a changed lid.
  - Lid: 5 walls, line width 0.42 mm, 100 % infill, seam "back", flow ratio 1.03. Support: off.
- Supports: None. The J1 hole is closed on top by a skin of one layer (0.2 mm) so the turret roof prints as a 13 mm bridge.
- Look at the finished parts:
  - The gasket groove on the underside is clean. Its outer wall is only 1.2 mm thick: handle it with care.
  - The turret roof is closed and flat on the inside (this is the nut seat).
  - The ribs and the back fence on the top face are complete (the harness loop lies between the fence and the turret).
- Work after printing:
  - Drill the skin of the J1 hole: push an 8.2 mm drill by hand from the underside through the existing hole (the hole guides the drill). Use the thread size of your socket if it differs. Deburr the nut seat.
  - Leave the USB-C mark on the top closed.
  - For a development module that will be opened often: melt 5 M3 inserts into the tub bosses instead of using PT screws.

### Step 13 - MOD-TPU-1: module gasket [module case 1.0; NEW in 6.4] - only when the module is reprinted alone

Skip this step if you printed TPU-2: the module gasket is on that plate too.

- File: `Kibble_Module_case_1.0_TPU.bambu.3mf`, plate 1. Other slicers: `plates/MOD-TPU-1_module_gasket.3mf`. Picture: `preview/MOD-TPU-1_top.png`.
- Parts on the plate:
  - modulo_guarnizione_v64 x1: Module lid lip gasket (TPU 95A yellow; new in 6.4)
- Time and filament: 0 h 18 min; TPU yellow 1.2 g; colour swaps: 0.
- Load: TPU 95A on the external spool holder ("External spool").
- Check in the slicer before printing:
  - Wall generator "Arachne", wall speed 15 mm/s, 2 walls, 100 % infill.
- Supports: None.
- Look at the finished parts:
  - A closed loop with a clean, continuous lip.
- Work after printing:
  - Trim strings with scissors.

## Step 14: final checks before assembly

1. Tick every part in the check list below.
2. Press the rim lip seal into the bowl groove, the skirt lip into the lower flange plate and the cap lip seal into the cap. Each must seat all round.
3. Push the cap onto the servo bay without screws: the cap lip touches the bay rim all round.
4. Slide the empty module up into the chassis: it moves freely, the two sockets find the posts over the last 18 mm, and the seams to the cap and the shell are even (0.35 mm). Hold the module when it leaves the posts on the way out.
5. Drive each PT screw by hand (about 0.6 N m) and open each PT joint at most 5 times. Tighten the M3x40 stack screws to 0.4 N m and the two M3x16 module screws to 0.5 N m.
6. Hose-test the closed servo bay with the cap, and the closed module, before electronics go inside.

## Totals

- Chassis (PETG-0 to PETG-7, TPU-0, TPU-1): 38 h 45 min, PETG 968 g, TPU 6.8 g, 10 plates, 18 colour swaps.
- Module case 1.0 (MOD-1, MOD-2): 5 h 01 min, PETG 108 g, TPU 0.0 g, 2 plates, 0 colour swaps.
- Shared plate TPU-2 (cap lip seal + module gasket): 0 h 26 min, TPU 2.2 g.
- Everything: 44 h 13 min over 13 plates, PETG 1076 g, TPU 9.0 g, 18 colour swaps.
- Module reprinted alone later (MOD-1, MOD-2, MOD-TPU-1): 5 h 20 min, 109 g.
- Times and grams are slicer estimates. They include supports, the prime tower and flushing.

## Check list: all printed parts

Chassis: 18 PETG parts (18 pieces) and 10 TPU pieces. Module: 3 PETG pieces and 1 TPU piece. Plus 8 test pieces.

### Chassis

- [ ] guscio_v64 x1: Pod shell (module opening, return ribs); PETG black; plate PETG-1 [changed in 6.4]
- [ ] scatola_v64 x1: Servo bay + module holder posts; PETG black; plate PETG-7 [changed in 6.4]; sub-assembly: servo bay
- [ ] fondello_v64 x1: Pod cap (module opening, 4 PT screws); PETG black; plate PETG-7 [changed in 6.4]
- [ ] guarnizione_fondello_v64 x1: Cap lip seal (smaller bay outline); TPU 95A yellow; plate TPU-2 [changed in 6.4]
- [ ] chiocciola_v63 x1: Bowl (PT pilots, P3 insert moved); PETG black; plate PETG-2 [unchanged since 6.3.0]
- [ ] flangia_piano_v63 x1: Lower flange plate (dowel hole); PETG black; plate PETG-3 [unchanged since 6.3.0]
- [ ] flangia_alta_v63 x1: Upper flange plate (3 press-fit pins, tie window); PETG black; plate PETG-4 [unchanged since 6.3.0]
- [ ] colonna_v63 x1: Tower (3 pillars); PETG black; plate PETG-3 [unchanged since 6.3.0]; sub-assembly: drive tower
- [ ] albero_v6 x1: Shaft; PETG black; plate PETG-3 [unchanged since 6.3.0]; sub-assembly: drive tower
- [ ] mozzo_v6 x1: Servo hub; PETG black; plate PETG-3 [unchanged since 6.3.0]; sub-assembly: servo bay (hub on the servo)
- [ ] piastra_gate_v62 x1: Gate plate; PETG black + green; plate PETG-5 [unchanged since 6.3.0]
- [ ] piastra_finestra_v62 x1: Window plate; PETG black + green; plate PETG-5 [unchanged since 6.3.0]
- [ ] saracinesca_v63 x1: Gate blade (one colour); PETG green; plate PETG-5 [unchanged since 6.3.0]
- [ ] scivolo_v611 x1: Chute; PETG green; plate PETG-5 [unchanged since 6.3.0]
- [ ] colletto_v6 x1: Funnel collar; PETG green; plate PETG-5 [unchanged since 6.3.0]
- [ ] disco_v61 x1: Dosing disc (self-cleaning); PETG orange + black; plate PETG-6 [unchanged since 6.3.0]
- [ ] anello_saracinesca_v63 x1: Interlock ring (teardrop window); PETG orange; plate PETG-6 [unchanged since 6.3.0]
- [ ] linguetta_sicura_v63 x1: Safety latch; PETG orange; plate PETG-6 [unchanged since 6.3.0]
- [ ] pulsante_v611 x1: Latch push-button; PETG orange; plate PETG-6 [unchanged since 6.3.0]
- [ ] labbro_pettine_v62 x4: Comb lip (common, x4); TPU 95A yellow; plate TPU-1 [unchanged since 6.3.0]
- [ ] guarnizione_baionetta_v61 x1: Rim lip seal; TPU 95A yellow; plate TPU-1 [unchanged since 6.3.0]
- [ ] guarnizione_piano_v5 x1: Flange-shelf gasket ring; TPU 95A yellow; plate TPU-1 [unchanged since 6.3.0]
- [ ] labbro_ombra_v611 x1: Skirt lip ring; TPU 95A yellow; plate TPU-1 [unchanged since 6.3.0]
- [ ] labbro_scivolo_v611 x1: Chute lip ring; TPU 95A yellow; plate TPU-1 [unchanged since 6.3.0]
- [ ] passacavo_v63 x1: Cable tunnel grommet (raised tunnel); TPU 95A yellow; plate TPU-1 [unchanged since 6.3.0]

### Electronics module, case 1.0

- [ ] modulo_vasca_v64 x1: Module tub (outer skin, control panel, board slots); PETG black; plate MOD-1 [new in 6.4]
- [ ] modulo_coperchio_v64 x1: Module lid (J1 turret, gasket groove); PETG black; plate MOD-2 [new in 6.4]
- [ ] modulo_anello_speaker_v64 x1: Speaker ring (for a d23 speaker); PETG black; plate MOD-1 [new in 6.4]
- [ ] modulo_guarnizione_v64 x1: Module lid lip gasket; TPU 95A yellow; plate TPU-2, MOD-TPU-1 [new in 6.4]

### Test pieces

- [ ] test_scanalato x1: Spline fit test (3 coupons); PETG black; plate PETG-0
- [ ] test_groove_rim x1: Bowl rim groove coupon (30 mm cut of chiocciola_v63); PETG black; plate PETG-0
- [ ] test_groove_cap x1: Cap upstand groove coupon (20 mm cut of fondello_v64); PETG black; plate PETG-0
- [ ] test_groove_skirt x1: Flange skirt groove coupon (30 mm cut of flangia_piano_v63); PETG black; plate PETG-0
- [ ] test_rim_lip x1: TPU rim lip seal test arc (30 mm); TPU 95A yellow; plate TPU-0
- [ ] test_cap_lip x1: TPU cap lip seal test strip (20 mm); TPU 95A yellow; plate TPU-0
- [ ] test_skirt_lip x1: TPU skirt lip test arc (30 mm); TPU 95A yellow; plate TPU-0
- [ ] test_comb_lip x1: TPU comb lip test (spare labbro_pettine_v62); TPU 95A yellow; plate TPU-0

## Bought parts (not printed)

### Chassis

- [ ] 1 x dowel pin ISO 2338 4 m6 x 6, stainless: gate blade pivot, pressed into the lower flange plate
- [ ] 4 x wood screw 5x35 pan head (5x30 for an 18 mm shelf): flange set -> shelf (they also clamp the cable jacket)
- [ ] 9 x M3 heat-set insert RX-M3x5.7: 3 in the bowl (stack screws P1..P3), 4 in the servo cradle of the bay, 2 in the lower ends of the holder posts (module lock)
- [ ] 3 x M3x40 DIN912 A2: servo bay + tower + bowl stack, from below
- [ ] 1 x O-ring NBR70 3x1: under the P2 stack-screw head (the only stack screw inside the bay)
- [ ] 4 x EJOT PT K30x12 thread-forming screw, Torx T10: cap -> bay bosses, from below
- [ ] 4 x O-ring NBR70 3x1: under the four cap screw heads
- [ ] 3 x EJOT PT K30x12 thread-forming screw: shell tabs -> bowl (d2.5 pilots, no inserts)
- [ ] 2 x EJOT PT K30x10 thread-forming screw: chute ears -> bowl (d2.5 pilots, no inserts)
- [ ] 4 x M3x8 DIN912 A2 + washer: servo -> cradle inserts
- [ ] 1 x M3x8 DIN912 A2: hub -> servo spline
- [ ] 2 x O-ring NBR70 9x2: shaft (tower module)
- [ ] 1 x O-ring NBR70 24x2: tower <-> bay face seal
- [ ] 1 x O-ring NBR70 14x1.5: latch push-button, in the shell bore groove
- [ ] 1 x M12x1.5 cable gland IP68, cable range 3 to 6.5 mm, + locknut: bay south wall; seals on the round servo branch of the harness (dome nut 2.5 N m)
- [ ] 1 x adhesive ePTFE vent patch d12: servo bay vent (d2 hole)
- [ ] 1 x M8 A-coded 4-pin IP67 inline connector pair: unit pigtail <-> supply cable, in the pod top (as 6.3)
- [ ] 1 x M8 5-pin A-coded MALE cordset, angled, PUR d4.5, ready-made 0.5 m (cut to a 190 mm tail, plug body to splice centre): harness tail: plugs into J1 on the module lid; service loop parked on the lid; lets the module down 120 mm
- [ ] 1 x round 3-core PUR cable 3 x 0.25 mm2, d4.0, 100 mm: harness servo branch: splice -> M12 gland -> 12 mm inside the bay (40 mm spare)
- [ ] 1 x JR/Futaba 3-pin servo housing, female, 2.54 mm + 3 female crimp terminals for 22-26 AWG: crimped on the servo branch inside the bay after it passes the gland (signal, +6 V, GND); the servo plugs into it
- [ ] 1 x 2-core PUR cable 90 mm (or the pigtail of an M8 4-pin A-coded male field connector): harness 12 V branch: splice -> pod-top M8 IP67 pair
- [ ] 1 x adhesive-lined heat shrink d8 x 20 mm: over the soldered Y splice (tail 1 -> 12 V +, 3 -> GND both, 2 -> servo signal, 4 -> servo +6 V, 5 not connected)
- [ ] 1 x cable tie 2.5 x 100: harness tail anchored round the lug bar of the servo bay
- [ ] 1 x 12 V supply cable PUR 4x0.34 d5: runs through the flange tunnel
- [ ] 1 x cable tie 3.6 x 140, UV-stable PA66: strain relief, cinched in the upper plate window
- [ ] 1 x standard servo (25T spline): drive, in the servo bay
- [ ] 1 x food-grade silicone grease NSF H1: O-rings

### Electronics module, case 1.0

- [ ] 2 x M3x16 ISO 4762 A2 (hex 2.5): module lock, from below into the post inserts, 0.5 N m; they stay with the module
- [ ] 5 x EJOT PT K30x10 thread-forming screw: lid -> tub bosses (or melt M3 inserts into the 5 bosses for a development module)
- [ ] 5 x O-ring NBR70 3x1: under the five lid screw heads
- [ ] 1 x M8 5-pin A-coded panel socket (female), front mount: J1 in the lid turret; thread and nut size (10 to 13 mm AF assumed) TO VERIFY before printing or drilling the lid
- [ ] 1 x IP67 12 mm momentary push-button, short body: control panel, d17 recess
- [ ] 2 x panel light pipe d5 (clear PC) + O-ring NBR70 5x1 each: status and Wi-Fi LEDs
- [ ] 2 x LED 3 mm (status green, Wi-Fi blue) + series resistors on the board: behind the light pipes
- [ ] 1 x IP67 adhesive acoustic membrane, ePTFE, d15: inside, over the 7 x d1.5 speaker grille in the tub floor
- [ ] 1 x speaker d23 (d20 to d24 with a matching ring): in the printed speaker ring on the tub floor
- [ ] 1 x 50 x 70 perfboard + ESP32-WROVER dev board on socket strips + 6 V servo regulator + 5 V logic regulator + 1000 uF capacitor: electronics (demo layout of v64.json; the case is generic)

Changes from 6.3: 9 heat-set inserts instead of 7 (2 new in the holder posts). 4 cap screws with O-rings instead of 3. One O-ring 3x1 on the stack (P2 only). No seam O-ring 132x2. An adhesive vent patch instead of the M12 vent. A chassis harness made from a cut M8 5-pin angled cordset, a round 3-core servo branch through the M12 gland with a JR female crimped on inside the bay (the servo and its flat lead are not cut), a 2-core 12 V branch, heat shrink over the splice and a 2.5 mm cable tie. The panel parts, the speaker and the electronics now belong to the module.

Harness (lengths from v64.json interface.electrical_J1.harness):
- Tail: cut the M8 5-pin male angled cordset to 190 mm from the plug body (cable exit) to the centre of the splice.
- Servo branch: 100 mm of round 3-core cable from the splice through the gland; 12 mm inside the bay plus 40 mm spare so the JR pair can be pulled out under the bay with the cap off. Pass the stripped cable through dome nut, seal and gland body from outside, then crimp the 3 terminals (open-barrel crimper) and push them into the JR housing: signal, +6 V, GND. Tighten the dome nut to 2.5 N m.
- 12 V branch: 90 mm from the splice up the inside of the shell to the pod-top M8 pair.
- Splice: tail pin 1 to 12 V +, pin 3 to 12 V GND and servo GND, pin 2 to servo signal, pin 4 to servo +6 V, pin 5 not connected. Solder, cover with the d8 x 20 adhesive heat shrink.
- Tie the tail round the lug bar of the servo bay (2.5 x 100 tie) and snap it into the C-hook on the south post. With the module in, the service loop lies on the lid between the back fence and the turret.

## Notes and deviations

- **Module tub**: the first 6.4 package needed 5 support columns under the lid-screw bosses. In the final 6.4.0 CAD the bosses grow from the wall on 45 degree corbels and those 5 enforcers are gone. With support off the slicer still reports "floating regions": the cause is the two upper corners of the 17 mm button recess, where the recess rim meets the leaning outer skin at print Z 21.5 mm (checked by slicing the tub in bands: below Z 20 and above Z 23 there is no warning). This package supports those two corners only. A CAD change (a 45 degree or teardrop top on the recess rim) would remove them.
- **Sealed parts, filament settings**: v64.json asks for 245 to 250 C and a fan of 40 % or less. The Generic PETG profile already prints at 255 C, so the nozzle stays there. The fan is limited to 20 to 40 %. Bridges and overhangs steeper than about 28 degrees still get the profile overhang fan (90 %): the threshold was raised from 10 % to 25 % so the leaning outer skin of the tub prints with the low fan.
- **Speaker ring colour**: the viewer shows it orange. It is inside the sealed module, so this package prints it black with the tub.
- **Flange plates (unchanged plates PETG-3 and PETG-4)**: the reviewer could not rule out warping of the two 180 mm plates on an open printer. Their plates are kept exactly as in print_v63 (no brim). If a corner lifts, add an outer brim of 5 mm to that object.
- **Mouse ears and brims**: shell 6 mm brim, interlock ring 5 mm brim, shaft 5 mm brim, tub 2 mouse ears. Nothing else has one.
- **Test coupons**: the cap groove coupon and the cap lip strip are cut from the 6.4 parts. Their section and size are the same as in 6.3.
- **Plain 3MF files** carry no settings, supports or enforcers (the tub mouse ears are in them as geometry).
- The Bambu projects are generated by a script in the Bambu Studio project format (metadata `BambuStudio-02.05.00.00`). The settings come from the Bambu system profiles (BambuStudio master, resources/profiles/BBL, profile version 02.09.00.74, fetched 2026-11-09). Every plate was opened and sliced with the OrcaSlicer 2.5.0 command line, but not in Bambu Studio itself. After opening a project in Bambu Studio, check the plate list and the filament mapping and slice once.
- **Final 6.4.0 CAD** (this package): tub bosses on corbels, zero-volume fins gone from all files, cap ledge partly chamfered, harness tie lug and C-hook on the servo bay, harness fence on the module lid. The 21 unchanged files are still byte-identical to 6.3.0.
- Times and grams come from the OrcaSlicer estimator with the A1 profiles. Bambu Studio may differ by 5 to 10 %.
- Slicer warnings: none on any plate.

