import logging
log = logging.getLogger(__name__)

LIMITS = {
    "sleep_hours":        (0,    16),
    "energy_level":       (1,    10),
    "stress_level":       (1,    10),
    "rpe":                (1,    10),
    "sets":               (1,    20),
    "reps":               (1,   100),
    "weight_kg":          (0,   500),
    "heart_rate_resting": (30,  120),
    "heart_rate_max":     (60,  230),
    "vo2_max":            (10,   90),
    "calories_burned":    (0,  10000),
    "steps":              (0, 100000),
    "readiness_score":    (0,   100),
    "acwr":               (0,     5),
    "distance_km":        (0,   300),
    "duration_minutes":   (1,  1440),
}

def validate(value, field, user_id=None, context=""):
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        log.warning(f"[VALIDATION] {field}={value!r} ogiltig typ")
        return None
    if field not in LIMITS:
        return v
    lo, hi = LIMITS[field]
    if not (lo <= v <= hi):
        log.warning(f"[VALIDATION] {field}={v} utanfor [{lo}, {hi}] — ignoreras")
        return None
    return v

def clamp(value, field):
    if value is None:
        return None
    if field not in LIMITS:
        return float(value)
    lo, hi = LIMITS[field]
    return max(lo, min(hi, float(value)))

def is_valid_recovery(sleep_hours, energy_level, stress_level):
    return (
        validate(sleep_hours,  "sleep_hours")  is not None and
        validate(energy_level, "energy_level") is not None and
        validate(stress_level, "stress_level") is not None
    )