# MicroPython firmware (baseline)

The owner's own firmware for prototype 1, and the baseline firmware of this project: it is his learning path. The ESPHome configuration in [`../esphome/`](../esphome/) is an alternative for Home Assistant and OTA later, not a replacement.

## Provenance: dev folder snapshot, not an on-device readback

- Source: a snapshot of the owner's development folder for his project "feedr-outdoor", imported on 2026-11-08: version 0.1.0 (2026-03-24) plus the uncommitted edits found in that folder, also from 2026-03-24 (arcade "feeding fanfare", speaker duty 512, 2 s boot delay, chained mpremote deploy). No git history came with it.
- Every file is byte-for-byte as received. Only this README is new. Machine-local files (`.claude/`) were left out.
- It is **not** a copy read back from the ESP32. The files on the board may be an older version (for example `CatFeeder.py` or an earlier `main.py`). The on-device readback is still pending and goes to [`../../import/previous-chat/`](../../import/previous-chat/README.md) (see step 4 of the quick start). Compare the two before deploying anything.
- `PROJECT.md` (the original hardware and behaviour spec) and `CLAUDE.md` (the owner's notes for Claude Code) are also as received. The end of `PROJECT.md` is cut off. Where they differ from this README (LED polarity, meow or fanfare, branch model), this README and [CONTRIBUTING.md](../../CONTRIBUTING.md) describe the current state.

## What it does

- Boots OFF: after a 2 s delay (so mpremote can connect), the servo goes to the closed angle, the speaker is silent and the LED is off. A reset never dispenses.
- The power button toggles ON/OFF, and the LED shows the state. Switching ON triggers exactly one dispense straight away.
- The dispense button gives one portion per press, only while ON. Holding it down does not repeat (50 ms software debounce, one event per press).
- One dispense: the gate opens to `SERVO_OPEN_ANGLE` while the speaker plays the feeding fanfare (about 0.8 s: three chirps, a rising C-major arpeggio, a trill and a final high note), the gate stays open for `DISPENSE_OPEN_TIME_MS`, then closes.
- No Wi-Fi, no timers, no automatic feeding.

The fanfare replaced the earlier meow sweep (750 → 1300 → 500 Hz), which is still in `legacy/CatFeeder.py`.

## Files

- `src/`: the modules uploaded to the root of the board's filesystem. Dependency order: `config` → `hardware` → `servo`, `speaker`, `buttons` → `dispenser` → `main`. Pins and calibration live only in `src/config.py`.
- `legacy/CatFeeder.py`: the original single-file prototype, kept for reference. The Makefile does not deploy it.
- `Makefile`: mpremote commands (`make` lists them). `requirements.txt`: mpremote and ruff. `ruff.toml`: lint settings. `VERSION`: firmware version.

## Board

Freenove ESP32-WROVER, as documented in the owner's `PROJECT.md`; to be verified on the device. It is a classic ESP32 (not an ESP32-S3) with PSRAM. The as-built notes record MicroPython 1.27.0 reporting "Generic ESP32 module with SPIRAM", which fits. The board in the [photos](../../docs/photos/README.md) is the camera (CAM) version; this firmware does not use the camera.

## Pin map

As defined in the dev source `src/config.py`; not yet electrically verified against the wired prototype. An earlier experiment drove the servo from GPIO4 (see [CLAUDE.md](../../CLAUDE.md)), so check the real wiring before deploying.

- GPIO2: status LED, external and active-high (GPIO → resistor → LED → GND)
- GPIO13: power (ON/OFF) button to GND, active-low with the internal pull-up
- GPIO14: servo signal (yellow wire), 50 Hz PWM
- GPIO26: speaker, through a 100-220 Ω series resistor to the red wire; black wire to GND
- GPIO27: dispense button to GND, active-low with the internal pull-up

Classic ESP32 notes:

- Strapping pins 0, 2, 5, 12, 15: do not use them as inputs or pull them at boot. GPIO12 pulled high at boot stops a 3.3 V flash module from starting. GPIO2 is fine here as the LED output: the LED to GND keeps it low, which is what the boot ROM expects.
- GPIO6-11 (flash) and GPIO16-17 (PSRAM on the WROVER) are not available. GPIO34-39 are input-only, with no pull-ups.
- GPIO14 can toggle briefly while the ESP32 boots, so the servo may twitch at reset. The planned outdoor wiring keeps the servo unpowered during boot (regulator enable, see [../README.md](../README.md)).
- GPIO26 and 27 are fine on a classic ESP32, but on the WROVER CAM board they are the camera's control bus (SCCB). The camera also uses GPIO4, 5, 18, 19, 21-23, 25 and 34-39. If the camera is ever used, move the speaker and the dispense button, for example to GPIO32 and GPIO33.

## Power for prototype 1 (bench)

As documented in `PROJECT.md`; check it against the wired prototype.

- A 5 V bench supply (5.0 V, current limit about 3 A) feeds the servo: red wire to +5 V, brown to GND.
- Put a 470-1000 µF electrolytic capacitor (10 V or more, mind the polarity) across the servo rail, close to the servo connector. The servo's current spikes otherwise pull the rail down.
- During development the board runs from USB-C. If it is fed from the same 5 V supply through its 5V pin instead, do not connect USB at the same time unless the board has a diode between the two.
- All grounds are common: bench supply, board, servo, speaker and buttons. Never power the servo from the board's 3.3 V pin.

This is a bench set-up only. The planned outdoor design (external 12 V adapter, a separate 6 V servo regulator with an enable pin, a 5 V logic regulator and input protection) is in [../README.md](../README.md#wiring-from-the-wall-socket-to-the-servo) and in section 6 of the [research notes](../../docs/research/elettronica-e-tenuta.it.md) (Italian). Those parts are not installed yet.

## Quick start

Run everything from `firmware/micropython/`. mpremote finds the board's USB serial port on its own; keep other boards unplugged.

1. Install the tools: `pip install -r requirements.txt`
2. MicroPython on the board: if `make ls` (step 3) lists files, MicroPython is already there; skip this step. Only for a blank board, download the "Support for SPIRAM / WROVER" build (`ESP32_GENERIC-SPIRAM-<date>-<version>.bin`) from <https://micropython.org/download/ESP32_GENERIC/> and flash it:
   ```
   pip install esptool
   esptool.py --port <PORT> erase_flash
   esptool.py --port <PORT> --baud 460800 write_flash 0x1000 ESP32_GENERIC-SPIRAM-<date>-<version>.bin
   ```
   `erase_flash` deletes every file on the board. Never run it before the backup in step 4.
3. `make ls`: list the files on the board.
4. `make backup`: copy `CatFeeder.py`, `main.py` and `boot.py` from the board into `backups/<timestamp>/` (git-ignored). It copies only those three. If `make ls` shows more files (for example `config.py` or `servo.py`), copy each one too: `mpremote cp :config.py backups/<timestamp>/config.py`. This read-only copy is the on-device readback: add it, with a provenance note, to [`../../import/previous-chat/`](../../import/previous-chat/README.md), after removing any Wi-Fi passwords.
5. `make deploy`: upload every file in `src/` in one mpremote session, then reset the board. This replaces `main.py` on the board.
6. Test, with the disc removed first:
   - About 2 s after the reset, the servo moves to the closed angle and the LED is off.
   - Dispense button: nothing happens (machine OFF).
   - Power button: the LED turns on and one dispense runs straight away (gate opens, fanfare, gate closes).
   - Dispense button: one dispense per press; holding it down gives only one.
   - Power button again: the LED turns off and the dispense button is ignored.
   - `make repl` shows errors (Ctrl-C stops the loop, Ctrl-D soft-resets). `make deploy-main` re-uploads only `main.py`.

## Calibration

The constants are in `src/config.py`. Change them, then `make deploy`.

- `SERVO_CLOSED_ANGLE`: closed position, now 10°
- `SERVO_OPEN_ANGLE`: open position, now 100°
- `DISPENSE_OPEN_TIME_MS`: how long the gate stays open after the fanfare, now 800 ms (so it is open for about 1.6 s in total)

Angles map linearly to the pulse width: 0° = `SERVO_MIN_US` (500 µs), 180° = `SERVO_MAX_US` (2500 µs). The PWM duty is 10-bit, so one step is about 1.8°: smaller changes round to the same pulse.

The designed disc ([disco_v3](../../hardware/README.md)) turns 180° to release a portion, so `SERVO_OPEN_ANGLE` will have to move towards 170-180° (with the closed angle near 0°). The current 10°/100° travel and the 180° disc are not interchangeable. With the disc removed, find the servo's internal stops and stay 2-3° inside them at both ends.

## Lint

`make lint` runs ruff with `ruff.toml`. On the imported code it reports import order (I001) and, in `main.py`, imports placed after the `BOOT_DELAY_S` constant (E402). The code is kept as received, so CI runs ruff with those two rules ignored until a separate clean-up commit.
