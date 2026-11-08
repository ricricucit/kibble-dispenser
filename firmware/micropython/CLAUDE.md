# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Feedr Outdoor — a resellable outdoor pellet feeder built on **ESP32 WROVER** with **MicroPython**. Currently a cat food dispenser; designed to be adaptable to different container types and dispensing mechanisms. `PROJECT.md` is the authoritative spec for hardware, wiring, and behavioral requirements.

## Commands

Run `make` to see all commands. Key ones:

```
make setup          # Install mpremote, ruff
make lint           # Lint with ruff
make format         # Auto-format with ruff
make deploy         # Upload all src/ files to ESP32
make deploy-reset   # Deploy and reboot
make deploy-main    # Upload only main.py (quick iteration)
make run            # Run on board without saving (testing)
make repl           # MicroPython REPL
make ls             # List files on board
make clean-board    # Remove all .py from board
```

## Architecture

Modular structure under `src/`. Files are uploaded individually to the ESP32 filesystem.

```
src/
  config.py      # All constants: pins, servo angles, timings (zero imports)
  hardware.py    # Pin/PWM object creation (imports config)
  servo.py       # Gate open/close, angle conversion (imports config, hardware)
  speaker.py     # Tones, meow sound (imports config, hardware)
  buttons.py     # DebouncedButton class (imports config)
  dispenser.py   # Dispenser class: machine state + dispense cycle (imports servo, speaker, hardware)
  main.py        # Entry point: init + polling loop (imports everything)
```

Dependency flow: `config → hardware → servo/speaker/buttons → dispenser → main`

Runtime model: single-threaded polling loop, no async, no threads. Blocking during dispense is acceptable.

## Git Workflow

- **main** — tagged releases only, always deployable
- **develop** — integration branch
- **feature/*** — short-lived branches, merged to develop

Commits follow [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `build:`

Tags follow [Semantic Versioning](https://semver.org/). Update `VERSION` and `CHANGELOG.md` on each release.

## Key Conventions

- All comments in English
- Constants use `micropython.const()` for memory optimization, grouped in `config.py`
- LED is **active-high** (`led.value(1)` = ON) — external LED, mini table lamp tutorial wiring
- Buttons are **active-low** with internal pull-ups (`0` = pressed)
- Machine boots **OFF**; turning ON triggers exactly one immediate dispense
- One button press = exactly one action (debounce prevents repeat triggers)
- `Dispenser.dispense()` is the single source of truth for feeding events — never duplicate its logic
- Gate opens simultaneously with meow sound (not sequentially)
- Speaker is PWM-driven through a resistor — only simple tones/sweeps, not real audio

## Development Rules

- Do not break existing button behavior or remove immediate dispense-on-power-on unless explicitly asked
- Keep `Dispenser.dispense()` as the single entry point for all feeding events
- Keep pin numbers and calibration values in `config.py` only — never scatter through other modules
- Prefer readability over abstraction; code should stay beginner-friendly
- Run `make lint` before committing
- All modules must be importable independently for REPL testing

## Pin Map

| Signal          | GPIO |
|-----------------|------|
| LED             | 2    |
| Power button    | 13   |
| Servo PWM       | 14   |
| Speaker PWM     | 26   |
| Dispense button | 27   |
