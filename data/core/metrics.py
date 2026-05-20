"""
metrics.py — Backwards compatibility layer.
All math has moved to core/domain/
Import from domain directly for new code.
"""
from core.domain.fatigue import calculate_fatigue, calculate_fatigue_ratio
from core.domain.recovery import calculate_recovery_score
from core.domain.acwr import calculate_acwr_ema, get_acwr_label
from core.domain.readiness import calculate_composite_readiness, get_readiness_label

__all__ = [
    "calculate_fatigue",
    "calculate_fatigue_ratio",
    "calculate_recovery_score",
    "calculate_acwr_ema",
    "get_acwr_label",
    "calculate_composite_readiness",
    "get_readiness_label",
]
