# Design v6: the one-twist unit

**Archived: design v6 is hardware 6.0.0, replaced by [design v6.2](../v6.2/README.md) (closed pod, shut-off gate, cable channel). Print v6.2, not these files.**

**Status: designed and checked in CAD only. Nothing of v6 has been printed, assembled or tested.** The working prototype is still prototype 1 (see [the as-built baseline](../../docs/AS_BUILT_BASELINE.it.md)).

Everything under the shelf (the dosing bowl with its rotary disc, the chute, the tower with the sealed shaft, the electronics box with the servo) comes off with one quarter-turn of the bowl bayonet; only the shelf flange stays screwed to the shelf. The disc is driven coaxially (servo, hub, shaft, disc: no gears), the box hangs from the tower, and its cover closes with four printed quarter-turn buttons, so the cover needs no tools.

- 3D model, full screen: <https://ricricucit.github.io/kibble-dispenser/v6/3d/>
- Bought parts, in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/v6/parts/> (also [docs/BOM-v6.md](../../docs/BOM-v6.md))
- Design data: [cad/v6.json](cad/v6.json) (parts, hardware, z-stack, assembly, sealing, checks, grams, print orientation, files)

All dimensions are in mm. Frame: Z up, shaft axis at x = y = 0, Z = 0 at the underside of the bowl base.

## Folders

- `cad/`: generator scripts and data
  - `build_v6.py`: builds the 12 new parts, exports them, runs the checks and publishes the files below
  - `build_v6_checks.py`: interference, clearance, passage, slope, bayonet sweep, coaxiality and access checks; writes `v6.json`, the viewer manifest and `check_v6.png` (run by `build_v6.py`)
  - `build_dosing.py` (v4b dosing core), `build_v5.py` and `build_v5_checks.py` (v5), `build_drivetrain.py` (drivetrain v4, used as a geometry library) and `layout_v4.json`: earlier iterations that v6 imports and whose parts it reuses. These are not the drivetrain v3 files in `../cad/`.
  - `publish_v6.py`: copies the deliverables from `cad/build/` into the folders below and writes the viewer manifest with names in three languages
  - `v6.json`, `check_v6.png`: design data and the section check image
- `stl/`: print-ready STLs, already oriented for the bed. Multi-colour parts also have one STL per filament colour (`<part>_<colour>.stl`).
- `3mf/`: the same parts, print-ready, one object per filament colour, for multi-colour printing. Unlike prototype 1, these 3MF files are in print orientation; the assembled positions are in `assembly/`.
- `assembly/`: meshes at the assembled position for the 3D viewer (colour bodies, reused parts, simple placeholders for the bought parts) and `v6_viewer.json`. Not for printing.
- `plates/`: print plates for the Bambu Lab A1 with AMS lite (Bambu Studio projects, plate 3MFs, STL files in print orientation, previews, slicer statistics, the print guide and the generator scripts in `plates/tools/`)
- `bom.json`: the bought parts in three languages, checked against `cad/v6.json` and rendered by `site/bom.py`.

## Printed parts

Print estimate about 610 g in total (602 g PETG, 7 g TPU 95A), from a 1.2 mm shell and 15 % infill; v5 needed about 950 g. Colours follow the project rule: black for structure, orange where you act, green for the food path, yellow TPU for seals.

New in v6:

- `chiocciola_v6`, dosing bowl, PETG black (about 165 g): v4b dosing core plus an outward funnel ending on the base plane; inserts for the tower and the chute, a 3 mm well drain and a drip groove. Print as assembled, flat base on the bed; supports only under the three bayonet lugs.
- `scivolo_v6`, chute, PETG green: 55° tube, 44 mm inside, a drip ring and a spigot for an optional DN50 pipe; the horizontal outlet cut makes a 32 mm hood. Flipped, joint flange on the bed; no supports.
- `disco_v6`, dosing disc, PETG orange with a black label: the v4b disc without the screw bore, closed top. Flipped, disc top on the bed (label in the first 3 layers); no supports.
- `colonna_v6`, tower, PETG black: 24 mm dry tower with the shaft bushing at its top and a face O-ring groove at its foot. As assembled, lobed flange on the bed; at least 4 walls; no supports.
- `albero_v6`, shaft, PETG black: 12 mm, solid, keyed hex at both ends, two O-ring grooves. Bottom hex on the bed; 100 % infill, 0.15 mm layers.
- `mozzo_v6`, hub, PETG black: on the 25-tooth servo spline, keyed hex socket for the shaft, one M3x8. Spline socket on the bed; 100 % infill. Print the spline test (`../stl/test_scanalato.stl`) first.
- `scatola_v6`, electronics box, PETG black (about 146 g): 2.4 mm walls, hip roof with a drip lip, servo cradle in the roof, breadboard rails, gland pad, posts for the cover buttons. Flipped, roof plateau on the bed; a thin bed-only support wedge under the 2.5° roof slopes.
- `fondello_v6`, box cover, PETG black with orange lettering: skirt, inner lip, lip-seal groove, four ears. Outer face on the bed (lettering in the first 3 layers); no supports.
- `nottolino_v6`, quarter-turn button, PETG orange, **print 4**: captive on the box posts, with a detent. Flat side on the bed; 100 % infill.
- `guarnizione_fondello_v6`, cover lip seal, TPU 95A yellow. Base on the bed, lip up; 100 % infill, slow. Print a test strip and hose-test the closed box.
- `flangia_piano_v6`, shelf flange, PETG black (about 76 g): 4 mm plate, four wood-screw ears, skirt with three bayonet hooks, three hold-down pins. Flipped, shelf face on the bed; the hook tongues print as 4 mm ledges (support optional).
- `colletto_v6`, funnel collar, PETG green: lines the shelf hole and drains it through 6 weep slots. Flipped, top rim on the bed; no supports.

