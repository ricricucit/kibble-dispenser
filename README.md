# Kibble Dispenser

[![Software: MIT](https://img.shields.io/badge/software-MIT-blue)](LICENSES/MIT.txt)
[![Hardware: CERN-OHL-P-2.0](https://img.shields.io/badge/hardware-CERN--OHL--P--2.0-blue)](LICENSES/CERN-OHL-P-2.0.txt)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC_BY_4.0-lightgrey)](LICENSES/CC-BY-4.0.txt)
[![Status: prototype 1](https://img.shields.io/badge/status-prototype_1-orange)](#status)
[![Design v6: CAD only](https://img.shields.io/badge/design_v6-CAD_only%2C_not_printed-lightgrey)](#design-v6)

A DIY, weatherproof cat-kibble dispenser you can build from 3D-printed parts and off-the-shelf electronics. The kibble sits in a container above a bowl. A servo inside a sealed box turns a disc in the bowl to release one portion at a time, and a chute carries it out. The repository contains an ESPHome **draft** for future Home Assistant integration; it has **not been flashed or hardware-tested**. A separate **working ESP32/MicroPython physical prototype already exists**, including physical ON/OFF and dispense buttons, LED, and a meow sound. The proposed outdoor 12 V power architecture is not yet verified as installed.

The owner's MicroPython firmware is the baseline firmware for prototype 1, and ESPHome is the alternative for Home Assistant and OTA later. Its source, as a snapshot of the owner's development folder (not an on-device readback), is in [`firmware/micropython/`](firmware/micropython/README.md). The board is documented as a Freenove ESP32-WROVER (a classic ESP32) in the owner's `PROJECT.md`, to be verified on the device; earlier repository text that said ESP32-S3 was wrong.

## Versions

Hardware, firmware and the sellable product each have their own version line and tags (`hw-v6.0.0`, `fw-v0.1.0+dev.20260324`, `product-v…`), published as [GitHub Releases](https://github.com/ricricucit/kibble-dispenser/releases) by a workflow on every push to `main`. Design v6 is hardware 6.0.0, status designed; no product has been released yet. Bump rules, statuses and the compatibility table: [VERSIONS.md](VERSIONS.md).

## Physical prototype first: do not overwrite

**The owner already has a working physical dispenser.** Its confirmed core interactions are: ON/OFF button + state LED; exactly one dispense when switched ON; exactly one dispense for each physical dispense-button press while ON; and a meow sound with each dispensing cycle. Before changing hardware, GPIO assignments or firmware, read [the as-built baseline](docs/AS_BUILT_BASELINE.it.md) and [the collaboration instructions](CLAUDE.md). The exact original MicroPython source still needs to be copied **non-destructively** from the ESP32 to [the import area](import/previous-chat/README.md). Historical pin values are provisional until compared against that code and physical wiring.

Update 2026-11-08: the owner's development source ("feedr-outdoor" 0.1.0 plus uncommitted edits of 2026-03-24) is now in [`firmware/micropython/`](firmware/micropython/README.md), byte-for-byte. It is a dev folder snapshot, not a copy read back from the board, so the on-device readback for the import area is still pending. Its `src/config.py` defines LED 2, ON/OFF 13, servo 14, speaker 26 and dispense 27, not yet electrically verified. It boots OFF, so a reset does not dispense, and its sound is now an arcade fanfare instead of the meow.

## Status

Prototype 1, work in progress. The next design, v6, is designed and checked in CAD, **not yet printed or tested** (see [Design v6](#design-v6)).

- Design v6 (current design, CAD only): the one-twist unit in [`hardware/v6/`](hardware/v6/README.md)
- Designed and exported, superseded as the design by v6 (not printed or mounted): drivetrain v3 with the rotating disc and its labyrinth cap, shaft and hub, sealed bushing with built-in servo cradle (`passante_culla`), spline fit test; chute
- Bought or reused: waterproof box (265 x 185 mm), 25 kg·cm servo with a 25-tooth spline, bowl
- Still to design: hopper and shelf, container
- Firmware: physical prototype runs MicroPython (source recovery pending); a separate ESPHome draft passes config checks but has not been tested on hardware yet
  - MicroPython (baseline): dev folder snapshot in `firmware/micropython/`; the on-device readback is still pending
  - ESPHome (alternative): unflashed draft, now aimed at the classic ESP32 of the documented board

## Design v6

**Designed and checked in CAD only: not yet printed, assembled or tested.**

1. A one-twist unit: the bowl with its rotary disc, the chute, the sealed tower and shaft, and the electronics box with the servo hang together and come off the shelf with one quarter-turn; only the shelf flange stays screwed on.
2. Coaxial drive (servo, hub, shaft, disc), every wet/dry joint sealed with an O-ring or a TPU seal, one cable gland, and a box cover that closes with four printed quarter-turn buttons.
3. 12 new printed parts plus 9 reused ones (about 610 g of PETG and TPU), 17 screws, 12 heat-set inserts and 3 O-rings; the kit ships the electronics box pre-assembled.

- 3D model, full screen, in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/v6/3d/>
- Bought parts (screws, seals, electronics module, tools), in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/v6/parts/>, also in [docs/BOM.md](docs/BOM.md)
- CAD scripts, print-ready STL and 3MF, design data and print notes: [hardware/v6/](hardware/v6/README.md)
- Print plates for a Bambu Lab A1 with AMS lite (preview, v6.1 will replace them): <https://ricricucit.github.io/kibble-dispenser/v6/print/>, files in [hardware/v6/plates/](hardware/v6/plates/README.md)
- Step-by-step assembly wizard (English, Italian, German): coming soon
- Pocket manual, A6 PDF: coming soon

## Live model

The project site presents design v6 in English, Italian and German: <https://ricricucit.github.io/kibble-dispenser/>. Design v6 has its own full-screen 3D page, with a workshop view and a view in the woods: <https://ricricucit.github.io/kibble-dispenser/v6/3d/>, and a print-files page: <https://ricricucit.github.io/kibble-dispenser/v6/print/>. The prototype 1 assembly, as a 3D model you can orbit, cut in section, explode and run, is on the earlier-versions page: <https://ricricucit.github.io/kibble-dispenser/earlier/>.

- The site lives in `site/` (plain HTML, CSS and JavaScript, with three.js bundled in `site/vendor/three/`, so it loads no third-party scripts or fonts).
- `python site/build.py` writes the home page and the v6 print-files page with `site/pages.py` (texts in `site/content/*.toml`, numbers from `hardware/v6/plates/summary.json` and `hardware/v6/cad/v6.json`, downloads from `hardware/v6/plates/`), and copies the prototype 1 assembly meshes from `hardware/assembly/` and the process photos into `site/_build/`, so the site always matches the repository. Preview it locally with `python -m http.server -d site/_build`.
- The same build writes the v6 pages: the 3D page from `hardware/v6/assembly/` with the generator in `site/viewer/` (meshes decimated into separate STL files, three.js r128 bundled in `site/vendor/three-r128/`), and the bought-parts page from `hardware/v6/bom.json` with `site/bom.py`. It needs `pip install numpy fast_simplification`. `python site/viewer/make_viewer.py MANIFEST OUT.html` also writes a single-file preview with the meshes embedded.
- `.github/workflows/pages.yml` builds and publishes it on every push to `main`. GitHub Pages has to be enabled once by the owner: Settings > Pages > Source: GitHub Actions. A Pages site is always public, and Pages on a private repository needs a paid GitHub plan.

## How it works

1. A container holds the kibble.
2. A hopper funnels it into the bowl.
3. In the bowl, a disc with a trapezoid opening rotates 180° to let one portion through.
4. The portion leaves through the chute.
5. **Planned sealed design:** servo hangs from the underside of the box lid, driving a printed shaft through a sealed bushing (O-rings). The earlier physically mounted side/wall servo support and spacer must be reconciled first. The design now has the cradle built into the bushing (`passante_culla`, drivetrain v3); it is designed, not printed or mounted, and the prototype still uses the third-party wall bracket, which stays out of the repository (CC BY-NC-SA).
6. **Planned outdoor electrical design:** an ESP32 drives the servo from a separately regulated branch of an external 12 V supply, so the enclosure sees low voltage. This does not imply the current wired prototype already uses these parts. The owner's `firmware/micropython/PROJECT.md` documents a 5 V bench supply for the prototype.

## Repository map

- `hardware/`: CAD generator scripts, print-ready STLs, 3MF files, assembly meshes for the 3D viewer and per-part print notes ([hardware/README.md](hardware/README.md)); design v6 in `hardware/v6/` ([README](hardware/v6/README.md))
- `firmware/`: MicroPython firmware (baseline) in `firmware/micropython/`, ESPHome configuration (alternative) in `firmware/esphome/`, wiring summary and flashing steps ([firmware/README.md](firmware/README.md))
- `docs/`: build guide, bought parts of v6 ([BOM.md](docs/BOM.md)), research notes and process photos ([docs/README.md](docs/README.md))
- `site/`: the project website with the live 3D models, the v6 viewer generator (`site/viewer/`), the bought-parts renderer (`site/bom.py`) and the build script
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
- Print notes: [hardware/v6/README.md](hardware/v6/README.md) (v6), [hardware/README.md](hardware/README.md) (prototype 1)
- Bought parts for v6: [docs/BOM.md](docs/BOM.md)
- Wiring and flashing: [firmware/README.md](firmware/README.md)

## Contributing

Issues, build reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Please report security issues privately, as described in [SECURITY.md](SECURITY.md).

## Licence

This project is open source with permissive licences: anyone, the author included, may build, modify, fork and sell it.

- Software (the firmware, including all of `firmware/micropython/` with its Markdown files, the CAD scripts in `hardware/cad/*.py` and `hardware/v6/cad/*.py`, the website code in `site/`, CI and config files): [MIT](LICENSES/MIT.txt). The bundled three.js libraries (0.160.1 and r128) are MIT too.
- Hardware design files (`hardware/stl/`, `hardware/3mf/`, `hardware/assembly/`, the JSON design data in `hardware/cad/`, and the same folders plus `bom.json` in `hardware/v6/`): [CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt)
- Documentation and photos (`docs/`, the README files, the website text in `site/index.html`, the v6 check image `hardware/v6/cad/check_v6.png` and other prose): [CC BY 4.0](LICENSES/CC-BY-4.0.txt)

The project follows the [REUSE](https://reuse.software) specification. `REUSE.toml` lists the licence and copyright for every path, and [LICENSE](LICENSE) explains the split in plain words.
