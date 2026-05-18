import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from translations import t, LANGUAGE_OPTIONS

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
engine = create_engine(os.getenv("DATABASE_URL"))

st.set_page_config(page_title="HealthApp Dashboard", page_icon="🏋️", layout="wide")

@st.cache_data
def load_data():
    with engine.connect() as conn:
        sessions = pd.read_sql(text("SELECT ws.*, u.name AS user_name FROM workout_sessions ws JOIN users u ON ws.user_id = u.id"), conn)
        exercises = pd.read_sql(text("""
            SELECT we.*, e.name AS exercise_name, bp.name AS body_part,
                e.difficulty, e.calories_per_minute, ws.date, ws.user_id
            FROM workout_exercises we
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            JOIN workout_sessions ws ON we.session_id = ws.id
        """), conn)
        records = pd.read_sql(text("SELECT pr.*, e.name AS exercise_name FROM personal_records pr JOIN exercises e ON pr.exercise_id = e.id"), conn)
        recovery = pd.read_sql(text("SELECT * FROM recovery_logs ORDER BY date"), conn)
        recommendations = pd.read_sql(text("""
            SELECT r.*, e.name AS exercise_name, bp.name AS body_part
            FROM recommendations r
            JOIN exercises e ON r.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            ORDER BY score DESC
        """), conn)
        biometrics = pd.read_sql(text("SELECT * FROM biometrics ORDER BY date"), conn)
        running = pd.read_sql(text("SELECT * FROM running_sessions ORDER BY date"), conn)
        goals = pd.read_sql(text("SELECT DISTINCT ON (user_id, goal_type) * FROM user_goals ORDER BY user_id, goal_type, id"), conn)
        plans = pd.read_sql(text("SELECT * FROM training_plans ORDER BY id"), conn)
        users = pd.read_sql(text("SELECT id, name, email, age, weight_kg, height_cm, fitness_level, fitness_goal, experience_level FROM users"), conn)
        foods = pd.read_sql(text("SELECT * FROM foods ORDER BY category, name"), conn)
        nutrition_goals = pd.read_sql(text("SELECT DISTINCT ON (user_id) * FROM nutrition_goals ORDER BY user_id, id"), conn)
        meal_logs = pd.read_sql(text("""
            SELECT ml.*, f.name AS food_name, f.category, f.calories_per_100g,
                f.protein_per_100g, f.carbs_per_100g, f.fat_per_100g
            FROM meal_logs ml
            JOIN foods f ON ml.food_id = f.id
            ORDER BY ml.date DESC
        """), conn)
        challenges = pd.read_sql(text("SELECT DISTINCT ON (name) * FROM challenges ORDER BY name, id"), conn)
        leaderboard = pd.read_sql(text("SELECT l.*, u.name FROM leaderboard l JOIN users u ON l.user_id = u.id ORDER BY points DESC"), conn)
        ai_insights = pd.read_sql(text("SELECT DISTINCT ON (title) * FROM ai_insights ORDER BY title, created_at DESC"), conn)
        streaks = pd.read_sql(text("SELECT us.*, u.name FROM user_streaks us JOIN users u ON us.user_id = u.id"), conn)
        achievements = pd.read_sql(text("""
            SELECT DISTINCT ON (ua.user_id, a.name)
                ua.user_id, ua.id,
                a.name AS achievement_name, a.description,
                a.requirement_type, a.requirement_value
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.id
            ORDER BY ua.user_id, a.name, ua.id
        """), conn)
        notifications = pd.read_sql(text("SELECT * FROM notifications ORDER BY created_at DESC"), conn)
        health_calc = pd.read_sql(text("SELECT DISTINCT ON (user_id) * FROM health_calculations ORDER BY user_id, date DESC"), conn)
        body_measurements = pd.read_sql(text("SELECT * FROM body_measurements ORDER BY date DESC"), conn)
        muscle_groups = pd.read_sql(text("SELECT * FROM muscle_groups"), conn)
        user_progress = pd.read_sql(text("SELECT * FROM user_progress ORDER BY date DESC"), conn)
        activity_feed = pd.read_sql(text("""
            SELECT af.*, u.name AS user_name
            FROM activity_feed af
            JOIN users u ON af.user_id = u.id
            ORDER BY af.created_at DESC LIMIT 20
        """), conn)
    return (sessions, exercises, records, recovery, recommendations, biometrics,
            running, goals, plans, users, foods, nutrition_goals, meal_logs,
            challenges, leaderboard, ai_insights, streaks, achievements,
            notifications, health_calc, body_measurements, muscle_groups,
            user_progress, activity_feed)

