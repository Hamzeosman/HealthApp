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

st.markdown("""
<style>
.metric-card {
    background: #f8f9fa;
    border-radius: 12px;
    padding: 1rem;
    border-left: 4px solid #378ADD;
}
.section-header {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    with engine.connect() as conn:
        sessions = pd.read_sql(text("""
            SELECT ws.*, u.name AS user_name
            FROM workout_sessions ws
            JOIN users u ON ws.user_id = u.id
        """), conn)
        exercises = pd.read_sql(text("""
            SELECT we.*, e.name AS exercise_name,
                bp.name AS body_part, e.difficulty,
                e.calories_per_minute, ws.date, ws.user_id
            FROM workout_exercises we
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            JOIN workout_sessions ws ON we.session_id = ws.id
        """), conn)
        records = pd.read_sql(text("""
            SELECT pr.*, e.name AS exercise_name
            FROM personal_records pr
            JOIN exercises e ON pr.exercise_id = e.id
        """), conn)
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
    return sessions, exercises, records, recovery, recommendations, biometrics, running, goals, plans, measurements, users

sessions, exercises, records, recovery, recommendations, biometrics, running, goals, plans, measurements, users = load_data()

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2964/2964514.png", width=80)
    st.title("HealthApp")
    st.markdown("---")

    st.subheader("Filter")
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

    st.markdown("---")
    st.subheader("Navigation")
    page = st.radio("Go to", [
        "Overview",
        "Training",
        "Running",
        "Biometrics",
        "Recovery",
        "Goals & Plans",
        "Recommendations"
    ])

    st.markdown("---")
    st.caption("Data Engineer: Abdulrahman Fahmi")

# ================================
# OVERVIEW PAGE
# ================================
if page == "Overview":
    st.title("Overview")
    st.markdown("A complete summary of your health and training data.")
    st.markdown("---")

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Training Sessions", len(sessions), help="Total number of logged sessions")
    with col2:
        total_vol = (exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)).sum()
        st.metric("Total Volume", f"{total_vol:,.0f} kg", help="Total kg lifted")
    with col3:
        avg_rpe = exercises['rpe'].mean() if not exercises.empty else 0
        st.metric("Avg RPE", f"{avg_rpe:.1f}/10", help="Average effort level")
    with col4:
        st.metric("Personal Records", len(records), help="Total personal bests")
    with col5:
        avg_sleep = recovery['sleep_hours'].mean() if not recovery.empty else 0
        st.metric("Avg Sleep", f"{avg_sleep:.1f}h", help="Average hours of sleep")
    with col6:
        total_steps = int(biometrics['steps'].sum()) if not biometrics.empty else 0
        st.metric("Total Steps", f"{total_steps:,}", help="Total steps logged")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Most trained muscle groups")
        if not exercises.empty:
            body_counts = exercises.groupby('body_part').size().reset_index(name='Antal')
            body_counts = body_counts.sort_values('Antal', ascending=True)
            fig = px.bar(body_counts, x='Antal', y='body_part', orientation='h',
                color='Antal', color_continuous_scale='Blues',
                labels={'Antal': 'Number of exercises', 'body_part': 'Muscle group'})
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Difficulty level distribution")
        if not exercises.empty:
            diff_counts = exercises.groupby('difficulty').size().reset_index(name='Antal')
            fig = px.pie(diff_counts, values='Antal', names='difficulty',
                color_discrete_sequence=['#5DCAA5', '#378ADD', '#D85A30'], hole=0.4)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

# ================================
# TRAINING PAGE
# ================================
elif page == "Training":
    st.title("Training Analysis")
    st.markdown("Weekly volume, top exercises and personal records.")
    st.markdown("---")

    st.subheader("Training volume per week (kg)")
    if not exercises.empty:
        exercises['week'] = pd.to_datetime(exercises['date']).dt.strftime('%Y-W%W')
        exercises['volume'] = exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)
        weekly_vol = exercises.groupby('week')['volume'].sum().reset_index()
        fig = px.bar(weekly_vol, x='week', y='volume',
            color_discrete_sequence=['#378ADD'],
            labels={'week': 'Week', 'volume': 'Volume (kg)'})
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top exercises by effort (RPE)")
        if not exercises.empty:
            top = exercises.groupby('exercise_name')['rpe'].mean().reset_index()
            top = top.sort_values('rpe', ascending=True).tail(8)
            fig = px.bar(top, x='rpe', y='exercise_name', orientation='h',
                color='rpe', color_continuous_scale='Reds',
                labels={'rpe': 'Avg RPE', 'exercise_name': 'Exercise'})
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Personal records")
        if not records.empty:
            fig = px.bar(records.sort_values('weight_kg', ascending=True),
                x='weight_kg', y='exercise_name', orientation='h',
                color='weight_kg', color_continuous_scale='Greens',
                labels={'weight_kg': 'Weight (kg)', 'exercise_name': 'Exercise'})
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

# ================================
# RUNNING PAGE
# ================================
elif page == "Running":
    st.title("Running")
    st.markdown("Distance, pace and heart rate from your running sessions.")
    st.markdown("---")

    if not running.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total runs", len(running))
        with col2:
            st.metric("Total distance", f"{running['distance_km'].sum():.1f} km")
        with col3:
            st.metric("Avg pace", f"{running['avg_pace_min_per_km'].mean():.1f} min/km")

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
                title='Pace over time')
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No running sessions logged yet.")

# ================================
# BIOMETRICS PAGE
# ================================
elif page == "Biometrics":
    st.title("Biometrics")
    st.markdown("Daily steps, heart rate and calories burned.")
    st.markdown("---")

    if not biometrics.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = px.bar(biometrics, x='date', y='steps',
                color_discrete_sequence=['#378ADD'],
                labels={'steps': 'Steps', 'date': 'Date'},
                title='Daily steps')
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.line(biometrics, x='date',
                y=['heart_rate_resting', 'heart_rate_avg'],
                labels={'value': 'BPM', 'date': 'Date'},
                title='Heart rate',
                color_discrete_sequence=['#5DCAA5', '#D85A30'])
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)

        with col3:
            fig = px.bar(biometrics, x='date', y='calories_burned',
                color_discrete_sequence=['#EF9F27'],
                labels={'calories_burned': 'Calories', 'date': 'Date'},
                title='Calories burned')
            fig.update_layout(height=280)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No biometric data logged yet.")

# ================================
# RECOVERY PAGE
# ================================
elif page == "Recovery":
    st.title("Recovery & Sleep")
    st.markdown("Sleep quality, energy levels and stress over time.")
    st.markdown("---")

    if not recovery.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg sleep", f"{recovery['sleep_hours'].mean():.1f}h")
        with col2:
            st.metric("Avg energy", f"{recovery['energy_level'].mean():.1f}/10")
        with col3:
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

        st.markdown("---")
        st.subheader("Recovery status")
        avg_sleep = recovery['sleep_hours'].mean()
        avg_energy = recovery['energy_level'].mean()
        avg_stress = recovery['stress_level'].mean()

        if avg_sleep >= 7 and avg_energy >= 7:
            st.success("OPTIMAL — Your body is ready to perform at its best!")
        elif avg_sleep < 6:
            st.error("WARNING — Too little sleep! Aim for 7-9 hours for optimal recovery.")
        elif avg_stress > 7:
            st.warning("WARNING — High stress levels! Consider lighter training this week.")
        elif avg_energy < 5:
            st.warning("WARNING — Low energy! Prioritize rest and recovery.")
        else:
            st.info("GOOD — Keep up the great work!")
    else:
        st.info("No recovery data logged yet.")

# ================================
# GOALS & PLANS PAGE
# ================================
elif page == "Goals & Plans":
    st.title("Goals & Training Plans")
    st.markdown("Track your progress towards your goals and explore available training plans.")
    st.markdown("---")

    st.subheader("Your goals")
    if not goals.empty:
        for _, row in goals.iterrows():
            if row['goal_type'] in ['gå_ner_i_vikt', 'target_body_fat']:
                progress = max(0, min(100, (1 - (row['current_value'] - row['target_value']) /
                    max(row['current_value'], 0.01)) * 100))
            else:
                progress = min(100, (row['current_value'] / row['target_value']) * 100) if row['target_value'] > 0 else 0

            col1, col2 = st.columns([4, 1])
            with col1:
                label = row['goal_type'].replace('_', ' ').title()
                st.write(f"**{label}** — {row['current_value']} / {row['target_value']} {row['unit']} | Deadline: {row['deadline']}")
                st.progress(int(progress))
            with col2:
                st.metric("Progress", f"{progress:.0f}%")
    else:
        st.info("No goals set yet.")

    st.markdown("---")
    st.subheader("Available training plans")

    goal_colors = {
        'bygga_muskler': '#378ADD',
        'gå_ner_i_vikt': '#D85A30',
        'gå_upp_i_vikt': '#1D9E75',
        'löpning': '#EF9F27',
        'hålla_sig_i_form': '#7F77DD'
    }

    cols = st.columns(3)
    for i, (_, plan) in enumerate(plans.iterrows()):
        with cols[i % 3]:
            color = goal_colors.get(plan['goal'], '#378ADD')
            weeks = f"{plan['duration_weeks']} weeks" if plan['duration_weeks'] > 0 else "Ongoing"
            st.markdown(f"""
            <div style="border-left: 4px solid {color}; padding: 12px; margin-bottom: 12px; background: #f8f9fa; border-radius: 8px;">
                <strong>{plan['name']}</strong><br>
                <span style="color: #666; font-size: 13px;">
                Goal: {plan['goal'].replace('_', ' ')}<br>
                {weeks} — {plan['days_per_week']}x/week<br>
                Level: {plan['difficulty']}
                </span>
            </div>
            """, unsafe_allow_html=True)

# ================================
# RECOMMENDATIONS PAGE
# ================================
elif page == "Recommendations":
    st.title("Smart Recommendations")
    st.markdown("Personalized exercise recommendations based on your training history.")
    st.markdown("---")

    if not recommendations.empty:
        for _, row in recommendations.iterrows():
            score = row['score']
            if score >= 0.8:
                st.error(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
            elif score >= 0.5:
                st.warning(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
            else:
                st.info(f"**{row['exercise_name']}** ({row['body_part']}) — {row['reason']}")
    else:
        st.success("All muscle groups have been trained recently!")