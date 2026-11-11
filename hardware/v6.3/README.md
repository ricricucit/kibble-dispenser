# Design v6.3: simpler pod with a control panel

**Status: designed and checked in CAD only (hardware 6.3.0, status designed). Nothing of v6.3 has been printed, assembled or tested yet, and the firmware for its one-button control panel does not exist yet ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)).** The working prototype is still prototype 1 on the bench, with its two buttons (see [the as-built baseline](../../docs/AS_BUILT_BASELINE.it.md)).

v6.3 keeps the closed pod, the shut-off gate with its ring interlock and the mechanism of [design v6.2](../v6.2/README.md) and makes it simpler to print and to assemble, with a control panel on the pod:

- no cable channel under the shelf: the supply cable leaves the flange at the back rim, through a bell mouth, held by a UV cable tie cinched in a window of the upper plate; a pull or a bite outside cannot reach the M8 connector. The user clips the cable along the shelf;
- fewer pieces: 28 printed pieces instead of 36 (18 PETG and 10 TPU, 25 parts). The three thumb-turns with keys, O-rings and cups become three PT K30 × 12 thread-forming screws with an O-ring under each head (T10 driver); the three flange screws become press-fit pins; five heat-set inserts become PT screws in pilot holes; the gate blade is one colour;
- a control panel on the room side of the cap: one push-button in a Ø17 × 8 mm recess (a fingertip reaches it, a paw pad or a snout does not), two flush light pipes with LEDs (status and Wi-Fi), a sealed speaker opening facing down with an IP67 acoustic membrane, and three flush blind knock-outs for future switches (a drilling recipe is in `cad/v63.json`). All panel parts are fitted from the dry side, and the cap is the floor of the dry box, so the panel adds no new joint;
- a second labyrinth drain in the cap for a corner of the wet region that had none in v6.2, a full wall round the dowel seat of the gate pivot, and the seam spigot joined to the cap wall;
- the print orientations of the v6.2 print package are now in the CAD, so the CAD print files are the print files.

Pages, in English, Italian and German:

- 3D model, full screen: <https://ricricucit.github.io/kibble-dispenser/3d/>
- Print files: <https://ricricucit.github.io/kibble-dispenser/print/> (files in [`plates/`](plates/README.md))
- Bought parts: <https://ricricucit.github.io/kibble-dispenser/parts/> (also [docs/BOM.md](../../docs/BOM.md))
- Assembly guide, "Install the kit" and "Build it yourself": <https://ricricucit.github.io/kibble-dispenser/assembly/>
- Manual (A6 booklet and A4 print version per language) and drilling template: <https://ricricucit.github.io/kibble-dispenser/manual/> (files in [docs/manual/](../../docs/manual/) and [`template/`](template/))

All dimensions are in mm. Frame as v6.2: Z up, shaft axis at x = y = 0, Z = 0 at the underside of the bowl base, bayonet locked, gate open; the shelf underside is at z = 78.1.

## Folders

- `cad/`: generator scripts and design data
  - `build_v63.py`: builds the v6.3 parts, runs the checks (`build_v63_checks.py`, which runs `build_v63_report.py`) and publishes the files below with `publish_v63.py`. It runs the earlier stages first, each into `cad/build/` (not committed): `build_v6.py` (with `build_dosing.py` and `build_v5.py`), `build_v61.py`, `build_v611.py` and `build_v62.py`, all with their checks, because v6.3 imports their parameters and reuses their parts. These are copies of the scripts of those iterations with relative paths; they never publish into the folders of the earlier designs. The grams and pieces comparison with v6.2 reads the committed v6.2 print package (`../v6.2/plates/`).
  - `los.py` and `toolaccess.py`: line-of-sight and hex-key access helpers of the checks; `ref/measure_v61.json` and `ref/ta_v611.json`: baseline measurements that the checks compare against.
  - `v63.json`: design data (6.3.0 fixes, changes with the control panel spec and the knock-out drilling recipe, build order, kit split, shelf and template, changed and reused parts, checks, load case, grams, print orientations, open risks); `check_v63.png`: section and check image.
