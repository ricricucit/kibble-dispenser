# Firmware

Two firmwares for the same board:

- **MicroPython, the baseline**: [`micropython/`](micropython/README.md). The owner's own firmware for prototype 1, and his learning path: a power button with a status LED, a dispense button, a sound with every portion and the servo. It is a snapshot of his development folder ("feedr-outdoor" 0.1.0 plus uncommitted edits of 2026-03-24), not a copy read back from the board. Start with [micropython/README.md](micropython/README.md).
- **ESPHome, the alternative**: [`esphome/kibble-dispenser.yaml`](esphome/kibble-dispenser.yaml), for Home Assistant and OTA later. Unflashed draft, not the baseline: it passes `esphome config` (ESPHome 2026.10.2) but has never been compiled, flashed or tested, and it has no physical buttons, LED or sound yet.

Before flashing either one, back up the files that are on the board now (step 4 of the [MicroPython quick start](micropython/README.md#quick-start)) and read [the as-built baseline](../docs/AS_BUILT_BASELINE.it.md).

## Board

Freenove ESP32-WROVER, as documented in the owner's `micropython/PROJECT.md`; to be verified on the device. It is a classic ESP32 (not an ESP32-S3) on an ESP32-WROVER module with PSRAM, with USB-C through a USB-UART bridge. The board in the photos is the camera (CAM) version; neither firmware uses the camera. An earlier version of this page and of the ESPHome draft wrongly said Freenove ESP32-S3 WROOM CAM.

## Pins

MicroPython, as defined in the dev source `micropython/src/config.py`; not yet electrically verified (an earlier experiment drove the servo from GPIO4, see [CLAUDE.md](../CLAUDE.md)):

- GPIO2: status LED (active-high, external)
- GPIO13: power button (active-low, internal pull-up)
- GPIO14: servo signal
- GPIO26: speaker, through 100-220 Ω
- GPIO27: dispense button (active-low, internal pull-up)

ESPHome draft:

- GPIO14: servo signal (LEDC PWM, 50 Hz), the same pin as in the MicroPython source
- GPIO32: servo regulator enable, through an N-MOSFET (see the wiring list below)

Classic ESP32 rules behind these choices:

- Strapping pins 0, 2, 5, 12, 15: no inputs or pull-ups/pull-downs on them at boot. GPIO12 pulled high at boot stops a 3.3 V flash module from starting. GPIO2 drives the LED here, which is fine for an output.
- Not available: GPIO6-11 (flash) and GPIO16-17 (PSRAM on the WROVER). Input-only: GPIO34-39.
- Camera on the WROVER CAM board: GPIO4, 5, 18, 19, 21-23, 25-27 and 34-39. GPIO26 and 27 (speaker and dispense button) are fine on a classic ESP32, but collide with the camera interface if the camera is ever used. GPIO2, 13, 14, 32 and 33 stay clear of it.
- GPIO14 can toggle briefly while the ESP32 boots. The regulator enable keeps the servo unpowered until the firmware is running.

Kept free for later:

- GPIO33 (ADC1, which still works with Wi-Fi on): optional 12 V monitor through a resistor divider
- GPIO21 (SDA) and GPIO22 (SCL), the classic ESP32 I2C defaults: an optional INA219 jam sensor, as long as the camera is not used

## Power

Prototype 1 runs on a 5 V bench supply, with a 470-1000 µF capacitor on the servo rail (see [micropython/README.md](micropython/README.md#power-for-prototype-1-bench)). The list below is the planned outdoor design; its parts are not installed yet.

## Wiring, from the wall socket to the servo

Summary of section 6 of the research notes (`docs/research/elettronica-e-tenuta.it.md`, in Italian).

1. Mains: indoor socket, or an outdoor IP55 socket with a cover. A certified 12 V 3 A adapter, efficiency level VI (for example Mean Well GST36 12 V). No 230 V inside the box.
2. Cable: H05RN-F 2 x 0.75 or 1 mm², up to about 10-15 m, with a drip loop. SP13 female plug on the adapter side.
3. Box entry: Weipu SP13 panel socket, or a vented M16 cable gland with a short cable and an inline waterproof connector.
4. Input protection, in this order:
   - T3.15 A fuse (5x20 in a PCB holder) or a 2.5-3 A PTC
   - SS54 Schottky diode in series against reverse polarity (or a 30 V+ low-resistance P-MOSFET)
   - SMBJ15A TVS diode between 12 V and ground
   - 470 µF / 25 V plus 100 nF: this is the star ground point
5. Servo branch:
   - 12 V into a Pololu D36V50F6 (6 V). Alternatives: D36V50F7 (7.5 V), or a Hobbywing UBEC 5A set to 6 V (that one has no EN pin)
   - EN driven from GPIO32 through a 2N7002 N-MOSFET. EN has an internal pull-up to the 12 V input, so never connect it straight to the GPIO. GPIO high turns the MOSFET on and the regulator off, so the YAML inverts the pin. A 10 kΩ pull-up from the gate to 3.3 V keeps the servo unpowered while the ESP32 boots
   - 1000 µF low-ESR / 16 V plus 100 nF at the servo connector
   - 0.5 mm² wire to the servo, screw terminals or solder (no Dupont jumpers on servo power)
6. Logic branch: 12 V into a 5 V 1 A regulator (Pololu D24V10F5 or D36V6F5), then 100-470 µF plus 100 nF, then the board's 5V pin. Do not power the board from USB and the 5V pin at the same time unless there is a diode between them. Check the input range of the board's DC jack before feeding it 12 V directly.
7. Signal: GPIO14, 220-330 Ω in series, then the servo signal input, with 10 kΩ from the signal to ground. If the servo jitters, add a 74AHCT1G125 buffer powered from 5 V.
8. Grounds: everything goes back to the star point. The servo return goes straight to its regulator or the star point, never through the ESP32 board.
9. Optional: a resistor divider from 12 V to GPIO33 to monitor the supply, and an INA219 on the servo branch to detect a jammed disc.

## What the ESPHome draft does

Home Assistant gets three entities:

- Dispense (button)
- Portions (number, 1-10, remembered)
- Dwell time (number, seconds the disc stays open, default 1.5 s)

When you press Dispense, the `dispense` script:

1. turns the servo regulator on and waits 80 ms
2. sends its first pulses at the last stored position, so the servo does not jump
3. ramps to the closed position
4. repeats once per portion: open (180°), wait the dwell time, close
5. waits 0.5 s, stops the pulses, then turns the regulator off

The last position is saved in flash, so it survives a reboot.

## Flashing the ESPHome draft

The first USB flash replaces MicroPython and every file on the board. Back them up first (see above).

1. Install ESPHome: `pip install esphome`, or use the ESPHome Device Builder add-on in Home Assistant.
2. Make the secrets file: `cd firmware/esphome && cp secrets.example.yaml secrets.yaml`, then fill in your values. Generate the API key with `openssl rand -base64 32`. Use unique passwords for every device. `secrets.yaml` is git-ignored.
3. Check the config: `esphome config kibble-dispenser.yaml`
4. First flash over USB-C: `esphome run kibble-dispenser.yaml` and pick the serial port. Windows and macOS may need the driver for the board's USB-UART bridge (CH340 or CH343, depending on the revision). If the upload does not start, hold BOOT, tap EN/RST, then release BOOT.
5. Later updates go over Wi-Fi (OTA, protected by the password in `secrets.yaml`).
6. In Home Assistant, add the device through the ESPHome integration and paste the API encryption key.

## Calibrating the servo (ESPHome)

For the MicroPython firmware, see [Calibration](micropython/README.md#calibration).

Do this with the disc removed, so a wrong end position cannot strain the printed spline.

1. Press Dispense and watch both end positions.
2. Widen `servo_min_level` and `servo_max_level` in small steps (about 0.25 %) until the travel reaches 0° and 180°. Leave 2-3° of margin from the servo's internal stops.
3. If the disc would open the wrong way, swap `closed_position` and `open_position`.
4. Re-flash, then fit the disc.
