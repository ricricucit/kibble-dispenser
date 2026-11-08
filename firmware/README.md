# Firmware

Status: first draft. `esphome/kibble-dispenser.yaml` passes `esphome config` (ESPHome 2026.10.2). It has not been compiled, flashed or tested on the real hardware yet.

## Firmware choice is still open

This folder has an ESPHome draft. An earlier Python-based software, written in another conversation, is being recovered into `import/previous-chat/`. Whether the dispenser runs ESPHome or that Python code has not been decided. Do not delete or overwrite `import/previous-chat/`.

## Board

Freenove ESP32-S3 WROOM CAM: ESP32-S3 module (8 MB flash, 8 MB octal PSRAM), OV2640-type camera, USB-C through a CH343 USB-UART bridge, DC jack. The camera is not used by this draft.

## Pins

- GPIO14: servo signal (LEDC PWM, 50 Hz)
- GPIO21: servo regulator enable, through an N-MOSFET (see the wiring list below)

Why these two: on this board they are not used by the camera (GPIO 4-13 and 15-18), the SD card slot (38-40), native USB (19, 20), the UART0 bridge (43, 44), the module's flash and PSRAM (26-37) or the strapping pins (0, 3, 45, 46). They also stay clear of GPIO 2 and 48, which drive on-board LEDs on Freenove S3 boards (check your board revision).

Kept free for later:

- GPIO1 (ADC1): optional 12 V monitor through a resistor divider
- GPIO41 and GPIO42: an I2C bus for an optional INA219 jam sensor

Other boards: the YAML header lists the changes for a classic ESP32 (esp32dev) and an ESP32-C3.

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
   - EN driven from GPIO21 through a 2N7002 N-MOSFET. EN has an internal pull-up to the 12 V input, so never connect it straight to the GPIO. GPIO high turns the MOSFET on and the regulator off, so the YAML inverts the pin. A 10 kΩ pull-up from the gate to 3.3 V keeps the servo unpowered while the ESP32 boots
   - 1000 µF low-ESR / 16 V plus 100 nF at the servo connector
   - 0.5 mm² wire to the servo, screw terminals or solder (no Dupont jumpers on servo power)
6. Logic branch: 12 V into a 5 V 1 A regulator (Pololu D24V10F5 or D36V6F5), then 100-470 µF plus 100 nF, then the board's 5V pin. Do not power the board from USB and the 5V pin at the same time unless there is a diode between them. Check the input range of the board's DC jack before feeding it 12 V directly.
7. Signal: GPIO14, 220-330 Ω in series, then the servo signal input, with 10 kΩ from the signal to ground. If the servo jitters, add a 74AHCT1G125 buffer powered from 5 V.
8. Grounds: everything goes back to the star point. The servo return goes straight to its regulator or the star point, never through the ESP32 board.
9. Optional: a resistor divider from 12 V to GPIO1 to monitor the supply, and an INA219 on the servo branch to detect a jammed disc.

## What the firmware does

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

## Flashing

1. Install ESPHome: `pip install esphome`, or use the ESPHome Device Builder add-on in Home Assistant.
2. Make the secrets file: `cd firmware/esphome && cp secrets.example.yaml secrets.yaml`, then fill in your values. Generate the API key with `openssl rand -base64 32`. Use unique passwords for every device. `secrets.yaml` is git-ignored.
3. Check the config: `esphome config kibble-dispenser.yaml`
4. First flash over USB-C: `esphome run kibble-dispenser.yaml` and pick the serial port. Windows and macOS may need the CH343 driver. If the upload does not start, hold BOOT, tap RST, then release BOOT.
5. Later updates go over Wi-Fi (OTA, protected by the password in `secrets.yaml`).
6. In Home Assistant, add the device through the ESPHome integration and paste the API encryption key.

## Calibrating the servo

Do this with the disc removed, so a wrong end position cannot strain the printed spline.

1. Press Dispense and watch both end positions.
2. Widen `servo_min_level` and `servo_max_level` in small steps (about 0.25 %) until the travel reaches 0° and 180°. Leave 2-3° of margin from the servo's internal stops.
3. If the disc would open the wrong way, swap `closed_position` and `open_position`.
4. Re-flash, then fit the disc.
