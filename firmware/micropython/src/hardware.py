"""
Hardware initialization.

Creates Pin and PWM objects for all peripherals.
Other modules import hardware objects from here.
"""

from machine import Pin, PWM
from config import (
    LED_PIN, POWER_BUTTON_PIN, DISPENSE_BUTTON_PIN,
    SERVO_PIN, SERVO_FREQUENCY_HZ,
    SPEAKER_PIN,
)

# ── Outputs ────────────────────────────────────────────

led = Pin(LED_PIN, Pin.OUT)
servo_pwm = PWM(Pin(SERVO_PIN), freq=SERVO_FREQUENCY_HZ)
speaker_pwm = PWM(Pin(SPEAKER_PIN))
speaker_pwm.duty(0)

# ── Inputs ─────────────────────────────────────────────

power_button = Pin(POWER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
dispense_button = Pin(DISPENSE_BUTTON_PIN, Pin.IN, Pin.PULL_UP)
