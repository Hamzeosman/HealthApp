from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

VOLUME_GUIDELINES = {
    "Rygg":      {"min": 10, "optimal": 14, "max": 20},
    "Brost":     {"min": 10, "optimal": 12, "max": 20},
    "Ben":       {"min": 10, "optimal": 16, "max": 20},
    "Axlar":     {"min": 8,  "optimal": 12, "max": 20},
    "Armar":     {"min": 8,  "optimal": 12, "max": 18},
    "Mage":      {"min": 8,  "optimal": 10, "max": 16},
    "Kondition": {"min": 3,  "optimal": 5,  "max": 7},
}

def get_weekly_load(conn, user_id, week_offset=0):
    last = conn.execute(text(
        "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
    ), {"uid": user_id}).scalar()
    if last is None:
        return (0, 7, 0, 0)
    from datetime import date as date_type
    if isinstance(last, date_type):
        last = datetime.combine(last, datetime.min.time())
    end_date = last - timedelta(weeks=week_offset)
    start_date = end_date - timedelta(days=7)
    result = conn.execute(text("""
        SELECT
            COALESCE(SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)), 0) AS total_volume,
            COALESCE(AVG(we.rpe), 7) AS avg_rpe,
            COALESCE(SUM(we.sets), 0) AS total_sets,
            COUNT(DISTINCT ws.id) AS sessions
        FROM workout_exercises we
        JOIN workout_sessions ws ON we.session_id = ws.id
        WHERE ws.user_id = :uid
        AND ws.date >= :start_date
        AND ws.date < :end_date
    """), {"uid": user_id,
           "start_date": start_date.date(),
           "end_date": end_date.date()}).fetchone()
    return result

def calculate_acwr_ema(conn, user_id):
    """
    Beraknar ACWR med Exponential Moving Average (EMA) for chronic load.
    Mer stabilt an enkelt 4-veckors snitt.
    Kalla: Gabbett et al. sports science forskning.
    EMA viktar nyare veckor mer an aldre.
    """
    acute = get_weekly_load(conn, user_id, week_offset=0)
    acute_load = float(acute[0] or 0) * float(acute[1] or 7)

    # EMA med alpha=0.5 — nyare veckor viktas mer
    alpha = 0.5
    ema = None
    for week in range(4, 0, -1):
        week_data = get_weekly_load(conn, user_id, week_offset=week)
        load = float(week_data[0] or 0) * float(week_data[1] or 7)
        if ema is None:
            ema = load
        else:
            ema = alpha * load + (1 - alpha) * ema

    chronic_ema = ema if ema else 1.0
    acwr = acute_load / chronic_ema if chronic_ema > 0 else 1.0
    return round(acwr, 2), chronic_ema

def get_acwr_status(acwr):
    if acwr < 0.8:
        return "UNDERTRAINING", f"ACWR {acwr} — for lag traning, risk for detraining"
    elif acwr <= 1.3:
        return "OPTIMAL ZONE", f"ACWR {acwr} — optimal traning, liten skaderisk"
    elif acwr <= 1.5:
        return "CAUTION ZONE", f"ACWR {acwr} — hog akut belastning, var forsiktig"
    else:
        return "DANGER ZONE", f"ACWR {acwr} — mycket hog risk for skada eller overtraning"

def calculate_weekly_volume(conn, user_id):
    last = conn.execute(text(
        "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
    ), {"uid": user_id}).scalar()
    if last is None:
        return []
    from datetime import date as date_type
    if isinstance(last, date_type):
        last = datetime.combine(last, datetime.min.time())
    week_start = last - timedelta(days=7)
    result = conn.execute(text("""
        SELECT
            bp.name AS muscle_group,
            COUNT(we.id) AS total_exercises,
            SUM(we.sets) AS total_sets,
            SUM(we.sets * we.reps) AS total_reps,
            SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS total_volume_kg,
            AVG(we.rpe) AS avg_rpe
        FROM workout_exercises we
        JOIN workout_sessions ws ON we.session_id = ws.id
        JOIN exercises e ON we.exercise_id = e.id
        JOIN body_parts bp ON e.body_part_id = bp.id
        WHERE ws.user_id = :uid
        AND ws.date >= :week_start
        GROUP BY bp.name
        ORDER BY total_sets DESC
    """), {"uid": user_id, "week_start": week_start.date()})
    return result.fetchall()

