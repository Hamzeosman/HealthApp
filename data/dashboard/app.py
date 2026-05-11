import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
engine = create_engine(os.getenv("DATABASE_URL"))

st.set_page_config(
    page_title="HealthApp Dashboard",
    page_icon="🏋️",
    layout="wide"
)

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
        goals = pd.read_sql(text("SELECT * FROM user_goals"), conn)
        plans = pd.read_sql(text("SELECT * FROM training_plans"), conn)
        measurements = pd.read_sql(text("SELECT * FROM body_measurements ORDER BY date"), conn)
        users = pd.read_sql(text("SELECT id, name FROM users"), conn)
        foods = pd.read_sql(text("SELECT * FROM foods"), conn)
        nutrition_goals = pd.read_sql(text("SELECT * FROM nutrition_goals"), conn)
        challenges = pd.read_sql(text("SELECT * FROM challenges"), conn)
        leaderboard = pd.read_sql(text("SELECT l.*, u.name FROM leaderboard l JOIN users u ON l.user_id = u.id ORDER BY points DESC"), conn)
        ai_insights = pd.read_sql(text("SELECT * FROM ai_insights ORDER BY created_at DESC"), conn)
        streaks = pd.read_sql(text("SELECT us.*, u.name FROM user_streaks us JOIN users u ON us.user_id = u.id"), conn)
        achievements = pd.read_sql(text("""
            SELECT ua.*, a.name AS achievement_name, a.description, a.requirement_type
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.id
        """), conn)
        notifications = pd.read_sql(text("SELECT * FROM notifications ORDER BY created_at DESC"), conn)
        health_calc = pd.read_sql(text("SELECT * FROM health_calculations ORDER BY date DESC"), conn)
    return (sessions, exercises, records, recovery, recommendations,
            biometrics, running, goals, plans, measurements, users,
            foods, nutrition_goals, challenges, leaderboard, ai_insights,
            streaks, achievements, notifications, health_calc)

(sessions, exercises, records, recovery, recommendations,
 biometrics, running, goals, plans, measurements, users,
 foods, nutrition_goals, challenges, leaderboard, ai_insights,
 streaks, achievements, notifications, health_calc) = load_data()

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.title("HealthApp")
    st.markdown("---")

    user_options = ["All users"] + users['name'].tolist()
    selected_user = st.selectbox("Select user", user_options)

    if selected_user != "All users":
        user_id = users[users['name'] == selected_user]['id'].values[0]
        sessions = sessions[sessions['user_id'] == user_id]
        exercises = exercises[exercises['user_id'] == user_id]
        recovery = recovery[recovery['user_id'] == user_id]
        biometrics = biometrics[biometrics['user_id'] == user_id]
        running = running[running['user_id'] == user_id]
        goals = goals[goals['user_id'] == user_id]
        recommendations = recommendations[recommendations['user_id'] == user_id]
        measurements = measurements[measurements['user_id'] == user_id]
        nutrition_goals = nutrition_goals[nutrition_goals['user_id'] == user_id]
        ai_insights = ai_insights[ai_insights['user_id'] == user_id]
        streaks = streaks[streaks['user_id'] == user_id]
        achievements = achievements[achievements['user_id'] == user_id]
        notifications = notifications[notifications['user_id'] == user_id]
        health_calc = health_calc[health_calc['user_id'] == user_id]

    st.markdown("---")

    # Streak i sidebar
    if not streaks.empty:
        s = streaks.iloc[0]
        st.metric("Current streak", f"{s['current_streak']} days")
        st.metric("Best streak", f"{s['longest_streak']} days")
        st.metric("Total sessions", s['total_workouts'])

    st.markdown("---")

    # Notifikationer i sidebar
    unread = notifications[notifications['is_read'] == False] if not notifications.empty else pd.DataFrame()
    if not unread.empty:
        st.markdown(f"**{len(unread)} unread notifications**")
        for _, n in unread.head(3).iterrows():
            st.warning(f"{n['title']}")

    st.markdown("---")
    page = st.radio("Navigation", [
        "Overview",
        "Training",
        "Running",
        "Biometrics",
        "Recovery",
        "Nutrition",
        "Goals & Plans",
        "Social & Challenges",
        "Achievements",
        "Health Calculator",
        "AI Insights",
        "Recommendations"
    ])
    st.markdown("---")
    st.caption("Data Engineer: Abdulrahman Fahmi")

