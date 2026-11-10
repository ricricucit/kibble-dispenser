# Design v6.2: closed pod, shut-off gate, cable channel

**Status: designed and checked in CAD only (hardware 6.2.0, status designed). Nothing of v6.2 has been printed, assembled or tested yet.** The working prototype is still prototype 1 on the bench (see [the as-built baseline](../../docs/AS_BUILT_BASELINE.it.md)).

v6.2 keeps the mechanism of [design v6](../v6/README.md) (coaxial servo, hub, shaft and two-pocket disc; the whole unit comes off the shelf with one twist of a bayonet) and closes it in a smooth, claw-proof pod:

- a shut-off gate in the flange: a green blade turned 113° by an orange ring round the top of the pod. The ring covers the release button except through one window, which lines up with the button only at the end of the closing stroke, after the blade has covered the opening (strict interlock, no springs). The unit can only come down with the gate closed;
- a closed pod: a smooth shell, a flat cap with three flush orange thumb-turns, the chute hidden inside and ending in the outlet in the flat bottom, O-rings at the seam, the button and the thumb-turns, and a membrane vent in the sealed electronics box;
- the 12 V cable leaves through a tunnel in the flange and runs in a snap-in channel under the shelf; an IP67 M8 connector hangs in the top of the pod and comes free when the unit is lowered 8 cm. No second hole in the shelf;
- one screw set: three M3 × 40 clamp box, tower and bowl in one stack from below, each reachable with a straight key in the assembly order;
- near-zero maintenance: the drive is greased for life at assembly, no silica gel, a self-cleaning disc.

Pages, in English, Italian and German:

- 3D model, full screen: <https://ricricucit.github.io/kibble-dispenser/3d/>
- Print files: <https://ricricucit.github.io/kibble-dispenser/print/> (files in [`plates/`](plates/README.md))
- Bought parts: <https://ricricucit.github.io/kibble-dispenser/parts/> (also [docs/BOM.md](../../docs/BOM.md))
- Assembly guide, "Install the kit" and "Build it yourself": <https://ricricucit.github.io/kibble-dispenser/assembly/>
- Manual (A6 booklet and A4 print version per language) and drilling template: <https://ricricucit.github.io/kibble-dispenser/manual/> (files in [docs/manual/](../../docs/manual/) and [`template/`](template/))

All dimensions are in mm. Frame: Z up, shaft axis at x = y = 0, Z = 0 at the underside of the bowl base, bayonet locked, gate open; the shelf underside is at z = 78.1.

## Iterations in this design

v6.2 was designed in three steps on top of v6. Only v6.2 is released (`hw-v6.2.0`); 6.1.0 and 6.1.1 were design iterations, recorded in [CHANGELOG.md](../../CHANGELOG.md).

- v6.1 (6.1.0), the pod: one smooth claw-proof shell round the whole unit, flat cap with flush thumb-turns, chute moved inside, flush latch button, self-cleaning disc with sweeper ribs and scissor edges, sealed box with a 70 × 50 board, M12 gland and ePTFE vent.
- v6.1.1 (6.1.1), the closed pod: the pod becomes a second seal round the dry box: O-ring 132 × 2 at the shell/cap seam, O-rings on the thumb-turn shafts and the button, steel keys that make the thumb-turns captive, a TPU skirt lip under the flange, a TPU lip ring on the chute, one labyrinth drain.
- v6.2 (6.2.0), gate, channel and screws: the shut-off gate with the ring interlock (two flange plates), the cable tunnel and channel with the M8 connector, the M3 × 40 stack that replaces the two unreachable screw sets, one common comb lip for all four plate grooves, the 1:1 drilling template, and a thicker web between the cap dishes and the outlet against fox bites.

## Folders

- `cad/`: generator scripts and design data
  - `build_v62.py`: builds the v6.2 parts, runs the checks (`build_v62_checks.py`) and publishes the files below with `publish_v62.py`. It runs the earlier stages first, each into `cad/build/` (not committed): `build_v6.py` (with `build_dosing.py` and `build_v5.py`), `build_v61.py` and `build_v611.py`, all with their checks, because v6.2 imports their parameters and reuses their parts. These are copies of the scripts of those iterations with relative paths; `build_v6.py` here never publishes into `../v6/`.
  - `los.py` and `toolaccess.py`: line-of-sight and hex-key access helpers of the checks; `ref/measure_v61.json` and `ref/ta_v611.json`: baseline measurements of v6.1 and v6.1.1, made once, that the checks compare against.
  - `v62.json`: design data (changes, kit split, hardware delta, shelf and template, changed, new and reused parts, checks, load case, grams, print notes, open risks); `check_v62.png`: section and check image.