def get_recovery_score(conn, user_id):
    last_workout = conn.execute(text(
        "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
    ), {"uid": user_id}).scalar()
    if last_workout is None:
        return None
    result = conn.execute(text("""
        SELECT
            AVG(sleep_hours)    AS avg_sleep,
            AVG(energy_level)   AS avg_energy,
            AVG(stress_level)   AS avg_stress,
            AVG(sleep_quality)  AS avg_sleep_quality
        FROM recovery_logs
        WHERE user_id = :uid
        AND date >= :since
    """), {
        "uid": user_id,
        "since": (last_workout - timedelta(days=3))
    }).fetchone()
    return result

def calculate_recovery_score(recovery):
    if not recovery or recovery[0] is None:
        return 50.0
    sleep = float(recovery[0] or 7)
    energy = float(recovery[1] or 7)
    stress = float(recovery[2] or 5)
    sleep_quality = float(recovery[3] or 7)
    sleep_score = min(100, (sleep / 9) * 100)
    energy_score = (energy / 10) * 100
    stress_score = ((10 - stress) / 10) * 100
    quality_score = (sleep_quality / 10) * 100
    total = (sleep_score * 0.35 + energy_score * 0.30 +
             stress_score * 0.20 + quality_score * 0.15)
    return round(total, 1)

def calculate_composite_readiness(recovery_score, acwr, fatigue_ratio):
    """
    Composite Readiness Score — kombinerar alla signaler.
    readiness = (0.4 * recovery) + (0.3 * acwr_norm) + (0.3 * fatigue_norm)
    Baserat pa Hamzes rekommendation och sports science principer.
    """
    # Normalisera ACWR: optimal ar 1.0, avvikelse sanker score
    acwr_norm = max(0, 1 - abs(acwr - 1.0)) * 100

    # Normalisera fatigue ratio: optimal ar 1.0
    fatigue_norm = max(0, min(100, (1 - max(0, fatigue_ratio - 1.0)) * 100))

    readiness = (0.4 * recovery_score +
                 0.3 * acwr_norm +
                 0.3 * fatigue_norm)
    return round(readiness, 1)

def get_readiness_status(score):
    if score >= 80:
        return "READY TO TRAIN HARD", "Alla signaler gröna. Perfekt för tung träning och PR."
    elif score >= 65:
        return "GOOD TO TRAIN", "Bra readiness. Träna normalt."
    elif score >= 50:
        return "TRAIN LIGHT", "Måttlig readiness. Välj lättare träning."
    else:
        return "REST OR DELOAD", "Låg readiness. Vila eller deload rekommenderas."

