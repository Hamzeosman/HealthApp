"""
recommendation_engine.py
Rule-based AI Coach Engine.
Genererar warnings, recommendations och coach-meddelanden.
Designad för att enkelt bytas ut mot XGBoost/sklearn senare.
"""
from datetime import date
from sqlalchemy import text
from core.db import get_engine

engine = get_engine()


def _get_user_context(user_id: int, conn) -> dict:
    """Hämtar all kontext för en user."""
    # Fatigue + readiness
    fs = conn.execute(text("""
        SELECT readiness_score, recovery_score, fatigue_score,
               acwr, training_zone, deload_recommended
        FROM fatigue_scores
        WHERE user_id = :uid ORDER BY date DESC LIMIT 1
    """), {"uid": user_id}).fetchone()

    # Model predictions
    mp = conn.execute(text("""
        SELECT injury_risk_score, dropout_risk_score,
               plateau_risk_score, overtraining_risk_score,
               recommended_intensity, primary_recommendation
        FROM model_predictions
        WHERE user_id = :uid ORDER BY date DESC LIMIT 1
    """), {"uid": user_id}).fetchone()

    # Daily features
    df = conn.execute(text("""
        SELECT sleep_hours_7d_avg, sleep_consistency_score,
               days_since_last_workout, workout_consistency_30d,
               hrv_7d_avg, stress_7d_avg, energy_7d_avg,
               sessions_7d, volume_7d, volume_28d_avg
        FROM user_daily_features
        WHERE user_id = :uid ORDER BY date DESC LIMIT 1
    """), {"uid": user_id}).fetchone()

    # User info
    user = conn.execute(text("""
        SELECT id, name, fitness_goal, fitness_level
        FROM users WHERE id = :uid
    """), {"uid": user_id}).fetchone()

    return {
        "user_id": user_id,
        "name": user[1] if user else "Unknown",
        "fitness_goal": user[2] if user else None,
        "fitness_level": user[3] if user else None,
        "readiness": float(fs[0]) if fs and fs[0] else 50.0,
        "recovery": float(fs[1]) if fs and fs[1] else 50.0,
        "fatigue": float(fs[2]) if fs and fs[2] else 50.0,
        "acwr": float(fs[3]) if fs and fs[3] else 1.0,
        "training_zone": fs[4] if fs else "optimal",
        "deload_recommended": bool(fs[5]) if fs else False,
        "injury_risk": float(mp[0]) if mp and mp[0] else 0.0,
        "dropout_risk": float(mp[1]) if mp and mp[1] else 0.0,
        "plateau_risk": float(mp[2]) if mp and mp[2] else 0.0,
        "overtraining_risk": float(mp[3]) if mp and mp[3] else 0.0,
        "recommended_intensity": mp[4] if mp else "moderate",
        "sleep_avg": float(df[0]) if df and df[0] else 7.0,
        "sleep_consistency": float(df[1]) if df and df[1] else 80.0,
        "days_since_workout": int(df[2]) if df and df[2] else 0,
        "consistency_30d": float(df[3]) if df and df[3] else 50.0,
        "hrv_avg": float(df[4]) if df and df[4] else None,
        "stress_avg": float(df[5]) if df and df[5] else 5.0,
        "energy_avg": float(df[6]) if df and df[6] else 7.0,
        "sessions_7d": int(df[7]) if df and df[7] else 0,
        "volume_7d": float(df[8]) if df and df[8] else 0.0,
        "volume_28d": float(df[9]) if df and df[9] else 0.0,
    }


