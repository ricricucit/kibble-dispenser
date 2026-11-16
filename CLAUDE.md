# Collaboration instructions — Kibble Dispenser (as-built first)

**Read `docs/AS_BUILT_BASELINE.it.md` before proposing changes to firmware, pins, mechanical mount or assembly plan.**

This repo currently holds a newly imported CAD package and an **unflashed ESPHome draft**. The owner has separately built and used an **ESP32 + MicroPython physical prototype** in earlier ChatGPT sessions. The owner's explicit instruction on 2026-11-08 is to preserve and document **the existing physical hardware and working on-device interactions as the starting point**. Do not silently replace it with a clean-slate implementation.

## User-confirmed behavioral contract

- Physical ON/OFF button toggles active state and LED.
- Turning the system ON causes **exactly one dispensing cycle** (distinguish commanded ON from MCU reboot before implementation).
- Physical dispense button triggers **exactly one cycle per press**, only when ON (no held-button repeats).
- **Meow/sound via a speaker** for every dispensing action.
- No autonomous continuous servo cycling.
- Code and inline comments in English.

**Update 2026-11-10 (owner decision):** from hardware 6.3 the pod has **one recessed push-button + 2 LEDs** (plus a sealed speaker opening and 3 blind knock-outs). New mapping: single press = dispense one portion (only while ON); double press = ON/OFF; long press 5 s = reset all but Wi-Fi; long press 10 s = full reset. The other rules above still apply, plus: never dispense at power-on (store the last rest position). The firmware will be adapted later: see issue #2. The bench prototype keeps its two buttons until then; don't flash it.

## Evidence / uncertainty discipline

- These behaviors are **owner-confirmed**; the exact MicroPython source currently flashed onto the board **has not yet been recovered**. *(2026-11-08: a dev folder snapshot of the source is now in `firmware/micropython/`; the copy on the board is still not recovered. See the update below.)*
- Historic March 2026 WROVER *proposed/documented* GPIO map: LED=2, ON/OFF=13, dispense=27, servo PWM=14, speaker PWM=26, active-low buttons with internal pullups. These are **not yet electrically verified**.
- An even earlier experiment discussed servo GPIO4. **Do not silently choose one without checking actual wired hardware / firmware.**
- Historic proposed servo range 10° closed / 100° open, 400ms settling / 800ms open; proposed meow 750→1300→500Hz. These are not confirmed firmware-readback.
- The repository's later `firmware/esphome/kibble-dispenser.yaml` targets a **Freenove ESP32-S3 WROOM CAM**, uses GPIO14 for servo and GPIO21 for regulator enable, and currently omits physical buttons, LED, and meow. It was only configuration-validated, not flashed. **No hardware identification yet proves which ESP32 board is running the working firmware.** *(2026-11-08: the draft now targets a classic ESP32, `esp32dev`, with GPIO14 for the servo and GPIO32 for the regulator enable. It is still an unflashed draft, not the baseline.)*
- The old 5V bench power discussion and the proposed future 12V outdoor power system are **not evidence of the same installed circuit**.

## Physical mechanical work not yet captured by current CAD

The owner developed and mounted a **wall/side servo bracket** from ChatGPT attachment(s) `RC_Servo_Mounts.3mf` / `RC_Servo_Mounts(1).3mf`. The last discussion requests a **shape-preserving offset spacer**, **no lateral shift**, nominal **3mm provisional** (4–5mm questioned), to align servo horn with a hole in the plastic. These 3MF attachments are not in this repo. The current new CAD claims a **lid-mounted integrated servo cradle** as a future solution, but do **not** imply that the existing physical bracket has been replaced. *(2026-11-08: the cradle is now designed as `passante_culla`, drivetrain v3: designed, not printed or mounted.)* Collect the original bracket files and alignment measurement before finalizing mount design.

## Order of work

1. Preserve the running hardware and firmware. Recover the actual `boot.py`, `main.py`, etc. from the MCU via Thonny **without flashing or erasing** and **redact secrets** before committing; store exact originals under `import/previous-chat/` with provenance.
2. Photograph and label actual board/servo/LED/buttons/speaker, wiring and enclosure; reconcile the pin map.
3. Preserve `RC_Servo_Mounts*.3mf` source files and the actual spacer iteration. *(Keep them privately, outside this repository: the bracket is CC BY-NC-SA. See the update below.)*
4. Compare current working implementation against the behavioral contract, then extend or port it if chosen.
5. Validate hardware and acceptance checklist from `docs/AS_BUILT_BASELINE.it.md` before flashing a new image.

Don't treat documentation guesses as as-built measurements. Never overwrite the existing running firmware simply because the ESPHome YAML passes config checks. Keep code in English.