def analyze_muscle_balance(weekly_volume):
    """
    Analyserar push/pull ratio och upper/lower balans.
    Baserat pa evidensbaserade riktlinjer för muskelbalans.
    """
    push_muscles = {"Brost", "Axlar"}
    pull_muscles = {"Rygg", "Armar"}
    upper_muscles = {"Brost", "Rygg", "Axlar", "Armar"}
    lower_muscles = {"Ben", "Mage"}

    muscle_sets = {row[0]: int(row[2] or 0) for row in weekly_volume}

    push_vol = sum(muscle_sets.get(m, 0) for m in push_muscles)
    pull_vol = sum(muscle_sets.get(m, 0) for m in pull_muscles)
    upper_vol = sum(muscle_sets.get(m, 0) for m in upper_muscles)
    lower_vol = sum(muscle_sets.get(m, 0) for m in lower_muscles)

    flags = []

    # Push/Pull ratio — bör vara nära 1:1
    if push_vol > 0 and pull_vol > 0:
        pp_ratio = push_vol / pull_vol
        if pp_ratio > 1.5:
            flags.append(f"Push/Pull obalans: {push_vol} push vs {pull_vol} pull sets — mer dragövningar behövs")
        elif pp_ratio < 0.6:
            flags.append(f"Push/Pull obalans: {pull_vol} pull vs {push_vol} push sets — mer pressövningar behövs")
        else:
            flags.append(f"Push/Pull ratio: {pp_ratio:.1f} — bra balans")

    # Upper/Lower ratio — bör vara nära 1:1
    if upper_vol > 0 and lower_vol > 0:
        ul_ratio = upper_vol / lower_vol
        if ul_ratio > 2.0:
            flags.append(f"Upper/Lower obalans: {upper_vol} övre vs {lower_vol} nedre sets — mer benträning behövs")
        elif ul_ratio < 0.5:
            flags.append(f"Upper/Lower obalans: {lower_vol} nedre vs {upper_vol} övre sets — mer överkroppsträning behövs")
        else:
            flags.append(f"Upper/Lower ratio: {ul_ratio:.1f} — bra balans")

    return flags

def detect_progression(conn, user_id):
    """
    Detekterar progression genom att jämföra:
    - volym denna vecka vs förra veckan
    - styrka (max vikt) trend
    - RPE vid samma vikt (sjunkande RPE = starkare)
    """
    current = get_weekly_load(conn, user_id, week_offset=0)
    previous = get_weekly_load(conn, user_id, week_offset=1)

    current_vol = float(current[0] or 0)
    previous_vol = float(previous[0] or 0)
    current_rpe = float(current[1] or 7)
    previous_rpe = float(previous[1] or 7)

    insights = []

    if previous_vol > 0:
        vol_change = ((current_vol - previous_vol) / previous_vol) * 100
        if vol_change > 10:
            insights.append(f"Volym okade med {vol_change:.1f}% vs forriga veckan — bra progression!")
        elif vol_change < -10:
            insights.append(f"Volym minskade med {abs(vol_change):.1f}% vs forriga veckan")
        else:
            insights.append(f"Volym stabil ({vol_change:+.1f}%) vs forriga veckan")

    if previous_rpe > 0 and current_rpe > 0:
        rpe_change = current_rpe - previous_rpe
        if rpe_change < -0.3:
            insights.append(f"RPE sjunker ({rpe_change:+.1f}) — du blir starkare!")
        elif rpe_change > 0.3:
            insights.append(f"RPE stiger ({rpe_change:+.1f}) — kan tyda pa trotthet")

    return insights

def calculate_fatigue_score(total_volume_kg, avg_rpe, chronic_baseline):
    if not total_volume_kg or not avg_rpe:
        return 0, 1.0, "NO DATA"
    fatigue = float(total_volume_kg) * float(avg_rpe)
    fatigue_ratio = fatigue / chronic_baseline if chronic_baseline > 0 else 1.0
    if fatigue_ratio < 0.8:
        msg = "LOW — Under normal niva"
    elif fatigue_ratio < 1.2:
        msg = "NORMAL — Inom normal niva"
    elif fatigue_ratio < 1.5:
        msg = "HIGH — 20-50% over normal"
    else:
        msg = "VERY HIGH — Over 50% over normal, overvaeg deload"
    return round(fatigue), round(fatigue_ratio, 2), msg

