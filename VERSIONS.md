# Versions

The project has four version lines. Each has its own tag and its own GitHub Release, so a printed unit, its electronics module, the firmware on its board and a sold kit can always be matched to each other.

- **Hardware**, tag `hw-vMAJOR.MINOR.PATCH`. Source of truth: [`hardware/VERSION`](hardware/VERSION) (version, status, design folder). A release has four kinds of assets: an STL zip (the print-ready STL files), a plate 3MF zip (Bambu Studio projects and a plain 3MF per plate), both with the print guide, the bought-parts list and the licences, the drilling template (PDF) and the manuals (PDF, `docs/manual/`).
- **Electronics module (case)**, tag `case-vMAJOR.MINOR.PATCH`, from hardware 6.4. Source of truth: [`hardware/module/VERSION`](hardware/module/VERSION) (version, name such as "case 1.0", status, folder, the print package it comes from, the hardware it fits). The module is the detachable, sealed electronics case that slides into the chassis from below; its outside fits the holder interface of the chassis, which is fixed from 6.4 on, and its inside evolves on its own. A release has an STL zip and a plate 3MF zip of the module parts (from the 6.4 print package, with the print guide and the licences), the module folder with its README, and the interface drawing (PDF).
- **Firmware**, tag `fw-vX.Y.Z`. Source of truth: [`firmware/VERSION`](firmware/VERSION). It has to agree with `firmware/micropython/VERSION`, the firmware's own version file, which is kept byte-for-byte as it came from the owner's development folder and is never edited here. A release contains the MicroPython sources. The ESPHome draft in `firmware/esphome/` is not versioned: it stays "draft".
- **Product**, tag `product-vX.Y.Z`. Source of truth: [`product/product.json`](product/product.json), a lock file that pins one hardware tag and one firmware tag, plus the manual, the bill of materials and the kit details (enclosure, packaging). See [`product/README.md`](product/README.md).

Until the public launch the repository, the website and the releases show only the latest version of each line: no archives and no upgrade paths between versions. Version numbers keep rising as usual, and the history lives in git.

Releases: <https://github.com/ricricucit/kibble-dispenser/releases>. The website footer shows the current versions and the commit it was built from.

The module line follows the owner decision of 2026-11-14: the product splits into the chassis (mechanics with a holder for the electronics, the hardware line) and a detachable electronics module (the case line); the servo stays in the chassis. See [hardware/module/README.md](hardware/module/README.md) and [docs/PROTOTYPE_BENCH.md](docs/PROTOTYPE_BENCH.md).

## Bump rules

Hardware follows SemVer, read for physical parts:

- MAJOR: a new architecture, or parts that no longer fit the previous version (a v7 would be 7.0.0).
- MINOR: a compatible design change within the same architecture (6.4.0 to 6.5.0). The design always lives in `hardware/`.
- PATCH: a fix that does not change the fit, such as a print setting, a label or a tolerance inside one part.

The module case follows SemVer for physical parts too: MAJOR when it no longer fits the holder interface of the chassis, MINOR for a compatible change of the case (another board slot, another panel layout), PATCH for a fix that does not change the fit. "case 1.0" is version 1.0.0. Its status follows the same scale as the hardware status below.

Firmware follows SemVer too: MAJOR when the behaviour contract, the pin map or the required hardware changes in a way that breaks a working unit; MINOR for a compatible feature; PATCH for a fix. While the version starts with 0, anything may still change. Build metadata such as `+dev.20260324` marks a snapshot of a development folder that its author has not released as such.

Product: MAJOR for a new hardware major or a kit that is not compatible with the previous one; MINOR when it pins a newer hardware or firmware minor, or adds something to the kit; PATCH for kit-only fixes (packaging, a manual correction).

## Hardware status

Every hardware release carries one status, and the status can rise without a new version. Any change to a part needs a new version.

1. **designed**: modelled and checked in CAD; nothing printed yet.
2. **printed**: every part printed and assembled at least once.
3. **tested**: an assembled unit passes the acceptance checks (closed-box hose test, portions weighed, firmware running on it).
4. **field-proven**: units have run outdoors in real use, through rain, without a fix.

The release title shows the status (for example "Hardware 6.4.0 · designed"). Releases with the status designed or printed, and firmware releases below 1.0.0 or with a pre-release or build suffix, are marked as pre-releases on GitHub.

## How a release is made

1. Bump the version file (`hardware/VERSION`, `hardware/module/VERSION`, `firmware/VERSION` or `product/product.json`) and update [`CHANGELOG.md`](CHANGELOG.md). Until the public launch it has a single section, `## [pre-launch]`, that describes the current state, with one `### ` part per line (Hardware, Electronics module, Firmware, Product); after the launch each release gets a section named after its tag, for example `## [hw-v7.0.0] - 2027-03-01`.
2. Push to `main`. The workflow [`release.yml`](.github/workflows/release.yml) runs [`tools/release.py`](tools/release.py): for each line whose tag does not exist yet it creates an annotated tag and a GitHub Release with the assets. The notes describe the current state of the line: the section named after the tag when there is one, otherwise the pre-launch section (its first paragraph and the part for the line).
3. A new tag points at the commit that brings the new version to `main` (the head of the push), and the assets are read from that commit. The release notes also name the last commit that changed the line's files (`hardware/` or `firmware/micropython/`), when that is an earlier one. The workflow cannot tag older commits: GitHub refuses to let the workflow's token create a ref on a commit whose workflow files differ from `main`.

   The firmware tag `fw-v0.1.0+dev.20260324` was backfilled this way right after the version lines were introduced: it points at commit `b74b26c`, and its files are the same as in commit `b6b40bf` (the firmware import).
4. A product release only goes out when the pinned hardware and firmware tags exist and the hardware status is tested or field-proven.

Run `python tools/release.py` (a dry run: it prints the plan and builds the assets in a temporary folder, without tagging) to check a release before you push. The workflow can also be started by hand from the Actions tab.

## Compatibility

| Hardware | Status | Module | Firmware | Product |
|---|---|---|---|---|
| `hw-v6.4.0` (hardware 6.4, chassis) | designed | `case-v1.0.0` (case 1.0, designed): the first module, it fits the holder interface of 6.4; later cases 1.x fit too | **Needs the one-button firmware of [issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2), which does not exist yet**: single press = one portion (only while ON), double press = ON/OFF (switching ON dispenses one portion), long press 5 s = reset everything except Wi-Fi, 10 s = full reset, a sound at every portion, never dispense at power-on (store and restore the last rest position). The panel (one button, two LEDs, speaker) is on the module. `fw-v0.1.0+dev.20260324` is two-button firmware for the bench prototype and is not to be flashed for 6.4. Its speaker and dispense pins (GPIO 26, 27) are camera pins of the WROVER board ([issue #3](https://github.com/ricricucit/kibble-dispenser/issues/3)); prototype 1 has no camera. The disc zero has to be set after assembly. | `product-v1.0.0` will pin the first tested hardware, module and firmware |
