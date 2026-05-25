"""
progression_engine.py — Adaptive Progression Intelligence
"""
from sqlalchemy import text
from datetime import date, timedelta


def detect_plateau(user_id: int, exercise_id: int, conn, lookback_weeks: int = 4) -> dict:
    since = date.today() - timedelta(weeks=lookback_weeks)
    rows  = conn.execute(text("""
        SELECT ws.date, AVG(we.weight_kg) as avg_weight, AVG(we.rpe) as avg_rpe
        FROM workout_exercises we
        JOIN workout_sessions ws ON we.session_id = ws.id
        WHERE ws.user_id = :uid AND we.exercise_id = :eid AND ws.date >= :since
        GROUP BY ws.date ORDER BY ws.date
    """), {"uid": user_id, "eid": exercise_id, "since": since}).fetchall()

    if len(rows) < 3:
        return {"plateau_detected": False, "reason": "insufficient_data"}

    weights = [float(r[1]) for r in rows if r[1]]
    if len(weights) < 3:
        return {"plateau_detected": False, "reason": "no_weight_data"}

    weight_change = max(weights[-3:]) - min(weights[-3:])
    plateau       = weight_change < 2.5
    rpes          = [float(r[2]) for r in rows if r[2]]
    rpe_trend     = "stable"
    if len(rpes) >= 3:
        if rpes[-1] > rpes[0] + 1:  rpe_trend = "increasing"
        elif rpes[-1] < rpes[0] - 1: rpe_trend = "decreasing"

    return {
        "plateau_detected": plateau,
        "weight_change": round(weight_change, 2),
        "avg_weight": round(sum(weights)/len(weights), 2),
        "rpe_trend": rpe_trend,
        "sessions_analyzed": len(rows),
        "recommendation": _plateau_rec(plateau, rpe_trend, weights[-1])
    }


def _plateau_rec(plateau: bool, rpe_trend: str, current_weight: float) -> dict:
    if not plateau:
        if rpe_trend == "decreasing":
            return {"action": "increase_weight", "amount_kg": max(2.5, round(current_weight * 0.025, 1)),
                    "reason": "RPE sjunker — redo för mer vikt"}
        return {"action": "maintain", "reason": "Bra progression"}
    if rpe_trend == "increasing":
        return {"action": "deload", "amount_percent": -20, "reason": "Platå + ökande RPE"}
    return {"action": "swap_exercise", "reason": "Platå — byt övning för ny stimulus"}


def calculate_auto_progression(user_id: int, exercise_id: int, conn) -> dict | None:
    last = conn.execute(text("""
        SELECT we.weight_kg, we.reps, we.sets, we.rpe
        FROM workout_exercises we
        JOIN workout_sessions ws ON we.session_id = ws.id
        WHERE ws.user_id = :uid AND we.exercise_id = :eid
        ORDER BY ws.date DESC LIMIT 3
    """), {"uid": user_id, "eid": exercise_id}).fetchall()

    if not last: return None
    latest = last[0]
    weight = float(latest[0]) if latest[0] else 0
    reps   = int(latest[1])   if latest[1] else 0
    rpe    = float(latest[3]) if latest[3] else 8.0

    if rpe < 7.0 and reps >= 12:
        return {"action": "increase_weight", "current_weight": weight,
                "new_weight": weight + 2.5, "reason": f"RPE {rpe} < 7 och {reps} reps"}
    elif rpe < 7.0 and reps < 12:
        return {"action": "increase_reps", "current_reps": reps, "target_reps": reps + 1,
                "reason": f"RPE {rpe} < 7 — lägg till 1 rep"}
    elif rpe > 9.0:
        return {"action": "decrease_weight", "current_weight": weight,
                "new_weight": round(weight * 0.9, 1), "reason": f"RPE {rpe} > 9 — för tungt"}
    return {"action": "maintain", "current_weight": weight,
            "reason": f"RPE {rpe} — optimal zon"}


def analyze_readiness_trend(user_id: int, conn, lookback_days: int = 14) -> dict:
    since = date.today() - timedelta(days=lookback_days)
    rows  = conn.execute(text("""
        SELECT date, readiness_score, recovery_score, fatigue_score, acwr
        FROM fatigue_scores
        WHERE user_id = :uid AND date >= :since ORDER BY date ASC
    """), {"uid": user_id, "since": since}).fetchall()

    if len(rows) < 2: return {"status": "insufficient_data"}

    r_vals   = [float(r[1]) for r in rows if r[1]]
    acwr_vals= [float(r[4]) for r in rows if r[4]]
    avg_r    = sum(r_vals) / len(r_vals)
    recent   = sum(r_vals[-3:]) / min(3, len(r_vals))
    slope    = (r_vals[-1] - r_vals[0]) / max(len(r_vals), 1)
    mean     = avg_r
    vol      = (sum((x-mean)**2 for x in r_vals)/len(r_vals))**0.5
    avg_acwr = sum(acwr_vals)/len(acwr_vals) if acwr_vals else 1.0

    burnout = 0.0
    if avg_r < 55:    burnout += 30
    if avg_acwr > 1.3: burnout += 25
    if slope < -2:    burnout += 25
    if vol > 10:      burnout += 20
    burnout = min(100, burnout)

    acwr_trend = "stable"
    if len(acwr_vals) >= 2:
        if acwr_vals[-1] > acwr_vals[0]:  acwr_trend = "increasing"
        elif acwr_vals[-1] < acwr_vals[0]: acwr_trend = "decreasing"

    result = {
        "readiness_avg": round(avg_r, 1),
        "readiness_recent": round(recent, 1),
        "readiness_slope": round(slope, 3),
        "readiness_volatility": round(vol, 2),
        "acwr_avg": round(avg_acwr, 3),
        "acwr_trend": acwr_trend,
        "burnout_risk_score": round(burnout, 1),
        "plateau_risk_score": round(max(0, (55 - avg_r) + vol), 1),
        "anomaly_detected": vol > 15 or burnout > 60,
    }

    try:
        conn.execute(text("""
            INSERT INTO readiness_trends
                (user_id, calculated_at, readiness_7d_avg, readiness_28d_avg,
                 readiness_slope, readiness_volatility, acwr_7d_avg,
                 acwr_trend, burnout_risk_score, plateau_risk_score, anomaly_detected)
            VALUES (:uid, :date, :r7, :r28, :slope, :vol, :acwr, :trend, :burnout, :plateau, :anomaly)
            ON CONFLICT (user_id, calculated_at) DO UPDATE SET
                readiness_7d_avg = EXCLUDED.readiness_7d_avg,
                burnout_risk_score = EXCLUDED.burnout_risk_score
        """), {"uid": user_id, "date": date.today(), "r7": result["readiness_recent"],
               "r28": result["readiness_avg"], "slope": result["readiness_slope"],
               "vol": result["readiness_volatility"], "acwr": result["acwr_avg"],
               "trend": result["acwr_trend"], "burnout": result["burnout_risk_score"],
               "plateau": result["plateau_risk_score"], "anomaly": result["anomaly_detected"]})
        conn.commit()
    except Exception:
        pass

    return result