def analyze_volume(muscle_group, total_sets):
    guidelines = VOLUME_GUIDELINES.get(muscle_group, {"min": 8, "optimal": 12, "max": 18})
    if total_sets < guidelines["min"]:
        return "LOW", f"{total_sets} sets — minimum {guidelines['min']} sets/vecka"
    elif total_sets <= guidelines["optimal"]:
        return "OPTIMAL", f"{total_sets} sets — optimal zon ({guidelines['min']}-{guidelines['optimal']} sets/vecka)"
    elif total_sets <= guidelines["max"]:
        return "HIGH", f"{total_sets} sets — hog volym, sakerstall aterhamtning"
    else:
        return "TOO HIGH", f"{total_sets} sets — overstiger max ({guidelines['max']} sets/vecka)"

def save_training_metrics(conn, uid, recovery_score, fatigue_score,
                          weekly_volume, weekly_sets, acwr, readiness):
    ref_date = conn.execute(text(
        "SELECT MAX(date) FROM workout_sessions WHERE user_id = :uid"
    ), {"uid": uid}).scalar()
    if ref_date is None:
        return
    existing = conn.execute(text("""
        SELECT id FROM training_metrics WHERE user_id = :uid AND date = :date
    """), {"uid": uid, "date": ref_date}).fetchone()
    if existing:
        conn.execute(text("""
            UPDATE training_metrics
            SET recovery_score = :recovery,
                fatigue_score  = :fatigue,
                weekly_volume_kg = :volume,
                weekly_sets    = :sets,
                acwr           = :acwr,
                readiness_status = :readiness
            WHERE user_id = :uid AND date = :date
        """), {
            "uid": uid, "date": ref_date,
            "recovery": recovery_score, "fatigue": fatigue_score,
            "volume": weekly_volume, "sets": weekly_sets,
            "acwr": acwr, "readiness": readiness
        })
    else:
        conn.execute(text("""
            INSERT INTO training_metrics
                (user_id, date, recovery_score, fatigue_score,
                 weekly_volume_kg, weekly_sets, acwr, readiness_status)
            VALUES (:uid, :date, :recovery, :fatigue, :volume, :sets, :acwr, :readiness)
        """), {
            "uid": uid, "date": ref_date,
            "recovery": recovery_score, "fatigue": fatigue_score,
            "volume": weekly_volume, "sets": weekly_sets,
            "acwr": acwr, "readiness": readiness
        })

