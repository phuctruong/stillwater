"""
Deterministic weather banter generator.

Rule-based. No network. No randomness. No ML.
Caller supplies WeatherContext; we never fetch weather ourselves.

All rules are evaluated in order; first match wins (deterministic).

rung_target: 641
"""

from __future__ import annotations

from typing import Optional

from .models import WeatherContext


# ---------------------------------------------------------------------------
# Location-specific overrides (checked before generic rules)
# ---------------------------------------------------------------------------

_LOCATION_RULES: list[tuple[str, str]] = [
    ("San Francisco", "Beautiful SF day. The Golden Gate Bridge agrees: perfect weather for code."),
    ("Seattle", "Rain in Seattle? Shocking. (Not.) Perfect coding weather."),
    ("New York", "New York weather: unpredictable, like a production outage."),
    ("London", "London drizzle + good headphones = flow state unlocked."),
    ("Tokyo", "Tokyo weather is always a vibe. Embrace it."),
    ("Austin", "Austin heat means stay inside and ship features."),
    ("Denver", "Mile-high altitude, mile-high ambitions."),
    ("Chicago", "Windy City coding: stack the commits like pancakes."),
    ("Miami", "Miami sun? Close the blinds, open the terminal."),
    ("Portland", "Portland rain and coffee — the classic developer combo."),
]

# ---------------------------------------------------------------------------
# Temperature rules (Fahrenheit)
# ---------------------------------------------------------------------------

_TEMP_RULES: list[tuple[str, float, Optional[float], str]] = [
    # (description, min_f, max_f_or_None, banter)
    ("scorching",   100.0, None,  "Over 100F out there! Stay hydrated. The code will wait."),
    ("very_hot",    90.0,  100.0, "Hot day for coding! Keep the AC on and the tests green."),
    ("warm",        75.0,   90.0, "Nice and warm. A cold drink + a hot terminal session."),
    ("comfortable", 60.0,   75.0, "Perfect coding temperature. No excuses not to ship."),
    ("chilly",      40.0,   60.0, "A little chilly. Hot coffee recommended before the next PR."),
    ("cold",        20.0,   40.0, "Cold outside. Time to generate some CPU heat."),
    ("freezing",    None,   20.0, "Freezing! Let the CPU warm up the room."),
]

# ---------------------------------------------------------------------------
# Condition rules
# ---------------------------------------------------------------------------

_CONDITION_RULES: list[tuple[str, str]] = [
    ("snow",     "Snowy weather = cozy coding vibes. Stay warm and ship something."),
    ("sleet",    "Sleet outside. Good reason to stay in and debug."),
    ("rain",     "Perfect day for deep focus (thanks, rain)."),
    ("drizzle",  "A light drizzle and a good problem to solve. Classic."),
    ("storm",    "Storm rolling in. Make sure your work is committed."),
    ("thunder",  "Thunder outside. Close the windows; open the diff."),
    ("fog",      "Foggy outside, clear code inside. Keep going."),
    ("cloudy",   "Overcast but focused. Clouds outside, clarity in the terminal."),
    ("clear",    "Clear sky, clear mind. Good day to tackle the backlog."),
    ("windy",    "Windy day. Your ideas have momentum too."),
    ("humid",    "Humid and sticky outside. Crisp code is the antidote."),
    ("sunny",    "Sunny day! Natural light is good for the eyes — and the code."),
]

# ---------------------------------------------------------------------------
# Time-of-day rules (hour 0-23 in caller's local time)
# ---------------------------------------------------------------------------

_TIME_RULES: list[tuple[int, int, str]] = [
    # (start_hour_inclusive, end_hour_exclusive, banter)
    (5,   9,  "Early morning session. Coffee first, commits second."),
    (9,  12,  "Morning momentum. Good time to tackle the hard problem."),
    (12, 14,  "Midday grind. Take a lunch break if you haven't."),
    (14, 17,  "Afternoon zone. Deep work window — protect it."),
    (17, 20,  "Evening shift. One more feature before dinner?"),
    (20, 23,  "Night owl session. Remember to commit before sleep."),
    (23, 24,  "Late night coding. Tomorrow's self will thank present self."),
    (0,   5,  "Midnight code. Legendary. Just make sure to commit."),
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_weather_banter(
    weather: Optional[WeatherContext] = None,
    local_hour: Optional[int] = None,
) -> str:
    """
    Generate a contextual weather/time banter string.

    Priority order (first match wins):
    1. Location-specific override
    2. Precipitation (snow / rain)
    3. Temperature extremes
    4. General condition
    5. Time of day
    6. Generic fallback

    All deterministic. No randomness.

    Args:
        weather:    WeatherContext from caller (None → time-only or generic fallback)
        local_hour: Caller's local hour (0-23) for time-based banter

    Returns:
        A short banter string (< 120 chars).
    """
    if weather:
        # 1. Location override
        if weather.location:
            loc = weather.location.strip()
            for location, banter in _LOCATION_RULES:
                if location.lower() in loc.lower():
                    return banter

        # 2. Precipitation
        if weather.is_snowing:
            return "Snowy weather = cozy coding vibes. Stay warm and ship something."
        if weather.is_raining:
            return "Perfect day for deep focus (thanks, rain)."

        # 3. Temperature
        if weather.temp_f is not None:
            for desc, min_f, max_f, banter in _TEMP_RULES:
                if min_f is not None and max_f is not None:
                    if min_f <= weather.temp_f < max_f:
                        return banter
                elif min_f is not None and weather.temp_f >= min_f:
                    return banter
                elif max_f is not None and weather.temp_f < max_f:
                    return banter

        # 4. Condition string
        if weather.condition:
            cond = weather.condition.lower()
            for keyword, banter in _CONDITION_RULES:
                if keyword in cond:
                    return banter

    # 5. Time of day
    if local_hour is not None:
        hour = local_hour % 24
        for start, end, banter in _TIME_RULES:
            if start <= hour < end:
                return banter

    # 6. Generic fallback
    return "Keep coding. You're doing great."
