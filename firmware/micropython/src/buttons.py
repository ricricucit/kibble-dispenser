"""
Debounced button input handling.
"""

from time import ticks_ms, ticks_diff
from config import DEBOUNCE_MS


class DebouncedButton:
    """
    Debounced active-low push button.

    pressed_event() returns True once per valid press (falling edge).
    """

    def __init__(self, pin, debounce_ms=DEBOUNCE_MS):
        self.pin = pin
        self.debounce_ms = debounce_ms
        self.last_raw_state = pin.value()
        self.stable_state = pin.value()
        self.last_change_time = ticks_ms()

    def pressed_event(self):
        """Return True exactly once when a clean press is detected."""
        now = ticks_ms()
        raw_state = self.pin.value()

        if raw_state != self.last_raw_state:
            self.last_raw_state = raw_state
            self.last_change_time = now

        if ticks_diff(now, self.last_change_time) >= self.debounce_ms:
            if self.stable_state != raw_state:
                self.stable_state = raw_state
                # Active-low: 0 means pressed
                if self.stable_state == 0:
                    return True

        return False
