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

## Evidence / uncertainty discipline

- These behaviors are **owner-confirmed**; the exact MicroPython source currently flashed onto the board **has not yet been recovered**.
- Historic March 2026 WROVER *proposed/documented* GPIO map: LED=2, ON/OFF=13, dispense=27, servo PWM=14, speaker PWM=26, active-low buttons with internal pullups. These are **not yet electrically verified**.
- An even earlier experiment discussed servo GPIO4. **Do not silently choose one without checking actual wired hardware / firmware.**
- Historic proposed servo range 10° closed / 100° open, 400ms settling / 800ms open; proposed meow 750→1300→500Hz. These are not confirmed firmware-readback.
- The repository's later `firmware/esphome/kibble-dispenser.yaml` targets a **Freenove ESP32-S3 WROOM CAM**, uses GPIO14 for servo and GPIO21 for regulator enable, and currently omits physical buttons, LED, and meow. It was only configuration-validated, not flashed. **No hardware identification yet proves which ESP32 board is running the working firmware.**
- The old 5V bench power discussion and the proposed future 12V outdoor power system are **not evidence of the same installed circuit**.

## Physical mechanical work not yet captured by current CAD

The owner developed and mounted a **wall/side servo bracket** from ChatGPT attachment(s) `RC_Servo_Mounts.3mf` / `RC_Servo_Mounts(1).3mf`. The last discussion requests a **shape-preserving offset spacer**, **no lateral shift**, nominal **3mm provisional** (4–5mm questioned), to align servo horn with a hole in the plastic. These 3MF attachments are not in this repo. The current new CAD claims a **lid-mounted integrated servo cradle** as a future solution, but do **not** imply that the existing physical bracket has been replaced. Collect the original bracket files and alignment measurement before finalizing mount design.

## Order of work

1. Preserve the running hardware and firmware. Recover the actual `boot.py`, `main.py`, etc. from the MCU via Thonny **without flashing or erasing** and **redact secrets** before committing; store exact originals under `import/previous-chat/` with provenance.
2. Photograph and label actual board/servo/LED/buttons/speaker, wiring and enclosure; reconcile the pin map.
3. Preserve `RC_Servo_Mounts*.3mf` source files and the actual spacer iteration.
4. Compare current working implementation against the behavioral contract, then extend or port it if chosen.
5. Validate hardware and acceptance checklist from `docs/AS_BUILT_BASELINE.it.md` before flashing a new image.

Don't treat documentation guesses as as-built measurements. Never overwrite the existing running firmware simply because the ESPHome YAML passes config checks. Keep code in English.