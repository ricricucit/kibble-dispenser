# Kibble Dispenser

[![Software: MIT](https://img.shields.io/badge/software-MIT-blue)](LICENSES/MIT.txt)
[![Hardware: CERN-OHL-P-2.0](https://img.shields.io/badge/hardware-CERN--OHL--P--2.0-blue)](LICENSES/CERN-OHL-P-2.0.txt)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC_BY_4.0-lightgrey)](LICENSES/CC-BY-4.0.txt)
[![Status: prototype 1](https://img.shields.io/badge/status-prototype_1-orange)](#status)

A DIY, weatherproof cat-kibble dispenser you can build from 3D-printed parts and off-the-shelf electronics. The kibble sits in a container above a bowl. A servo inside a sealed box turns a disc in the bowl to release one portion at a time, and a chute carries it out. The servo is driven by an ESP32 running ESPHome, so the feeder shows up in Home Assistant. Everything runs on low voltage from an external 12 V adapter, which suits a box that lives outdoors.

## Status

Prototype 1, work in progress.

- Designed and exported: rotating disc, shaft and hub, sealed shaft bushing, spline fit test, chute
- Bought or reused: waterproof box (265 x 185 mm), 25 kg·cm servo with a 25-tooth spline, bowl
- Still to design: servo cradle, hopper and shelf, container
- Firmware: first ESPHome draft; it passes the config check but has not been tested on hardware yet

## How it works

1. A container holds the kibble.
2. A hopper funnels it into the bowl.
3. In the bowl, a disc with a trapezoid opening rotates 180° to let one portion through.
4. The portion leaves through the chute.
5. The servo hangs from the underside of the box lid. It drives a printed shaft that passes through the lid in a sealed bushing (O-rings), so water and crumbs stay out of the box.
6. An ESP32 inside the box drives the servo. Power comes from an external 12 V adapter; the box only ever sees low voltage.

## Repository map

- `hardware/`: CAD generator scripts, print-ready STLs, 3MF files and per-part print notes ([hardware/README.md](hardware/README.md))
- `firmware/`: ESPHome configuration, wiring summary and flashing steps ([firmware/README.md](firmware/README.md))
- `docs/`: build guide, research notes and process photos ([docs/README.md](docs/README.md))
- `LICENSES/` and `REUSE.toml`: licence texts and which licence covers which file
- `.github/`: CI workflow, issue and pull request templates

## Quick links

- Build guide: [docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md) (exported from the living build guide; placeholder for now)
- Power, servo and sealing research (Italian): [docs/research/elettronica-e-tenuta.it.md](docs/research/elettronica-e-tenuta.it.md)
- Process photos: [docs/photos/](docs/photos/README.md)
- Print notes: [hardware/README.md](hardware/README.md)
- Wiring and flashing: [firmware/README.md](firmware/README.md)

## Contributing

Issues, build reports and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md). Please report security issues privately, as described in [SECURITY.md](SECURITY.md).

## Licence

This project is open source with permissive licences: anyone, the author included, may build, modify, fork and sell it.

- Software (the firmware, the CAD scripts in `hardware/cad/*.py`, CI and config files): [MIT](LICENSES/MIT.txt)
- Hardware design files (`hardware/stl/`, `hardware/3mf/`, the JSON design data in `hardware/cad/`): [CERN-OHL-P-2.0](LICENSES/CERN-OHL-P-2.0.txt)
- Documentation and photos (`docs/`, the README files and other prose): [CC BY 4.0](LICENSES/CC-BY-4.0.txt)

The project follows the [REUSE](https://reuse.software) specification. `REUSE.toml` lists the licence and copyright for every path, and [LICENSE](LICENSE) explains the split in plain words.
