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

## Update 2026-11-08

- The owner's MicroPython source arrived as a **dev folder snapshot** ("feedr-outdoor" 0.1.0 plus uncommitted edits of 2026-03-24) and is in [`../../firmware/micropython/`](../../firmware/micropython/README.md). It is not an on-device readback, so this directory still waits for the files read from the board.
- Read-only alternative to Thonny, from `firmware/micropython/`: `make ls`, then `make backup` (it copies only `CatFeeder.py`, `main.py` and `boot.py`), then `mpremote cp :<file> <local path>` for every other file listed. Do not run `make deploy` or erase the board before this copy is saved here.
- Board: documented as Freenove ESP32-WROVER in the owner's `PROJECT.md`; to be verified on the device. The repository photo first captioned as an ESP32-S3 was mislabelled (see `docs/photos/README.md`).