def _generate_warnings(ctx: dict) -> list:
    warnings = []

    if ctx['acwr'] > 1.5:
        warnings.append({
            "type": "overtraining",
            "message": f"ACWR är {ctx['acwr']:.2f} — kritisk överbelastningsrisk.",
            "severity": "critical"
        })
    elif ctx['acwr'] > 1.3:
        warnings.append({
            "type": "overtraining",
            "message": f"ACWR är {ctx['acwr']:.2f} — hög träningsbelastning.",
            "severity": "high"
        })

    if ctx['sleep_avg'] < 6.0:
        warnings.append({
            "type": "sleep",
            "message": f"Sömnmedelvärde {ctx['sleep_avg']:.1f}h — under rekommenderat minimum.",
            "severity": "high"
        })
    elif ctx['sleep_avg'] < 7.0:
        warnings.append({
            "type": "sleep",
            "message": f"Sömnmedelvärde {ctx['sleep_avg']:.1f}h — något lågt.",
            "severity": "medium"
        })

    if ctx['sleep_consistency'] < 70:
        warnings.append({
            "type": "sleep_consistency",
            "message": f"Sömnkonsistens {ctx['sleep_consistency']:.0f}% — oregelbundna sömnmönster.",
            "severity": "medium"
        })

    if ctx['days_since_workout'] > 14:
        warnings.append({
            "type": "inactivity",
            "message": f"Ingen träning på {ctx['days_since_workout']} dagar — risk för detraining.",
            "severity": "high"
        })
    elif ctx['days_since_workout'] > 7:
        warnings.append({
            "type": "inactivity",
            "message": f"Ingen träning på {ctx['days_since_workout']} dagar.",
            "severity": "medium"
        })

    if ctx['injury_risk'] > 70:
        warnings.append({
            "type": "injury_risk",
            "message": f"Hög skaderisk ({ctx['injury_risk']:.0f}/100) — minska belastning.",
            "severity": "critical"
        })
    elif ctx['injury_risk'] > 50:
        warnings.append({
            "type": "injury_risk",
            "message": f"Förhöjd skaderisk ({ctx['injury_risk']:.0f}/100).",
            "severity": "high"
        })

    if ctx['stress_avg'] > 7.5:
        warnings.append({
            "type": "stress",
            "message": f"Hög stressnivå ({ctx['stress_avg']:.1f}/10) — påverkar återhämtning.",
            "severity": "medium"
        })

    if ctx['dropout_risk'] > 70:
        warnings.append({
            "type": "dropout",
            "message": "Hög avhoppsrisk — engagemang och motivation behöver uppmärksamhet.",
            "severity": "high"
        })

    if ctx['plateau_risk'] > 60:
        warnings.append({
            "type": "plateau",
            "message": "Platåindikation — progressionen kan ha stannat av.",
            "severity": "medium"
        })

    return sorted(warnings, key=lambda w: {"critical": 0, "high": 1, "medium": 2, "low": 3}[w['severity']])


def _generate_recommendations(ctx: dict) -> list:
    recs = []
    priority = 1

    if ctx['deload_recommended'] or ctx['acwr'] > 1.5:
        recs.append({
            "category": "training_load",
            "action": "Ta en deload-vecka — minska volym med 40-50%",
            "reason": f"ACWR {ctx['acwr']:.2f} indikerar överbelastning",
            "priority": priority
        })
        priority += 1

    if ctx['sleep_avg'] < 7.0:
        recs.append({
            "category": "recovery",
            "action": "Prioritera 7-9 timmars sömn per natt",
            "reason": "Sömn är den viktigaste återhämtningsfaktorn",
            "priority": priority
        })
        priority += 1

    if ctx['readiness'] < 55:
        recs.append({
            "category": "training_intensity",
            "action": "Välj lättare träning idag — RPE max 6-7",
            "reason": f"Readiness {ctx['readiness']:.0f}/100 indikerar nedsatt kapacitet",
            "priority": priority
        })
        priority += 1

    if ctx['consistency_30d'] < 50:
        recs.append({
            "category": "consistency",
            "action": "Sikta på minst 3 träningspass per vecka",
            "reason": f"Träningskonsistens {ctx['consistency_30d']:.0f}% är under optimalt",
            "priority": priority
        })
        priority += 1

    if ctx['stress_avg'] > 7:
        recs.append({
            "category": "recovery",
            "action": "Lägg till en aktiv restitutionsdag",
            "reason": "Hög stress påverkar återhämtningen negativt",
            "priority": priority
        })
        priority += 1

    if ctx['days_since_workout'] > 5:
        recs.append({
            "category": "activity",
            "action": "Börja med en lätt träningssession idag",
            "reason": f"{ctx['days_since_workout']} dagar utan träning — håll igång rörelsen",
            "priority": priority
        })
        priority += 1

    if ctx['acwr'] < 0.7 and ctx['days_since_workout'] < 3:
        recs.append({
            "category": "training_load",
            "action": "Öka träningsvolymen gradvis med 10-15% per vecka",
            "reason": "ACWR under optimal zon — du tränar för lite relativt din kapacitet",
            "priority": priority
        })
        priority += 1

    if not recs:
        recs.append({
            "category": "maintenance",
            "action": "Fortsätt med din nuvarande träningsplan",
            "reason": "Alla indikatorer ser bra ut",
            "priority": 1
        })

    return sorted(recs, key=lambda r: r['priority'])


