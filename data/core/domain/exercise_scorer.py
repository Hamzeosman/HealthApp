"""
exercise_scorer.py — Smart Exercise Scoring Engine
Ersätter ORDER BY RANDOM() med intelligent scoring.
Score = readiness + equipment + fatigue + injury + goal + difficulty
"""
from sqlalchemy import text


def score_exercise(exercise: dict, ctx: dict) -> float:
    score = 50.0
    is_compound = exercise.get('is_compound', False)
    systemic_fatigue = exercise.get('systemic_fatigue') or 5
    spinal_load = exercise.get('spinal_load') or 3
    readiness = ctx['readiness']
    acwr = ctx['acwr']

    # 1. Readiness → compound vs isolation
    if readiness >= 75:
        if is_compound: score += 20
    elif readiness >= 55:
        if is_compound: score += 10
    else:
        score += max(0, (5 - systemic_fatigue) * 4)
        if is_compound and systemic_fatigue >= 8: score -= 15

    # 2. Fatigue penalty
    if acwr > 1.3:
        score -= systemic_fatigue * acwr * 2
    elif acwr < 0.8:
        if is_compound: score += 10

    # 3. Injury penalties
    shoulder_stress = exercise.get('shoulder_stress') or 0
    knee_stress     = exercise.get('knee_stress') or 0
    lower_back      = exercise.get('lower_back_stress') or 0
    hip_stress      = exercise.get('hip_stress') or 0

    for injury in ctx.get('injuries', []):
        bp  = injury['body_part'].lower()
        sev = injury['severity'] or 1
        if 'axel' in bp:      score -= shoulder_stress * sev * 2
        if 'knä'  in bp:      score -= knee_stress     * sev * 2
        if 'rygg' in bp:      score -= (lower_back + spinal_load) * sev
        if 'höft' in bp:      score -= hip_stress      * sev
        if exercise.get('name','').lower() in [r.lower() for r in (injury.get('restricted') or [])]:
            score -= 100

    # 4. Equipment match
    ex_eq     = exercise.get('equipment_name')
    available = ctx.get('available_equipment', [])
    if ex_eq is None or ex_eq == 'Kroppsvikt': score += 10
    elif ex_eq in available:                    score += 15
    else:                                       score -= 50

    # 5. Goal/focus alignment
    focus       = ctx.get('focus_area', 'general_fitness')
    force_curve = exercise.get('force_curve')
    if focus in ['hypertrophy', 'strength_hypertrophy']:
        if force_curve in ['ascending', 'bell_curve']: score += 10
        if is_compound: score += 8
    elif focus == 'metabolic':
        if systemic_fatigue and systemic_fatigue >= 6: score += 8
    elif focus == 'mobility_recovery':
        score += max(0, (5 - systemic_fatigue) * 3)
        if spinal_load and spinal_load <= 3: score += 10

    # 6. Days since workout
    if ctx.get('days_since_workout', 0) > 7:
        skill = exercise.get('skill_requirement') or 3
        score += max(0, (3 - skill) * 5)

    # 7. Difficulty match
    level_map = {'nybörjare': 1, 'medel': 2, 'avancerad': 3}
    diff_map  = {'nybörjare': 1, 'medel': 2, 'avancerad': 3}
    user_lvl  = level_map.get(ctx.get('fitness_level', 'medel'), 2)
    ex_diff   = diff_map.get(exercise.get('difficulty', 'medel'), 2)
    delta     = abs(user_lvl - ex_diff)
    if delta == 0:   score += 10
    elif delta == 1: score += 5
    else:            score -= 10

    # 8. Deload override
    if ctx.get('deload_recommended'):
        if systemic_fatigue and systemic_fatigue >= 8: score -= 30
        if spinal_load and spinal_load >= 8:           score -= 20

    return round(score, 2)


def get_scored_exercises(muscle_groups: list, ctx: dict, conn,
                         limit_per_muscle: int = 3,
                         exercise_type: str = 'styrka') -> list:
    all_scored = []
    for muscle in muscle_groups:
        rows = conn.execute(text("""
            SELECT e.id, e.name, e.difficulty, e.exercise_type,
                   e.is_compound, e.systemic_fatigue, e.spinal_load,
                   e.shoulder_stress, e.knee_stress, e.lower_back_stress,
                   e.hip_stress, e.force_curve, e.skill_requirement,
                   e.movement_pattern, e.fatigue_score,
                   eq.name as equipment_name, bp.name as body_part
            FROM exercises e
            LEFT JOIN body_parts bp ON e.body_part_id = bp.id
            LEFT JOIN equipment eq ON e.equipment_id = eq.id
            WHERE bp.name = :muscle AND e.exercise_type = :etype
            LIMIT 20
        """), {"muscle": muscle, "etype": exercise_type}).fetchall()

        for row in rows:
            ex = {
                "id": row[0], "name": row[1], "difficulty": row[2],
                "exercise_type": row[3], "is_compound": row[4] or False,
                "systemic_fatigue": row[5], "spinal_load": row[6],
                "shoulder_stress": row[7], "knee_stress": row[8],
                "lower_back_stress": row[9], "hip_stress": row[10],
                "force_curve": row[11], "skill_requirement": row[12],
                "movement_pattern": row[13], "fatigue_score": row[14],
                "equipment_name": row[15], "body_part": row[16]
            }
            ex['score'] = score_exercise(ex, ctx)
            all_scored.append(ex)

    all_scored.sort(key=lambda x: x['score'], reverse=True)
    selected = []
    muscle_count = {}
    for ex in all_scored:
        m = ex['body_part']
        if muscle_count.get(m, 0) < limit_per_muscle:
            selected.append(ex)
            muscle_count[m] = muscle_count.get(m, 0) + 1
    return selected
