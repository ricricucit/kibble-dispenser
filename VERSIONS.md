# Versions

The project has three version lines. Each has its own tag and its own GitHub Release, so a printed unit, the firmware on its board and a sold kit can always be matched to each other.

- **Hardware**, tag `hw-vMAJOR.MINOR.PATCH`. Source of truth: [`hardware/VERSION`](hardware/VERSION) (version, status, design folder). A release contains the design folder's STL files, the plate 3MFs and print guide, the bought-parts list, and the manuals (PDF) once they exist.
- **Firmware**, tag `fw-vX.Y.Z`. Source of truth: [`firmware/VERSION`](firmware/VERSION). It has to agree with `firmware/micropython/VERSION`, the firmware's own version file, which is kept byte-for-byte as it came from the owner's development folder and is never edited here. A release contains the MicroPython sources. The ESPHome draft in `firmware/esphome/` is not versioned: it stays "draft".
- **Product**, tag `product-vX.Y.Z`. Source of truth: [`product/product.json`](product/product.json), a lock file that pins one hardware tag and one firmware tag, plus the manual, the bill of materials and the kit details (enclosure, packaging). See [`product/README.md`](product/README.md).

Releases: <https://github.com/ricricucit/kibble-dispenser/releases>. The website footer shows the current versions and the commit it was built from.

## Bump rules

Hardware follows SemVer, read for physical parts:

- MAJOR: a new architecture, or parts that no longer fit the previous version (design v6 is 6.0.0; a v7 would be 7.0.0).
- MINOR: a compatible design change: the parts still fit the other parts of the same major (v6.1, now in design, will be 6.1.0).
- PATCH: a fix that does not change the fit, such as a print setting, a label or a tolerance inside one part.

Firmware follows SemVer too: MAJOR when the behaviour contract, the pin map or the required hardware changes in a way that breaks a working unit; MINOR for a compatible feature; PATCH for a fix. While the version starts with 0, anything may still change. Build metadata such as `+dev.20260324` marks a snapshot of a development folder that its author has not released as such.

Product: MAJOR for a new hardware major or a kit that is not compatible with the previous one; MINOR when it pins a newer hardware or firmware minor, or adds something to the kit; PATCH for kit-only fixes (packaging, a manual correction).

## Hardware status

Every hardware release carries one status, and the status can rise without a new version. Any change to a part needs a new version.

1. **designed**: modelled and checked in CAD; nothing printed yet.
2. **printed**: every part printed and assembled at least once.
3. **tested**: an assembled unit passes the acceptance checks (closed-box hose test, portions weighed, firmware running on it).
4. **field-proven**: units have run outdoors in real use, through rain, without a fix.

The release title shows the status (for example "Hardware 6.0.0 · designed"). Releases with the status designed or printed, and firmware releases below 1.0.0 or with a pre-release or build suffix, are marked as pre-releases on GitHub.

## How a release is made

1. Bump the version file (`hardware/VERSION`, `firmware/VERSION` or `product/product.json`) and add a section named after the tag to [`CHANGELOG.md`](CHANGELOG.md), for example `## [hw-v6.1.0] - 2026-12-01`.
2. Push to `main`. The workflow [`release.yml`](.github/workflows/release.yml) runs [`tools/release.py`](tools/release.py): for each line whose tag does not exist yet it creates an annotated tag and a GitHub Release with the assets, and takes the notes from the matching CHANGELOG section.
3. A new tag points at the commit that brings the new version to `main` (the head of the push), and the assets are read from that commit. The release notes also name the last commit that changed the line's files (`hardware/` or `firmware/micropython/`), when that is an earlier one. The workflow cannot tag older commits: GitHub refuses to let the workflow's token create a ref on a commit whose workflow files differ from `main`.

   The first two tags were backfilled this way when the version lines were introduced: `hw-v6.0.0` and `fw-v0.1.0+dev.20260324` point at that commit, and their files are the same as in commit `58943c9` (design v6 with its print plates) and commit `b6b40bf` (the firmware import).
4. A product release only goes out when the pinned hardware and firmware tags exist and the hardware status is tested or field-proven.

Run `python tools/release.py` (a dry run: it prints the plan and builds the assets in a temporary folder, without tagging) to check a release before you push. The workflow can also be started by hand from the Actions tab.

## Compatibility

| Hardware | Status | Firmware | Product |
|---|---|---|---|
| prototype 1 (bench, not tagged) | built | `fw-v0.1.0+dev.20260324`: the development source; the copy flashed on the board has not been read back yet | none |
| `hw-v6.0.0` (design v6) | designed | `fw-v0.1.0+dev.20260324` expected (same pins and behaviour), not run on v6 yet; the disc zero has to be set after assembly | none |
| `hw-v6.1.0` (v6.1, in design) | not released | to be decided | `product-v1.0.0` will pin the first tested hardware and firmware pair |
