"""
ai_coach_engine.py — AI Coach Engine v2
"""
import json
from datetime import date
from sqlalchemy import text
from core.db import get_engine

engine = get_engine()


def _get_full_context(user_id: int, conn) -> dict:
    fs = conn.execute(text("""
        SELECT readiness_score, recovery_score, fatigue_score,
               acwr, training_zone, deload_recommended
        FROM fatigue_scores WHERE user_id = :uid ORDER BY date DESC LIMIT 1
    """), {"uid": user_id}).fetchone()

    injuries = conn.execute(text("""
        SELECT i.body_part, i.severity, i.status,
               ARRAY_AGG(e.name) as restricted_exercises
        FROM injuries i
        LEFT JOIN injury_exercise_restrictions ier ON i.id = ier.injury_id
        LEFT JOIN exercises e ON ier.exercise_id = e.id
        WHERE i.user_id = :uid AND i.status IN ('active','recovering')
        GROUP BY i.id, i.body_part, i.severity, i.status
    """), {"uid": user_id}).fetchall()

    user = conn.execute(text("""
        SELECT fitness_goal, fitness_level, experience_level, weight_kg, age
        FROM users WHERE id = :uid
    """), {"uid": user_id}).fetchone()

    recovery = conn.execute(text("""
        SELECT sleep_hours, sleep_quality, energy_level, stress_level
        FROM recovery_logs WHERE user_id = :uid ORDER BY date DESC LIMIT 1
    """), {"uid": user_id}).fetchone()

    features = conn.execute(text("""
        SELECT sessions_7d, volume_7d, days_since_last_workout,
               workout_consistency_30d, hrv_7d_avg
        FROM user_daily_features WHERE user_id = :uid ORDER BY date DESC LIMIT 1
    """), {"uid": user_id}).fetchone()

    equipment = conn.execute(text("""
        SELECT DISTINCT e.name, e.category
        FROM equipment e
        JOIN gym_equipment ge ON e.id = ge.equipment_id
        JOIN user_gym_memberships ugm ON ge.gym_id = ugm.gym_id
        WHERE ugm.user_id = :uid AND ugm.is_active = TRUE
    """), {"uid": user_id}).fetchall()

    if not equipment:
        equipment = conn.execute(text(
            "SELECT name, category FROM equipment WHERE is_active = TRUE"
        )).fetchall()

    return {
        "user_id": user_id,
        "readiness": float(fs[0]) if fs and fs[0] else 50.0,
        "recovery": float(fs[1]) if fs and fs[1] else 50.0,
        "fatigue": float(fs[2]) if fs and fs[2] else 50.0,
        "acwr": float(fs[3]) if fs and fs[3] else 1.0,
        "training_zone": fs[4] if fs else "optimal",
        "deload_recommended": bool(fs[5]) if fs else False,
        "injuries": [{"body_part": i[0], "severity": i[1], "status": i[2],
                      "restricted": i[3] or []} for i in injuries],
        "fitness_goal": user[0] if user else "hålla_sig_i_form",
        "fitness_level": user[1] if user else "medel",
        "experience_level": user[2] if user else "medel",
        "sleep_hours": float(recovery[0]) if recovery and recovery[0] else 7.0,
        "energy_level": float(recovery[2]) if recovery and recovery[2] else 7.0,
        "stress_level": float(recovery[3]) if recovery and recovery[3] else 5.0,
        "sessions_7d": int(features[0]) if features and features[0] else 0,
        "days_since_workout": int(features[2]) if features and features[2] else 0,
        "consistency_30d": float(features[3]) if features and features[3] else 50.0,
        "available_equipment": [e[0] for e in equipment],
    }