(sessions, exercises, records, recovery, recommendations, biometrics,
 running, goals, plans, users, foods, nutrition_goals, meal_logs,
 challenges, leaderboard, ai_insights, streaks, achievements,
 notifications, health_calc, body_measurements, muscle_groups,
 user_progress, activity_feed) = load_data()

with st.sidebar:
    st.title("HealthApp 🏋️")
    st.markdown("---")
    selected_lang_name = st.selectbox(
        "🌍 Language / Språk / اللغة",
        options=list(LANGUAGE_OPTIONS.keys()),
        index=0
    )
    lang = LANGUAGE_OPTIONS[selected_lang_name]
    st.markdown("---")
    user_options = [t("all_users", lang)] + users['name'].tolist()
    selected_user = st.selectbox(t("select_user", lang), user_options)
    if selected_user != t("all_users", lang):
        user_id = users[users['name'] == selected_user]['id'].values[0]
        sessions = sessions[sessions['user_id'] == user_id]
        exercises = exercises[exercises['user_id'] == user_id]
        recovery = recovery[recovery['user_id'] == user_id]
        biometrics = biometrics[biometrics['user_id'] == user_id]
        running = running[running['user_id'] == user_id]
        goals = goals[goals['user_id'] == user_id]
        recommendations = recommendations[recommendations['user_id'] == user_id]
        nutrition_goals = nutrition_goals[nutrition_goals['user_id'] == user_id]
        meal_logs = meal_logs[meal_logs['user_id'] == user_id]
        ai_insights = ai_insights[ai_insights['user_id'] == user_id]
        streaks = streaks[streaks['user_id'] == user_id]
        achievements = achievements[achievements['user_id'] == user_id]
        notifications = notifications[notifications['user_id'] == user_id]
        health_calc = health_calc[health_calc['user_id'] == user_id]
        body_measurements = body_measurements[body_measurements['user_id'] == user_id]
        user_progress = user_progress[user_progress['user_id'] == user_id]
        activity_feed = activity_feed[activity_feed['user_id'] == user_id]
    st.markdown("---")
    if not streaks.empty:
        s = streaks.iloc[0]
        st.metric(t("current_streak", lang), f"{s['current_streak']} {t('days', lang)}")
        st.metric(t("best_streak", lang), f"{s['longest_streak']} {t('days', lang)}")
        st.metric(t("total_sessions", lang), s['total_workouts'])
    st.markdown("---")
    unread = notifications[notifications['is_read'] == False] if not notifications.empty else pd.DataFrame()
    if not unread.empty:
        st.markdown(f"**{len(unread)} {t('unread_notifications', lang)}**")
        for _, n in unread.head(3).iterrows():
            st.warning(f"{n['title']}")
    st.markdown("---")
    page = st.radio(t("navigation", lang), [
        t("overview", lang), t("training", lang), t("running", lang),
        t("biometrics", lang), t("recovery", lang), t("nutrition", lang),
        t("goals_plans", lang), t("training_programs", lang),
        t("social_challenges", lang), t("achievements", lang),
        t("health_calculator", lang), t("ai_insights", lang),
        t("recommendations", lang),
    ])
    st.markdown("---")
    st.caption(t("data_engineer", lang))

goal_colors = {
    'bygga_muskler': '#378ADD', 'gå_ner_i_vikt': '#D85A30',
    'gå_upp_i_vikt': '#1D9E75', 'löpning': '#EF9F27',
    'hålla_sig_i_form': '#7F77DD', 'öka_kondition': '#E040FB'
}

