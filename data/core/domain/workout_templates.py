"""
workout_templates.py — Evidensbaserade träningsprogram
AI modifierar dem baserat på readiness, injuries, fatigue.
"""
TEMPLATES = {
    "PPL": {
        "name": "Push Pull Legs",
        "days": 6,
        "description": "Klassiskt 6-dagars program.",
        "sessions": {
            1: {"name": "Push A", "muscles": ["Bröst","Axlar","Armar"], "focus": "hypertrophy"},
            2: {"name": "Pull A", "muscles": ["Rygg","Armar"], "focus": "hypertrophy"},
            3: {"name": "Legs A", "muscles": ["Ben","Mage"], "focus": "hypertrophy"},
            4: {"name": "Push B", "muscles": ["Bröst","Axlar","Armar"], "focus": "strength_hypertrophy"},
            5: {"name": "Pull B", "muscles": ["Rygg","Armar"], "focus": "strength_hypertrophy"},
            6: {"name": "Legs B", "muscles": ["Ben","Mage"], "focus": "strength_hypertrophy"},
        }
    },
    "Upper_Lower": {
        "name": "Upper/Lower Split",
        "days": 4,
        "description": "4-dagars upper/lower.",
        "sessions": {
            1: {"name": "Upper A", "muscles": ["Bröst","Rygg","Axlar","Armar"], "focus": "strength_hypertrophy"},
            2: {"name": "Lower A", "muscles": ["Ben","Mage"], "focus": "strength_hypertrophy"},
            3: {"name": "Upper B", "muscles": ["Bröst","Rygg","Axlar","Armar"], "focus": "hypertrophy"},
            4: {"name": "Lower B", "muscles": ["Ben","Mage"], "focus": "hypertrophy"},
        }
    },
    "Full_Body": {
        "name": "Full Body 3x/vecka",
        "days": 3,
        "description": "Helkroppsträning. Perfekt för nybörjare.",
        "sessions": {
            1: {"name": "Full Body A", "muscles": ["Bröst","Rygg","Ben","Axlar"], "focus": "general_fitness"},
            2: {"name": "Full Body B", "muscles": ["Rygg","Bröst","Ben","Armar"], "focus": "general_fitness"},
            3: {"name": "Full Body C", "muscles": ["Ben","Bröst","Rygg","Mage"], "focus": "general_fitness"},
        }
    },
    "Powerbuilding": {
        "name": "Powerbuilding",
        "days": 4,
        "description": "Styrka + hypertrofi kombinerat.",
        "sessions": {
            1: {"name": "Chest + Triceps", "muscles": ["Bröst","Armar"], "focus": "strength_hypertrophy"},
            2: {"name": "Back + Biceps",   "muscles": ["Rygg","Armar"], "focus": "strength_hypertrophy"},
            3: {"name": "Shoulders + Arms","muscles": ["Axlar","Armar"], "focus": "hypertrophy"},
            4: {"name": "Legs",            "muscles": ["Ben","Mage"], "focus": "strength_hypertrophy"},
        }
    },
    "Deload": {
        "name": "Deload Week",
        "days": 3,
        "description": "Aktiv vila. 50% volym, RPE 5-6.",
        "sessions": {
            1: {"name": "Light Upper",     "muscles": ["Bröst","Rygg"], "focus": "mobility_recovery"},
            2: {"name": "Light Lower",     "muscles": ["Ben","Mage"],   "focus": "mobility_recovery"},
            3: {"name": "Full Body Light", "muscles": ["Bröst","Rygg","Ben"], "focus": "mobility_recovery"},
        }
    },
    "Home_Gym": {
        "name": "Hemmaträning",
        "days": 3,
        "description": "Kroppsvikt + band. Ingen maskin behövs.",
        "sessions": {
            1: {"name": "Push",          "muscles": ["Bröst","Axlar","Armar"], "focus": "hypertrophy"},
            2: {"name": "Pull + Core",   "muscles": ["Rygg","Armar","Mage"],   "focus": "hypertrophy"},
            3: {"name": "Legs + Cardio", "muscles": ["Ben","Kondition"],        "focus": "metabolic"},
        }
    }
}


def select_template(ctx: dict) -> str:
    if ctx.get('deload_recommended') or ctx.get('acwr', 1) > 1.5:
        return "Deload"
    available = ctx.get('available_equipment', [])
    has_gym   = any(e in available for e in ['Bänkpressmaskin','Leg Press Machine','Lat Pulldown Machine'])
    if not has_gym and len(available) <= 3:
        return "Home_Gym"
    level = ctx.get('fitness_level', 'medel')
    goal  = ctx.get('fitness_goal', 'hålla_sig_i_form')
    if level == 'nybörjare':
        return "Full_Body"
    elif goal in ['bygga_muskler', 'gå_upp_i_vikt']:
        return "PPL" if level == 'avancerad' else "Powerbuilding"
    elif goal in ['öka_kondition', 'gå_ner_i_vikt']:
        return "Full_Body"
    return "Upper_Lower"


def get_todays_session(template_name: str, day_of_week: int) -> dict:
    template = TEMPLATES.get(template_name, TEMPLATES["Full_Body"])
    sessions  = template["sessions"]
    day       = (day_of_week % len(sessions)) + 1
    return sessions.get(day, sessions[1])
