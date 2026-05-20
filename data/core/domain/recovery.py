RECOVERY_MODEL_VERSION = "v1.0"

def calculate_recovery_score(sleep_hours, energy_level, stress_level, sleep_quality):
    sleep_score   = min(100, (sleep_hours / 9) * 100)
    energy_score  = (energy_level / 10) * 100
    stress_score  = ((10 - stress_level) / 10) * 100
    quality_score = (sleep_quality / 10) * 100
    return round(sleep_score * 0.35 + energy_score * 0.30 + stress_score * 0.20 + quality_score * 0.15, 1)

def get_recovery_label(score):
    if score >= 80: return "OPTIMAL"
    elif score >= 65: return "GOOD"
    elif score >= 50: return "MODERATE"
    else: return "LOW"
