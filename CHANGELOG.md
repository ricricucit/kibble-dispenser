# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). The project has no versioned releases yet.

## [Unreleased]

### Added

- 2026-11-08: Initial import of prototype 1.
  - Drivetrain parts: rotating disc (disco_v3), shaft and hub (albero_mozzo), sealed bushing (passante_stagno), spline fit test (test_scanalato), with the `build_drivetrain.py` generator, `layout_v3.json` and `drivetrain.json`.
  - Chute (scivolo_v1) with the `build_disc_v2_chute.py` generator.
  - Print-ready STLs, 3MF files and per-part print notes.
  - Mesh check script (`check_meshes.py`).
  - First ESPHome draft for the Freenove ESP32-S3 WROOM CAM, with the wiring summary and flashing steps.
  - Research notes on power, servo and sealing (Italian), and process photos with location data removed.
  - Licensing: MIT (software), CERN-OHL-P-2.0 (hardware), CC BY 4.0 (docs and photos), following the REUSE specification.
  - Contributing guide, Code of Conduct (Contributor Covenant 2.1), security policy, issue and pull request templates, CI workflow.
