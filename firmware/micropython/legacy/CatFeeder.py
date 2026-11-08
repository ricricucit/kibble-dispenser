"""
ESP32 Cat Dispenser
===================

Features:
1. Power button toggles the machine ON/OFF
2. LED indicates machine state
3. Turning ON triggers one immediate dispense
4. Dispense button triggers one manual dispense
5. Every dispense plays a meow-like sound

Hardware assumptions:
- LED on GPIO2
- Power button on GPIO13
- Dispense button on GPIO27
- Servo signal on GPIO14
- Speaker on GPIO26 through a 100Ω-220Ω resistor
- Servo powered from 5V
- Buttons wired as active-low using internal pull-up resistors

Important:
- The speaker must NOT be connected directly without a resistor.
- This speaker setup generates tones, not real sampled audio.
"""

from machine import Pin, PWM
from time import sleep_ms, ticks_ms, ticks_diff


# ============================================================
# Pin configuration
# ============================================================

LED_PIN = 2
POWER_BUTTON_PIN = 13
DISPENSE_BUTTON_PIN = 27
SERVO_PIN = 14
SPEAKER_PIN = 26


# ============================================================
# Servo configuration
# ============================================================

SERVO_FREQUENCY_HZ = 50
SERVO_MIN_US = 500
SERVO_MAX_US = 2500
SERVO_PERIOD_US = 20000

# Adjust these values to match your mechanical setup
SERVO_CLOSED_ANGLE = 10
SERVO_OPEN_ANGLE = 100

SERVO_SETTLE_TIME_MS = 400
DISPENSE_OPEN_TIME_MS = 800


# ============================================================
# Speaker configuration
# ============================================================

SPEAKER_DUTY = 350


# ============================================================
# Button debounce configuration
# ============================================================

DEBOUNCE_MS = 50
LOOP_DELAY_MS = 10


# ============================================================
# Hardware setup
# ============================================================

led = Pin(LED_PIN, Pin.OUT)
power_button = Pin(POWER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
dispense_button = Pin(DISPENSE_BUTTON_PIN, Pin.IN, Pin.PULL_UP)

servo_pwm = PWM(Pin(SERVO_PIN), freq=SERVO_FREQUENCY_HZ)
speaker_pwm = PWM(Pin(SPEAKER_PIN))
speaker_pwm.duty(0)


# ============================================================
# Global state
# ============================================================

machine_enabled = False


# ============================================================
# Utility helpers
# ============================================================

def clamp(value, minimum, maximum):
    """
    Clamp a numeric value into a safe range.
    """
    return max(minimum, min(maximum, value))


# ============================================================
# Servo helpers
# ============================================================

def angle_to_duty(angle_deg):
    """
    Convert an angle in degrees into a PWM duty value for the servo.
    """
    safe_angle = clamp(angle_deg, 0, 180)
    pulse_us = SERVO_MIN_US + (SERVO_MAX_US - SERVO_MIN_US) * safe_angle / 180
    return int(pulse_us * 1023 / SERVO_PERIOD_US)


def set_servo_angle(angle_deg, settle_time_ms=SERVO_SETTLE_TIME_MS):
    """
    Move the servo to the requested angle and wait for the mechanism
    to settle.
    """
    servo_pwm.duty(angle_to_duty(angle_deg))
    sleep_ms(settle_time_ms)


def open_gate():
    """
    Move the dispenser gate to the open position.
    """
    set_servo_angle(SERVO_OPEN_ANGLE)


def close_gate():
    """
    Move the dispenser gate to the closed position.
    """
    set_servo_angle(SERVO_CLOSED_ANGLE)


# ============================================================
# Speaker helpers
# ============================================================

def speaker_off():
    """
    Stop speaker output cleanly.
    """
    speaker_pwm.duty(0)


def play_tone(frequency_hz, duration_ms, duty=SPEAKER_DUTY, gap_ms=20):
    """
    Play a single tone for a fixed duration.
    """
    speaker_pwm.freq(int(frequency_hz))
    speaker_pwm.duty(int(duty))
    sleep_ms(int(duration_ms))
    speaker_off()
    sleep_ms(int(gap_ms))


def play_meow():
    """
    Play a simple meow-like synthesized sound.

    This is a frequency sweep that sounds more expressive than a beep.
    """
    # Rising part
    for freq in range(750, 1300, 30):
        speaker_pwm.freq(freq)
        speaker_pwm.duty(SPEAKER_DUTY)
        sleep_ms(12)

    # Falling part
    for freq in range(1300, 500, -16):
        speaker_pwm.freq(freq)
        speaker_pwm.duty(SPEAKER_DUTY)
        sleep_ms(18)

    speaker_off()
    sleep_ms(50)


# ============================================================
# Dispenser action
# ============================================================

def dispense():
    """
    Execute one full dispense cycle:
    1. Open the gate and play meow simultaneously
    2. Wait for food to fall
    3. Close the gate
    """
    servo_pwm.duty(angle_to_duty(SERVO_OPEN_ANGLE))
    play_meow()
    sleep_ms(DISPENSE_OPEN_TIME_MS)
    close_gate()


# ============================================================
# LED / state helpers
# ============================================================

def update_led():
    """
    Update the LED to reflect the current machine state.

    External LED wired active-high (e.g. mini table lamp tutorial):
    - 1 = ON
    - 0 = OFF
    """
    if machine_enabled:
        led.value(1)
    else:
        led.value(0)


def set_machine_enabled(enabled):
    """
    Change the machine state and apply side effects.

    When the machine is turned ON:
    - LED turns on
    - one immediate dispense is triggered
    """
    global machine_enabled
    machine_enabled = bool(enabled)
    update_led()

    if machine_enabled:
        dispense()


def toggle_machine():
    """
    Toggle machine ON/OFF state.
    """
    set_machine_enabled(not machine_enabled)


# ============================================================
# Button edge detector with debounce
# ============================================================

class DebouncedButton:
    """
    Debounced active-low push button.

    pressed_event() returns True once for each valid press.
    """

    def __init__(self, pin, debounce_ms=DEBOUNCE_MS):
        self.pin = pin
        self.debounce_ms = debounce_ms
        self.last_raw_state = pin.value()
        self.stable_state = pin.value()
        self.last_change_time = ticks_ms()

    def pressed_event(self):
        """
        Return True exactly once when a clean press is detected.
        """
        now = ticks_ms()
        raw_state = self.pin.value()

        if raw_state != self.last_raw_state:
            self.last_raw_state = raw_state
            self.last_change_time = now

        if ticks_diff(now, self.last_change_time) >= self.debounce_ms:
            if self.stable_state != raw_state:
                self.stable_state = raw_state

                # Active-low button: 0 means pressed
                if self.stable_state == 0:
                    return True

        return False


# ============================================================
# Initialization
# ============================================================

def initialize():
    """
    Put the system in a known safe state at boot.
    """
    close_gate()
    speaker_off()
    update_led()


initialize()

power_button_input = DebouncedButton(power_button)
dispense_button_input = DebouncedButton(dispense_button)


# ============================================================
# Main loop
# ============================================================

while True:
    if power_button_input.pressed_event():
        toggle_machine()

    if machine_enabled and dispense_button_input.pressed_event():
        dispense()

    sleep_ms(LOOP_DELAY_MS)