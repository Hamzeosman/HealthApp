ACWR_MODEL_VERSION = "v1.0"

def calculate_acwr_ema(loads, alpha=0.5):
    if not loads or len(loads) < 2: return 1.0
    acute = loads[0]
    ema = loads[-1]
    for load in reversed(loads[1:]):
        ema = alpha * load + (1 - alpha) * ema
    return round(acute / ema, 2) if ema > 0 else 1.0

def get_acwr_label(acwr):
    if acwr < 0.8: return "UNDERTRAINING"
    elif acwr <= 1.3: return "OPTIMAL ZONE"
    elif acwr <= 1.5: return "CAUTION ZONE"
    else: return "DANGER ZONE"

def is_danger_zone(acwr):
    return acwr > 1.5