- `assembly/`: meshes at the assembled position (gate open) for the 3D viewer, with simple placeholders of the bought parts, and `v62_viewer.json` with names in English, Italian and German. Not for printing.
- `plates/`: the print package for a Bambu Lab A1 with AMS lite (Bambu Studio projects, a plain 3MF per plate, every part as an STL in print orientation, previews, slicer statistics, `summary.json` with the bought-parts list, the print guide `README.md` and the generator scripts in `plates/tools/`). **This is the authoritative print set of v6.2**, see below.
- `template/`: the 1:1 drilling template for the shelf (A4, SVG and PDF), also on the manual page.
- `bom.json`: the bought parts in three languages, checked against `plates/summary.json` by `site/bom.py`.

## Print from plates/, not from the CAD exports

The print package in [`plates/`](plates/README.md) was made from the CAD exports and validated by slicing every plate with OrcaSlicer 2.5 (not opened in Bambu Studio yet). It differs from the CAD print exports in `cad/build/` in two ways, and it is the one to print:

- Print orientations corrected, each with less overhang: `canalina_base_v62` flipped (wood face on the bed), `canalina_coperchio_v62` open side up, `canalina_tappo_v62` on its other side (1.9 instead of 115 mm² of overhang), `passacavo_v62` lip on the bed.
- The lower flange plate `flangia_piano_v62` is printed without its Ø4 × 3.3 printed pivot pin for the gate blade, which would stand on the bed face: the print file has a Ø4.0 × 2.7 mm blind hole at the centre for a pressed-in stainless dowel pin Ø4 × 6 (ISO 2338, m6), which is in the bought parts. The unmodified CAD print file is kept as `plates/stl/flangia_piano_v62_print_cad_original.stl`. The designer still has to confirm this change in the CAD script.

The CAD print exports are not published in this folder, so that there is only one set of print files.

## Parts

Slicer estimate for one dispenser, test pieces included: 1047 g of PETG (848 g black, 132 g orange, 66 g green) and 8 g of TPU 95A, 41 h 14 min over 9 plates with 33 colour swaps (`plates/summary.json`). 22 PETG parts (26 pieces) and 10 TPU pieces, plus 8 test pieces.

- New in v6.2: `flangia_alta_v62` (upper flange plate with the blade pocket and the cable tunnel), `saracinesca_v62` (gate blade, green with an orange arm), `anello_saracinesca_v62` (orange interlock ring), `passacavo_v62` (TPU cable grommet), `labbro_pettine_v62` (comb lip, print 4), `canalina_base_v62` (× 2), `canalina_coperchio_v62` (× 2) and `canalina_tappo_v62` (cable channel).
- Changed in v6.2: `chiocciola_v62` (bowl: stack inserts moved), `colonna_v62` (tower: three pillars for the stack), `scatola_v62` (box: ear and two sealed through holes, vent moved), `fondello_v62` (cap: Ø24 dishes), `flangia_piano_v62` (lower flange plate: gate pivot, ring groove), `piastra_gate_v62` and `piastra_finestra_v62` (grooves for the common lip).
- Reused unchanged: `guscio_v611`, `pulsante_v611`, `labbro_ombra_v611`, `scivolo_v611`, `labbro_scivolo_v611`, `nottolino_v611` (× 3), `disco_v61`, `guarnizione_baionetta_v61`, `guarnizione_fondello_v61`, `colletto_v6`, `guarnizione_piano_v5`, `linguetta_sicura`, `albero_v6`, `mozzo_v6`.

Colours follow the project rule: black for structure, orange where you act, green for the food path, yellow TPU for seals. Per-part print settings, the IP66 settings of the box and the cap, and the check list are in the print guide.

## Bought parts and kit

