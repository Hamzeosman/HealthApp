"""
readiness_service.py — Pure orchestration, no math.
All math lives in core/domain/
"""
from core.domain.builder import build_training_state
from core.domain.readiness import TrainingState
from core.repositories.metrics_repo import save_training_metrics
from core.repositories.insights_repo import save_insight
from core.repositories.workout_repo import get_weekly_load
from datetime import datetime

def get_user_readiness(user_id: int) -> TrainingState:
    """Returns typed TrainingState for a user."""
    return build_training_state(user_id)

def save_user_readiness(user_id: int) -> TrainingState:
    """Orchestrates: build state → save metrics → save insight."""
    state = build_training_state(user_id)
    current = get_weekly_load(user_id, week_offset=0)

    save_training_metrics(user_id, {
        "recovery": state.recovery_score,
        "fatigue": state.readiness_score,
        "volume": float(current[0] or 0),
        "sets": int(current[2] or 0),
        "acwr": state.acwr,
        "readiness": state.readiness_label
    })

    title = f"Training Intelligence — {datetime.now().strftime('%Y-%m-%d')}"
    content = (f"Readiness: {state.readiness_score}/100 — {state.readiness_label}. "
               f"Recovery: {state.recovery_score}/100. "
               f"ACWR: {state.acwr} ({state.acwr_label}).")
    if state.deload_recommended:
        content += " Deload rekommenderas."

    save_insight(user_id, title, content, "weekly_analysis")
    return state
