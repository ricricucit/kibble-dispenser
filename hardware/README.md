# Hardware 6.4: chassis with a detachable electronics module

**Status: designed and checked in CAD only (hardware 6.4.0, status designed; electronics module case 1.0, status designed). Nothing of 6.4 has been printed, assembled or tested yet, and the firmware for its one-button control panel does not exist yet ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)).** The working prototype is still prototype 1 on the bench, with its two buttons (see [the as-built baseline](../docs/AS_BUILT_BASELINE.it.md) and [the bench notes](../docs/PROTOTYPE_BENCH.md)).

The product is two parts: the **chassis** (mechanics and a holder for the electronics, this folder, version line 6.x) and a detachable **electronics module** with its own version line (case 1.x, in [`module/`](module/README.md)). The electronics inside the module can evolve without touching the chassis.

- The servo stays in the chassis, coaxial and structural, in its own sealed **servo bay** (`scatola_v64`: tower face, servo cradle and gland wall). Two posts with M3 inserts on the bay hold the module.
- The **module case 1.0** is a sealed case (tub, lid, speaker ring, lid gasket) that slides into an opening of the shell and the cap from below, locks with two M3 × 16 screws and connects with one M8 5-pin plug (J1). Its outer wall is the missing piece of the pod skin and carries the control panel: hang the dispenser with the panel facing you. The interface is described in [`module/case-1.0/README.md`](module/case-1.0/README.md).
- The shell (`guscio_v64`) has the module opening with return ribs; the cap (`fondello_v64`) closes the servo bay from below, with its lip seal (`guarnizione_fondello_v64`) and the module opening.
- A short harness in the chassis joins the supply, the servo and the module: a 190 mm M8 tail to J1 with a service loop on the module lid, a 12 V branch to the M8 connector in the pod top, and a round servo branch through the M12 gland to a JR connector in the bay. The servo and its lead stay untouched and replaceable.
- The panel is on the module: the push-button faces 60° clockwise from the release button (seen from above), on the side away from the bowl, because the servo body blocks the room side.

Pages, in English, Italian and German:

- 3D model, full screen: <https://ricricucit.github.io/kibble-dispenser/3d/>
- Step-by-step print guide: <https://ricricucit.github.io/kibble-dispenser/print/> (files in [`plates/`](plates/PRINT_GUIDE.md))
- The electronics module: <https://ricricucit.github.io/kibble-dispenser/module/>
- Bought parts, chassis and module: <https://ricricucit.github.io/kibble-dispenser/parts/> (also [docs/BOM.md](../docs/BOM.md))
- Assembly guide, "Install the kit" and "Build it yourself", with a module chapter: <https://ricricucit.github.io/kibble-dispenser/assembly/>
- Manual (A6 booklet and A4 print version per language) and drilling template: <https://ricricucit.github.io/kibble-dispenser/manual/>

All dimensions are in mm. Frame: Z up, shaft axis at x = y = 0, Z = 0 at the underside of the bowl base, bayonet locked, gate open, module in place.

## Folders

- `cad/`: generator scripts and design data
  - `build_v64.py`: builds the chassis parts and the module case 1.0 parts, runs the checks (`build_v64_checks.py`, which runs `build_v64_report.py`) and publishes with `publish_v64.py`. It first runs the stages it builds on, each into `cad/build/` (not committed): `build_v6.py` (with `build_dosing.py` and `build_v5.py`, which take their drivetrain geometry from `build_drivetrain.py`), `build_v61.py`, `build_v611.py`, `build_v62.py` and `build_v63.py`, each with its checks. The stages make most of the chassis parts; only `build_v64.py` publishes.
  - `los.py`, `toolaccess.py`: check helpers; `ref/`: reference measurements and part data the stage checks compare against.
  - `v64.json`: design data (split, decisions, interface with the harness, module, parts with the hashes of the print files, build order, checks, load case, grams, hardware, print notes, open risks, review answers); `check_v64.png`: section and check image.
- `assembly/`: meshes at the assembled position for the 3D viewer, chassis and module, with simple placeholders of the bought parts, and `v64_viewer.json` in English, Italian and German. Not for printing.
- `plates/`: the print package for a Bambu Lab A1 with AMS lite, for both products: five Bambu Studio projects (chassis PETG, chassis IP66 PETG, chassis TPU, module PETG, module TPU), a plain 3MF per plate, every part as an STL in print orientation, previews, slicer statistics, `summary.json` (products, plates, parts, times, grams, bought parts) and the step-by-step procedure [`PRINT_GUIDE.md`](plates/PRINT_GUIDE.md); generator scripts in `plates/tools/`. Validated by slicing every plate with OrcaSlicer 2.5 (not opened in Bambu Studio yet). Two parts need supports, both set up in the projects: tree supports under the three bowl tabs of the shell, and two tiny columns under the upper corners of the button recess of the module tub.
- `template/`: the 1:1 drilling template for the shelf (A4, SVG and PDF), with the panel direction.
- `bom.json`: the bought parts in three languages, grouped by product, checked against `plates/summary.json` by `site/bom.py`.
- `module/`: the electronics module line; the module parts as exported by the CAD and the interface drawing are in [`module/case-1.0/`](module/case-1.0/README.md).

