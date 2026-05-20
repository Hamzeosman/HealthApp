FATIGUE_MODEL_VERSION = "v1.0"

def calculate_fatigue(volume_kg, avg_rpe):
    return float(volume_kg) * float(avg_rpe)

def calculate_fatigue_ratio(current_fatigue, chronic_baseline):
    if chronic_baseline <= 0: return 1.0
    return round(current_fatigue / chronic_baseline, 2)

def get_fatigue_label(fatigue_ratio):
    if fatigue_ratio < 0.8: return "LOW"
    elif fatigue_ratio < 1.2: return "NORMAL"
    elif fatigue_ratio < 1.5: return "HIGH"
    else: return "VERY HIGH"

def is_overreaching(current_fatigue, previous_fatigue):
    if previous_fatigue <= 0: return False
    return current_fatigue > previous_fatigue * 1.5
