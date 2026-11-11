# Kibble Dispenser

[![Software: MIT](https://img.shields.io/badge/software-MIT-blue)](LICENSES/MIT.txt)
[![Hardware: CERN-OHL-P-2.0](https://img.shields.io/badge/hardware-CERN--OHL--P--2.0-blue)](LICENSES/CERN-OHL-P-2.0.txt)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC_BY_4.0-lightgrey)](LICENSES/CC-BY-4.0.txt)
[![Status: prototype 1](https://img.shields.io/badge/status-prototype_1-orange)](#status)
[![Design v6.3: CAD only](https://img.shields.io/badge/design_v6.3-CAD_only%2C_not_printed-lightgrey)](#design-v63)

A DIY, weatherproof cat-kibble dispenser you can build from 3D-printed parts and off-the-shelf electronics. The kibble sits in a container above a bowl. A servo inside a sealed box turns a disc in the bowl to release one portion at a time, and a chute carries it out. The repository contains an ESPHome **draft** for future Home Assistant integration; it has **not been flashed or hardware-tested**. A separate **working ESP32/MicroPython physical prototype already exists**, including physical ON/OFF and dispense buttons, LED, and a meow sound. The proposed outdoor 12 V power architecture is not yet verified as installed.

The owner's MicroPython firmware is the baseline firmware for prototype 1, and ESPHome is the alternative for Home Assistant and OTA later. Its source, as a snapshot of the owner's development folder (not an on-device readback), is in [`firmware/micropython/`](firmware/micropython/README.md). The board is documented as a Freenove ESP32-WROVER (a classic ESP32) in the owner's `PROJECT.md`, to be verified on the device; earlier repository text that said ESP32-S3 was wrong.

## Versions

Hardware, firmware and the sellable product each have their own version line and tags (`hw-v6.3.0`, `fw-v0.1.0+dev.20260324`, `product-v…`), published as [GitHub Releases](https://github.com/ricricucit/kibble-dispenser/releases) by a workflow on every push to `main`. Design v6.3 is hardware 6.3.0, status designed (the earlier designs are `hw-v6.2.0` and `hw-v6.0.0`); it needs the one-button firmware that is still to be written ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)). No product has been released yet. Bump rules, statuses and the compatibility table: [VERSIONS.md](VERSIONS.md).

## Physical prototype first: do not overwrite

**The owner already has a working physical dispenser.** Its confirmed core interactions are: ON/OFF button + state LED; exactly one dispense when switched ON; exactly one dispense for each physical dispense-button press while ON; and a meow sound with each dispensing cycle. Before changing hardware, GPIO assignments or firmware, read [the as-built baseline](docs/AS_BUILT_BASELINE.it.md) and [the collaboration instructions](CLAUDE.md). The exact original MicroPython source still needs to be copied **non-destructively** from the ESP32 to [the import area](import/previous-chat/README.md). Historical pin values are provisional until compared against that code and physical wiring.

Update 2026-11-08: the owner's development source ("feedr-outdoor" 0.1.0 plus uncommitted edits of 2026-03-24) is now in [`firmware/micropython/`](firmware/micropython/README.md), byte-for-byte. It is a dev folder snapshot, not a copy read back from the board, so the on-device readback for the import area is still pending. Its `src/config.py` defines LED 2, ON/OFF 13, servo 14, speaker 26 and dispense 27, not yet electrically verified. It boots OFF, so a reset does not dispense, and its sound is now an arcade fanfare instead of the meow.

## Status

Prototype 1, work in progress. The current design, **v6.3, is designed and checked in CAD, not yet printed or tested** (see [Design v6.3](#design-v63)).

- Design v6.3 (current design, CAD only): closed pod, shut-off gate, control panel with one recessed push-button and two LEDs, no cable channel, in [`hardware/v6.3/`](hardware/v6.3/README.md)
- Design v6.2 (hardware 6.2.0, archived, never printed): closed pod, shut-off gate, cable channel, in [`hardware/v6.2/`](hardware/v6.2/README.md)
- Design v6 (hardware 6.0.0, archived, never printed): the one-twist unit in [`hardware/v6/`](hardware/v6/README.md)
- Designed and exported, superseded (not printed or mounted): drivetrain v3 with the rotating disc and its labyrinth cap, shaft and hub, sealed bushing with built-in servo cradle (`passante_culla`), spline fit test; chute
- Bought or reused: waterproof box (265 x 185 mm), 25 kg·cm servo with a 25-tooth spline, bowl
- Firmware: physical prototype runs MicroPython (source recovery pending); a separate ESPHome draft passes config checks but has not been tested on hardware yet
  - MicroPython (baseline): dev folder snapshot in `firmware/micropython/`; the on-device readback is still pending
  - ESPHome (alternative): unflashed draft, now aimed at the classic ESP32 of the documented board
  - v6.3 needs new firmware for its one-button panel, not written yet ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)): single press = one portion (only while ON), double press = ON/OFF, long press 5 s / 10 s = reset; never dispense at power-on (store the last rest position of the disc and return to it at boot), see [VERSIONS.md](VERSIONS.md). The bench prototype keeps its two buttons until then.

## Design v6.3

**Designed and checked in CAD only: not yet printed, assembled or tested. Its one-button firmware is still to be written ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)).**

1. The v6 mechanism (coaxial servo, hub, shaft and two-pocket disc; the whole unit comes off the shelf with one twist) closed in a smooth, claw-proof pod with the chute hidden inside.
2. A shut-off gate in the flange, turned by an orange ring round the top of the pod; the ring frees the release button only when the gate is closed, so the unit cannot come down while food can fall out.
3. A control panel on the room side of the cap: one recessed push-button (a fingertip reaches it, a paw or a snout does not), two flush LEDs, a sealed speaker opening facing down and three flush knock-outs for future switches.
4. Simpler: 28 printed pieces instead of 36, no cable channel (the cable leaves the flange at the back, held by a cable tie), three screws instead of the thumb-turns on the cap; about 1000 g of PETG and 8 g of TPU 95A over 9 plates, 18 colour swaps (slicer estimate). The planned kit is the pre-assembled unit and the flange set.

The website always shows the current design at these stable addresses, in English, Italian and German:

- 3D model, full screen: <https://ricricucit.github.io/kibble-dispenser/3d/>
- Print files for a Bambu Lab A1 with AMS lite: <https://ricricucit.github.io/kibble-dispenser/print/>, files in [hardware/v6.3/plates/](hardware/v6.3/plates/README.md)
- Bought parts: <https://ricricucit.github.io/kibble-dispenser/parts/>, also in [docs/BOM.md](docs/BOM.md)
- Assembly guide, "Install the kit" and "Build it yourself": <https://ricricucit.github.io/kibble-dispenser/assembly/>
- Manual (A6 booklet and A4 print version) and drilling template: <https://ricricucit.github.io/kibble-dispenser/manual/>, files in [docs/manual/](docs/manual/)
- CAD scripts, viewer meshes, design data, open points: [hardware/v6.3/](hardware/v6.3/README.md)
- Earlier designs, archived: v6.2 at <https://ricricucit.github.io/kibble-dispenser/v6.2/>, v6 at <https://ricricucit.github.io/kibble-dispenser/v6/>

## Live model

The project site presents the current design in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/>, with the stable pages above. Earlier designs keep versioned pages: design v6.2 at <https://ricricucit.github.io/kibble-dispenser/v6.2/>, design v6 at <https://ricricucit.github.io/kibble-dispenser/v6/>, and prototype 1 with its live 3D model (orbit, section, exploded view, servo angle) on the earlier-versions page: <https://ricricucit.github.io/kibble-dispenser/earlier/>.

- The site lives in `site/` (plain HTML, CSS and JavaScript, with three.js bundled in `site/vendor/`, so it loads no third-party scripts or fonts).
- `python site/build.py` builds it into `site/_build/` from the repository: the home page, the print-files pages, the manual pages and the v6.2 and v6 archive pages with `site/pages.py` (texts in `site/content/*.toml`, numbers from the plates' `summary.json`), the 3D pages from `hardware/v6.3/assembly/`, `hardware/v6.2/assembly/` and `hardware/v6/assembly/` with the generator in `site/viewer/` (meshes decimated into separate STL files, three.js r128), the bought-parts pages from the `bom.json` files with `site/bom.py`, and the earlier-versions page. The assembly guides are copied as built from `site/assembly/` (v6.3) and `site/v6.2/assembly/`. It needs `pip install numpy fast_simplification pillow`. Preview it locally with `python -m http.server -d site/_build`.
- `.github/workflows/pages.yml` builds and publishes it on every push to `main`.

## How it works

1. A container holds the kibble.
2. A hopper funnels it into the bowl.
3. In the bowl, a disc with a trapezoid opening rotates 180° to let one portion through.
4. The portion leaves through the chute.
5. **Planned sealed design:** servo hangs from the underside of the box lid, driving a printed shaft through a sealed bushing (O-rings). The earlier physically mounted side/wall servo support and spacer must be reconciled first. The design now has the cradle built into the bushing (`passante_culla`, drivetrain v3); it is designed, not printed or mounted, and the prototype still uses the third-party wall bracket, which stays out of the repository (CC BY-NC-SA).
6. **Planned outdoor electrical design:** an ESP32 drives the servo from a separately regulated branch of an external 12 V supply, so the enclosure sees low voltage. This does not imply the current wired prototype already uses these parts. The owner's `firmware/micropython/PROJECT.md` documents a 5 V bench supply for the prototype.

## Repository map

- `hardware/`: CAD generator scripts, print-ready STLs, 3MF files, assembly meshes for the 3D viewer and per-part print notes ([hardware/README.md](hardware/README.md)); design v6.3 (current) in `hardware/v6.3/` ([README](hardware/v6.3/README.md)), designs v6.2 and v6 (archived) in `hardware/v6.2/` and `hardware/v6/`
- `firmware/`: MicroPython firmware (baseline) in `firmware/micropython/`, ESPHome configuration (alternative) in `firmware/esphome/`, wiring summary and flashing steps ([firmware/README.md](firmware/README.md))
- `docs/`: build guide, bought parts of v6.3 ([BOM.md](docs/BOM.md)), v6.2 ([BOM-v6.2.md](docs/BOM-v6.2.md)) and v6 ([BOM-v6.md](docs/BOM-v6.md)), the v6.3 manuals ([docs/manual/](docs/manual/)), research notes and process photos ([docs/README.md](docs/README.md))
- `site/`: the project website with the live 3D models, the viewer generator (`site/viewer/`), the assembly guide (`site/assembly/`, copied as built), the bought-parts renderer (`site/bom.py`) and the build script
- `LICENSES/` and `REUSE.toml`: licence texts and which licence covers which file
- `.github/`: CI workflow, issue and pull request templates

## Quick links

- **Start here for working hardware and software:** [as-built baseline from prior ChatGPT work](docs/AS_BUILT_BASELINE.it.md)
- **For Claude Code / future collaborators:** [CLAUDE.md](CLAUDE.md)
- **Original firmware import (not yet recovered):** [import/previous-chat/](import/previous-chat/README.md)
- **MicroPython firmware (dev folder snapshot, baseline):** [firmware/micropython/](firmware/micropython/README.md)
- Build guide: [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) (exported from the living build guide; placeholder for now)
- Power, servo and sealing research (Italian): [docs/research/elettronica-e-tenuta.it.md](docs/research/elettronica-e-tenuta.it.md)
- Process photos: [docs/photos/](docs/photos/README.md)
- Design notes and print guide: [hardware/v6.3/README.md](hardware/v6.3/README.md) and [hardware/v6.3/plates/README.md](hardware/v6.3/plates/README.md) (v6.3), [hardware/v6.2/README.md](hardware/v6.2/README.md) (v6.2, archived), [hardware/v6/README.md](hardware/v6/README.md) (v6, archived), [hardware/README.md](hardware/README.md) (prototype 1)
- Bought parts for v6.3: [docs/BOM.md](docs/BOM.md)
- Wiring and flashing: [firmware/README.md](firmware/README.md)

## Contributing

Issues, build reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Please report security issues privately, as described in [SECURITY.md](SECURITY.md).

## Licence

This project is open source with permissive licences: anyone, the author included, may build, modify, fork and sell it.

- Software (the firmware, including all of `firmware/micropython/` with its Markdown files, the CAD scripts in `hardware/cad/*.py`, `hardware/v6/cad/*.py`, `hardware/v6.2/cad/*.py` and `hardware/v6.3/cad/*.py`, the print-package generators in `plates/tools/`, the website code in `site/` including the assembly guide's code, CI and config files): [MIT](LICENSES/MIT.txt). The bundled three.js libraries (0.160.1 and r128) are MIT too.
- Hardware design files (`hardware/stl/`, `hardware/3mf/`, `hardware/assembly/`, the JSON design data in `hardware/cad/`, the same folders plus `bom.json` in `hardware/v6/`, and in `hardware/v6.2/` and `hardware/v6.3/` the viewer meshes, design data, print package, drilling template and `bom.json`; the assembly guide's meshes): [CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt)
- Documentation and photos (`docs/` with the manuals, the README files and print guides, the website texts in `site/content/`, the assembly guide's step texts, the check images `check_v6.png` and `check_v62.png`, plate previews and other prose): [CC BY 4.0](LICENSES/CC-BY-4.0.txt)

The project follows the [REUSE](https://reuse.software) specification. `REUSE.toml` lists the licence and copyright for every path, and [LICENSE](LICENSE) explains the split in plain words.
