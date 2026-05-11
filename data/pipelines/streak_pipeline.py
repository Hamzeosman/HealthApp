from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
import os
from datetime import date, timedelta

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

load_dotenv()

try:
    engine = create_engine(os.getenv("DATABASE_URL"))
    log.info("Connected to database!")
except Exception as e:
    log.error(f"Could not connect: {e}")
    exit(1)

def get_all_users() -> list:
    with engine.connect() as conn:
        return conn.execute(text("SELECT id, name FROM users")).fetchall()

def get_workout_dates(user_id: int) -> list:
    """Get all unique workout dates for a user."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT date FROM workout_sessions
            WHERE user_id = :user_id
            ORDER BY date DESC
        """), {"user_id": user_id})
        return [row[0] for row in result.fetchall()]

def calculate_streak(workout_dates: list) -> tuple:
    """Calculate current and longest streak."""
    if not workout_dates:
        return 0, 0

    workout_dates = sorted(set(workout_dates), reverse=True)
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Current streak
    current_streak = 0
    if workout_dates[0] in [today, yesterday]:
        current_streak = 1
        for i in range(1, len(workout_dates)):
            diff = (workout_dates[i-1] - workout_dates[i]).days
            if diff == 1:
                current_streak += 1
            else:
                break

    # Longest streak
    longest_streak = 1
    temp_streak = 1
    for i in range(1, len(workout_dates)):
        diff = (workout_dates[i-1] - workout_dates[i]).days
        if diff == 1:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 1

    return current_streak, longest_streak

def check_achievements(user_id: int, user_name: str, current_streak: int, total_workouts: int):
    """Check and unlock achievements."""
    with engine.connect() as conn:
        achievements = conn.execute(text("""
            SELECT a.id, a.name, a.requirement_type, a.requirement_value
            FROM achievements a
            WHERE a.id NOT IN (
                SELECT achievement_id FROM user_achievements
                WHERE user_id = :user_id
            )
        """), {"user_id": user_id}).fetchall()

        for achievement in achievements:
            ach_id = achievement[0]
            ach_name = achievement[1]
            req_type = achievement[2]
            req_value = achievement[3]

            unlocked = False

            if req_type == 'total_sessions' and total_workouts >= req_value:
                unlocked = True
            elif req_type == 'streak_days' and current_streak >= req_value:
                unlocked = True

            if unlocked:
                conn.execute(text("""
                    INSERT INTO user_achievements (user_id, achievement_id)
                    VALUES (:user_id, :ach_id)
                    ON CONFLICT DO NOTHING
                """), {"user_id": user_id, "ach_id": ach_id})

                conn.execute(text("""
                    INSERT INTO notifications (user_id, title, message, notification_type)
                    VALUES (:user_id, :title, :message, 'streak_milestone')
                """), {
                    "user_id": user_id,
                    "title": f"Achievement unlocked: {ach_name}!",
                    "message": f"Congratulations {user_name}! You just unlocked '{ach_name}'!"
                })

                log.info(f"[{user_name}] Achievement unlocked: {ach_name}!")

        conn.commit()

def send_workout_reminder(user_id: int, user_name: str, last_workout: date, current_streak: int):
    """Send reminder notification if user has not trained in 2+ days."""
    days_since = (date.today() - last_workout).days if last_workout else 999

    with engine.connect() as conn:
        if days_since >= 2:
            existing = conn.execute(text("""
                SELECT id FROM notifications
                WHERE user_id = :user_id
                AND notification_type = 'workout_reminder'
                AND DATE(created_at) = CURRENT_DATE
            """), {"user_id": user_id}).fetchone()

            if not existing:
                if current_streak > 0:
                    message = f"You have not trained in {days_since} days. Your {current_streak}-day streak is at risk!"
                else:
                    message = f"You have not trained in {days_since} days. Time to get back in the gym!"

                conn.execute(text("""
                    INSERT INTO notifications (user_id, title, message, notification_type)
                    VALUES (:user_id, :title, :message, 'workout_reminder')
                """), {
                    "user_id": user_id,
                    "title": "Time to train!",
                    "message": message
                })
                conn.commit()
                log.info(f"[{user_name}] Workout reminder sent — {days_since} days since last session.")

def update_streak(user_id: int, user_name: str):
    """Update streak data for a user."""
    try:
        workout_dates = get_workout_dates(user_id)
        total_workouts = len(workout_dates)

        if not workout_dates:
            log.warning(f"[{user_name}] No workouts found.")
            return

        current_streak, longest_streak = calculate_streak(workout_dates)
        last_workout = workout_dates[0] if workout_dates else None

        with engine.connect() as conn:
            existing = conn.execute(text(
                "SELECT id FROM user_streaks WHERE user_id = :user_id"
            ), {"user_id": user_id}).fetchone()

            if existing:
                conn.execute(text("""
                    UPDATE user_streaks SET
                        current_streak = :current,
                        longest_streak = GREATEST(longest_streak, :longest),
                        last_workout_date = :last_workout,
                        total_workouts = :total
                    WHERE user_id = :user_id
                """), {
                    "current": current_streak,
                    "longest": longest_streak,
                    "last_workout": last_workout,
                    "total": total_workouts,
                    "user_id": user_id
                })
            else:
                conn.execute(text("""
                    INSERT INTO user_streaks
                        (user_id, current_streak, longest_streak, last_workout_date, total_workouts)
                    VALUES (:user_id, :current, :longest, :last_workout, :total)
                """), {
                    "user_id": user_id,
                    "current": current_streak,
                    "longest": longest_streak,
                    "last_workout": last_workout,
                    "total": total_workouts
                })
            conn.commit()

        log.info(f"[{user_name}] Streak: {current_streak} days | Best: {longest_streak} days | Total: {total_workouts} sessions")

        check_achievements(user_id, user_name, current_streak, total_workouts)
        send_workout_reminder(user_id, user_name, last_workout, current_streak)

    except Exception as e:
        log.error(f"Error updating streak for {user_name}: {e}")

if __name__ == "__main__":
    log.info("Starting streak pipeline...")
    users = get_all_users()

    if not users:
        log.warning("No users found!")
        exit(0)

    for user in users:
        update_streak(user[0], user[1])

    log.info("Streak pipeline complete!")