# ================================
# OVERVIEW
# ================================
if page == t("overview", lang):
    st.title(t("overview_title", lang))
    st.markdown(t("overview_subtitle", lang))
    st.markdown("---")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric(t("sessions", lang), len(sessions))
    with col2:
        total_vol = (exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)).sum()
        st.metric(t("total_volume", lang), f"{total_vol:,.0f} kg")
    with col3:
        avg_rpe = exercises['rpe'].mean() if not exercises.empty else 0
        st.metric(t("avg_rpe", lang), f"{avg_rpe:.1f}/10")
    with col4:
        st.metric(t("prs", lang), len(records))
    with col5:
        avg_sleep = recovery['sleep_hours'].mean() if not recovery.empty else 0
        st.metric(t("avg_sleep", lang), f"{avg_sleep:.1f}h")
    with col6:
        total_steps = int(biometrics['steps'].sum()) if not biometrics.empty else 0
        st.metric(t("total_steps", lang), f"{total_steps:,}")
    st.markdown("---")
    st.subheader(t("health_status", lang))
    col1, col2, col3 = st.columns(3)
    with col1:
        if not recovery.empty:
            avg_sleep = recovery['sleep_hours'].mean()
            if avg_sleep >= 7:
                st.success(f"Sleep: {avg_sleep:.1f}h — {t('sleep_optimal', lang)}")
            elif avg_sleep >= 6:
                st.warning(f"Sleep: {avg_sleep:.1f}h — {t('sleep_better', lang)}")
            else:
                st.error(f"Sleep: {avg_sleep:.1f}h — {t('sleep_low', lang)}")
    with col2:
        if not recovery.empty:
            avg_stress = recovery['stress_level'].mean()
            if avg_stress <= 4:
                st.success(f"Stress: {avg_stress:.1f}/10 — {t('stress_low', lang)}")
            elif avg_stress <= 7:
                st.warning(f"Stress: {avg_stress:.1f}/10 — {t('stress_moderate', lang)}")
            else:
                st.error(f"Stress: {avg_stress:.1f}/10 — {t('stress_high', lang)}")
    with col3:
        if not exercises.empty:
            avg_rpe = exercises['rpe'].mean()
            if avg_rpe <= 7:
                st.success(f"Load: {avg_rpe:.1f}/10 — {t('load_balanced', lang)}")
            elif avg_rpe <= 8.5:
                st.warning(f"Load: {avg_rpe:.1f}/10 — {t('load_hard', lang)}")
            else:
                st.error(f"Load: {avg_rpe:.1f}/10 — {t('load_very_hard', lang)}")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("muscle_groups", lang))
        if not exercises.empty:
            body_counts = exercises.groupby('body_part').size().reset_index(name='count')
            body_counts = body_counts.sort_values('count', ascending=True)
            fig = px.bar(body_counts, x='count', y='body_part', orientation='h',
                color='count', color_continuous_scale='Blues')
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=280)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader(t("weekly_volume", lang))
        if not exercises.empty:
            exercises['week'] = pd.to_datetime(exercises['date']).dt.strftime('%Y-W%W')
            exercises['volume'] = exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)
            weekly_vol = exercises.groupby('week')['volume'].sum().reset_index()
            fig = px.bar(weekly_vol, x='week', y='volume', color_discrete_sequence=['#378ADD'])
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
    if not activity_feed.empty:
        st.markdown("---")
        st.subheader("📢 Activity Feed")
        for _, act in activity_feed.head(5).iterrows():
            st.info(f"**{act['user_name']}** — {act['activity_type']}: {act['description']}")

