"""
Servo motor control for the dispensing gate.
"""

from time import sleep_ms
from config import (
    SERVO_MIN_US, SERVO_MAX_US, SERVO_PERIOD_US,
    SERVO_CLOSED_ANGLE, SERVO_OPEN_ANGLE, SERVO_SETTLE_TIME_MS,
)
from hardware import servo_pwm


def clamp(value, minimum, maximum):
    """Clamp a numeric value into [minimum, maximum]."""
    return max(minimum, min(maximum, value))


def angle_to_duty(angle_deg):
    """Convert an angle (0-180) into a PWM duty value for the servo."""
    safe_angle = clamp(angle_deg, 0, 180)
    pulse_us = SERVO_MIN_US + (SERVO_MAX_US - SERVO_MIN_US) * safe_angle / 180
    return int(pulse_us * 1023 / SERVO_PERIOD_US)


def set_servo_angle(angle_deg, settle_time_ms=SERVO_SETTLE_TIME_MS):
    """Move the servo to the requested angle and wait for it to settle."""
    servo_pwm.duty(angle_to_duty(angle_deg))
    sleep_ms(settle_time_ms)


def open_gate():
    """Move the dispenser gate to the open position."""
    set_servo_angle(SERVO_OPEN_ANGLE)


def close_gate():
    """Move the dispenser gate to the closed position."""
    set_servo_angle(SERVO_CLOSED_ANGLE)