# ================================
# OVERVIEW
# ================================
if page == "Overview":
    st.title("Overview")
    st.markdown("Your complete health and training summary at a glance.")
    st.markdown("---")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Sessions", len(sessions))
    with col2:
        total_vol = (exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)).sum()
        st.metric("Total Volume", f"{total_vol:,.0f} kg")
    with col3:
        avg_rpe = exercises['rpe'].mean() if not exercises.empty else 0
        st.metric("Avg RPE", f"{avg_rpe:.1f}/10")
    with col4:
        st.metric("PRs", len(records))
    with col5:
        avg_sleep = recovery['sleep_hours'].mean() if not recovery.empty else 0
        st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
    with col6:
        total_steps = int(biometrics['steps'].sum()) if not biometrics.empty else 0
        st.metric("Total Steps", f"{total_steps:,}")

    st.markdown("---")
    st.subheader("Health status today")
    col1, col2, col3 = st.columns(3)

    with col1:
        if not recovery.empty:
            avg_sleep = recovery['sleep_hours'].mean()
            if avg_sleep >= 7:
                st.success(f"Sleep: {avg_sleep:.1f}h — Optimal")
            elif avg_sleep >= 6:
                st.warning(f"Sleep: {avg_sleep:.1f}h — Could be better")
            else:
                st.error(f"Sleep: {avg_sleep:.1f}h — Too little!")
    with col2:
        if not recovery.empty:
            avg_stress = recovery['stress_level'].mean()
            if avg_stress <= 4:
                st.success(f"Stress: {avg_stress:.1f}/10 — Low")
            elif avg_stress <= 7:
                st.warning(f"Stress: {avg_stress:.1f}/10 — Moderate")
            else:
                st.error(f"Stress: {avg_stress:.1f}/10 — High!")
    with col3:
        if not exercises.empty:
            avg_rpe = exercises['rpe'].mean()
            if avg_rpe <= 7:
                st.success(f"Training load: {avg_rpe:.1f}/10 — Balanced")
            elif avg_rpe <= 8.5:
                st.warning(f"Training load: {avg_rpe:.1f}/10 — Hard")
            else:
                st.error(f"Training load: {avg_rpe:.1f}/10 — Very hard!")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Most trained muscle groups")
        if not exercises.empty:
            body_counts = exercises.groupby('body_part').size().reset_index(name='count')
            body_counts = body_counts.sort_values('count', ascending=True)
            fig = px.bar(body_counts, x='count', y='body_part', orientation='h',
                color='count', color_continuous_scale='Blues',
                labels={'count': 'Exercises', 'body_part': 'Muscle group'})
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=280)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Weekly volume trend")
        if not exercises.empty:
            exercises['week'] = pd.to_datetime(exercises['date']).dt.strftime('%Y-W%W')
            exercises['volume'] = exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)
            weekly_vol = exercises.groupby('week')['volume'].sum().reset_index()
            fig = px.bar(weekly_vol, x='week', y='volume',
                color_discrete_sequence=['#378ADD'],
                labels={'week': 'Week', 'volume': 'Volume (kg)'})
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)