# ================================
# TRAINING
# ================================
elif page == t("training", lang):
    st.title(t("training_title", lang))
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t("total_sessions", lang), len(sessions))
    with col2:
        total_vol = (exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)).sum()
        st.metric(t("total_volume_kg", lang), f"{total_vol:,.0f} kg")
    with col3:
        st.metric(t("personal_records", lang), len(records))
    with col4:
        avg_rpe = exercises['rpe'].mean() if not exercises.empty else 0
        st.metric(t("avg_rpe", lang), f"{avg_rpe:.1f}/10")
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(t("volume_per_week", lang))
        if not exercises.empty:
            exercises['week'] = pd.to_datetime(exercises['date']).dt.strftime('%Y-W%W')
            exercises['volume'] = exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)
            weekly_vol = exercises.groupby('week')['volume'].sum().reset_index()
            fig = px.bar(weekly_vol, x='week', y='volume', color_discrete_sequence=['#378ADD'])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader(t("top_exercises_rpe", lang))
        if not exercises.empty:
            top = exercises.groupby('exercise_name')['rpe'].mean().reset_index()
            top = top.sort_values('rpe', ascending=True).tail(8)
            fig = px.bar(top, x='rpe', y='exercise_name', orientation='h',
                color='rpe', color_continuous_scale='Reds')
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
    st.subheader(t("personal_records", lang))
    if not records.empty:
        fig = px.bar(records.sort_values('weight_kg', ascending=True),
            x='weight_kg', y='exercise_name', orientation='h',
            color='weight_kg', color_continuous_scale='Greens')
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
    if not user_progress.empty:
        st.markdown("---")
        st.subheader("📈 Progress tracking")
        fig = px.line(user_progress, x='date', y='value', color='metric_name',
            title='Progress over time')
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# ================================
# RUNNING
# ================================
elif page == t("running", lang):
    st.title(t("running_title", lang))
    st.markdown("---")
    if not running.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("total_runs", lang), len(running))
        with col2:
            st.metric(t("total_distance", lang), f"{running['distance_km'].sum():.1f} km")
        with col3:
            st.metric(t("avg_pace", lang), f"{running['avg_pace_min_per_km'].mean():.1f} min/km")
        with col4:
            st.metric(t("avg_heart_rate", lang), f"{running['avg_heart_rate'].mean():.0f} bpm")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(running, x='date', y='distance_km',
                color_discrete_sequence=['#1D9E75'], title=t("distance_per_run", lang))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(running, x='date', y='avg_pace_min_per_km',
                markers=True, color_discrete_sequence=['#D85A30'],
                title=t("pace_improvement", lang))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            route_dist = running.groupby('route_type')['distance_km'].sum().reset_index()
            fig = px.pie(route_dist, values='distance_km', names='route_type',
                title='Distance by route type', color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.scatter(running, x='distance_km', y='avg_pace_min_per_km',
                color='avg_heart_rate', size='calories_burned',
                title='Distance vs Pace', color_continuous_scale='RdYlGn_r')
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        st.subheader(t("session_details", lang))
        st.dataframe(running[['date', 'distance_km', 'duration_minutes',
            'avg_pace_min_per_km', 'avg_heart_rate', 'calories_burned', 'route_type']],
            use_container_width=True)
    else:
        st.info(t("no_running", lang))

# ================================
# BIOMETRICS
# ================================
elif page == t("biometrics", lang):
    st.title(t("biometrics_title", lang))
    st.markdown("---")
    if not biometrics.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("avg_daily_steps", lang), f"{biometrics['steps'].mean():,.0f}")
        with col2:
            st.metric(t("avg_resting_hr", lang), f"{biometrics['heart_rate_resting'].mean():.0f} bpm")
        with col3:
            st.metric(t("avg_calories", lang), f"{biometrics['calories_burned'].mean():,.0f} kcal")
        with col4:
            st.metric(t("avg_active_min", lang), f"{biometrics['active_minutes'].mean():.0f} min")
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = px.bar(biometrics, x='date', y='steps',
                color_discrete_sequence=['#378ADD'], title=t("daily_steps", lang))
            fig.add_hline(y=10000, line_dash="dash", line_color="green", annotation_text="Goal: 10,000")
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(biometrics, x='date', y=['heart_rate_resting', 'heart_rate_avg'],
                title=t("heart_rate", lang), color_discrete_sequence=['#5DCAA5', '#D85A30'])
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig = px.bar(biometrics, x='date', y='calories_burned',
                color_discrete_sequence=['#EF9F27'], title=t("calories_burned", lang))
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        if 'vo2_max' in biometrics.columns and biometrics['vo2_max'].notna().any():
            st.markdown("---")
            st.subheader("VO2 Max trend")
            fig = px.line(biometrics.dropna(subset=['vo2_max']), x='date', y='vo2_max',
                markers=True, color_discrete_sequence=['#7F77DD'],
                title='VO2 Max over time')
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        if not body_measurements.empty:
            st.markdown("---")
            st.subheader("📏 Body measurements")
            st.dataframe(body_measurements[['date', 'weight_kg', 'body_fat_percentage',
                'chest_cm', 'waist_cm', 'hips_cm', 'bicep_cm', 'thigh_cm']].head(10),
                use_container_width=True)
    else:
        st.info(t("no_biometrics", lang))