def _calculate_volume_multiplier(ctx: dict) -> float:
    base = 1.0
    acwr = ctx['acwr']
    r    = ctx['readiness']
    if acwr > 1.5:   base *= 0.5
    elif acwr > 1.3: base *= 0.7
    elif acwr < 0.7: base *= 1.15
    if r < 40:       base *= 0.6
    elif r < 55:     base *= 0.8
    elif r >= 80:    base *= 1.1
    if ctx['sleep_hours'] < 6:  base *= 0.85
    if ctx['stress_level'] > 7: base *= 0.9
    if any(i['severity'] >= 4 for i in ctx['injuries']): base *= 0.7
    return round(min(1.3, max(0.4, base)), 2)


def _get_recommended_intensity(ctx: dict) -> tuple[str, str]:
    r    = ctx['readiness']
    acwr = ctx['acwr']
    if ctx['deload_recommended'] or acwr > 1.5: return "very_light", "RPE 5-6"
    elif r >= 80 and acwr <= 1.2:               return "hard",       "RPE 8-9"
    elif r >= 70:                               return "moderate",   "RPE 7-8"
    elif r >= 55:                               return "light",      "RPE 6-7"
    elif r >= 40:                               return "very_light", "RPE 5-6"
    else:                                       return "rest",       "Vila idag"


def _get_focus_area(ctx: dict) -> str:
    goal     = ctx['fitness_goal']
    r        = ctx['readiness']
    injuries = [i['body_part'].lower() for i in ctx['injuries']]
    if r < 50 or ctx['deload_recommended']: return "mobility_recovery"
    focus = {
        'bygga_muskler': 'hypertrophy', 'gå_ner_i_vikt': 'metabolic',
        'gå_upp_i_vikt': 'strength_hypertrophy', 'öka_kondition': 'cardio_endurance',
        'hålla_sig_i_form': 'general_fitness', 'löpning': 'cardio_running'
    }.get(goal, 'general_fitness')
    if ('knä' in injuries or 'ben' in injuries) and focus in ['hypertrophy','strength_hypertrophy']:
        focus = 'upper_body_focus'
    if ('axel' in injuries or 'axlar' in injuries) and focus in ['hypertrophy','strength_hypertrophy']:
        focus = 'lower_body_focus'
    return focus


def _generate_workout(ctx: dict, focus: str, intensity: str,
                      vol_multiplier: float, conn) -> list:
    from core.domain.exercise_scorer import get_scored_exercises
    focus_muscles = {
        'hypertrophy': ['Bröst','Rygg','Ben','Axlar','Armar'],
        'strength_hypertrophy': ['Bröst','Rygg','Ben'],
        'metabolic': ['Ben','Bröst','Rygg'],
        'upper_body_focus': ['Bröst','Rygg','Axlar','Armar'],
        'lower_body_focus': ['Ben'],
        'general_fitness': ['Bröst','Rygg','Ben','Axlar'],
        'cardio_endurance': ['Kondition'],
        'cardio_running': ['Kondition','Ben'],
        'mobility_recovery': ['Ben','Rygg'],
    }
    target   = focus_muscles.get(focus, ['Bröst','Rygg','Ben'])
    base_sets= {'very_light':2,'light':3,'moderate':3,'hard':4,'rest':1}.get(intensity, 3)
    sets     = max(1, round(base_sets * vol_multiplier))
    reps     = {'hypertrophy':'8-12','strength_hypertrophy':'5-8','metabolic':'12-15',
                'upper_body_focus':'10-12','lower_body_focus':'10-12',
                'general_fitness':'10-12','cardio_endurance':'15-20',
                'cardio_running':'15-20','mobility_recovery':'12-15'}.get(focus, '10-12')

    scored = get_scored_exercises(
        muscle_groups=target,
        ctx={**ctx, 'focus_area': focus},
        conn=conn, limit_per_muscle=2
    )
    return [{
        "exercise_id": ex['id'], "exercise_name": ex['name'],
        "sets": sets, "reps": reps,
        "equipment": ex['equipment_name'] or 'Kroppsvikt',
        "rest_seconds": 90 if intensity in ['moderate','hard'] else 60,
        "score": ex['score'], "body_part": ex['body_part'],
        "is_compound": ex.get('is_compound', False),
    } for ex in scored[:6]]