# ================================
# TRAINING
# ================================
elif page == "Training":
    st.title("Training Analysis")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total sessions", len(sessions))
    with col2:
        total_vol = (exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)).sum()
        st.metric("Total volume", f"{total_vol:,.0f} kg")
    with col3:
        st.metric("Personal records", len(records))
    with col4:
        avg_rpe = exercises['rpe'].mean() if not exercises.empty else 0
        st.metric("Avg RPE", f"{avg_rpe:.1f}/10")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Volume per week")
        if not exercises.empty:
            exercises['week'] = pd.to_datetime(exercises['date']).dt.strftime('%Y-W%W')
            exercises['volume'] = exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)
            weekly_vol = exercises.groupby('week')['volume'].sum().reset_index()
            fig = px.bar(weekly_vol, x='week', y='volume',
                color_discrete_sequence=['#378ADD'],
                labels={'week': 'Week', 'volume': 'Volume (kg)'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Top exercises by RPE")
        if not exercises.empty:
            top = exercises.groupby('exercise_name')['rpe'].mean().reset_index()
            top = top.sort_values('rpe', ascending=True).tail(8)
            fig = px.bar(top, x='rpe', y='exercise_name', orientation='h',
                color='rpe', color_continuous_scale='Reds',
                labels={'rpe': 'Avg RPE', 'exercise_name': 'Exercise'})
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Personal records")
    if not records.empty:
        fig = px.bar(records.sort_values('weight_kg', ascending=True),
            x='weight_kg', y='exercise_name', orientation='h',
            color='weight_kg', color_continuous_scale='Greens',
            labels={'weight_kg': 'Weight (kg)', 'exercise_name': 'Exercise'})
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

# ================================
# RUNNING
# ================================
elif page == "Running":
    st.title("Running")
    st.markdown("---")

    if not running.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total runs", len(running))
        with col2:
            st.metric("Total distance", f"{running['distance_km'].sum():.1f} km")
        with col3:
            st.metric("Avg pace", f"{running['avg_pace_min_per_km'].mean():.1f} min/km")
        with col4:
            st.metric("Avg heart rate", f"{running['avg_heart_rate'].mean():.0f} bpm")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(running, x='date', y='distance_km',
                color_discrete_sequence=['#1D9E75'],
                labels={'distance_km': 'Distance (km)', 'date': 'Date'},
                title='Distance per run')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(running, x='date', y='avg_pace_min_per_km',
                markers=True, color_discrete_sequence=['#D85A30'],
                labels={'avg_pace_min_per_km': 'Pace (min/km)', 'date': 'Date'},
                title='Pace improvement over time')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Session details")
        st.dataframe(running[['date', 'distance_km', 'duration_minutes',
            'avg_pace_min_per_km', 'avg_heart_rate', 'calories_burned', 'route_type']],
            use_container_width=True)
    else:
        st.info("No running sessions logged yet.")

# ================================
# BIOMETRICS
# ================================
elif page == "Biometrics":
    st.title("Biometrics")
    st.markdown("---")

    if not biometrics.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg daily steps", f"{biometrics['steps'].mean():,.0f}")
        with col2:
            st.metric("Avg resting HR", f"{biometrics['heart_rate_resting'].mean():.0f} bpm")
        with col3:
            st.metric("Avg calories", f"{biometrics['calories_burned'].mean():,.0f} kcal")
        with col4:
            st.metric("Avg active min", f"{biometrics['active_minutes'].mean():.0f} min")

        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = px.bar(biometrics, x='date', y='steps',
                color_discrete_sequence=['#378ADD'], title='Daily steps',
                labels={'steps': 'Steps', 'date': 'Date'})
            fig.add_hline(y=10000, line_dash="dash", line_color="green",
                annotation_text="Goal: 10,000")
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(biometrics, x='date',
                y=['heart_rate_resting', 'heart_rate_avg'],
                title='Heart rate', labels={'value': 'BPM', 'date': 'Date'},
                color_discrete_sequence=['#5DCAA5', '#D85A30'])
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig = px.bar(biometrics, x='date', y='calories_burned',
                color_discrete_sequence=['#EF9F27'], title='Calories burned',
                labels={'calories_burned': 'Calories', 'date': 'Date'})
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No biometric data logged yet.")

# ================================
# RECOVERY
# ================================
elif page == "Recovery":
    st.title("Recovery & Sleep")
    st.markdown("---")

    if not recovery.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg sleep", f"{recovery['sleep_hours'].mean():.1f}h")
        with col2:
            st.metric("Sleep quality", f"{recovery['sleep_quality'].mean():.1f}/10")
        with col3:
            st.metric("Avg energy", f"{recovery['energy_level'].mean():.1f}/10")
        with col4:
            st.metric("Avg stress", f"{recovery['stress_level'].mean():.1f}/10")

        st.markdown("---")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=recovery['date'], y=recovery['sleep_hours'],
            name='Sleep (h)', mode='lines+markers', line=dict(color='#5DCAA5')))
        fig.add_trace(go.Scatter(x=recovery['date'], y=recovery['energy_level'],
            name='Energy', mode='lines+markers', line=dict(color='#378ADD')))
        fig.add_trace(go.Scatter(x=recovery['date'], y=recovery['stress_level'],
            name='Stress', mode='lines+markers', line=dict(color='#D85A30')))
        fig.update_layout(height=350, legend=dict(orientation='h'),
            title='Recovery trends over time')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recovery status")
        avg_sleep = recovery['sleep_hours'].mean()
        avg_energy = recovery['energy_level'].mean()
        avg_stress = recovery['stress_level'].mean()

        if avg_sleep >= 7 and avg_energy >= 7 and avg_stress <= 4:
            st.success("OPTIMAL — Your body is fully recovered and ready to perform!")
        elif avg_sleep < 6:
            st.error("WARNING — Too little sleep! Aim for 7-9 hours.")
        elif avg_stress > 7:
            st.warning("WARNING — High stress! Consider a deload week.")
        elif avg_energy < 5:
            st.warning("WARNING — Low energy! Prioritize rest and nutrition.")
        else:
            st.info("GOOD — Keep up the great work!")
    else:
        st.info("No recovery data logged yet.")

