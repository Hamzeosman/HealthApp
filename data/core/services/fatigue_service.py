from core.repositories.workout_repo import get_weekly_load

def get_fatigue_trend(user_id: int, weeks: int = 4) -> list:
    trend = []
    for week in range(weeks):
        w = get_weekly_load(user_id, week_offset=week)
        volume = float(w[0] or 0)
        rpe = float(w[1] or 7)
        trend.append({
            "week_offset": week,
            "volume": round(volume, 2),
            "avg_rpe": round(rpe, 2),
            "fatigue": round(volume * rpe, 2)
        })
    return trend

def is_overreaching(user_id: int) -> bool:
    trend = get_fatigue_trend(user_id, weeks=2)
    if len(trend) < 2:
        return False
    return trend[0]["fatigue"] > trend[1]["fatigue"] * 1.5
