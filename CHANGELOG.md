# Changelog

All notable changes to this project are documented in this file.

Until the public launch the project keeps only its current state: this file has a single pre-launch entry that describes what the repository holds now, and the release notes of every version line are taken from it. Earlier design iterations (prototype drivetrains, designs v6 to v6.3) and their history are in the git history only. Version numbers keep rising as usual; see [VERSIONS.md](VERSIONS.md). After the launch the file follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), with a section named after each tag.

## [pre-launch] - 2026-11-16

Current state before the public launch: hardware 6.4.0 (the chassis), the electronics module case 1.0 (1.0.0) and firmware 0.1.0+dev.20260324. The hardware and the module are designed and checked in CAD, with an independent print review; nothing of them has been printed, assembled or tested yet. They need the one-button firmware of [issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2), which does not exist yet; the bench prototype keeps its two buttons and its firmware. No product release yet.

### Hardware 6.4.0 (chassis)

- The chassis: flange set with a shut-off gate and an interlock ring, dosing bowl with a two-pocket disc, drive tower with a sealed shaft, the servo in its own sealed bay (cap lip seal, tower face O-ring, shaft O-rings, M12 gland, ePTFE vent patch), a closed claw-proof pod with a hidden chute, and two posts that hold the electronics module. The servo stays in the chassis.
- A chassis harness: a 190 mm M8 5-pin tail to the module connector J1 with a service loop, a 12 V branch to the M8 connector in the pod top and a round servo branch through the gland to a JR connector in the bay.
- CAD in `hardware/cad/`: Python scripts that build every part (`build_v64.py` runs the stages it builds on, about 16 minutes from a clean checkout), check them (closed meshes, no hard interference, free module removal, seals, dry volumes, tool access, control panel) and publish `assembly/` (viewer meshes and `v64_viewer.json`), `template/` (the 1:1 drilling template), `cad/v64.json` and `cad/check_v64.png`.
- Print package in `hardware/plates/` for a Bambu Lab A1 with AMS lite: five Bambu Studio projects (chassis PETG, chassis IP66 PETG, chassis TPU, module PETG, module TPU), 14 plates (one only for reprinting the module gasket), every part as an STL, previews, slicer statistics, `summary.json` and the step-by-step procedure `PRINT_GUIDE.md`. Everything: 44 h 13 min, 1076 g of PETG and 9 g of TPU. Validated by slicing every plate with OrcaSlicer 2.5, not opened in Bambu Studio yet. Two parts need supports, both set up in the projects: tree supports under the three bowl tabs of the shell and two small columns under the button recess of the module tub.
- Bought parts in `hardware/bom.json` (chassis and module), rendered to `docs/BOM.md`.
- The independent print review of 2026-11-15 (0 blocker, 3 major, 19 minor) and its answers: `docs/reviews/2026-11-15-v6.4-print-review/`, recorded in `v64.json` (`review_2026_11_15`).

### Electronics module case 1.0 (1.0.0)

- A sealed case that slides into the chassis from below and locks with two M3 screws; one M8 5-pin plug (J1) connects it. Its outer wall carries the control panel: one push-button in a recessed, paw-proof seat, two light pipes, a speaker grille facing down and three blind knock-outs.
- `hardware/module/VERSION` (the source of truth of the module line) and `hardware/module/case-1.0/`: the four printed parts (tub with the control panel, lid with the J1 turret, lid gasket, speaker ring), the dimensioned interface drawing and a README with the interface spec (opening and envelope, posts, sockets and lock screws, J1 and its pinout, harness lengths, usable space inside). The inside is generic; the board wiring is provisional.
- Print files in the print package (projects `Kibble_Module_case_1.0_PETG.bambu.3mf` and `Kibble_Module_case_1.0_TPU.bambu.3mf`, plates MOD-1, MOD-2, MOD-TPU-1): 5 h 01 min, 108 g of PETG.

### Firmware 0.1.0+dev.20260324

- MicroPython firmware for the bench prototype in `firmware/micropython/`, imported byte-for-byte from a snapshot of the owner's development folder for "feedr-outdoor" (0.1.0 of 2026-03-24 plus the uncommitted edits of the same day). It is not a readback of the board: the firmware actually flashed on the bench prototype may differ.
- Behaviour: two buttons (ON/OFF and dispense), one LED, boots OFF (a reset does not dispense), one portion on a commanded ON and one per press while ON, no repeats on hold, an arcade "feeding fanfare" at every portion. Pins as defined in the source (not yet electrically verified): LED 2, ON/OFF 13, servo 14, speaker 26, dispense 27.
- Modular `src/`, the original single-file prototype as `legacy/CatFeeder.py`, `PROJECT.md`, `Makefile` (mpremote), `VERSION`. The ESPHome draft in `firmware/esphome/` is an unflashed alternative and is not versioned.

### Website, docs and tooling

- Website (`site/`, English, Italian and German) at stable URLs: home, `3d/` (full-screen 3D model), `print/` (the step-by-step print guide), `parts/` (bought parts), `module/` (the electronics module), `assembly/` (assembly guide with the 3D model: "Install the kit" and "Build it yourself") and `manual/` (A6 booklet and A4 print version of the manual, and the drilling template). Every footer shows the hardware, module, firmware and product versions.
- Docs: `docs/PROTOTYPE_BENCH.md` (bench measurements and open points), `docs/AS_BUILT_BASELINE.it.md`, the manuals in `docs/manual/`, process and bench photos in `docs/photos/`.
- CI: mesh checks of the committed hardware, print package and module parts on every push; the CAD workflow regenerates the whole hardware when its scripts change; site build, BOM check, firmware lint, REUSE lint. `tools/release.py` tags and publishes the hardware, module, firmware and product lines.
- Licences: MIT (software), CERN-OHL-P-2.0 (hardware), CC BY 4.0 (docs and images), following the REUSE specification.