# ================================
# NUTRITION
# ================================
elif page == "Nutrition":
    st.title("Nutrition")
    st.markdown("---")

    if not nutrition_goals.empty:
        ng = nutrition_goals.iloc[0]
        st.subheader("Daily nutrition targets")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Calories", f"{ng['calories_target']} kcal")
        with col2:
            st.metric("Protein", f"{ng['protein_target_g']}g")
        with col3:
            st.metric("Carbs", f"{ng['carbs_target_g']}g")
        with col4:
            st.metric("Fat", f"{ng['fat_target_g']}g")
        with col5:
            st.metric("Water", f"{ng['water_target_ml']} ml")

    st.markdown("---")
    st.subheader("Food database")
    if not foods.empty:
        category_filter = st.selectbox("Filter by category",
            ["All"] + foods['category'].unique().tolist())
        filtered = foods if category_filter == "All" else foods[foods['category'] == category_filter]

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(filtered[['name', 'category', 'calories_per_100g',
                'protein_per_100g', 'carbs_per_100g', 'fat_per_100g']].rename(columns={
                'calories_per_100g': 'Cal/100g', 'protein_per_100g': 'Protein',
                'carbs_per_100g': 'Carbs', 'fat_per_100g': 'Fat'
            }), use_container_width=True, height=400)
        with col2:
            fig = px.bar(filtered, x='name', y='protein_per_100g',
                color='category', title='Protein per 100g',
                labels={'protein_per_100g': 'Protein (g)', 'name': 'Food'})
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