# ================================
# RECOVERY
# ================================
elif page == t("recovery", lang):
    st.title(t("recovery_title", lang))
    st.markdown("---")
    if not recovery.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("avg_sleep", lang), f"{recovery['sleep_hours'].mean():.1f}h")
        with col2:
            st.metric(t("sleep_quality", lang), f"{recovery['sleep_quality'].mean():.1f}/10")
        with col3:
            st.metric(t("avg_energy", lang), f"{recovery['energy_level'].mean():.1f}/10")
        with col4:
            st.metric(t("avg_stress", lang), f"{recovery['stress_level'].mean():.1f}/10")
        st.markdown("---")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=recovery['date'], y=recovery['sleep_hours'],
            name='Sleep (h)', mode='lines+markers', line=dict(color='#5DCAA5')))
        fig.add_trace(go.Scatter(x=recovery['date'], y=recovery['energy_level'],
            name='Energy', mode='lines+markers', line=dict(color='#378ADD')))
        fig.add_trace(go.Scatter(x=recovery['date'], y=recovery['stress_level'],
            name='Stress', mode='lines+markers', line=dict(color='#D85A30')))
        fig.update_layout(height=350, legend=dict(orientation='h'), title=t("recovery_trends", lang))
        st.plotly_chart(fig, use_container_width=True)
        avg_sleep = recovery['sleep_hours'].mean()
        avg_energy = recovery['energy_level'].mean()
        avg_stress = recovery['stress_level'].mean()
        if avg_sleep >= 7 and avg_energy >= 7 and avg_stress <= 4:
            st.success(t("recovery_optimal", lang))
        elif avg_sleep < 6:
            st.error(t("recovery_sleep_low", lang))
        elif avg_stress > 7:
            st.warning(t("recovery_stress_high", lang))
        elif avg_energy < 5:
            st.warning(t("recovery_energy_low", lang))
        else:
            st.info(t("recovery_good", lang))
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            sleep_dist = pd.cut(recovery['sleep_hours'],
                bins=[0,5,6,7,8,24],
                labels=['<5h','5-6h','6-7h','7-8h','>8h'])
            sleep_counts = sleep_dist.value_counts().reset_index()
            sleep_counts.columns = ['range', 'count']
            fig = px.pie(sleep_counts, values='count', names='range',
                title='Sleep distribution',
                color_discrete_sequence=['#D85A30','#EF9F27','#5DCAA5','#378ADD','#7F77DD'])
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.scatter(recovery, x='sleep_hours', y='energy_level',
                color='stress_level', color_continuous_scale='RdYlGn_r',
                title='Sleep vs Energy (color = stress)')
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t("no_recovery", lang))

# ================================
# NUTRITION
# ================================
elif page == t("nutrition", lang):
    st.title(t("nutrition_title", lang))
    st.markdown("---")
    if not nutrition_goals.empty:
        ng = nutrition_goals.iloc[0]
        st.subheader(t("daily_targets", lang))
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(t("calories", lang), f"{ng['calories_target']} kcal")
        with col2:
            st.metric(t("protein", lang), f"{ng['protein_target_g']}g")
        with col3:
            st.metric(t("carbs", lang), f"{ng['carbs_target_g']}g")
        with col4:
            st.metric(t("fat", lang), f"{ng['fat_target_g']}g")
        with col5:
            st.metric(t("water", lang), f"{ng['water_target_ml']} ml")
    if not meal_logs.empty:
        st.markdown("---")
        st.subheader("🍽️ Recent meals")
        today_meals = meal_logs.head(10)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(today_meals[['date', 'food_name', 'meal_type', 'amount_grams',
                'category']].rename(columns={'amount_grams': 'Amount (g)'}),
                use_container_width=True, height=300)
        with col2:
            if not meal_logs.empty:
                meal_logs['calories'] = meal_logs['amount_grams'] * meal_logs['calories_per_100g'] / 100
                cal_by_type = meal_logs.groupby('meal_type')['calories'].sum().reset_index()
                fig = px.pie(cal_by_type, values='calories', names='meal_type',
                    title='Calories by meal type',
                    color_discrete_sequence=px.colors.qualitative.Set3)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.subheader(t("food_database", lang))
    if not foods.empty:
        col1, col2 = st.columns(2)
        with col1:
            category_filter = st.selectbox(t("filter_category", lang),
                [t("all", lang)] + sorted(foods['category'].unique().tolist()))
        with col2:
            search = st.text_input("🔍 Search food", "")
        filtered = foods.copy()
        if category_filter != t("all", lang):
            filtered = filtered[filtered['category'] == category_filter]
        if search:
            filtered = filtered[filtered['name'].str.contains(search, case=False)]
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(filtered[['name', 'category', 'calories_per_100g',
                'protein_per_100g', 'carbs_per_100g', 'fat_per_100g']].rename(columns={
                'calories_per_100g': 'Cal/100g',
                'protein_per_100g': t("protein", lang),
                'carbs_per_100g': t("carbs", lang),
                'fat_per_100g': t("fat", lang)}),
                use_container_width=True, height=400)
        with col2:
            top_protein = filtered.nlargest(10, 'protein_per_100g')
            fig = px.bar(top_protein, x='protein_per_100g', y='name', orientation='h',
                color='category', title=f"Top 10 — {t('protein', lang)} per 100g")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

