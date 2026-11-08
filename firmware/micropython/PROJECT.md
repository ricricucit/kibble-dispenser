# PROJECT.md

## Project Overview

This project is a **DIY cat food dispenser** built on an **ESP32 (Freenove ESP32 WROVER kit)** using **MicroPython**.

The dispenser uses:
- a **servo motor** to rotate a dispensing gate/disc
- a **speaker** to play a short meow-like sound on every dispense
- an **on/off button** to enable or disable the machine
- a **manual dispense button** to trigger one dispense on demand
- an **LED** to show whether the machine is enabled

The system is intentionally simple, robust, and easy to evolve.

---

## High-Level Functional Requirements

### Current required behavior
1. **On/off button**
   - Toggles machine state between OFF and ON
   - LED is ON when the machine is ON
   - When the machine is turned ON, it performs **exactly one dispense immediately**

2. **Dispense button**
   - When machine is ON, each press triggers **exactly one dispense**
   - When machine is OFF, pressing the dispense button does nothing

3. **Sound**
   - Every dispense plays a **meow-like synthesized sound**
   - The current speaker setup only supports tones / sweeps, not real audio playback

4. **Servo action**
   - Dispense sequence should be:
     1. play meow sound
     2. move servo to open position
     3. wait a short time so kibble can fall
     4. move servo back to closed position

---

## Hardware Context

### Board
- **Freenove ESP32 WROVER**
- Programmed in **MicroPython**

### Servo
- Standard RC servo
- Wire colors:
  - **Brown** = GND
  - **Red** = +5V
  - **Yellow** = PWM signal
- Current control signal pin:
  - **GPIO14**

### Speaker
- Small speaker from the kit
- 2 wires:
  - **Red**
  - **Black**
- Speaker is connected **through a series resistor**
- Current control pin:
  - **GPIO26**
- The other speaker wire goes to **GND**

### LED
- LED used as machine ON indicator
- Current pin:
  - **GPIO2**
- Important: depending on the Freenove board wiring, the onboard LED may be **active-low**
  - This means `led.value(0)` may turn the LED ON
  - This must be verified in real hardware

### Buttons
There are **two buttons** in the design:

#### 1. Power / on-off button
- Used to toggle machine enabled state
- Current pin:
  - **GPIO13**

#### 2. Dispense button
- Used to trigger one manual dispense
- Current pin:
  - **GPIO27**
- Important: earlier discussion considered GPIO27 for speaker, but that was changed
- Final choice:
  - **GPIO26 = speaker**
  - **GPIO27 = dispense button**

### Power
- System uses a **single power source**
- ESP32 is powered from external 5V supply / USB-C from lab supply
- Servo is powered from the same 5V rail
- Speaker is passive and driven from GPIO through resistor
- All grounds must be common

### Recommended power notes
- Servo power draw can spike
- Keep power wiring short and solid
- A bulk capacitor across servo power is recommended:
  - e.g. **470uF to 1000uF**
- Avoid powering a heavy servo from weak USB sources
- In this project, using the bench PSU / stable 5V source is acceptable

---

## Final Wiring Summary

### Servo
- `GPIO14` -> servo **yellow**
- `5V` -> servo **red**
- `GND` -> servo **brown**

### Speaker
- `GPIO26` -> **100Ω to 220Ω resistor** -> speaker **red**
- `GND` -> speaker **black**

### Power button
- `GPIO13` -> button
- Button uses internal pull-up in software
- Therefore:
  - released = `1`
  - pressed = `0`

### Dispense button
- `GPIO27` -> button
- Also uses internal pull-up
- Therefore:
  - released = `1`
  - pressed = `0`

### LED
- `GPIO2` -> LED indicator
- Likely active-low depending on board behavior

---

## Mechanical Context

The dispenser concept is:
- a rotating disc / gate
- partially perforated or shaped to release kibble
- kibble falls by gravity through a chute

### Mechanical assumptions
- Servo rotates between a **closed angle** and an **open angle**
- The servo should not grind at end stops
- Open angle and open time must be calibrated experimentally
- Do not assume full 180° is needed
- Safer starting range:
  - closed near `10°`
  - open near `80°–110°`

### Calibration variables
The software must keep these as clear constants:
- `SERVO_CLOSED_ANGLE`
- `SERVO_OPEN_ANGLE`
- `DISPENSE_OPEN_TIME_MS`

These should be easy to tune without changing core logic.

---

## Software Platform

- **Language**: MicroPython
- **Main runtime model**: single main loop with polling
- **No threads**
- **No async required**
- **Button handling** should be debounced in software
- Code should remain beginner-readable but professionally structured

---

## Coding Standards

### Mandatory coding style
All code must follow these rules:

1. **All code comments must be in English**
2. Use **clear constant names** in uppercase for hardware config and timings
3. Use **small functions** with single responsibility
4. Prefer **explicit names** over clever short names
5. Keep hardware pin assignments at the top of the file
6. Keep calibration values grouped in a dedicated section
7. Keep user-adjustable behavior easy to find
8. Use **docstrings** for key functions and classes
9. Avoid magic numbers in logic
10. Keep the code robust and easy to extend

### Best practices to always follow
- Debounce buttons properly
- Prevent repeated trigger spam from a held button
- Separate:
  - hardware config
  - helpers
  - actions
  - state handling
  - main loop
- Use defensive helper functions like:
  - `clamp()`
  - `speaker_off()`
  - `close_gate()`
- Initialize hardware into a known safe state on boot
- Machine should boot into **OFF state**
- Servo should be moved to **closed position** during initialization

---

## Behavioral Design

### Machine OFF state
- LED OFF
- Dispense button ignored
- Servo idle in closed position
- Speaker silent

### Machine ON state
- LED ON
- Turning ON immediately triggers one dispense
- Dispense button active
- Each valid press triggers exactly one dispense

### Dispense behavior
A single dispense must:
1. play the meow sound
2. open the servo gate
3. wait for food to drop
4. close the gate

### Important behavioral constraints
- No infinite auto-dispensing loop
- No periodic dispense unless explicitly added later
- No sound outside dispense events unless explicitly added later
- Holding the button down should not create repeated accidental multiple dispenses
- One button press = one action

---

## Current Pin Map

Use this as the source of truth unless explicitly changed later:

```python
LED_PIN = 2
POWER_BUTTON_PIN = 13
DISPENSE_BUTTON_PIN = 27
SERVO_PIN = 14
SPEAKER_PIN = 26