# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project has no versioned releases yet. The MicroPython firmware keeps its own version in `firmware/micropython/VERSION`; its history before the import is under [feedr-outdoor 0.1.0](#feedr-outdoor-010---2026-03-24) at the end of this file.

## [Unreleased]

### Added

- 2026-11-08: MicroPython firmware, the baseline firmware for prototype 1, in `firmware/micropython/`.
  - Imported byte-for-byte from a snapshot of the owner's development folder for "feedr-outdoor": version 0.1.0 plus the uncommitted edits of 2026-03-24 (see Changed). Not an on-device readback; that readback is still pending for `import/previous-chat/`.
  - Modular `src/` (config, hardware, servo, speaker, buttons, dispenser, main), the original single-file prototype as `legacy/CatFeeder.py`, `PROJECT.md`, `CLAUDE.md`, `Makefile` (mpremote), `ruff.toml`, `requirements.txt`, `VERSION`.
  - New `firmware/micropython/README.md`: provenance, behaviour, pin map as defined in the dev source (not yet electrically verified), 5 V bench power, quick start, calibration.
  - CI lints the firmware with ruff (I001 and E402 ignored until the imported code is tidied in a separate commit). `REUSE.toml` covers `firmware/micropython/**` as MIT.
- 2026-11-08: As-built baseline (`docs/AS_BUILT_BASELINE.it.md`), collaboration notes (`CLAUDE.md`), import area for the on-device firmware (`import/previous-chat/`) and a "physical prototype first" section in the README, from the ChatGPT contributor; extended with the firmware import, the board correction and the licence of the third-party wall bracket (CC BY-NC-SA, prototype only, not in the repository).
- 2026-11-08: Project website with a live 3D model of the assembly (orbit, full screen, section, exploded view, servo angle, part isolation), published to GitHub Pages.
  - `site/`: static page, CSS and JavaScript modules, with three.js 0.160.1 bundled in `site/vendor/three/`; `site/build.py` builds it from the repository.
  - `hardware/cad/build_assembly.py` and `hardware/assembly/`: assembly-frame meshes and `assembly.json` for the viewer.
  - `.github/workflows/pages.yml`, plus a site build check in CI. `check_meshes.py` also checks the assembly meshes.
- 2026-11-08: Initial import of prototype 1.
  - Drivetrain parts: rotating disc (disco_v3), shaft and hub (albero_mozzo), sealed bushing (passante_stagno), spline fit test (test_scanalato), with the `build_drivetrain.py` generator, `layout_v3.json` and `drivetrain.json`.
  - Chute (scivolo_v1) with the `build_disc_v2_chute.py` generator.
  - Print-ready STLs, 3MF files and per-part print notes.
  - Mesh check script (`check_meshes.py`).
  - First ESPHome draft, with the wiring summary and flashing steps (aimed at a Freenove ESP32-S3 WROOM CAM by mistake; see Changed).
  - Research notes on power, servo and sealing (Italian), and process photos with location data removed.
  - Licensing: MIT (software), CERN-OHL-P-2.0 (hardware), CC BY 4.0 (docs and photos), following the REUSE specification.
  - Contributing guide, Code of Conduct (Contributor Covenant 2.1), security policy, issue and pull request templates, CI workflow.

### Changed

- 2026-11-08: Board corrected to the Freenove ESP32-WROVER (classic ESP32), as documented in the owner's `PROJECT.md` and still to be verified on the device. Earlier text said Freenove ESP32-S3 WROOM CAM.
  - ESPHome draft: `board: esp32dev`, 4 MB flash, servo on GPIO14 (as in the MicroPython source) and regulator enable on GPIO32 (was GPIO21, a camera pin on the WROVER CAM board). Labelled as the alternative firmware and an unflashed draft, not the baseline.
  - `firmware/README.md`: two firmwares, MicroPython first; classic ESP32 pin rules; the optional 12 V monitor moves to GPIO33.
  - README, site text, assembly data (`build_assembly.py`, `assembly.json`), issue templates, `SECURITY.md` and `LICENSE` updated to match.
  - Photo renamed from `esp32-s3-cam-board-breadboard-wiring.jpg` to `freenove-esp32-cam-board-breadboard-wiring.jpg`, with a corrected caption.
- 2026-11-08: `CONTRIBUTING.md` adopts the owner's conventions: Conventional Commits, SemVer tags, `main` always deployable, feature branches.
- 2026-03-24 (firmware, uncommitted in feedr-outdoor, imported as found):
  - Arcade "feeding fanfare" (chirps, rising C-major arpeggio, trill, final high note) replaces the meow sound.
  - Speaker duty 512 (50 %, the loudest clean square wave).
  - 2 s boot delay in `main.py`, so mpremote can connect before the loop starts.
  - `make deploy` chains the mpremote copies in one serial session, so the board's `main.py` does not restart between files.

### Fixed

- 2026-11-08: `reuse lint` failed on `import/previous-chat/README.md`; `REUSE.toml` now covers `import/**/*.md` as documentation (CC BY 4.0).

## [feedr-outdoor 0.1.0] - 2026-03-24

The owner's MicroPython firmware before it moved into this repository, copied from its own changelog. The single-file prototype is now `firmware/micropython/legacy/CatFeeder.py`.

### Added

- Single-file cat feeder prototype (`CatFeeder.py`)
- Servo-driven dispensing gate with configurable angles
- Meow-like synthesized sound on every dispense
- Power on/off button with LED indicator
- Manual dispense button with debounce
- Makefile for ESP32 deployment via mpremote
- PROJECT.md with full hardware and behavioral spec