## Print review

An independent print review of every part was made before the first print: [docs/reviews/2026-11-15-v6.4-print-review/](../docs/reviews/2026-11-15-v6.4-print-review/README.md) (0 blocker, 3 major, 19 minor). The CAD answers every finding (`v64.json`, `review_2026_11_15`): the holder posts grow from the bed, the bottom edges of the cap and the tub start with a 45° chamfer, the module has a defined vertical stop, the lid takes PT K30 × 10 screws (5), the J1 bore is Ø16.5, and more. One major point stays partly open by design: the inner 12 mm of the three bowl tabs of the shell still need tree supports from the build plate.

## Assembly order (design, not tested)

From `v64.json`, `build_order`:

1. Latch, tower module, chute, shell.
2. Servo bay onto the tower: 3 × M3 × 40 from below.
3. Harness: servo branch through the gland, JR female crimped on and plugged to the servo; 12 V branch to the M8 connector in the pod top; tail tied to the bay lug with a 2.5 × 100 cable tie.
4. Cap: push on, 4 × PT K30 × 12 with an O-ring 3 × 1 from below (T10); the M8 plug hangs out of the opening on its tail.
5. Rim seal, comb lips, plates and disc from the top.
6. Module: plug J1 with the module below the pod, lay the tail loop on the lid, slide it up, 2 × M3 × 16 from below (0.5 N·m).

## Checks in CAD

`build_v64_checks.py` verifies, among others: every part watertight after export; no interference in 1457 pairs of parts; the module removal sweep (free all the way out); the servo bay and the module each one closed dry volume, separate from each other, the pod and the outside (voxel flood fill); seal continuity; a straight key reaching every screw; the panel probes (a paw pad or a snout does not reach the button, a fingertip does); knock-out skins and LED flushness; the pod seams; the load case. The print files of the parts made by the stages are checked against their hashes. CI checks the committed meshes on every push and regenerates the whole chain when the CAD scripts change (`.github/workflows/cad.yml`).

## Firmware

The control panel needs the one-button firmware of [issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2): single press = one portion (only while ON), double press = ON/OFF, long press 5 s = reset all but Wi-Fi, 10 s = full reset, never a portion at power-on. The bench prototype keeps its two buttons and `fw-v0.1.0+dev.20260324` until then, and nothing is flashed for 6.4. Note for the firmware: the camera of the WROVER board uses GPIO 26 and 27, which the bench firmware uses for the speaker and the dispense button ([issue #3](https://github.com/ricricucit/kibble-dispenser/issues/3)); prototype 1 has no camera.

## Open points

From `v64.json`, `open_risks`:

- The panel is not on the room side; the alternative would be a module without the panel plus a panel in the cap.
- A second full board fits only with a low ESP32 stack; an 80 × 60 × 45 mm box is not reachable in this pod.
- J1 (M8 5-pin) is a 3 A connector: fine for a standard servo, not for a high-torque one.
- Lid: about 105 mm of the gasket along the back and notch edges has no screw; water-test the module before trusting IP66.
- The J1 socket and its nut size are assumed: verify the bought part before printing the lid.
- PT screws in the lid bosses allow about 5 to 10 openings; a development module can take M3 inserts instead.
- The pod seams are 0.35 mm gaps without a seal: dust and insects are stopped by the ribs; everything behind them is sealed or drains.
- The module hangs on two M3 inserts in printed posts (safety factor 4.8 at 250 N): do not hang anything from it.

## Regenerating

```
pip install trimesh manifold3d shapely mapbox_earcut rtree numpy scipy networkx lxml matplotlib fast_simplification
python hardware/cad/build_v64.py
python hardware/cad/check_meshes.py hardware
python hardware/cad/check_meshes.py hardware/plates
python hardware/cad/check_meshes.py hardware/module/case-1.0
```

A full run from a clean checkout takes about 16 minutes (later runs only the last stage, about 4 minutes). Everything is written to `cad/build/` first; then `assembly/`, `template/`, `cad/v64.json`, `cad/check_v64.png` and the module folder are published. The PDFs are written without a timestamp. The clearance figures in `v64.json` come from sampled surface points, the 3MF files carry random UUIDs and the SVG drawings random clip ids, so those change slightly on every run; every mesh and image is reproduced byte for byte. Change the scripts, not the meshes; then rebuild the print package with `plates/tools/run_all.sh` (it needs the OrcaSlicer 2.5 command line).