def _generate_coach_message(ctx: dict) -> tuple[str, str]:
    """Returnerar (coach_message, next_action)."""
    readiness = ctx['readiness']
    acwr = ctx['acwr']
    days = ctx['days_since_workout']

    if acwr > 1.5:
        msg = (
            f"Du visar tydliga tecken på ackumulerad trötthet. "
            f"Din träningsbelastning har ökat kraftigt (ACWR {acwr:.2f}). "
            f"Det är inte svaghet att ta en deload — det är smart träning."
        )
        action = "Ta 5-7 dagars deload med max 50% av normal volym."

    elif days > 10:
        msg = (
            f"Det har gått {days} dagar sedan senaste träningspasset. "
            f"Kom ihåg varför du började — varje session räknas, "
            f"även en kort 30-minutersträning."
        )
        action = "Boka in ett enkelt pass idag — fokus på att komma igång."

    elif readiness >= 80:
        msg = (
            f"Fantastisk form! Readiness {readiness:.0f}/100 — "
            f"kroppen är redo att prestera. "
            f"Utnyttja detta tillfälle för en kvalitetssession."
        )
        action = f"Kör {ctx['recommended_intensity']} träning idag med full fokus."

    elif readiness >= 65:
        msg = (
            f"Du är i bra form (readiness {readiness:.0f}/100). "
            f"Träna normalt och lyssna på kroppen under passet."
        )
        action = f"Träna {ctx['recommended_intensity']} — följ din plan."

    elif readiness >= 50:
        msg = (
            f"Readiness {readiness:.0f}/100 — lite under optimal. "
            f"Välj lättare övningar och undvik max-ansträngning idag."
        )
        action = "Lätt träning eller aktiv återhämtning (promenad, stretching)."

    else:
        msg = (
            f"Låg readiness {readiness:.0f}/100. "
            f"Din kropp behöver vila mer än träning just nu. "
            f"Sömn och återhämtning är din investering i morgondagens träning."
        )
        action = "Vila idag. Prioritera sömn och näring."

    return msg, action


def generate_ai_coach_response(user_id: int) -> dict | None:
    with engine.connect() as conn:
        ctx = _get_user_context(user_id, conn)

    warnings = _generate_warnings(ctx)
    recommendations = _generate_recommendations(ctx)
    coach_msg, next_action = _generate_coach_message(ctx)

    return {
        "user_id": user_id,
        "user_name": ctx['name'],
        "date": date.today(),
        "readiness_score": ctx['readiness'],
        "recommended_intensity": ctx['recommended_intensity'],
        "risk_scores": {
            "injury_risk": ctx['injury_risk'],
            "dropout_risk": ctx['dropout_risk'],
            "plateau_risk": ctx['plateau_risk'],
            "overtraining_risk": ctx['overtraining_risk'],
        },
        "warnings": warnings,
        "recommendations": recommendations,
        "coach_message": coach_msg,
        "next_action": next_action,
    }
