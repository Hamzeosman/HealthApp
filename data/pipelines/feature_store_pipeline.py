"""
feature_store_pipeline.py
Bygger dagliga ML-features + predictions för alla users.
Refreshar alla 4 materialized views efter körning.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from datetime import date, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
engine = create_engine(os.getenv("DATABASE_URL"))


def build_features_for_user(user_id: int, conn) -> dict | None:
    today = date.today()
    d7  = today - timedelta(days=7)
    d28 = today - timedelta(days=28)
    d30 = today - timedelta(days=30)

    workouts = pd.read_sql(text("""
        SELECT ws.date,
            SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS volume,
            AVG(we.rpe) AS avg_rpe,
            COUNT(DISTINCT ws.id) AS sessions
        FROM workout_sessions ws
        JOIN workout_exercises we ON ws.id = we.session_id
        WHERE ws.user_id = :uid AND ws.date >= :d28
        GROUP BY ws.date ORDER BY ws.date
    """), conn, params={"uid": user_id, "d28": d28})

    if workouts.empty:
        return None

    recent_7d   = workouts[workouts['date'] >= d7]
    volume_7d   = float(recent_7d['volume'].sum()) if not recent_7d.empty else 0.0
    volume_28d  = float(workouts['volume'].mean()) if not workouts.empty else 0.0
    sessions_7d = int(recent_7d['sessions'].sum()) if not recent_7d.empty else 0
    avg_rpe_7d  = float(recent_7d['avg_rpe'].mean()) if not recent_7d.empty else 0.0

    acute   = volume_7d / 7 if volume_7d > 0 else 0
    chronic = volume_28d
    acwr    = round(acute / chronic, 3) if chronic > 0 else 1.0
    zone    = ('undertraining' if acwr < 0.8
               else 'optimal' if acwr <= 1.3
               else 'caution' if acwr <= 1.5
               else 'danger')

    recovery = pd.read_sql(text("""
        SELECT sleep_hours, sleep_quality, energy_level, stress_level
        FROM recovery_logs
        WHERE user_id = :uid AND date >= :d7
        ORDER BY date DESC
    """), conn, params={"uid": user_id, "d7": d7})

    sleep_avg  = float(recovery['sleep_hours'].mean())  if not recovery.empty else 7.0
    sleep_q    = float(recovery['sleep_quality'].mean()) if not recovery.empty else 7.0
    energy_avg = float(recovery['energy_level'].mean()) if not recovery.empty else 7.0
    stress_avg = float(recovery['stress_level'].mean()) if not recovery.empty else 5.0

    recovery_score = round(
        sleep_avg / 10 * 35 +
        energy_avg / 10 * 30 +
        (10 - stress_avg) / 10 * 20 +
        sleep_q / 10 * 15, 2)

    acwr_norm     = max(0.0, min(100.0, (1 - abs(acwr - 1.0)) * 100))
    fatigue_norm  = min(100.0, (volume_7d / max(volume_28d * 7, 1)) * 50)
    fatigue_score = round(max(0.0, 100.0 - fatigue_norm), 2)
    readiness     = round(0.4 * recovery_score + 0.3 * acwr_norm + 0.3 * fatigue_score, 2)

    wearable = pd.read_sql(text("""
        SELECT hrv_ms, heart_rate_resting FROM wearable_metrics
        WHERE user_id = :uid AND date >= :d7
    """), conn, params={"uid": user_id, "d7": d7})

    hrv_avg = float(wearable['hrv_ms'].mean())             if not wearable.empty else None
    hr_avg  = float(wearable['heart_rate_resting'].mean()) if not wearable.empty else None

    streak_row = conn.execute(text(
        "SELECT current_streak FROM user_streaks WHERE user_id = :uid"
    ), {"uid": user_id}).fetchone()
    current_streak = int(streak_row[0]) if streak_row else 0

    last_ws = conn.execute(text(
        "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
    ), {"uid": user_id}).fetchone()
    days_since = (today - last_ws[0]).days if last_ws and last_ws[0] else 999

    sess_30d = conn.execute(text("""
        SELECT COUNT(DISTINCT date) FROM workout_sessions
        WHERE user_id = :uid AND date >= :d30
    """), {"uid": user_id, "d30": d30}).fetchone()
    consistency = round((int(sess_30d[0]) / 30) * 100, 1) if sess_30d else 0.0

    body = pd.read_sql(text("""
        SELECT measured_at, weight_kg, body_fat_percentage
        FROM user_measurements WHERE user_id = :uid
        ORDER BY measured_at DESC LIMIT 8
    """), conn, params={"uid": user_id})

    weight_trend = None
    fat_trend    = None
    if len(body) >= 2:
        weight_trend = float(body['weight_kg'].iloc[0] - body['weight_kg'].iloc[-1])
        if body['body_fat_percentage'].notna().any():
            fat_trend = float(body['body_fat_percentage'].iloc[0] - body['body_fat_percentage'].iloc[-1])

    nutrition = pd.read_sql(text("""
        SELECT date, SUM(calories) AS cal, SUM(protein_g) AS prot
        FROM food_logs WHERE user_id = :uid AND date >= :d7
        GROUP BY date
    """), conn, params={"uid": user_id, "d7": d7})

    cal_avg  = float(nutrition['cal'].mean())  if not nutrition.empty else None
    prot_avg = float(nutrition['prot'].mean()) if not nutrition.empty else None

    target = conn.execute(text("""
        SELECT calories_target, protein_g FROM nutrition_targets
        WHERE user_id = :uid AND is_active = TRUE
        ORDER BY created_at DESC LIMIT 1
    """), {"uid": user_id}).fetchone()

    cal_adh  = round((cal_avg  / float(target[0])) * 100, 1) if cal_avg  and target else None
    prot_adh = round((prot_avg / float(target[1])) * 100, 1) if prot_avg and target else None

    return {
        "user_id": int(user_id), "date": today,
        "sleep_hours_7d_avg": float(round(sleep_avg, 2)),
        "sleep_quality_7d_avg": float(round(sleep_q, 2)),
        "sleep_consistency_score": float(round(sleep_avg / 9 * 100, 1)),
        "volume_7d": float(round(volume_7d, 2)),
        "volume_28d_avg": float(round(volume_28d * 7, 2)),
        "sessions_7d": sessions_7d,
        "avg_rpe_7d": float(round(avg_rpe_7d, 2)),
        "acwr": float(acwr),
        "training_zone": zone,
        "recovery_score": float(round(recovery_score, 2)),
        "readiness_score": float(round(readiness, 2)),
        "stress_7d_avg": float(round(stress_avg, 2)),
        "energy_7d_avg": float(round(energy_avg, 2)),
        "hrv_7d_avg": float(round(hrv_avg, 2)) if hrv_avg else None,
        "resting_hr_7d_avg": float(round(hr_avg, 2)) if hr_avg else None,
        "weight_trend": float(round(weight_trend, 2)) if weight_trend is not None else None,
        "body_fat_trend": float(round(fat_trend, 2)) if fat_trend is not None else None,
        "calories_7d_avg": float(round(cal_avg, 2)) if cal_avg else None,
        "protein_7d_avg": float(round(prot_avg, 2)) if prot_avg else None,
        "calorie_target_adherence": float(cal_adh) if cal_adh else None,
        "protein_target_adherence": float(prot_adh) if prot_adh else None,
        "days_since_last_workout": int(days_since),
        "streak_current": int(current_streak),
        "workout_consistency_30d": float(consistency),
        "_readiness": float(round(readiness, 2)),
        "_acwr": float(acwr),
        "_days_since": int(days_since),
        "_consistency": float(consistency),
    }


def compute_predictions(r: float, acwr: float, days: int, cons: float) -> dict:
    injury_risk      = round(min(100, max(0, (acwr - 1.0) * 60 + (100 - r) * 0.3)), 1)
    dropout_risk     = round(min(100, max(0, (100 - cons) * 0.5 + min(days, 20) * 3)), 1)
    plateau_risk     = round(min(100, max(0, 50 - cons * 0.3)), 1)
    overtraining_risk= round(min(100, max(0, (acwr - 1.3) * 80 if acwr > 1.3 else 0)), 1)
    intensity        = ('hard' if r >= 80 else 'moderate' if r >= 65
                        else 'light' if r >= 50 else 'very_light' if r >= 35 else 'rest')
    if acwr > 1.5:
        rec = "ACWR kritisk hög — ta en deload-vecka omedelbart."
    elif days > 7:
        rec = f"Ingen träning på {days} dagar — börja lätt idag."
    elif r < 50:
        rec = "Låg readiness — välj aktiv vila eller lätt mobilitet."
    elif overtraining_risk > 60:
        rec = "Hög överträningsrisk — minska volym med 20-30%."
    else:
        rec = f"Bra status — träna {intensity} idag."
    vol_mult = (0.7 if acwr > 1.3 else 1.2 if acwr < 0.7 else 0.8 if r < 50 else 1.0)
    return {
        "injury_risk_score": injury_risk,
        "dropout_risk_score": dropout_risk,
        "plateau_risk_score": plateau_risk,
        "overtraining_risk_score": overtraining_risk,
        "recommended_intensity": intensity,
        "recommended_volume_multiplier": float(round(vol_mult, 2)),
        "primary_recommendation": rec,
        "confidence_score": float(round(min(100, cons * 0.5 + r * 0.5), 1)),
    }


def run():
    print("=" * 60)
    print("FEATURE STORE PIPELINE — startar")
    print("=" * 60)

    with engine.connect() as conn:
        users = pd.read_sql(text(
            "SELECT id, name FROM users WHERE role='user' OR role IS NULL ORDER BY id"
        ), conn)

        if users.empty:
            print("Inga users.")
            return

        success = skipped = errors = 0

        for _, user in users.iterrows():
            uid  = int(user['id'])
            name = user['name']
            try:
                conn.execute(text("SAVEPOINT sp_fs"))
                features = build_features_for_user(uid, conn)

                if features is None:
                    print(f"  ⏭️  {name} — ingen data")
                    conn.execute(text("RELEASE SAVEPOINT sp_fs"))
                    skipped += 1
                    continue

                internal = {k: features.pop(k)
                            for k in ['_readiness','_acwr','_days_since','_consistency']}

                conn.execute(text("""
                    INSERT INTO user_daily_features (
                        user_id, date, sleep_hours_7d_avg, sleep_quality_7d_avg,
                        sleep_consistency_score, volume_7d, volume_28d_avg,
                        sessions_7d, avg_rpe_7d, acwr, training_zone,
                        recovery_score, readiness_score, stress_7d_avg,
                        energy_7d_avg, hrv_7d_avg, resting_hr_7d_avg,
                        weight_trend, body_fat_trend, calories_7d_avg,
                        protein_7d_avg, calorie_target_adherence,
                        protein_target_adherence, days_since_last_workout,
                        streak_current, workout_consistency_30d
                    ) VALUES (
                        :user_id, :date, :sleep_hours_7d_avg, :sleep_quality_7d_avg,
                        :sleep_consistency_score, :volume_7d, :volume_28d_avg,
                        :sessions_7d, :avg_rpe_7d, :acwr, :training_zone,
                        :recovery_score, :readiness_score, :stress_7d_avg,
                        :energy_7d_avg, :hrv_7d_avg, :resting_hr_7d_avg,
                        :weight_trend, :body_fat_trend, :calories_7d_avg,
                        :protein_7d_avg, :calorie_target_adherence,
                        :protein_target_adherence, :days_since_last_workout,
                        :streak_current, :workout_consistency_30d
                    )
                    ON CONFLICT (user_id, date) DO UPDATE SET
                        volume_7d = EXCLUDED.volume_7d,
                        acwr = EXCLUDED.acwr,
                        training_zone = EXCLUDED.training_zone,
                        recovery_score = EXCLUDED.recovery_score,
                        readiness_score = EXCLUDED.readiness_score,
                        days_since_last_workout = EXCLUDED.days_since_last_workout,
                        streak_current = EXCLUDED.streak_current,
                        workout_consistency_30d = EXCLUDED.workout_consistency_30d,
                        calculated_at = NOW()
                """), features)

                preds = compute_predictions(
                    internal['_readiness'], internal['_acwr'],
                    internal['_days_since'], internal['_consistency'])

                conn.execute(text("""
                    INSERT INTO model_predictions (
                        user_id, date, injury_risk_score, dropout_risk_score,
                        plateau_risk_score, overtraining_risk_score,
                        recommended_intensity, recommended_volume_multiplier,
                        primary_recommendation, confidence_score
                    ) VALUES (
                        :user_id, :date, :injury_risk_score, :dropout_risk_score,
                        :plateau_risk_score, :overtraining_risk_score,
                        :recommended_intensity, :recommended_volume_multiplier,
                        :primary_recommendation, :confidence_score
                    )
                    ON CONFLICT (user_id, date, model_version) DO UPDATE SET
                        injury_risk_score = EXCLUDED.injury_risk_score,
                        dropout_risk_score = EXCLUDED.dropout_risk_score,
                        recommended_intensity = EXCLUDED.recommended_intensity,
                        primary_recommendation = EXCLUDED.primary_recommendation,
                        confidence_score = EXCLUDED.confidence_score
                """), {"user_id": uid, "date": features['date'], **preds})

                conn.execute(text("RELEASE SAVEPOINT sp_fs"))

                emoji = "🟢" if preds['injury_risk_score'] < 30 else "🟡" if preds['injury_risk_score'] < 60 else "🔴"
                print(f"  {emoji} {name} — "
                      f"Readiness: {internal['_readiness']:.1f} | "
                      f"Injury: {preds['injury_risk_score']:.0f} | "
                      f"Rec: {preds['recommended_intensity']}")
                success += 1

            except Exception as e:
                conn.execute(text("ROLLBACK TO SAVEPOINT sp_fs"))
                conn.execute(text("RELEASE SAVEPOINT sp_fs"))
                print(f"  ❌ {name} — {e}")
                errors += 1

        conn.commit()

        print("\n🔄 Refreshar materialized views...")
        for view in ['mv_user_weekly_volume','mv_readiness_trends',
                     'mv_pr_progression','mv_fatigue_dashboard']:
            try:
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
                print(f"  ✅ {view}")
            except Exception as e:
                print(f"  ⚠️  {view}: {e}")
        conn.commit()

    print("=" * 60)
    print(f"✅ Success: {success} | ⏭️ Skipped: {skipped} | ❌ Errors: {errors}")
    print("=" * 60)


if __name__ == "__main__":
    run()
