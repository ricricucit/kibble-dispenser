# Prototype 1 on the bench: what is there (2026-11-14)

A record of the bench prototype's electronics as photographed and measured by the owner on 2026-11-14. It complements [the as-built baseline](AS_BUILT_BASELINE.it.md). Each statement belongs to one of three classes, kept apart on purpose:

- **Owner-measured**: measured by the owner on the real parts.
- **Read from photos**: what the photos show. **Not electrically verified**: nobody has buzzed a wire or read the firmware back from the board yet.
- **Open**: not known yet.

Nothing here is a reason to flash or rewire the prototype. Hardware 6.3 and its one-button panel are a separate, later step ([issue #2](https://github.com/ricricucit/kibble-dispenser/issues/2)).

## Photos

All in [`photos/`](photos/README.md), metadata removed:

- `2026-11-14-bench-breadboard-wrover-buttons-led-speaker.jpg`: overview of the breadboard
- `2026-11-14-wrover-board-top-view-with-ruler.jpg`: the ESP32 board from above, next to a ruler
- `2026-11-14-wrover-and-extension-board-along-ruler.jpg`: ESP32 board and extension board along a ruler
- `2026-11-14-extension-board-jumpers-close-up.jpg`: the jumpers on the extension board
- `2026-11-14-perfboards-with-caliper-and-ruler.jpg`: the perfboards on hand

## Owner-measured

- Breadboard: 165 × 55 × 10 mm.
- Freenove ESP32 GPIO Extension Board: T-shaped, 90 × 60 mm at its widest.

## Read from photos (not electrically verified)

- Board: a Freenove ESP32-WROVER board (silkscreen "FREENOVE ESP32 WROVER", USB-C) plugged into the Freenove ESP32 GPIO Extension Board, which sits on the breadboard. The camera module is fitted.
- Parts on the breadboard: two 12 mm tactile buttons with yellow caps, one red LED with resistors, and a speaker marked 8 Ω 2 W on two leads. The servo is on its own three-wire lead.
- Wiring: jumpers leave the extension board at the pins labelled 13, 14, 26 and 27, and the LED wire leaves near pin 2. This is consistent with `firmware/micropython/src/config.py` (LED 2, ON/OFF 13, servo 14, speaker 26, dispense 27). Consistent is not verified: which jumper ends at which part has not been traced.
- Size of the ESP32 board, estimated against the ruler (± 1 mm): about 28 × 53 mm, plus about 8 mm of antenna overhang; pin rows about 25 mm apart. No official drawing was found. A "27 × 40.5 mm" figure found on the web belongs to the AI-Thinker ESP32-CAM and is wrong for this board.

## Camera pins

According to Maker Advisor's pinout page for this board, the camera uses GPIO 26 (SIOD) and GPIO 27 (SIOC), among others. The current firmware uses those two pins for the speaker and the dispense button. Prototype 1 does not use the camera, so nothing changes now; the conflict is tracked in [issue #3](https://github.com/ricricucit/kibble-dispenser/issues/3).

## Kit and perfboards

- Kit: Freenove ESP32-WROVER starter kit, bought 2026-01-12: board, camera, extension board, LEDs, resistors, buttons, speaker and amplifier, sensors, perfboards.
- Perfboards on hand:
  - green, double-sided, plated-through, 5 × 7 cm: chosen for the soldered prototype (also 4 × 6, 3 × 7 and 2 × 8 cm);
  - a black solderable breadboard, about 83 × 52 mm: for trials;
  - many brown single-sided 5 × 7 cm boards: for practice.

## Decisions of 2026-11-14 (owner)

- The soldered prototype is built on a green 5 × 7 cm perfboard, with the ESP32 on socket strips and without the extension board.
- The project splits into three parts: mechanics with an electronics case holder (hardware 6.4, in design), a detachable electronics module with its own version line, and firmware. See [VERSIONS.md](../VERSIONS.md).
- The servo stays in the chassis, not in the electronics module.
- Prototype 1 has no camera.

## Open

- How the servo is powered on the bench: from the board's 5 V pin or from a separate supply.
- How the speaker is driven: straight from GPIO 26, through a resistor, a transistor or the kit's amplifier.
- The speaker's diameter.
- The firmware on the board has not been read back. `make ls` and `make backup` in `firmware/micropython/` only read; do not deploy anything before the readback has been compared with the source in the repository.
