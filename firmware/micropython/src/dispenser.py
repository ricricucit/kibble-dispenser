"""
Dispenser logic and machine state management.

This module owns the machine state and is the single source of truth
for all feeding events.
"""

from time import sleep_ms
from config import SERVO_OPEN_ANGLE, DISPENSE_OPEN_TIME_MS
from hardware import led
from servo import angle_to_duty, close_gate
from speaker import play_feeding_sound


class Dispenser:
    """
    Stateful dispenser controller.

    Manages machine on/off state and orchestrates dispense cycles.
    """

    def __init__(self):
        self.enabled = False

    def update_led(self):
        """
        Update the LED to reflect machine state.

        External LED wired active-high (mini table lamp tutorial):
        - 1 = ON
        - 0 = OFF
        """
        led.value(1 if self.enabled else 0)

    def dispense(self):
        """
        Execute one full dispense cycle:
        1. Open gate and play meow simultaneously
        2. Wait for food to fall
        3. Close the gate
        """
        from hardware import servo_pwm
        servo_pwm.duty(angle_to_duty(SERVO_OPEN_ANGLE))
        play_feeding_sound()
        sleep_ms(DISPENSE_OPEN_TIME_MS)
        close_gate()

    def set_enabled(self, enabled):
        """
        Change machine state. When turned ON, triggers one immediate dispense.
        """
        self.enabled = bool(enabled)
        self.update_led()
        if self.enabled:
            self.dispense()

    def toggle(self):
        """Toggle machine ON/OFF."""
        self.set_enabled(not self.enabled)