Screws, inserts, O-rings, the dowel pin, the M8 connector pair, the gland and vent, the electronics and the tools: [docs/BOM.md](../../docs/BOM.md) or the [bought-parts page](https://ricricucit.github.io/kibble-dispenser/parts/). The planned kit (`v62.json`, `kit_split`) ships the dispenser unit pre-assembled and closed, the flange set pre-assembled (both plates, blade, ring, skirt lip, grommet), the cable channel with its screws, the collar, the shelf gasket, the wood screws, the supply cable with the M8 connector and the drilling template. No kit is sold yet.

## Assembly order (design, not tested)

The assembly guide shows every step with the 3D model. The order that the tool-access check passes for every screw (`v62.json`, `1_screw_access.build_order`):

1. Latch into the bowl.
2. Drive module (tower, shaft with two greased O-rings 9 × 2, O-ring 24 × 2) on the bowl base, collar in the base hole, no screws yet.
3. Chute: 2 × M3 × 10 from below.
4. Shell, with the button and its O-ring: 3 × M3 × 12 from below (the box is not in yet, so nothing blocks the key).
5. Electronics box, cap off, lowered into the shell onto the tower (shaft into the hub, rib to the latch): 3 × M3 × 40 from below, with an O-ring 3 × 1 under the two heads inside the box. Tighten to 0.4 N·m and check again after a week.
6. Cap on, three thumb-turns a quarter turn.
7. Rim seal, comb lips, plates and disc from the top.

Flange set: skirt lip in the lower plate, ring snapped on, blade on the pivot pin (dowel) with the arm on the ring's peg, cable and grommet in the tunnel, upper plate on, 3 × ST 2.9 × 9.5 from the shelf side. On the shelf: drill with the template, flange set with 4 wood screws 5 × 35, cable channel with 4 wood screws 3.5 × 16, connect the unit, hang it with the gate closed, then open the gate.

## Sealing

The bowl, funnel and chute are wet; the tower bore below the shaft O-rings and the electronics box are dry, and the pod round them is a second barrier. Every joint between wet and dry has an O-ring or a TPU seal: two O-rings on the shaft, a face O-ring between tower and box, O-rings 3 × 1 under the two stack screws that pass the box roof, the gland and the ePTFE vent in the box; the shell/cap seam O-ring 132 × 2, the button O-ring 14 × 1.5, the thumb-turn O-rings 8 × 1.5, the TPU cap lip seal, the skirt lip and the chute lip ring in the pod. The only opening of the pod is the outlet, facing down, plus a labyrinth drain. It is a design approach, not a certification: the closed pod still has to pass a hose test.

## Checks in CAD

`build_v62_checks.py` (with the earlier stages' checks) verifies, among others: every part watertight after export; no interference in 1522 pairs of parts; the stack screws against the drilled parts; seal continuity all round; no line of sight into the pod through the thumb-turns or the shadow gap behind the ring; the bayonet removal sweep with the gate closed; the gate passage when open (0.999 of the v6.1.1 section) and the hold when closed under a full 200 L drum; the strict interlock; a straight key reaching every screw in the assembly order; clearances; the load case (250 N down and 100 N sideways at the bottom). The results are in `cad/v62.json` (`checks`, `load_case`) and `cad/check_v62.png`. CI checks the committed meshes on every push and regenerates the whole chain when the CAD scripts change (`.github/workflows/cad-v62.yml`).

## Firmware requirement

The firmware version stays `fw-v0.1.0+dev.20260324` (same pins and behaviour contract). v6.2 adds one requirement (`v62.json`, `8_firmware_note`): **the disc must never dispense at power-on.** Both rest positions (0° and 180°) are closed, so the firmware has to store the last commanded rest position in non-volatile memory (written only when it changes), command exactly that position at boot, and enable the servo PWM only after the stored value is loaded; a cold start without a stored value goes to 0°. This complements the existing contract (boots OFF, one cycle on a commanded ON, one per press). The current firmware has not been changed for it yet.

## Open points

- P3 stack-screw head sits 0.375 mm from the servo cradle and the board: check on the first print (a low-head DIN 7984 screw would give 1 mm).
- Stack screws: the governing vertical case has a safety factor of 3.6 on the inserts; printed PETG pillars creep under preload, so tighten to 0.4 N·m and re-check after a week.
- Gate pocket gaps of 0.2 mm: insects could walk the pocket (same class as the 0.7 mm comb slits; the kibble path is open by design).
- The 28 mm window of the ring is a bridge when printed on edge: the print package adds a small support.
- The cable bend in the flange (R 15) suits a Ø5 PUR cable in a fixed installation only; a stiffer PVC cable needs R 20.
- The unit hangs 182 mm below the shelf (8 mm more than v6.1.1).
- The pivot dowel replacing the printed pin is a change of the print package that the designer still has to confirm in the CAD.
- From v6.1: the speaker of the behaviour contract has no sound opening in the sealed box yet, and the physical ON/OFF and dispense buttons and the LED of the bench prototype are not on the pod yet.
- The hub can sit in 25 positions on the spline: set the disc zero in the firmware after assembly.

## Regenerating

```
pip install trimesh manifold3d shapely mapbox_earcut rtree numpy scipy networkx lxml matplotlib fast_simplification
python hardware/v6.2/cad/build_v62.py
python hardware/cad/check_meshes.py hardware/v6.2
```

A full run from a clean checkout takes about 10 minutes; later runs skip the earlier stages while their outputs are newer than their scripts. Everything is written to `cad/build/` first; then `assembly/`, `template/`, `cad/v62.json` and `cad/check_v62.png` are published. The sampled clearance checks are seeded, so `v62.json` is reproducible. The template PDF is rendered from the SVG with `rsvg-convert` when it is installed. Change the scripts, not the meshes; then rebuild the print package with `plates/tools/run_all.sh` (it needs the OrcaSlicer 2.5 command line for the slicer check). The site's 3D page is built from `assembly/` by `site/build.py`.
