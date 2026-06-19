from core.domain.readiness import TrainingState, calculate_composite_readiness, get_readiness_label, should_deload
from core.domain.fatigue import calculate_fatigue, calculate_fatigue_ratio, get_fatigue_label
from core.domain.acwr import calculate_acwr_ema, get_acwr_label
from core.domain.recovery import calculate_recovery_score, get_recovery_label
from core.repositories.workout_repo import get_weekly_load
from core.repositories.recovery_repo import get_recovery_data

def build_training_state(user_id: int) -> TrainingState:
    rec = get_recovery_data(user_id)
    recovery_score = 50.0
    if rec and rec[0]:
        recovery_score = calculate_recovery_score(float(rec[0]), float(rec[1]), float(rec[2]), float(rec[3]))

    loads = []
    for week in range(5):
        w = get_weekly_load(user_id, week_offset=week)
        loads.append(float(w[0] or 0) * float(w[1] or 7))

    acwr = calculate_acwr_ema(loads, alpha=0.5)
    current = get_weekly_load(user_id, week_offset=0)
    fatigue = calculate_fatigue(float(current[0] or 0), float(current[1] or 7))
    chronic_avg = sum(loads[1:]) / max(len(loads[1:]), 1)
    fatigue_ratio = calculate_fatigue_ratio(fatigue, chronic_avg)
    readiness = calculate_composite_readiness(recovery_score, acwr, fatigue_ratio)

    return TrainingState(
        user_id=user_id,
        recovery_score=round(recovery_score, 1),
        acwr=acwr,
        fatigue_ratio=fatigue_ratio,
        readiness_score=readiness,
        recovery_label=get_recovery_label(recovery_score),
        acwr_label=get_acwr_label(acwr),
        fatigue_label=get_fatigue_label(fatigue_ratio),
        readiness_label=get_readiness_label(readiness),
        deload_recommended=should_deload(readiness, acwr)
    )