Reused unchanged from earlier iterations:

- `piastra_gate_v4b`, gate plate, PETG black and green: as assembled, bottom face on the bed (OUT band and labels in the top 3 layers)
- `piastra_finestra_v4b`, window plate, PETG black and green: flipped, top face on the bed (window band and FOOD IN in the first 3 layers)
- `linguetta_sicura`, safety latch, PETG orange: on its back; 100 % infill, 4 walls
- `guarnizione_baionetta`, bayonet gasket, TPU 95A: flat ring, 100 % infill
- `labbro_uscita_1`, `labbro_uscita_2`, `labbro_finestra_1`, `labbro_finestra_2`, plate lips, TPU 95A: flat on the wide face
- `guarnizione_piano_v5`, shelf gasket, TPU 95A: flat ring, 100 % infill

Print plates for a Bambu Lab A1 with the AMS lite are in [`plates/`](plates/README.md): two Bambu Studio projects (PETG and TPU), a plain 3MF per plate, every part as an STL in print orientation, the AMS setup, settings and a check list, also on the site at <https://ricricucit.github.io/kibble-dispenser/v6/print/>. They are archived: design v6.2 replaced them with its own print package in [`../v6.2/plates/`](../v6.2/plates/README.md).

## Bought parts

Screws, inserts, O-rings, grease, the electronics module, the optional DN50 pipe and the tools: see [docs/BOM-v6.md](../../docs/BOM-v6.md) or the [bought-parts page](https://ricricucit.github.io/kibble-dispenser/v6/parts/). In the kit the electronics box comes pre-assembled.

## Assembly order (design, not tested)

1. Shelf: drill a 76 mm hole, its centre 27 mm from the shaft axis towards the window side (shelves 18 to 40 mm thick).
2. Flange: shelf gasket in the top groove, funnel collar on the plate (2 pins) with the neck in the hole, 4 wood screws from below.
3. Bowl, on the bench: press in 3 inserts for the tower and 2 for the chute from below; latch into its slot; rim gasket; chute onto the nose with 2 x M3x10 from below.
4. Box, on the bench: press in 3 inserts in the roof plateau and 4 in the servo pads; slide the breadboard with the ESP32, regulators and capacitor between the rails; M16 gland; silica gel bag.
5. Servo, on the bench: hub on the spline (note the spline position for the firmware zero), M3x8 from above through the hex socket; push the servo up into the cradle and fix it with 4 x M3x8 and washers.
6. Tower, on the bench: greased 24x2 O-ring in the flange groove, tower on the plateau (the lobes fit one way only), 3 x M3x10 from above.
7. Shaft, on the bench: 2 greased 9x2 O-rings on the shaft, push it down through the bushing into the hub socket.
8. Tower to bowl, on the bench: collar through the hole in the bowl base, lobes on the inserts, 3 x M3x12 from below (2.5 mm hex key).
9. Dosing core, from above: gate plate, disc on the hex (rib on the flat), window plate, 4 lips.
10. Cover: lip seal in the groove, push the cover up and turn the 4 orange buttons a quarter turn until they click.
11. Install: lift the unit to the flange, lugs into the slots, push up and turn 30° until the orange latch clicks; plug in the 12 V cable.

To remove it, press the orange latch, turn back 30° and lower: the whole unit comes down, and only the 12 V plug comes along. On the bench, the window plate, the disc and the gate plate lift out from the top, and the shaft pulls out upwards without opening the box.

## Sealing

The bowl, funnel and chute are wet; the tower bore below the shaft O-rings and the box are dry. Every joint between wet and dry has an O-ring or a TPU seal, and every opening faces down: two O-rings on the shaft, a face O-ring between the tower and the box (its screws sit outside it in blind inserts), a TPU lip seal under the cover, and one cable gland as the only opening. Details in `v6.json` (`ip65`).

## Checks in CAD

`build_v6_checks.py` checks that every part is watertight after export, that no two parts interfere (575 pairs), the passage for the kibble (at least 42.4 mm through the chute; the v4b pocket limits kibble to under 28 mm), slopes of at least 50° on every food face, clearances, the bayonet removal sweep, coaxiality and hex-key access. The results are in `v6.json` (`checks`) and `cad/check_v6.png`. CI regenerates v6 and checks every mesh on each push.

## Open points

- The cover lip seal is a printed TPU 95A lip: print a test strip, then hose-test the closed box.
- The hub's M3x8 goes into the servo's spline thread: check the real thread depth (3.5 mm engagement modelled).
- The hub can sit in 25 positions on the spline: set the disc zero in the firmware after assembly.
- The speaker of the behavioural contract has no sound opening in the sealed box yet; a speaker inside will be muffled.
- A DN50 pipe longer than about 0.5 m needs its own support (only 2 small screws hold the chute).
- The top 6 mm of the breadboard has no room for tall parts within 21 mm of the axis.
- The butt joint between bowl and chute may drip a little to the outside in heavy rain (not into the box).

## Regenerating

```
pip install trimesh manifold3d shapely mapbox_earcut rtree numpy scipy networkx lxml matplotlib
python hardware/v6/cad/build_v6.py
python hardware/cad/check_meshes.py hardware/v6
```

`build_v6.py` runs `build_dosing.py` and `build_v5.py` first when their outputs are missing or out of date, writes everything to `cad/build/` (not committed, about 45 s in total) and then publishes `stl/`, `3mf/`, `assembly/`, `cad/v6.json` and `cad/check_v6.png`. Regenerated meshes are identical; 3MF files differ only in their random object IDs. Change the scripts, not the meshes. The 3D page on the site is built from `assembly/` by `site/build.py`, which also needs `numpy` and `fast_simplification`.