# ================================
# GOALS & PLANS
# ================================
elif page == t("goals_plans", lang):
    st.title(t("goals_title", lang))
    st.markdown("---")
    st.subheader(t("active_goals", lang))
    if not goals.empty:
        for _, row in goals.iterrows():
            if row['goal_type'] in ['target_weight', 'target_body_fat']:
                progress = max(0, min(100, (1 - (row['current_value'] - row['target_value']) / max(row['current_value'], 0.01)) * 100)) if row['current_value'] > row['target_value'] else 100
            else:
                progress = min(100, (row['current_value'] / row['target_value']) * 100) if row['target_value'] > 0 else 0
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{row['goal_type'].replace('_', ' ').title()}** — {row['current_value']} / {row['target_value']} {row['unit']}")
                st.progress(int(progress))
            with col2:
                st.metric(t("progress", lang), f"{progress:.0f}%")
            with col3:
                days_left = (pd.to_datetime(row['deadline']) - pd.Timestamp.now()).days
                st.metric(t("days_left", lang), max(0, days_left))
    else:
        st.info("No active goals found.")
    st.markdown("---")
    st.subheader(t("available_plans", lang))
    if not plans.empty:
        st.dataframe(plans[['name', 'goal', 'difficulty', 'duration_weeks', 'days_per_week']].rename(columns={
            'name': 'Program', 'goal': 'Goal', 'difficulty': 'Level',
            'duration_weeks': 'Weeks', 'days_per_week': 'Days/week'}),
            use_container_width=True, height=300)

# ================================
# TRAINING PROGRAMS
# ================================
elif page == t("training_programs", lang):
    st.title(t("programs_title", lang))
    st.markdown(t("programs_subtitle", lang))
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        goal_filter = st.selectbox(t("filter_goal", lang), [t("all", lang), "bygga_muskler", "gå_ner_i_vikt", "gå_upp_i_vikt", "öka_kondition", "hålla_sig_i_form", "löpning"])
    with col2:
        level_filter = st.selectbox(t("filter_level", lang), [t("all", lang), "nybörjare", "medel", "avancerad"])
    filtered_plans = plans.copy()
    if goal_filter != t("all", lang):
        filtered_plans = filtered_plans[filtered_plans['goal'] == goal_filter]
    if level_filter != t("all", lang):
        filtered_plans = filtered_plans[filtered_plans['difficulty'] == level_filter]
    st.markdown(f"**{len(filtered_plans)} {t('programs_found', lang)}**")
    st.markdown("---")
    goal_labels = {
        'bygga_muskler': 'Build Muscle', 'gå_ner_i_vikt': 'Lose Weight',
        'gå_upp_i_vikt': 'Gain Weight', 'löpning': 'Running',
        'hålla_sig_i_form': 'Stay Fit', 'öka_kondition': 'Improve Cardio'
    }
    cols = st.columns(3)
    for i, (_, plan) in enumerate(filtered_plans.iterrows()):
        with cols[i % 3]:
            color = goal_colors.get(plan['goal'], '#378ADD')
            goal_label = goal_labels.get(plan['goal'], plan['goal'])
            weeks = f"{plan['duration_weeks']} {t('weeks', lang)}" if plan['duration_weeks'] > 0 else "Ongoing"
            level_badge = {'nybörjare': 'Beginner', 'medel': 'Intermediate', 'avancerad': 'Advanced'}.get(plan['difficulty'], plan['difficulty'])
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 14px;
                margin-bottom: 16px; background: #f8f9fa; border-radius: 8px;">
                <strong style="font-size: 15px;">{plan['name']}</strong><br><br>
                <span style="background: {color}; color: white; padding: 2px 8px;
                    border-radius: 4px; font-size: 11px;">{goal_label}</span>
                <span style="background: #888; color: white; padding: 2px 8px;
                    border-radius: 4px; font-size: 11px; margin-left: 4px;">{level_badge}</span>
                <br><br>
                <span style="color: #555; font-size: 13px;">
                {weeks} — {plan['days_per_week']}{t('per_week', lang)}<br><br>
                {plan['description']}<br><br>
                <em>{t('for', lang)}: {plan['target_audience']}</em>
                </span>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    overview = plans.groupby(['goal', 'difficulty']).size().reset_index(name='count')
    fig = px.bar(overview, x='goal', y='count', color='difficulty',
        color_discrete_map={'nybörjare': '#5DCAA5', 'medel': '#378ADD', 'avancerad': '#D85A30'},
        title=t("program_overview", lang))
    fig.update_layout(height=300, xaxis_tickangle=-20)
    st.plotly_chart(fig, use_container_width=True)

