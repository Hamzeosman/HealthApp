from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))

with engine.connect() as conn:
    # Testa 1: Kolla tabeller
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """))
    print(" Anslutning lyckades! Tabeller i databasen:")
    for row in result:
        print(f"   - {row[0]}")

    # Testa 2: Kolla övningar
    result = conn.execute(text("SELECT name, difficulty FROM exercises"))
    print("\n Övningar i databasen:")
    for row in result:
        print(f"   - {row[0]} ({row[1]})")

    # Testa 3: Kolla kroppsdelar
    result = conn.execute(text("SELECT name FROM body_parts"))
    print("\nKroppsdelar i databasen:")
    for row in result:
        print(f"   - {row[0]}")