"""
core/metrics.py — Single source of truth for all calculations.
Baserat pa evidensbaserade riktlinjer (Schoenfeld, Gabbett et al.)
"""

def calculate_recovery_score(sleep, energy, stress, sleep_quality):
    sleep_score = min(100, (sleep / 9) * 100)
    energy_score = (energy / 10) * 100
    stress_score = ((10 - stress) / 10) * 100
    quality_score = (sleep_quality / 10) * 100
    return round(sleep_score * 0.35 + energy_score * 0.30 +
                 stress_score * 0.20 + quality_score * 0.15, 1)

def calculate_fatigue(volume_kg, avg_rpe):
    """fatigue = volume * rpe (sports science standard)"""
    return float(volume_kg) * float(avg_rpe)

def calculate_acwr_ema(weekly_loads, alpha=0.5):
    """
    ACWR med Exponential Moving Average.
    acute = senaste veckan, chronic = EMA senaste 4 veckor.
    """
    if not weekly_loads or len(weekly_loads) < 2:
        return 1.0
    acute = weekly_loads[0]
    ema = weekly_loads[-1]
    for load in reversed(weekly_loads[1:]):
        ema = alpha * load + (1 - alpha) * ema
    return round(acute / ema, 2) if ema > 0 else 1.0

def calculate_composite_readiness(recovery_score, acwr, fatigue_ratio):
    """
    Composite Readiness Score.
    readiness = 0.4*recovery + 0.3*acwr_norm + 0.3*fatigue_norm
    """
    acwr_norm = max(0, 1 - abs(acwr - 1.0)) * 100
    fatigue_norm = max(0, min(100, (1 - max(0, fatigue_ratio - 1.0)) * 100))
    return round(0.4 * recovery_score + 0.3 * acwr_norm + 0.3 * fatigue_norm, 1)

def calculate_push_pull_ratio(muscle_sets):
    push = sum(muscle_sets.get(m, 0) for m in ["Brost", "Bröst", "Axlar"])
    pull = sum(muscle_sets.get(m, 0) for m in ["Rygg", "Armar"])
    return round(push / pull, 2) if pull > 0 else 0.0

def calculate_upper_lower_ratio(muscle_sets):
    upper = sum(muscle_sets.get(m, 0) for m in ["Brost", "Bröst", "Rygg", "Axlar", "Armar"])
    lower = sum(muscle_sets.get(m, 0) for m in ["Ben", "Mage"])
    return round(upper / lower, 2) if lower > 0 else 0.0

def get_readiness_label(score):
    if score >= 80:
        return "READY TO TRAIN HARD"
    elif score >= 65:
        return "GOOD TO TRAIN"
    elif score >= 50:
        return "TRAIN LIGHT"
    else:
        return "REST OR DELOAD"

def get_acwr_label(acwr):
    if acwr < 0.8:
        return "UNDERTRAINING"
    elif acwr <= 1.3:
        return "OPTIMAL ZONE"
    elif acwr <= 1.5:
        return "CAUTION ZONE"
    else:
        return "DANGER ZONE"