- `assembly/`: meshes at the assembled position (gate open) for the 3D viewer, with simple placeholders of the bought parts, and `v63_viewer.json` with names in English, Italian and German. Not for printing.
- `plates/`: the print package for a Bambu Lab A1 with AMS lite (Bambu Studio projects, a plain 3MF per plate, every part as an STL in print orientation, previews, slicer statistics, `summary.json` with the bought-parts list, the print guide `README.md` and the generator scripts in `plates/tools/`). Made from the 6.3.0 CAD print files without changes and validated by slicing every plate with OrcaSlicer 2.5 (not opened in Bambu Studio yet).
- `template/`: the 1:1 drilling template for the shelf (A4, SVG and PDF), also on the manual page. No channel strip any more: one Ø76 hole and four wood screws.
- `bom.json`: the bought parts in three languages, checked against `plates/summary.json` by `site/bom.py`.

## Parts

Slicer estimate for one dispenser, test pieces included: 1000 g of PETG (816 g black, 120 g orange, 64 g green) and 8 g of TPU 95A, 39 h 30 min over 9 plates with 18 colour swaps (v6.2: 1047 g, 41 h 14 min, 33 swaps).

- Changed in v6.3: `fondello_v63` (cap: PT counterbores and bosses instead of the thumb-turns, control panel, dry pocket, speaker cup and grille, second drain, seam spigot joined to the wall), `scatola_v63` (box: PT bosses instead of the cups, P3 moved), `chiocciola_v63` (bowl: P3 insert moved, PT pilots for the chute and the shell), `colonna_v63` (tower: P3 pillar moved), `flangia_piano_v63` (lower plate: dowel hole with a full wall, pin holes, raised tunnel), `flangia_alta_v63` (upper plate: no channel port, three press-fit pins, tie window, bell mouth), `anello_saracinesca_v63` (teardrop window, prints without support), `saracinesca_v63` (one colour), `passacavo_v63` (follows the raised tunnel), `linguetta_sicura_v63` (print orientation only).
- Removed: the cable channel (two bases, two covers, the end cap and their four wood screws) and the three thumb-turns.
- Reused unchanged: `guscio_v611`, `pulsante_v611`, `labbro_ombra_v611`, `scivolo_v611`, `labbro_scivolo_v611`, `disco_v61`, `guarnizione_baionetta_v61`, `guarnizione_fondello_v61`, `colletto_v6`, `guarnizione_piano_v5`, `albero_v6`, `mozzo_v6`, `piastra_gate_v62`, `piastra_finestra_v62`, `labbro_pettine_v62`.

Colours follow the project rule: black for structure, orange where you act, green for the food path, yellow TPU for seals.

## Bought parts and kit

