from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging
import os
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

# Kostplaner inspirerade av evidensbaserade riktlinjer från legitimerade dietister
NUTRITION_PLANS = [
    {
        "goal": "bygga_muskler",
        "calories_target": 3200,
        "prompt": "Muskelbygge kostplan — kaloriöverskott, högt protein, muskelåterhämtning",
        "plan_json": {
            "name": "Muskelbygge — Kostplan",
            "description": "Inspirerad av protein- och prestationsprinciper från dietister.",
            "disclaimer": "Kostplanerna är inspirerade av evidensbaserade riktlinjer och råd från legitimerade dietister.",
            "macros": {
                "protein_g_per_kg": 2.0,
                "carbs_level": "hög",
                "fat_level": "moderat",
                "calories": 3200,
                "protein_g": 180,
                "carbs_g": 380,
                "fat_g": 90
            },
            "meals": [
                {"meal_type": "frukost", "foods": ["Havregrynsgröt", "Banan", "Ägg", "Jordnötssmör", "Mjölk"], "calories": 750},
                {"meal_type": "mellanmål", "foods": ["Kvarg", "Nötter", "Bär"], "calories": 350},
                {"meal_type": "lunch", "foods": ["Kycklingfilé", "Ris", "Broccoli", "Olivolja"], "calories": 800},
                {"meal_type": "efter_träning", "foods": ["Proteinshake", "Banan"], "calories": 400},
                {"meal_type": "middag", "foods": ["Lax eller kött", "Potatis", "Grönsaker"], "calories": 700},
                {"meal_type": "kvällsmål", "foods": ["Keso", "Frukt"], "calories": 200}
            ]
        }
    },
    {
        "goal": "gå_ner_i_vikt",
        "calories_target": 1800,
        "prompt": "Viktnedgång kostplan — kaloriunderskott, mättnad, behålla muskler",
        "plan_json": {
            "name": "Viktnedgång — Kostplan",
            "description": "Baseras på hållbar viktnedgång och proteinrik kost enligt dietist-råd.",
            "disclaimer": "Kostplanerna är inspirerade av evidensbaserade riktlinjer och råd från legitimerade dietister.",
            "macros": {
                "protein_g_per_kg": 2.0,
                "carbs_level": "låg-medel",
                "fat_level": "låg",
                "calories": 1800,
                "protein_g": 150,
                "carbs_g": 180,
                "fat_g": 60
            },
            "meals": [
                {"meal_type": "frukost", "foods": ["Ägg", "Fullkornsbröd", "Avokado"], "calories": 400},
                {"meal_type": "mellanmål", "foods": ["Äpple", "Kvarg"], "calories": 200},
                {"meal_type": "lunch", "foods": ["Kycklingsallad", "Quinoa", "Grönsaker"], "calories": 500},
                {"meal_type": "mellanmål", "foods": ["Proteinshake"], "calories": 200},
                {"meal_type": "middag", "foods": ["Fisk", "Ugnsrostade grönsaker", "Potatis"], "calories": 450},
                {"meal_type": "kvällsmål", "foods": ["Grekisk yoghurt"], "calories": 150}
            ]
        }
    },
    {
        "goal": "öka_kondition",
        "calories_target": 2800,
        "prompt": "Kondition och uthållighet kostplan — energi för träning, återhämtning",
        "plan_json": {
            "name": "Viktuppgång — Kostplan",
            "description": "Fokus på hälsosam viktuppgång med energi- och näringstäta livsmedel.",
            "disclaimer": "Kostplanerna är inspirerade av evidensbaserade riktlinjer och råd från legitimerade dietister.",
            "macros": {
                "protein_g_per_kg": 1.8,
                "carbs_level": "mycket hög",
                "fat_level": "moderat-hög",
                "calories": 3800,
                "protein_g": 160,
                "carbs_g": 500,
                "fat_g": 110
            },
            "meals": [
                {"meal_type": "frukost", "foods": ["Havregryn", "Granola", "Yoghurt", "Honung", "Banan"], "calories": 800},
                {"meal_type": "mellanmål", "foods": ["Smoothie: mjölk, jordnötssmör, banan, havregryn"], "calories": 600},
                {"meal_type": "lunch", "foods": ["Pasta", "Köttfärssås", "Parmesan"], "calories": 900},
                {"meal_type": "mellanmål", "foods": ["Nötmix", "Proteinbar"], "calories": 500},
                {"meal_type": "middag", "foods": ["Kyckling", "Ris", "Avokado", "Sås"], "calories": 800},
                {"meal_type": "kvällsmål", "foods": ["Keso", "Jordnötssmörsmacka"], "calories": 400}
            ]
        }
    },
    {
        "goal": "hålla_sig_i_form",
        "calories_target": 2400,
        "prompt": "Hålla sig i form kostplan — balanserad kost, underhåll",
        "plan_json": {
            "name": "Hålla sig i form — Kostplan",
            "description": "Balanserad kost för att underhålla vikt och form enligt dietist-råd.",
            "disclaimer": "Kostplanerna är inspirerade av evidensbaserade riktlinjer och råd från legitimerade dietister.",
            "macros": {
                "protein_g_per_kg": 1.6,
                "carbs_level": "medel",
                "fat_level": "medel",
                "calories": 2400,
                "protein_g": 140,
                "carbs_g": 280,
                "fat_g": 75
            },
            "meals": [
                {"meal_type": "frukost", "foods": ["Yoghurt", "Müsli", "Bär", "Honung"], "calories": 500},
                {"meal_type": "mellanmål", "foods": ["Frukt", "Nötter"], "calories": 250},
                {"meal_type": "lunch", "foods": ["Lax", "Quinoa", "Spenat", "Citron"], "calories": 650},
                {"meal_type": "mellanmål", "foods": ["Kvarg", "Banan"], "calories": 250},
                {"meal_type": "middag", "foods": ["Kyckling", "Sötpotatis", "Broccoli"], "calories": 600},
                {"meal_type": "kvällsmål", "foods": ["Keso", "Bär"], "calories": 150}
            ]
        }
    }
]

def seed_nutrition_plans(conn):
    log.info("Adding nutrition plans...")
    count = 0
    for plan in NUTRITION_PLANS:
        existing = conn.execute(text("""
            SELECT id FROM ai_nutrition_plans WHERE goal = :goal AND user_id IS NULL
        """), {"goal": plan["goal"]}).fetchone()
        if existing:
            log.info(f"Plan for {plan['goal']} already exists, skipping.")
            continue
        conn.execute(text("""
            INSERT INTO ai_nutrition_plans
                (goal, prompt, plan_json, calories_target, is_active)
            VALUES
                (:goal, :prompt, :plan_json, :calories, true)
        """), {
            "goal": plan["goal"],
            "prompt": plan["prompt"],
            "plan_json": json.dumps(plan["plan_json"], ensure_ascii=False),
            "calories": plan["calories_target"]
        })
        count += 1
    conn.commit()
    log.info(f"Added {count} nutrition plans!")

if __name__ == "__main__":
    log.info("Starting nutrition plans seeder...")
    with engine.connect() as conn:
        seed_nutrition_plans(conn)
    log.info("Done!")
    log.info("Kostplanerna är inspirerade av evidensbaserade riktlinjer och råd från legitimerade dietister.")