# ================================
# SOCIAL & CHALLENGES
# ================================
elif page == t("social_challenges", lang):
    st.title(t("social_challenges", lang))
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Active challenges")
        if not challenges.empty:
            for _, c in challenges.iterrows():
                days_left = (pd.to_datetime(c['end_date']) - pd.Timestamp.now()).days
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <strong>{c['name']}</strong><br>
                    <span style="color: #555; font-size: 13px;">
                    {c['description']}<br>
                    Type: {c['challenge_type'].replace('_', ' ')}<br>
                    {t('days_left', lang)}: {max(0, days_left)}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active challenges.")
    with col2:
        st.subheader("🥇 Leaderboard")
        if not leaderboard.empty:
            lb = leaderboard[['name', 'total_sessions', 'total_volume_kg', 'total_steps', 'points']].copy()
            lb = lb.sort_values('points', ascending=False).reset_index(drop=True)
            lb.index += 1
            lb.columns = ['User', t('sessions', lang), 'Volume (kg)', t('total_steps', lang), 'Points']
            st.dataframe(lb, use_container_width=True)
    if not activity_feed.empty:
        st.markdown("---")
        st.subheader("📢 Activity Feed")
        for _, act in activity_feed.head(10).iterrows():
            st.info(f"**{act['user_name']}** — {act['activity_type']}: {act['description']}")

