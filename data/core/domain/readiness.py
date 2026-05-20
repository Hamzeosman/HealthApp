from dataclasses import dataclass, field

READINESS_MODEL_VERSION = "v1.0"

@dataclass
class TrainingState:
    user_id: int
    recovery_score: float
    acwr: float
    fatigue_ratio: float
    readiness_score: float = 0.0
    recovery_label: str = ""
    acwr_label: str = ""
    fatigue_label: str = ""
    readiness_label: str = ""
    deload_recommended: bool = False

def calculate_composite_readiness(recovery_score, acwr, fatigue_ratio):
    acwr_norm    = max(0, 1 - abs(acwr - 1.0)) * 100
    fatigue_norm = max(0, min(100, (1 - max(0, fatigue_ratio - 1.0)) * 100))
    return round(0.4 * recovery_score + 0.3 * acwr_norm + 0.3 * fatigue_norm, 1)

def get_readiness_label(score):
    if score >= 80: return "READY TO TRAIN HARD"
    elif score >= 65: return "GOOD TO TRAIN"
    elif score >= 50: return "TRAIN LIGHT"
    else: return "REST OR DELOAD"

def should_deload(readiness_score, acwr):
    return readiness_score < 40 or acwr > 1.5