# ================================
# GOALS & PLANS
# ================================
elif page == "Goals & Plans":
    st.title("Goals & Training Plans")
    st.markdown("---")

    st.subheader("Your active goals")
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
                st.metric("Progress", f"{progress:.0f}%")
            with col3:
                days_left = (pd.to_datetime(row['deadline']) - pd.Timestamp.now()).days
                st.metric("Days left", max(0, days_left))

    st.markdown("---")
    st.subheader("Available training plans")
    goal_colors = {
        'bygga_muskler': '#378ADD', 'gå_ner_i_vikt': '#D85A30',
        'gå_upp_i_vikt': '#1D9E75', 'löpning': '#EF9F27', 'hålla_sig_i_form': '#7F77DD'
    }
    cols = st.columns(3)
    for i, (_, plan) in enumerate(plans.iterrows()):
        with cols[i % 3]:
            color = goal_colors.get(plan['goal'], '#378ADD')
            weeks = f"{plan['duration_weeks']} weeks" if plan['duration_weeks'] > 0 else "Ongoing"
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 12px;
                margin-bottom: 12px; background: #f8f9fa; border-radius: 8px;">
                <strong>{plan['name']}</strong><br>
                <span style="color: #555; font-size: 13px;">
                Goal: {plan['goal'].replace('_', ' ')}<br>
                {weeks} — {plan['days_per_week']}x/week<br>
                Level: {plan['difficulty']}<br><br>
                {plan['description']}
                </span>
            </div>
            """, unsafe_allow_html=True)

# ================================
# SOCIAL & CHALLENGES
# ================================
elif page == "Social & Challenges":
    st.title("Social & Challenges")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Active challenges")
        if not challenges.empty:
            for _, c in challenges.iterrows():
                days_left = (pd.to_datetime(c['end_date']) - pd.Timestamp.now()).days
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <strong>{c['name']}</strong><br>
                    <span style="color: #555; font-size: 13px;">
                    {c['description']}<br>
                    Type: {c['challenge_type'].replace('_', ' ')}<br>
                    Days left: {max(0, days_left)}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        st.subheader("Leaderboard this week")
        if not leaderboard.empty:
            lb = leaderboard[['name', 'total_sessions', 'total_volume_kg', 'total_steps', 'points']].copy()
            lb = lb.sort_values('points', ascending=False).reset_index(drop=True)
            lb.index += 1
            lb.columns = ['User', 'Sessions', 'Volume (kg)', 'Steps', 'Points']
            st.dataframe(lb, use_container_width=True)

# ================================
# ACHIEVEMENTS
# ================================
elif page == "Achievements":
    st.title("Achievements")
    st.markdown("Badges and milestones you have unlocked.")
    st.markdown("---")

    if not streaks.empty:
        s = streaks.iloc[0]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current streak", f"{s['current_streak']} days")
        with col2:
            st.metric("Best streak", f"{s['longest_streak']} days")
        with col3:
            st.metric("Total workouts", s['total_workouts'])

    st.markdown("---")
    if not achievements.empty:
        st.subheader(f"{len(achievements)} achievements unlocked!")
        cols = st.columns(3)
        for i, (_, ach) in enumerate(achievements.iterrows()):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #378ADD; border-radius: 8px;
                    padding: 12px; margin-bottom: 12px; background: #f0f7ff;">
                    <strong>{ach['achievement_name']}</strong><br>
                    <span style="color: #555; font-size: 13px;">{ach['description']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No achievements unlocked yet. Start training to earn badges!")

# ================================
# HEALTH CALCULATOR
# ================================
elif page == "Health Calculator":
    st.title("Health Calculator")
    st.markdown("Calculate your BMI, BMR, TDEE and macro targets.")
    st.markdown("---")

    if not health_calc.empty:
        hc = health_calc.iloc[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            bmi_color = "success" if 18.5 <= hc['bmi'] <= 24.9 else "warning" if hc['bmi'] < 18.5 or hc['bmi'] <= 29.9 else "error"
            st.metric("BMI", f"{hc['bmi']:.1f}")
            if bmi_color == "success":
                st.success(f"Category: {hc['bmi_category']}")
            elif bmi_color == "warning":
                st.warning(f"Category: {hc['bmi_category']}")
            else:
                st.error(f"Category: {hc['bmi_category']}")
        with col2:
            st.metric("BMR", f"{hc['bmr']:,.0f} kcal")
            st.caption("Calories at complete rest")
        with col3:
            st.metric("TDEE", f"{hc['tdee']:,.0f} kcal")
            st.caption(f"Activity: {hc['activity_level'].replace('_', ' ')}")
        with col4:
            st.metric("Daily calories", f"{hc['calories_target']:,} kcal")
            st.caption("Based on your goal")

        st.markdown("---")
        st.subheader("Daily macro targets")
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(hc['protein_target_g']),
                title={'text': "Protein (g)"},
                gauge={'axis': {'range': [0, 300]}, 'bar': {'color': '#378ADD'}}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(hc['carbs_target_g']),
                title={'text': "Carbs (g)"},
                gauge={'axis': {'range': [0, 500]}, 'bar': {'color': '#EF9F27'}}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(hc['fat_target_g']),
                title={'text': "Fat (g)"},
                gauge={'axis': {'range': [0, 200]}, 'bar': {'color': '#D85A30'}}
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Calculate your own")
        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", value=80.0, step=0.5)
            height = st.number_input("Height (cm)", value=180.0, step=0.5)
            age = st.number_input("Age", value=25, step=1)
        with col2:
            gender = st.selectbox("Gender", ["male", "female"])
            activity = st.selectbox("Activity level", [
                "sedentary", "lightly_active", "moderately_active",
                "very_active", "super_active"
            ])
            goal = st.selectbox("Goal", [
                "lose_weight", "maintain", "gain_weight", "build_muscle"
            ])

        if st.button("Calculate"):
            bmi = weight / ((height / 100) ** 2)
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161

            multipliers = {
                "sedentary": 1.2, "lightly_active": 1.375,
                "moderately_active": 1.55, "very_active": 1.725, "super_active": 1.9
            }
            tdee = bmr * multipliers[activity]

            if goal == "lose_weight":
                calories = tdee - 500
            elif goal == "gain_weight" or goal == "build_muscle":
                calories = tdee + 300
            else:
                calories = tdee

            protein = weight * 2.0
            fat = calories * 0.25 / 9
            carbs = (calories - protein * 4 - fat * 9) / 4

            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("BMI", f"{bmi:.1f}")
            with col2:
                st.metric("BMR", f"{bmr:,.0f} kcal")
            with col3:
                st.metric("TDEE", f"{tdee:,.0f} kcal")
            with col4:
                st.metric("Daily calories", f"{calories:,.0f} kcal")

            st.success(f"Protein: {protein:.0f}g | Carbs: {carbs:.0f}g | Fat: {fat:.0f}g")
    else:
        st.info("No health calculation data found.")

# ================================
# AI INSIGHTS
# ================================
elif page == "AI Insights":
    st.title("AI Insights")
    st.markdown("Smart insights generated from your training data.")
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
        st.info("No AI insights yet. Run the pipelines to generate insights!")

# ================================
# RECOMMENDATIONS
# ================================
elif page == "Recommendations":
    st.title("Smart Recommendations")
    st.markdown("Personalized exercise recommendations based on your training history.")
    st.markdown("---")

    if not recommendations.empty:
        st.subheader(f"{len(recommendations)} recommendations for you")
        for _, row in recommendations.iterrows():
            score = row['score']
            if score >= 0.8:
                st.error(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
            elif score >= 0.5:
                st.warning(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
            else:
                st.info(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
    else:
        st.success("All muscle groups have been trained recently. Great work!")