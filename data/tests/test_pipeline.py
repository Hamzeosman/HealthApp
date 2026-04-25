import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pipelines.recommendation_pipeline import (
    get_all_users,
    get_untrained_body_parts,
    generate_recommendations
)

load_dotenv()

# =====================
# TEST 1: Databasanslutning
# =====================
def test_database_connection():
    """Testar att vi kan ansluta till databasen."""
    engine = create_engine(os.getenv("DATABASE_URL"))
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.fetchone()[0] == 1
    print("✅ Databasanslutning fungerar!")

# =====================
# TEST 2: Hämta användare
# =====================
def test_get_all_users():
    """Testar att vi kan hämta användare."""
    users = get_all_users()
    assert isinstance(users, list)
    assert len(users) > 0
    print(f"✅ Hittade {len(users)} användare!")

# =====================
# TEST 3: Kroppsdelar som inte tränats
# =====================
def test_get_untrained_body_parts():
    """Testar att vi hittar otränade kroppsdelar."""
    users = get_all_users()
    user_id = users[0][0]
    untrained = get_untrained_body_parts(user_id)
    assert isinstance(untrained, list)
    print(f"✅ Hittade {len(untrained)} otränade kroppsdelar!")

# =====================
# TEST 4: Generera rekommendationer
# =====================
def test_generate_recommendations():
    """Testar att rekommendationer genereras och sparas."""
    engine = create_engine(os.getenv("DATABASE_URL"))
    users = get_all_users()
    user_id = users[0][0]
    user_name = users[0][1]

    generate_recommendations(user_id, user_name)

    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) FROM recommendations 
            WHERE user_id = :user_id
        """), {"user_id": user_id})
        count = result.fetchone()[0]
        assert count > 0
    print(f"✅ {count} rekommendationer sparade i databasen!")

# =====================
# TEST 5: Schema - tabeller finns
# =====================
def test_database_tables_exist():
    """Testar att alla tabeller finns i databasen."""
    engine = create_engine(os.getenv("DATABASE_URL"))
    expected_tables = [
        "users", "exercises", "body_parts", "workout_sessions",
        "workout_exercises", "recommendations", "personal_records"
    ]
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        existing = [row[0] for row in result]
        for table in expected_tables:
            assert table in existing, f"❌ Tabell {table} saknas!"
    print("✅ Alla tabeller finns!")