def run_volume_and_recovery_analysis(user_id=None):
    with engine.connect() as conn:
        if user_id:
            users = [(user_id,)]
        else:
            users = conn.execute(text("SELECT id FROM users")).fetchall()

        for (uid,) in users:
            user = conn.execute(text(
                "SELECT name, fitness_level FROM users WHERE id = :uid"
            ), {"uid": uid}).fetchone()
            if not user:
                continue

            log.info(f"\n{'='*55}")
            log.info(f"Analyserar: {user[0]} ({user[1]}) (ID: {uid})")
            log.info(f"{'='*55}")

            # Recovery
            recovery = get_recovery_score(conn, uid)
            recovery_score = calculate_recovery_score(recovery)
            log.info(f"\nRECOVERY SCORE: {recovery_score}/100")
            if recovery and recovery[0]:
                log.info(f"  Somn: {float(recovery[0]):.1f}h | "
                        f"Energi: {float(recovery[1]):.1f}/10 | "
                        f"Stress: {float(recovery[2]):.1f}/10")

            # ACWR med EMA
            acwr, chronic_ema = calculate_acwr_ema(conn, uid)
            acwr_status, acwr_msg = get_acwr_status(acwr)
            log.info(f"\nACWR (EMA): {acwr} — {acwr_status}")
            log.info(f"  {acwr_msg}")

            # Volymanalys
            weekly_volume = calculate_weekly_volume(conn, uid)
            total_vol_kg = 0
            total_sets = 0
            avg_rpe_all = 7.0
            fatigue_ratio = 1.0

            if weekly_volume:
                log.info(f"\nVOLYM DENNA VECKA:")
                for row in weekly_volume:
                    muscle, exercises, sets, reps, volume, rpe = row
                    sets_int = int(sets) if sets else 0
                    total_sets += sets_int
                    total_vol_kg += float(volume or 0)
                    status_vol, msg = analyze_volume(muscle, sets_int)
                    label = {"LOW": "[LOW]", "OPTIMAL": "[OK]",
                             "HIGH": "[HIGH]", "TOO HIGH": "[MAX]"}.get(status_vol, "[?]")
                    log.info(f"  {label} {muscle}: {msg}")

                rpe_values = [float(r[5]) for r in weekly_volume if r[5]]
                if rpe_values:
                    avg_rpe_all = sum(rpe_values) / len(rpe_values)

                # Fatigue med relativ threshold
                fatigue, fatigue_ratio, fatigue_msg = calculate_fatigue_score(
                    total_vol_kg, avg_rpe_all, chronic_ema
                )
                log.info(f"\nFATIGUE SCORE: {fatigue:,} (ratio: {fatigue_ratio}x) — {fatigue_msg}")

                # Composite Readiness Score
                readiness_score = calculate_composite_readiness(
                    recovery_score, acwr, fatigue_ratio
                )
                readiness_status, readiness_msg = get_readiness_status(readiness_score)
                log.info(f"\nCOMPOSITE READINESS: {readiness_score}/100 — {readiness_status}")
                log.info(f"  {readiness_msg}")

                # Muskelbalans
                balance_flags = analyze_muscle_balance(weekly_volume)
                if balance_flags:
                    log.info(f"\nMUSKELBALANS:")
                    for flag in balance_flags:
                        log.info(f"  {flag}")

                # Progressionsdetektering
                progression = detect_progression(conn, uid)
                if progression:
                    log.info(f"\nPROGRESSION:")
                    for insight in progression:
                        log.info(f"  {insight}")

                # Deload rekommendation
                if readiness_score < 40 or (acwr > 1.5 and recovery_score < 50):
                    log.info(f"\nDELOAD REKOMMENDERAS!")
                    log.info(f"  Readiness {readiness_score}/100 + ACWR {acwr} — Minska volymen med 40%")

            else:
                log.info("\nIngen traning registrerad denna vecka.")
                readiness_score = recovery_score
                readiness_status = "NO TRAINING DATA"
                fatigue = 0

            # Spara metrics
            save_training_metrics(
                conn, uid, recovery_score, fatigue if weekly_volume else 0,
                total_vol_kg, total_sets, acwr, readiness_status
            )

            # Spara AI insight
            insight_title = f"Training Intelligence — {datetime.now().strftime('%Y-%m-%d')}"
            volume_summary = ""
            if weekly_volume:
                low_muscles = [row[0] for row in weekly_volume
                              if analyze_volume(row[0], int(row[2] or 0))[0] == "LOW"]
                if low_muscles:
                    volume_summary = f" Undertranande: {', '.join(low_muscles)}."
                if acwr > 1.5 and recovery_score < 50:
                    volume_summary += " Deload rekommenderas."

            insight_content = (f"Readiness: {readiness_score}/100. "
                              f"Recovery: {recovery_score}/100. "
                              f"ACWR: {acwr}.{volume_summary}")

            existing = conn.execute(text("""
                SELECT id FROM ai_insights WHERE user_id = :uid AND title = :title
            """), {"uid": uid, "title": insight_title}).fetchone()

            if not existing:
                conn.execute(text("""
                    INSERT INTO ai_insights (user_id, title, content, insight_type)
                    VALUES (:uid, :title, :content, :itype)
                """), {
                    "uid": uid,
                    "title": insight_title,
                    "content": insight_content,
                    "itype": "weekly_analysis"
                })

        conn.commit()
        log.info("\nAnalys klar! Metrics och AI insights sparade.")

if __name__ == "__main__":
    log.info("Startar Training Intelligence System...")
    log.info("Baserat pa evidensbaserade riktlinjer (Schoenfeld, Gabbett et al.)")
    run_volume_and_recovery_analysis()
