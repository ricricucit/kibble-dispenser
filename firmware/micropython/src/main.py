"""
Feedr Outdoor — ESP32 Cat Food Dispenser
=========================================

Entry point. Initializes hardware to a safe state, then runs the
polling loop for button inputs.
"""

from time import sleep, sleep_ms
from config import LOOP_DELAY_MS

# Brief startup delay so mpremote can connect for deploy/REPL
BOOT_DELAY_S = 2
from hardware import power_button, dispense_button
from servo import close_gate
from speaker import speaker_off
from buttons import DebouncedButton
from dispenser import Dispenser


def initialize():
    """Put the system in a known safe state at boot."""
    close_gate()
    speaker_off()


def main():
    """Main polling loop."""
    sleep(BOOT_DELAY_S)
    initialize()

    feeder = Dispenser()
    feeder.update_led()

    power_btn = DebouncedButton(power_button)
    dispense_btn = DebouncedButton(dispense_button)

    while True:
        if power_btn.pressed_event():
            feeder.toggle()

        if feeder.enabled and dispense_btn.pressed_event():
            feeder.dispense()

        sleep_ms(LOOP_DELAY_MS)


if __name__ == "__main__":
    main()
