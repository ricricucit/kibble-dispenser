# Kibble Dispenser

[![Software: MIT](https://img.shields.io/badge/software-MIT-blue)](LICENSES/MIT.txt)
[![Hardware: CERN-OHL-P-2.0](https://img.shields.io/badge/hardware-CERN--OHL--P--2.0-blue)](LICENSES/CERN-OHL-P-2.0.txt)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC_BY_4.0-lightgrey)](LICENSES/CC-BY-4.0.txt)
[![Status: prototype 1](https://img.shields.io/badge/status-prototype_1-orange)](#status)
[![Hardware 6.4: CAD only](https://img.shields.io/badge/hardware_6.4-CAD_only%2C_not_printed-lightgrey)](#hardware-64)

A DIY, weatherproof kibble dispenser for cats and dogs that you build from 3D-printed parts and off-the-shelf electronics. It hangs under a shelf or a table with the food container on top; a servo in a sealed bay turns a two-pocket disc that drops one portion at a time into a hidden chute, and the electronics live in a detachable, sealed module. The repository contains an ESPHome **draft** for future Home Assistant integration; it has **not been flashed or hardware-tested**. A separate **working ESP32/MicroPython physical prototype already exists**, including physical ON/OFF and dispense buttons, LED, and a meow sound. The proposed outdoor 12 V power architecture is not yet verified as installed.

The owner's MicroPython firmware is the baseline firmware for prototype 1, and ESPHome is the alternative for Home Assistant and OTA later. Its source, as a snapshot of the owner's development folder (not an on-device readback), is in [`firmware/micropython/`](firmware/micropython/README.md). The board is documented as a Freenove ESP32-WROVER (a classic ESP32) in the owner's `PROJECT.md`, to be verified on the device; earlier repository text that said ESP32-S3 was wrong.

## Versions

Hardware, the electronics module, firmware and the sellable product each have their own version line and tags (`hw-v6.4.0`, `case-v1.0.0`, `fw-v0.1.0+dev.20260324`, `product-v…`), published as [GitHub Releases](https://github.com/ricricucit/kibble-dispenser/releases) by a workflow on every push to `main`. The current hardware is 6.4.0 (the chassis) with the electronics module case 1.0 (`case-v1.0.0`), both status designed; it needs the one-button firmware that is still to be written ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)). No product has been released yet. Until the public launch only the latest version of each line is kept in the repository, on the website and in the releases; earlier iterations are in the git history. Bump rules, statuses and compatibility: [VERSIONS.md](VERSIONS.md).

## Physical prototype first: do not overwrite

**The owner already has a working physical dispenser.** Its confirmed core interactions are: ON/OFF button + state LED; exactly one dispense when switched ON; exactly one dispense for each physical dispense-button press while ON; and a meow sound with each dispensing cycle. Before changing hardware, GPIO assignments or firmware, read [the as-built baseline](docs/AS_BUILT_BASELINE.it.md) and [the collaboration instructions](CLAUDE.md). The exact original MicroPython source still needs to be copied **non-destructively** from the ESP32 to [the import area](import/previous-chat/README.md). Historical pin values are provisional until compared against that code and physical wiring.

Update 2026-11-08: the owner's development source ("feedr-outdoor" 0.1.0 plus uncommitted edits of 2026-03-24) is now in [`firmware/micropython/`](firmware/micropython/README.md), byte-for-byte. It is a dev folder snapshot, not a copy read back from the board, so the on-device readback for the import area is still pending. Its `src/config.py` defines LED 2, ON/OFF 13, servo 14, speaker 26 and dispense 27, not yet electrically verified. It boots OFF, so a reset does not dispense, and its sound is now an arcade fanfare instead of the meow.

## Status

Prototype 1, work in progress. The current design, **hardware 6.4, is designed and checked in CAD, not yet printed or tested** (see [Hardware 6.4](#hardware-64)).

- Hardware 6.4 (CAD only): the chassis with the servo in its own sealed bay and a holder for a detachable electronics module, in [`hardware/`](hardware/README.md); the module case 1.0 (with the control panel) in [`hardware/module/`](hardware/module/README.md)
- Prototype 1 on the bench (bought or reused parts): waterproof box (265 x 185 mm), 25 kg·cm servo with a 25-tooth spline, bowl, ESP32-WROVER on a breadboard with two buttons, an LED and a speaker; see [docs/PROTOTYPE_BENCH.md](docs/PROTOTYPE_BENCH.md)
- Firmware: physical prototype runs MicroPython (source recovery pending); a separate ESPHome draft passes config checks but has not been tested on hardware yet
  - MicroPython (baseline): dev folder snapshot in `firmware/micropython/`; the on-device readback is still pending
  - ESPHome (alternative): unflashed draft, now aimed at the classic ESP32 of the documented board
  - hardware 6.4 needs new firmware for its one-button panel, not written yet ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)): single press = one portion (only while ON), double press = ON/OFF, long press 5 s / 10 s = reset; never dispense at power-on (store the last rest position of the disc and return to it at boot), see [VERSIONS.md](VERSIONS.md). The bench prototype keeps its two buttons until then.

## Hardware 6.4

**Designed and checked in CAD only, with an independent print review done: not yet printed, assembled or tested. Its one-button firmware is still to be written ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)).**

1. The v6 mechanism (coaxial servo, hub, shaft and two-pocket disc; the whole unit comes off the shelf with one twist) closed in a smooth, claw-proof pod with the chute hidden inside, and a shut-off gate in the flange with an interlock on the release button.
2. The product splits in two: the chassis (hardware 6.4), with the servo in its own sealed bay, and a detachable electronics module with its own version line (case 1.0). The module slides in from below, locks with two screws and connects with one M8 plug; the electronics can change without reprinting the chassis.
3. The control panel is on the module: one recessed push-button (a fingertip reaches it, a paw or a snout does not), two flush LEDs, a speaker grille facing down and three flush knock-outs. Hang the dispenser with the panel facing you.
4. Everything: about 1076 g of PETG and 9 g of TPU 95A over 13 plates, 44 h of printing (slicer estimates).

The website always shows the current design at these stable addresses, in English, Italian and German:

- 3D model, full screen: <https://ricricucit.github.io/kibble-dispenser/3d/>
- Step-by-step print guide for a Bambu Lab A1 with AMS lite: <https://ricricucit.github.io/kibble-dispenser/print/>, files in [hardware/plates/](hardware/plates/PRINT_GUIDE.md)
- The electronics module (interface, connector, harness, space inside): <https://ricricucit.github.io/kibble-dispenser/module/>, files in [hardware/module/case-1.0/](hardware/module/case-1.0/README.md)
- Bought parts, chassis and module: <https://ricricucit.github.io/kibble-dispenser/parts/>, also in [docs/BOM.md](docs/BOM.md)
- Assembly guide, "Install the kit" and "Build it yourself": <https://ricricucit.github.io/kibble-dispenser/assembly/>
- Manual (A6 booklet and A4 print version) and drilling template: <https://ricricucit.github.io/kibble-dispenser/manual/>, files in [docs/manual/](docs/manual/)
- CAD scripts, viewer meshes, design data, open points: [hardware/](hardware/README.md); print review: [docs/reviews/2026-11-15-v6.4-print-review/](docs/reviews/2026-11-15-v6.4-print-review/README.md)

## Live model

The project site presents the current design in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/>, with the stable pages above.

- The site lives in `site/` (plain HTML, CSS and JavaScript, with three.js r128 bundled in `site/vendor/`, so it loads no third-party scripts or fonts).
- `python site/build.py` builds it into `site/_build/` from the repository: the home page and the manual page with `site/pages.py`, the step-by-step print guide (`site/printguide.py`) and the module page (`site/modulepage.py`), with the texts in `site/content/*.toml` and the numbers from `hardware/plates/summary.json`; the 3D page from `hardware/assembly/` with the generator in `site/viewer/` (meshes decimated into separate STL files); the bought-parts page from `hardware/bom.json` with `site/bom.py`. The assembly guide is copied as built from `site/assembly/`. It needs `pip install numpy fast_simplification pillow`. Preview it locally with `python -m http.server -d site/_build`.
- `.github/workflows/pages.yml` builds and publishes it on every push to `main`.

## How it works

1. The flange set is screwed under the shelf, over a Ø76 hole; the food container sits on top.
2. A shut-off gate in the flange closes the opening under the container; its orange ring uncovers the release button only when the gate is closed.
3. In the bowl, a disc with two pockets turns half a turn per portion: one pocket fills from above while the other empties into the chute. At rest there is no straight path from outside to the container.
4. The servo sits right under the disc in its own sealed bay and drives it through a hub and a sealed shaft, with no gears.
5. The chute runs inside a closed, claw-proof pod and ends in the outlet in its flat bottom.
6. The electronics and the control panel live in a sealed module that slides into the pod from below; one M8 plug connects it. An external 12 V supply feeds the unit through a cable with a waterproof M8 connector.

All of this is designed, not yet printed or tested. The bench prototype (prototype 1) is wired on a breadboard and powered at 5 V, as documented in the owner's `firmware/micropython/PROJECT.md`; the planned 12 V outdoor power is not yet verified as installed.

## Repository map

- `hardware/`: hardware 6.4 ([README](hardware/README.md)): CAD generator scripts and design data (`cad/`), viewer meshes (`assembly/`), the print package (`plates/`), the drilling template (`template/`), `bom.json`, and the electronics module line in `hardware/module/`
- `firmware/`: MicroPython firmware (baseline) in `firmware/micropython/`, ESPHome configuration (alternative) in `firmware/esphome/`, wiring summary and flashing steps ([firmware/README.md](firmware/README.md))
- `docs/`: build guide, bought parts ([BOM.md](docs/BOM.md)), the manuals ([docs/manual/](docs/manual/)), the print review ([docs/reviews/](docs/reviews/)), bench notes, research notes and process photos ([docs/README.md](docs/README.md))
- `site/`: the project website with the live 3D model, the viewer generator (`site/viewer/`), the assembly guide (`site/assembly/`, copied as built), the bought-parts renderer (`site/bom.py`) and the build script
- `LICENSES/` and `REUSE.toml`: licence texts and which licence covers which file
- `.github/`: CI workflow, issue and pull request templates

## Quick links

- **Start here for working hardware and software:** [as-built baseline from prior ChatGPT work](docs/AS_BUILT_BASELINE.it.md)
- **For Claude Code / future collaborators:** [CLAUDE.md](CLAUDE.md)
- **Original firmware import (not yet recovered):** [import/previous-chat/](import/previous-chat/README.md)
- **MicroPython firmware (dev folder snapshot, baseline):** [firmware/micropython/](firmware/micropython/README.md)
- Build guide: [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) (exported from the living build guide; placeholder for now)
- Power, servo and sealing research (Italian): [docs/research/elettronica-e-tenuta.it.md](docs/research/elettronica-e-tenuta.it.md)
- Prototype 1 on the bench (measurements, photo readings, open points): [docs/PROTOTYPE_BENCH.md](docs/PROTOTYPE_BENCH.md)
- Process photos: [docs/photos/](docs/photos/README.md)
- Design notes and print guide: [hardware/README.md](hardware/README.md), [hardware/plates/PRINT_GUIDE.md](hardware/plates/PRINT_GUIDE.md) and [hardware/module/case-1.0/README.md](hardware/module/case-1.0/README.md)
- Bought parts (chassis and module): [docs/BOM.md](docs/BOM.md)
- Wiring and flashing: [firmware/README.md](firmware/README.md)

## Contributing

Issues, build reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Please report security issues privately, as described in [SECURITY.md](SECURITY.md).

## Licence

This project is open source with permissive licences: anyone, the author included, may build, modify, fork and sell it.

- Software (the firmware, including all of `firmware/micropython/` with its Markdown files, the CAD scripts in `hardware/cad/*.py`, the print-package generators in `hardware/plates/tools/`, the scripts of the print reviews, the website code in `site/` including the assembly guide's code, CI and config files): [MIT](LICENSES/MIT.txt). The bundled three.js library (r128) is MIT too.
- Hardware design files (the viewer meshes in `hardware/assembly/`, the JSON design data and reference data in `hardware/cad/`, the print package in `hardware/plates/`, the drilling template in `hardware/template/`, `hardware/bom.json`, the module parts and interface drawing in `hardware/module/`, the assembly guide's meshes): [CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt)
- Documentation and photos (`docs/` with the manuals, the README files and print guides, the website texts in `site/content/`, the assembly guide's step texts, the check image `check_v64.png`, plate previews and other prose): [CC BY 4.0](LICENSES/CC-BY-4.0.txt)

The project follows the [REUSE](https://reuse.software) specification. `REUSE.toml` lists the licence and copyright for every path, and [LICENSE](LICENSE) explains the split in plain words.
