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

st.title("HealthApp - Training Dashboard")
st.markdown("---")

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
        recovery = pd.read_sql(text("SELECT * FROM recovery_logs"), conn)
        recommendations = pd.read_sql(text("""
            SELECT r.*, e.name AS exercise_name, bp.name AS body_part
            FROM recommendations r
            JOIN exercises e ON r.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
        """), conn)
    return sessions, exercises, records, recovery, recommendations

sessions, exercises, records, recovery, recommendations = load_data()

# ================================
# ROW 1: KEY METRICS
# ================================
st.subheader("Overview")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Training Sessions", len(sessions))
with col2:
    total_vol = (exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)).sum()
    st.metric("Total Volume", f"{total_vol:,.0f} kg")
with col3:
    avg_rpe = exercises['rpe'].mean()
    st.metric("Avg RPE", f"{avg_rpe:.1f}/10")
with col4:
    st.metric("Personal Records", len(records))
with col5:
    avg_sleep = recovery['sleep_hours'].mean() if not recovery.empty else 0
    st.metric("Avg Sleep", f"{avg_sleep:.1f}h")

st.markdown("---")

# ================================
# ROW 2: MUSCLE GROUPS & DIFFICULTY
# ================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Most Trained Muscle Groups")
    body_counts = exercises.groupby('body_part').size().reset_index(name='count')
    body_counts = body_counts.sort_values('count', ascending=True)
    fig = px.bar(
        body_counts, x='count', y='body_part', orientation='h',
        color='count', color_continuous_scale='Blues',
        labels={'count': 'Number of exercises', 'body_part': 'Muscle group'}
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Difficulty Level")
    diff_counts = exercises.groupby('difficulty').size().reset_index(name='count')
    fig = px.pie(
        diff_counts, values='count', names='difficulty',
        color_discrete_sequence=['#5DCAA5', '#378ADD', '#D85A30'],
        hole=0.4
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# ================================
# ROW 3: VOLUME PER WEEK
# ================================
st.subheader("Training Volume per Week")
exercises['week'] = pd.to_datetime(exercises['date']).dt.strftime('%Y-W%W')
exercises['volume'] = exercises['sets'] * exercises['reps'] * exercises['weight_kg'].fillna(0)
weekly_vol = exercises.groupby('week')['volume'].sum().reset_index()
fig = px.bar(
    weekly_vol, x='week', y='volume',
    color_discrete_sequence=['#378ADD'],
    labels={'week': 'Week', 'volume': 'Volume (kg)'}
)
fig.update_layout(height=300)
st.plotly_chart(fig, use_container_width=True)

# ================================
# ROW 4: PERSONAL RECORDS & RECOVERY
# ================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Personal Records")
    if not records.empty:
        fig = px.bar(
            records.sort_values('weight_kg', ascending=True),
            x='weight_kg', y='exercise_name', orientation='h',
            color='weight_kg', color_continuous_scale='Greens',
            labels={'weight_kg': 'Weight (kg)', 'exercise_name': 'Exercise'}
        )
        fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Recovery over Time")
    if not recovery.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=recovery['date'], y=recovery['sleep_hours'],
            name='Sleep (h)', mode='lines+markers', line=dict(color='#5DCAA5')
        ))
        fig.add_trace(go.Scatter(
            x=recovery['date'], y=recovery['energy_level'],
            name='Energy', mode='lines+markers', line=dict(color='#378ADD')
        ))
        fig.add_trace(go.Scatter(
            x=recovery['date'], y=recovery['stress_level'],
            name='Stress', mode='lines+markers', line=dict(color='#D85A30')
        ))
        fig.update_layout(height=300, legend=dict(orientation='h'))
        st.plotly_chart(fig, use_container_width=True)

# ================================
# ROW 5: RECOMMENDATIONS
# ================================
st.markdown("---")
st.subheader("Smart Recommendations")
if not recommendations.empty:
    for _, row in recommendations.iterrows():
        st.info(f"{row['exercise_name']} ({row['body_part']}) — {row['reason']}")
else:
    st.success("All muscle groups have been trained recently!")

st.markdown("---")
st.caption("HealthApp Data Dashboard — Abdulrahman Fahmi, Data Engineer")