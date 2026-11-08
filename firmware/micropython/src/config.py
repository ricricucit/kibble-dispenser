"""
Hardware configuration and calibration constants.

All pin assignments, servo angles, timing values, and speaker settings live here.
Import this module from any other module that needs hardware constants.
"""

from micropython import const

# ── Pin assignments ────────────────────────────────────

LED_PIN = const(2)
POWER_BUTTON_PIN = const(13)
DISPENSE_BUTTON_PIN = const(27)
SERVO_PIN = const(14)
SPEAKER_PIN = const(26)

# ── Servo calibration ─────────────────────────────────

SERVO_FREQUENCY_HZ = const(50)
SERVO_MIN_US = const(500)
SERVO_MAX_US = const(2500)
SERVO_PERIOD_US = const(20000)

# Adjust these to match your mechanical setup
SERVO_CLOSED_ANGLE = const(10)
SERVO_OPEN_ANGLE = const(100)

SERVO_SETTLE_TIME_MS = const(400)
DISPENSE_OPEN_TIME_MS = const(800)

# ── Speaker calibration ───────────────────────────────

SPEAKER_DUTY = const(512)

# ── Timing ─────────────────────────────────────────────

DEBOUNCE_MS = const(50)
LOOP_DELAY_MS = const(10)