def _generate_coach_message_v2(ctx: dict, focus: str,
                                intensity: str, subs: dict) -> tuple[str, str]:
    r    = ctx['readiness']
    acwr = ctx['acwr']
    days = ctx['days_since_workout']
    inj  = ctx['injuries']

    if acwr > 1.5:
        msg    = f"Din kropp signalerar överbelastning (ACWR {acwr:.2f}). En deload nu ger bättre resultat nästa vecka."
        action = "Deload — max 50% av normal volym, RPE 5-6."
    elif inj and any(i['severity'] >= 3 for i in inj):
        parts  = [i['body_part'] for i in inj if i['severity'] >= 3]
        msg    = f"Aktiva skador ({', '.join(parts)}). Träningen är anpassad för att skydda dessa områden."
        action = "Kör anpassat pass. Stoppa om smärta uppstår."
    elif days > 7:
        msg    = f"Det har gått {days} dagar sedan senaste passet. Välkommen tillbaka!"
        action = "Lätt pass idag. Fokus på teknik, inte belastning."
    elif r >= 80:
        msg    = f"Exceptionell form! Readiness {r:.0f}/100 och ACWR {acwr:.2f}. Kroppen är redo."
        action = f"Kör {intensity} pass med fullt fokus. Tryck på progressionen."
    elif r >= 65:
        msg    = f"Bra status (readiness {r:.0f}/100). Träna normalt och lyssna på kroppen."
        action = f"Följ planen — {intensity} intensitet."
    else:
        msg    = f"Readiness {r:.0f}/100 — lite under optimal. Välj lättare övningar."
        action = "Lätt session. Prioritera rörlighet och teknik."

    return msg, action


def generate_ai_coach_v2(user_id: int) -> dict | None:
    with engine.connect() as conn:
        ctx          = _get_full_context(user_id, conn)
        vol          = _calculate_volume_multiplier(ctx)
        intensity, rpe = _get_recommended_intensity(ctx)
        focus        = _get_focus_area(ctx)
        workout      = _generate_workout(ctx, focus, intensity, vol, conn)

        user_name = conn.execute(text(
            "SELECT name FROM users WHERE id = :uid"
        ), {"uid": user_id}).fetchone()[0]

        try:
            conn.execute(text("""
                INSERT INTO ai_coach_sessions
                    (user_id, session_date, readiness_at_time, acwr_at_time,
                     training_zone, recommended_volume_multiplier,
                     recommended_intensity, focus_area, deload_recommended,
                     workout_generated, coach_message)
                VALUES (:uid,:date,:r,:acwr,:zone,:vol,:intensity,:focus,:deload,:workout,:msg)
                ON CONFLICT DO NOTHING
            """), {
                "uid": user_id, "date": date.today(),
                "r": ctx['readiness'], "acwr": ctx['acwr'],
                "zone": ctx['training_zone'], "vol": vol,
                "intensity": intensity, "focus": focus,
                "deload": ctx['deload_recommended'],
                "workout": json.dumps(workout),
                "msg": _generate_coach_message_v2(ctx, focus, intensity, {})[0]
            })
            conn.commit()
        except Exception:
            pass

        coach_msg, next_action = _generate_coach_message_v2(ctx, focus, intensity, {})

        return {
            "user_id": user_id, "user_name": user_name,
            "date": date.today(), "readiness_score": ctx['readiness'],
            "acwr": ctx['acwr'], "training_zone": ctx['training_zone'],
            "focus_area": focus, "recommended_intensity": intensity,
            "rpe_target": rpe, "volume_multiplier": vol,
            "injuries_active": len(ctx['injuries']),
            "recommended_workout": workout,
            "coach_message": coach_msg, "next_action": next_action,
            "context": {
                "sleep_hours": ctx['sleep_hours'],
                "energy_level": ctx['energy_level'],
                "stress_level": ctx['stress_level'],
                "days_since_workout": ctx['days_since_workout'],
            }
        }
