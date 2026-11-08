"""
Speaker control and sound effects.

Retro arcade feeding sound — designed for max impact on a small
PWM-driven speaker through a resistor.
"""

from time import sleep_ms
from hardware import speaker_pwm

# 50% duty = loudest clean square wave on a passive speaker
LOUD = 512


def speaker_off():
    """Stop speaker output cleanly."""
    speaker_pwm.duty(0)


def play_tone(frequency_hz, duration_ms, duty=LOUD, gap_ms=0):
    """Play a single tone for a fixed duration."""
    speaker_pwm.freq(int(frequency_hz))
    speaker_pwm.duty(int(duty))
    sleep_ms(int(duration_ms))
    speaker_off()
    if gap_ms:
        sleep_ms(int(gap_ms))


def play_feeding_sound():
    """
    Arcade feeding fanfare.

    Three-part sound designed for a small PWM speaker:
    1. Alert chirps — quick staccato to grab attention
    2. Victory arpeggio — ascending major chord, classic power-up feel
    3. Fanfare finish — high triumphant trill

    Notes use the C major scale for a bright, happy sound.
    Mid-range frequencies (800-3500 Hz) are the sweet spot for small speakers.
    """
    d = LOUD

    # ── Part 1: attention chirps (short-short-short) ──
    for _ in range(3):
        play_tone(2500, 25, d)
        sleep_ms(25)

    sleep_ms(40)

    # ── Part 2: ascending power-up arpeggio ──
    # C5 → E5 → G5 → C6 → E6 → G6, getting faster
    arpeggio = [
        (1047, 55),   # C5
        (1319, 50),   # E5
        (1568, 45),   # G5
        (2093, 40),   # C6
        (2637, 35),   # E6
        (3136, 30),   # G6
    ]
    for freq, ms in arpeggio:
        play_tone(freq, ms, d)
        sleep_ms(8)

    # ── Part 3: triumphant finish ──
    # High note with a fast vibrato trill
    for i in range(6):
        f = 3520 if i % 2 == 0 else 3320  # A7 / ~G#7 trill
        speaker_pwm.freq(f)
        speaker_pwm.duty(d)
        sleep_ms(25)

    # Final long high note — the "you got the item!" moment
    play_tone(4186, 180, d)  # C8

    speaker_off()