# ================================
# ACHIEVEMENTS
# ================================
elif page == t("achievements", lang):
    st.title(t("achievements_title", lang))
    st.markdown(t("achievements_subtitle", lang))
    st.markdown("---")
    if not streaks.empty:
        s = streaks.iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(t("current_streak", lang), f"{s['current_streak']} {t('days', lang)}")
        with col2:
            st.metric(t("best_streak", lang), f"{s['longest_streak']} {t('days', lang)}")
        with col3:
            st.metric(t("total_workouts", lang), s['total_workouts'])
    st.markdown("---")
    if not achievements.empty:
        st.subheader(f"{len(achievements)} {t('achievements_unlocked', lang)}")
        cols = st.columns(3)
        for i, (_, ach) in enumerate(achievements.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #378ADD; border-radius: 8px;
                    padding: 14px; margin-bottom: 12px; background: #f0f7ff;">
                    <strong style="font-size: 15px;">🏆 {ach['achievement_name']}</strong><br><br>
                    <span style="color: #555; font-size: 13px;">{ach['description']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info(t("no_achievements", lang))

# ================================
# HEALTH CALCULATOR
# ================================
elif page == t("health_calculator", lang):
    st.title(t("calculator_title", lang))
    st.markdown(t("calculator_subtitle", lang))
    st.markdown("---")
    if not health_calc.empty:
        hc = health_calc.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("BMI", f"{hc['bmi']:.1f}")
            if 18.5 <= hc['bmi'] <= 24.9:
                st.success(f"Category: {hc['bmi_category']}")
            elif hc['bmi'] <= 29.9:
                st.warning(f"Category: {hc['bmi_category']}")
            else:
                st.error(f"Category: {hc['bmi_category']}")
        with col2:
            st.metric(t("bmr", lang), f"{hc['bmr']:,.0f} kcal")
        with col3:
            st.metric(t("tdee", lang), f"{hc['tdee']:,.0f} kcal")
        with col4:
            st.metric(t("daily_calories", lang), f"{hc['calories_target']:,} kcal")
        st.markdown("---")
        st.subheader(t("macro_targets", lang))
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=float(hc['protein_target_g']),
                title={'text': f"{t('protein', lang)} (g)"},
                gauge={'axis': {'range': [0, 300]}, 'bar': {'color': '#378ADD'}}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=float(hc['carbs_target_g']),
                title={'text': f"{t('carbs', lang)} (g)"},
                gauge={'axis': {'range': [0, 500]}, 'bar': {'color': '#EF9F27'}}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig = go.Figure(go.Indicator(mode="gauge+number", value=float(hc['fat_target_g']),
                title={'text': f"{t('fat', lang)} (g)"},
                gauge={'axis': {'range': [0, 200]}, 'bar': {'color': '#D85A30'}}))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    st.subheader(t("calculate_own", lang))
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input(t("weight_kg", lang), value=80.0, step=0.5)
        height = st.number_input(t("height_cm", lang), value=180.0, step=0.5)
        age = st.number_input(t("age", lang), value=25, step=1)
    with col2:
        gender = st.selectbox(t("gender", lang), [t("male", lang), t("female", lang)])
        activity = st.selectbox(t("activity_level", lang), ["sedentary", "lightly_active", "moderately_active", "very_active", "super_active"])
        goal = st.selectbox(t("goal", lang), ["lose_weight", "maintain", "gain_weight", "build_muscle"])
    if st.button(t("calculate", lang)):
        bmi = weight / ((height / 100) ** 2)
        bmr = 10 * weight + 6.25 * height - 5 * age + (5 if gender == t("male", lang) else -161)
        multipliers = {"sedentary": 1.2, "lightly_active": 1.375, "moderately_active": 1.55, "very_active": 1.725, "super_active": 1.9}
        tdee = bmr * multipliers[activity]
        calories = tdee - 500 if goal == "lose_weight" else tdee + 300 if goal in ["gain_weight", "build_muscle"] else tdee
        protein = weight * 2.0
        fat = calories * 0.25 / 9
        carbs = (calories - protein * 4 - fat * 9) / 4
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("BMI", f"{bmi:.1f}")
        with col2:
            st.metric(t("bmr", lang), f"{bmr:,.0f} kcal")
        with col3:
            st.metric(t("tdee", lang), f"{tdee:,.0f} kcal")
        with col4:
            st.metric(t("daily_calories", lang), f"{calories:,.0f} kcal")
        st.success(f"{t('protein', lang)}: {protein:.0f}g | {t('carbs', lang)}: {carbs:.0f}g | {t('fat', lang)}: {fat:.0f}g")

# ================================
# AI INSIGHTS
# ================================
elif page == t("ai_insights", lang):
    st.title(t("insights_title", lang))
    st.markdown(t("insights_subtitle", lang))
    st.markdown("---")
    if not ai_insights.empty:
        for _, insight in ai_insights.iterrows():
            if insight['insight_type'] in ['recovery_advice', 'progress_summary']:
                st.success(f"**{insight['title']}**\n\n{insight['content']}")
            elif insight['insight_type'] in ['training_tip', 'weekly_analysis']:
                st.info(f"**{insight['title']}**\n\n{insight['content']}")
            else:
                st.warning(f"**{insight['title']}**\n\n{insight['content']}")
    else:
        st.info(t("no_insights", lang))

# ================================
# RECOMMENDATIONS
# ================================
elif page == t("recommendations", lang):
    st.title(t("recs_title", lang))
    st.markdown(t("recs_subtitle", lang))
    st.markdown("---")
    if not recommendations.empty:
        st.subheader(f"{len(recommendations)} {t('recs_count', lang)}")
        for _, row in recommendations.iterrows():
            score = row['score']
            if score >= 0.8:
                st.error(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
            elif score >= 0.5:
                st.warning(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
            else:
                st.info(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
    else:
        st.success(t("no_recs", lang))
