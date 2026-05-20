"""
run_all_pipelines.py — Orchestrator.
Training Intelligence Platform v2.
"""
import logging
import sys
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pipeline.log")
    ]
)
log = logging.getLogger(__name__)
sys.path.insert(0, os.path.dirname(__file__))

from core.users import get_all_users

def safe_run_for_all_users(pipeline_name, func):
    """Kor en funktion per user med error isolation."""
    users = get_all_users()
    success_count = 0
    fail_count = 0
    for user_id, name, fitness_level, fitness_goal in users:
        try:
            func(user_id, name)
            success_count += 1
        except Exception as e:
            log.error(f"  [FEL] {pipeline_name} for user {name} (ID:{user_id}): {e}")
            fail_count += 1
    log.info(f"  Resultat: {success_count} OK, {fail_count} FEL")
    return fail_count == 0

def run_pipeline(name, func):
    log.info(f"\n{'='*50}")
    log.info(f"Kor: {name}")
    log.info(f"{'='*50}")
    start = datetime.now()
    try:
        result = func()
        duration = (datetime.now() - start).seconds
        log.info(f"[OK] {name} klar pa {duration}s!")
        return True
    except Exception as e:
        log.error(f"[FEL] {name}: {e}")
        return False

def run_all_recommendations():
    from pipelines.recommendation_pipeline import generate_recommendations
    return safe_run_for_all_users("Recommendations", generate_recommendations)

def run_all_personal_records():
    from pipelines.personal_records_pipeline import check_personal_records
    return safe_run_for_all_users("Personal Records", check_personal_records)

def run_all_progression():
    from pipelines.progression_pipeline import analyze_progression
    return safe_run_for_all_users("Progression", analyze_progression)

def run_all_streaks():
    from pipelines.streak_pipeline import update_streak
    return safe_run_for_all_users("Streaks", update_streak)

def run_all_weekly_reports():
    from pipelines.weekly_report_pipeline import generate_weekly_report
    return safe_run_for_all_users("Weekly Reports", generate_weekly_report)

def run_training_intelligence():
    from pipelines.volume_tracker_pipeline import run_volume_and_recovery_analysis
    run_volume_and_recovery_analysis()

# Pipeline registry
PIPELINE_REGISTRY = {
    "recommendations":  run_all_recommendations,
    "personal_records": run_all_personal_records,
    "progression":      run_all_progression,
    "streaks":          run_all_streaks,
    "training_intel":   run_training_intelligence,
    "weekly_reports":   run_all_weekly_reports,
}

if __name__ == "__main__":
    start = datetime.now()
    log.info(f"Training Intelligence Platform")
    log.info(f"Start: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    log.info(f"Pipelines registrerade: {list(PIPELINE_REGISTRY.keys())}")

    results = {}
    for name, func in PIPELINE_REGISTRY.items():
        results[name] = run_pipeline(name, func)

    duration = (datetime.now() - start).seconds
    ok = sum(1 for v in results.values() if v)
    fail = sum(1 for v in results.values() if not v)

    log.info(f"\n{'='*50}")
    log.info(f"Platform klar pa {duration}s — {ok} OK, {fail} FEL")
    log.info(f"{'='*50}")
    for name, success in results.items():
        log.info(f"  {'[OK]' if success else '[FEL]'} {name}")