## Update 2026-11-08: MicroPython import, board, bracket licence (added by Claude Code)

- `firmware/micropython/` holds the owner's MicroPython source, byte-for-byte: a **snapshot of his development folder** for "feedr-outdoor" (0.1.0 of 2026-03-24 plus uncommitted edits from the same day). It is **not** an on-device readback. That readback (Thonny, or `make backup` plus `mpremote cp`, read-only) still goes to `import/previous-chat/`, and the two must be compared. The MicroPython code is the baseline firmware for prototype 1; ESPHome stays the alternative.
- Pins as defined in the dev source `config.py`: LED 2, ON/OFF 13, servo 14, speaker 26, dispense 27; not yet electrically verified. The earlier GPIO4 servo experiment still has to be ruled out on the wiring.
- The dev source matches the behavioural contract: it boots OFF (a reset does not dispense), dispenses once on a commanded ON and once per press while ON, with no repeats on hold. Servo 10°/100°, 400 ms settle, 800 ms open. The sound is now an arcade "feeding fanfare"; the meow sweep survives in `firmware/micropython/legacy/CatFeeder.py`.
- Board: documented as Freenove ESP32-WROVER in the owner's `PROJECT.md`; to be verified on the device. The photo once captioned ESP32-S3 WROOM CAM (now `docs/photos/freenove-esp32-cam-board-breadboard-wiring.jpg`) reads "FREENOVE ESP… R" on the silkscreen, which fits the WROVER CAM board.
- Wall bracket licence: `RC_Servo_Mounts.3mf` is "Standard Servo Mounts - Horizontal and Vertical" by Tonym on MakerWorld (design id US15638e882ab9f8), licensed CC BY-NC-SA (non-commercial). Do not add the 3MF or any derivative (such as the shape-matching spacer) to this repository; record attribution, photos and measurements only. The bracket is prototype-only: a commercial product cannot use it, which is one reason the project designs its own lid-mounted cradle (passante_culla).

## Update 2026-11-14: project split (owner decision)

- The project splits into mechanics with an electronics case holder (hardware 6.4, in design), a detachable electronics module with its own version line, and firmware. The servo stays in the chassis; prototype 1 has no camera. The soldered prototype goes on a green 5 × 7 cm perfboard with the ESP32 on socket strips, without the extension board. Bench photos, measurements and open points: `docs/PROTOTYPE_BENCH.md` (photo readings are not electrically verified; the on-device firmware readback is still pending).

## Update 2026-11-16: only the latest version until launch (owner decision)

- Until public launch (owner will say when): only the latest version is kept in the repo tree, site, print guide, wizard and manuals; no upgrade paths, archives or per-version markings; bump versions normally; history lives in git.

## Restart here (firmware bench session, written 2026-11-14)

If the owner opens a fresh clone and asks to restart the software tests, do this, in order. He is on the bench with the breadboard prototype connected over USB.

1. Read `docs/PROTOTYPE_BENCH.md`, `firmware/micropython/CLAUDE.md` and `firmware/micropython/PROJECT.md`. Work in `firmware/micropython/`.
2. `make setup`, then **read-only** steps only: `make ls` and `make backup` (downloads the board's `.py` files to `backups/<timestamp>/`). Do **not** run `make deploy`, `make deploy-main`, `make clean-board` or anything that writes to the board yet.
3. Compare the backup with `src/` file by file and report the differences in plain words. Redact secrets (Wi-Fi name and password, tokens) before showing or committing anything; keep the raw backup out of git (store a redacted copy under `import/previous-chat/` with a short provenance note).
4. Ask the owner the three open bench questions and record the answers in `docs/PROTOTYPE_BENCH.md`: how the servo is powered (board 5 V pin or separate supply), how the speaker is driven (direct from GPIO 26, resistor, transistor or amplifier), the speaker diameter.
5. With the owner watching the hardware, check the behavioural contract on the board as it is (boots OFF and does not dispense on reset; ON dispenses once; one portion per press while ON; no repeats on hold; sound at every portion). Note what passes and what does not.
6. Only then start changes, on a branch, with the owner's go-ahead before each flash: first issue #2 (single button: single press = one portion, double press = ON/OFF, hold 5 s = reset all but Wi-Fi, hold 10 s = full reset; two LEDs; never dispense at power-on; move speaker and button off GPIO 26/27, see issue #3). Bump `firmware/VERSION` and update `VERSIONS.md` when the behaviour changes.

Hardware design work (6.4 with the detachable electronics module) continues in a separate cloud session; do not edit `hardware/` or `site/` from the bench session unless asked.