Screws, inserts, O-rings, the dowel pin, the cable tie, the M8 connector pair, the gland and vent, the panel parts (IP67 12 mm short-body push-button, two light pipes and LEDs, speaker, IP67 acoustic membrane, harness), the electronics and the tools: [docs/BOM.md](../../docs/BOM.md) or the [bought-parts page](https://ricricucit.github.io/kibble-dispenser/parts/). The planned kit (`v63.json`, `kit_split`) ships the dispenser unit pre-assembled and closed, with the panel fitted, the flange set pre-assembled (both plates, dowel, blade, ring, skirt lip), the grommet, the collar, the shelf gasket, the wood screws, the supply cable with the M8 connector, the cable tie and the drilling template. No kit is sold yet.

## Assembly order (design, not tested)

The order that the tool-access check passes for every screw (`v63.json`, `build_order`):

1. Latch into the bowl.
2. Drive module (tower, shaft, hub) on the bowl base.
3. Chute: 2 × PT K30 × 10 from below.
4. Shell, with the button and its O-ring: 3 × PT K30 × 12 through the tabs (the box is not in yet).
5. Electronics box onto the tower: 3 × M3 × 40 from below, with an O-ring 3 × 1 under the heads that pass the box roof. Tighten to 0.4 N·m and check again after a week.
6. Cap, with the panel parts fitted and the panel harness plugged into the board: push on, 3 × PT K30 × 12 with an O-ring 3 × 1 from below (T10, by hand, about 0.6 N·m).
7. Rim seal, comb lips, plates and disc from the top.

Flange set: ring snapped into the lower plate, dowel pin pressed in, blade on the dowel, upper plate pressed on (three pins). On site: drill with the template, cable through the tunnel with the grommet, cable tie cinched in the window, flange set with 4 wood screws 5 × 35, connect the unit, hang it with the gate closed, then open the gate.

## Checks in CAD

`build_v63_checks.py` (with the earlier stages' checks) verifies, among others: every part watertight after export; no interference in 1596 pairs of parts; the dry volume as one region, separate from the wet region and the outside, with both wet regions of the cap draining (voxel flood fill); seal continuity; no line of sight into the pod; the bayonet sweep; the gate passage when open (0.992 of the v6.1.1 section) and the hold when closed; the strict interlock; a straight key or driver reaching every screw in the assembly order; the panel probes (a paw pad or a snout does not reach the button, a fingertip does); the knock-out skins and their flushness; the load case. The results are in `cad/v63.json` (`checks`, `load_case`) and `cad/check_v63.png`. CI checks the committed meshes on every push and regenerates the whole chain when the CAD scripts change (`.github/workflows/cad-v63.yml`).

## Firmware: one button, not written yet

The control panel needs new firmware ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2), owner decision of 2026-11-10; `v63.json`, `4_firmware_ui_note`). The bench prototype keeps its two buttons and its firmware `fw-v0.1.0+dev.20260324` until then, and nothing is flashed for v6.3. Planned mapping:

- single press: dispense exactly one portion, only while the unit is ON (confirmed after the double-press window, so one press is one cycle);
- double press: ON/OFF; switching ON dispenses exactly one portion, switching OFF none;
- long press 5 s: reset everything except Wi-Fi; long press 10 s: full reset (no dispensing; LED patterns tell when to let go);
- a sound at every portion, no repeats while the button is held, no autonomous cycling;
- never dispense at power-on: store the last rest position of the disc and command exactly it at boot before the servo PWM is enabled; the unit boots OFF.

The pins in `v63.json` are a proposal only, not electrically verified.

## Open points

- Panel switch: the free depth behind the mount wall is 14 mm; pick a short-body IP67 type and check its datasheet.
- A fox canine on a flush knock-out: punching safety factor 1.88 on the 2.0 mm skin, 1.6 on the engraved line (250 N assumed).
- A future knock-out switch needs a 12 mm IP67 type with a nut of at most 14 AF and at most 14 mm behind the seat; the curved outer face needs silicone under the gasket or a printed bezel.
- PT screws in printed PETG: pull-out estimated, not tested; tighten by hand (0.6 N·m), at most about 5 re-assemblies per hole.
- Cap service now needs a T10 driver (it was tool-free) and releases the panel harness: unplug it before pulling the cap off.
- The cable stands 0.4 mm proud of the shelf face at the rim: on a very hard shelf the flange may stand 0.4 mm off the wood until the jacket yields.
- The A column sits 1.75 mm from the back of the board: keep the perfboard back free of leads there.
- The unit hangs 182.1 mm below the shelf (as v6.2). The hub can sit in 25 positions on the spline: set the disc zero in the firmware after assembly.

## Regenerating

```
pip install trimesh manifold3d shapely mapbox_earcut rtree numpy scipy networkx lxml matplotlib fast_simplification
python hardware/v6.3/cad/build_v63.py
python hardware/cad/check_meshes.py hardware/v6.3
```

A full run from a clean checkout takes about 12 minutes; later runs skip the earlier stages while their outputs are newer than their scripts. Everything is written to `cad/build/` first; then `assembly/`, `template/`, `cad/v63.json` and `cad/check_v63.png` are published. Change the scripts, not the meshes; then rebuild the print package with `plates/tools/run_all.sh` (it needs the OrcaSlicer 2.5 command line for the slicer check). The site's 3D page is built from `assembly/` by `site/build.py`.
