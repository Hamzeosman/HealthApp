"""
scheduler.py
APScheduler — kör pipelines automatiskt i bakgrunden.
Startar med FastAPI-appen via lifespan.

Jobs:
- Varje natt 02:00 — feature_store + fatigue + alla pipelines
- Varje timme — materialized views refresh
- Varje måndag 06:00 — weekly reports
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

log = logging.getLogger(__name__)
scheduler = BackgroundScheduler(timezone="Europe/Stockholm")


def job_feature_store():
    log.info("⏰ SCHEDULER: feature_store_pipeline startar")
    try:
        from pipelines.feature_store_pipeline import run
        run()
        log.info("✅ SCHEDULER: feature_store_pipeline klar")
    except Exception as e:
        log.error(f"❌ SCHEDULER: feature_store_pipeline fel: {e}")


def job_fatigue():
    log.info("⏰ SCHEDULER: fatigue_pipeline startar")
    try:
        from pipelines.fatigue_pipeline import run
        run()
        log.info("✅ SCHEDULER: fatigue_pipeline klar")
    except Exception as e:
        log.error(f"❌ SCHEDULER: fatigue_pipeline fel: {e}")


def job_recommendations():
    log.info("⏰ SCHEDULER: recommendation_pipeline startar")
    try:
        from core.repositories.users_repo import get_all_users
        from pipelines.recommendation_pipeline import generate_recommendations
        users = get_all_users()
        for user_id, name, *_ in users:
            try:
                generate_recommendations(user_id, name)
            except Exception as e:
                log.error(f"  ❌ {name}: {e}")
        log.info("✅ SCHEDULER: recommendation_pipeline klar")
    except Exception as e:
        log.error(f"❌ SCHEDULER: recommendation_pipeline fel: {e}")


def job_streaks():
    log.info("⏰ SCHEDULER: streak_pipeline startar")
    try:
        from core.repositories.users_repo import get_all_users
        from pipelines.streak_pipeline import update_streak
        users = get_all_users()
        for user_id, name, *_ in users:
            try:
                update_streak(user_id, name)
            except Exception as e:
                log.error(f"  ❌ {name}: {e}")
        log.info("✅ SCHEDULER: streak_pipeline klar")
    except Exception as e:
        log.error(f"❌ SCHEDULER: streak_pipeline fel: {e}")


def job_weekly_reports():
    log.info("⏰ SCHEDULER: weekly_report_pipeline startar")
    try:
        from core.repositories.users_repo import get_all_users
        from pipelines.weekly_report_pipeline import generate_weekly_report
        users = get_all_users()
        for user_id, name, *_ in users:
            try:
                generate_weekly_report(user_id, name)
            except Exception as e:
                log.error(f"  ❌ {name}: {e}")
        log.info("✅ SCHEDULER: weekly_report_pipeline klar")
    except Exception as e:
        log.error(f"❌ SCHEDULER: weekly_report fel: {e}")


def job_refresh_views():
    log.info("⏰ SCHEDULER: refreshar materialized views")
    try:
        from core.db import get_engine
        from sqlalchemy import text
        engine = get_engine()
        with engine.connect() as conn:
            for view in ['mv_user_weekly_volume', 'mv_readiness_trends',
                         'mv_pr_progression', 'mv_fatigue_dashboard']:
                conn.execute(text(f"REFRESH MATERIALIZED VIEW {view}"))
            conn.commit()
        log.info("✅ SCHEDULER: views refreshade")
    except Exception as e:
        log.error(f"❌ SCHEDULER: view refresh fel: {e}")


def setup_scheduler():
    # Nightly 02:00 — tung pipeline batch
    scheduler.add_job(job_feature_store,  CronTrigger(hour=2, minute=0),  id="feature_store")
    scheduler.add_job(job_fatigue,        CronTrigger(hour=2, minute=15), id="fatigue")
    scheduler.add_job(job_recommendations,CronTrigger(hour=2, minute=30), id="recommendations")
    scheduler.add_job(job_streaks,        CronTrigger(hour=2, minute=45), id="streaks")

    # Varje timme — views refresh
    scheduler.add_job(job_refresh_views,  CronTrigger(minute=0),          id="refresh_views")

    # Måndag 06:00 — veckorapporter
    scheduler.add_job(job_weekly_reports, CronTrigger(day_of_week="mon", hour=6), id="weekly_reports")

    scheduler.start()
    log.info("✅ APScheduler startad — 6 jobs schemalagda")
    for job in scheduler.get_jobs():
        log.info(f"  📅 {job.id}: {job.next_run_time}")

    return scheduler
