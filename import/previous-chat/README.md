# Previous ChatGPT / physical-prototype import

This directory is reserved for the **actual** MicroPython firmware and other original files recovered from the ESP32 prototype and earlier ChatGPT sessions.

## Current status (2026-11-08)

**Original on-device source has NOT been recovered into this GitHub repository.**

The owner confirms an existing ESP32 implementation with:
- Physical ON/OFF toggle and LED;
- One dispense on turning ON;
- One dispense per physical dispense-button press (only while ON);
- A meow/sound on every dispense.

For previously discussed GPIO map, mechanics and evidence qualifications, see `../../docs/AS_BUILT_BASELINE.it.md`.

## Import protocol

1. Connect with Thonny and **copy** `boot.py`, `main.py` and linked modules from the MicroPython filesystem without erasing or flashing the board.
2. Keep a dated, byte-identical copy of each original. Redact/strip passwords or Wi-Fi credentials from any tracked version, retaining safe backup privately.
3. Record board name, MicroPython version, actual wired pin map and tests performed.
4. Never call speculative reimplemented files "original firmware".
5. Do not overwrite an original file with the unflashed ESPHome draft or vice versa.

Historical note: work used an ESP32 Freenove WROVER and Thonny; later repository CAD photos show an ESP32-S3 CAM board. Verify **which is installed now**.