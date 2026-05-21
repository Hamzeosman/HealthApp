import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import io

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
engine = create_engine(os.getenv("DATABASE_URL"))

st.set_page_config(
    page_title="HealthApp — PT Dashboard",
    page_icon="🧑‍🏫",
    layout="wide"
)

# ── Dark theme card helper ───────────────────────────────────────────
def dark_card(icon, title, value, subtitle="", color="#378ADD"):
    return f"""
    <div style="background:#111827; border:1px solid #1f2937; border-radius:10px;
        padding:14px 16px; margin-bottom:10px;">
        <div style="font-size:22px;">{icon}</div>
        <div style="font-size:12px; color:#9ca3af; margin-top:2px;">{title}</div>
        <div style="font-size:22px; font-weight:700; color:{color};">{value}</div>
        <div style="font-size:11px; color:#6b7280;">{subtitle}</div>
    </div>"""

@st.cache_data
def load_all_clients():
    with engine.connect() as conn:
        clients = pd.read_sql(text("""
            SELECT
                u.id, u.name, u.email, u.age, u.weight_kg, u.height_cm,
                u.fitness_level, u.fitness_goal, u.experience_level, u.created_at,
                COUNT(DISTINCT ws.id) AS total_sessions,
                MAX(ws.date) AS last_session,
                AVG(we.rpe) AS avg_rpe,
                SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS total_volume
            FROM users u
            LEFT JOIN workout_sessions ws ON u.id = ws.user_id
            LEFT JOIN workout_exercises we ON ws.id = we.session_id
            WHERE u.role = 'user'
            GROUP BY u.id, u.name, u.email, u.age, u.weight_kg,
                     u.height_cm, u.fitness_level, u.fitness_goal,
                     u.experience_level, u.created_at
            ORDER BY total_sessions DESC
        """), conn)

        streaks = pd.read_sql(text("""
            SELECT user_id, current_streak, longest_streak, total_workouts
            FROM user_streaks
        """), conn)

        goals = pd.read_sql(text("""
            SELECT user_id, goal_type, target_value, current_value, unit,
                   deadline, is_achieved
            FROM user_goals
        """), conn)

        records = pd.read_sql(text("""
            SELECT pr.user_id, e.name AS exercise, pr.weight_kg, pr.date
            FROM personal_records pr
            JOIN exercises e ON pr.exercise_id = e.id
            ORDER BY pr.date DESC
        """), conn)

        recovery = pd.read_sql(text("""
            SELECT user_id, date, sleep_hours, sleep_quality,
                   energy_level, stress_level
            FROM recovery_logs
            ORDER BY date DESC
        """), conn)

        recommendations = pd.read_sql(text("""
            SELECT r.user_id, e.name AS exercise, bp.name AS body_part,
                   r.reason, r.score, r.created_at
            FROM recommendations r
            JOIN exercises e ON r.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            ORDER BY r.score DESC
        """), conn)

        plans = pd.read_sql(text("SELECT * FROM training_plans"), conn)

        notifications = pd.read_sql(text("""
            SELECT * FROM notifications ORDER BY created_at DESC
        """), conn)

        exercises_log = pd.read_sql(text("""
            SELECT we.*, e.name AS exercise_name, bp.name AS body_part,
                   eq.name AS equipment_name, ws.date, ws.user_id,
                   u.name AS client_name
            FROM workout_exercises we
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            LEFT JOIN equipment eq ON e.equipment_id = eq.id
            JOIN workout_sessions ws ON we.session_id = ws.id
            JOIN users u ON ws.user_id = u.id
            ORDER BY ws.date DESC
        """), conn)

        body_measurements = pd.read_sql(text("""
            SELECT * FROM body_measurements ORDER BY date DESC
        """), conn)

        ai_insights = pd.read_sql(text("""
            SELECT ai.*, u.name AS client_name
            FROM ai_insights ai
            JOIN users u ON ai.user_id = u.id
            ORDER BY ai.created_at DESC
        """), conn)

    # Recovery score beräkning (evidensbaserat)
    if not recovery.empty:
        recovery['recovery_score'] = (
            recovery['sleep_hours'].clip(0, 10) / 10 * 35 +
            recovery['energy_level'] / 10 * 30 +
            (10 - recovery['stress_level']) / 10 * 20 +
            recovery['sleep_quality'] / 10 * 15
        ).round(1)

    return (clients, streaks, goals, records, recovery, recommendations,
            plans, notifications, exercises_log, body_measurements, ai_insights)

(clients, streaks, goals, records, recovery, recommendations,
 plans, notifications, exercises_log, body_measurements, ai_insights) = load_all_clients()

# ── SIDEBAR ──────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧑‍🏫 PT Dashboard")
    st.markdown("*Personal Trainer View*")
    st.markdown("---")

    # Search
    search = st.text_input("🔍 Search client", "")

    page = st.radio("Navigation", [
        "📊 Client Overview",
        "👤 Client Detail",
        "💪 Muscle Balance",
        "😴 Recovery & Readiness",
        "📈 Progress Tracking",
        "🏋️ Equipment Analytics",
        "🧠 AI Insights & Alerts",
        "📋 Recommendations",
        "📅 Training Plans",
        "🔔 Notifications",
    ])

    st.markdown("---")

    # KPIs sidebar
    total = len(clients)
    active = len(clients[clients['total_sessions'] > 0])
    at_risk = 0
    if not recovery.empty:
        latest_rec = recovery.sort_values('date').groupby('user_id').last()
        at_risk = len(latest_rec[
            (latest_rec['sleep_hours'] < 6) |
            (latest_rec['energy_level'] < 5) |
            (latest_rec['stress_level'] > 7)
        ])

    st.markdown(f"""
    <div style="background:#111827; border:1px solid #1f2937; border-radius:8px; padding:12px;">
        <div style="font-size:12px; color:#9ca3af;">Total clients</div>
        <div style="font-size:20px; font-weight:700; color:#378ADD;">{total}</div>
        <div style="font-size:12px; color:#9ca3af; margin-top:6px;">Active</div>
        <div style="font-size:20px; font-weight:700; color:#1D9E75;">{active}</div>
        <div style="font-size:12px; color:#9ca3af; margin-top:6px;">⚠️ At risk</div>
        <div style="font-size:20px; font-weight:700; color:#D85A30;">{at_risk}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Data Engineer: Abdulrahman Fahmi")

# ── Filter clients by search ─────────────────────────────────────────
client_list = clients.copy()
if search:
    client_list = client_list[client_list['name'].str.contains(search, case=False)]

# =====================================================================
# CLIENT OVERVIEW
# =====================================================================
if page == "📊 Client Overview":
    st.title("📊 Client Overview")
    st.markdown("All your clients at a glance.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total clients", len(clients))
    with col2:
        st.metric("Avg sessions/client", f"{clients['total_sessions'].mean():.1f}")
    with col3:
        st.metric("Active clients", len(clients[clients['total_sessions'] > 0]))
    with col4:
        avg_rpe = clients['avg_rpe'].mean()
        st.metric("Avg RPE", f"{avg_rpe:.1f}/10" if not pd.isna(avg_rpe) else "N/A")

    st.markdown("---")

    # ── Alert banner ─────────────────────────────────────────────────
    if at_risk > 0:
        st.error(f"⚠️ **{at_risk} client(s) need attention** — low sleep, energy or high stress detected.")

    # ── Leaderboards i tabs ──────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📋 Client List", "🏆 Leaderboard", "📊 Distribution"])

    with tab1:
        display = client_list[['name', 'email', 'fitness_level', 'fitness_goal',
                               'total_sessions', 'last_session', 'avg_rpe']].copy()
        display.columns = ['Name', 'Email', 'Level', 'Goal', 'Sessions', 'Last Session', 'Avg RPE']
        display['Goal'] = display['Goal'].str.replace('_', ' ').str.title()
        display['Level'] = display['Level'].str.title()
        display['Avg RPE'] = display['Avg RPE'].round(1)
        st.dataframe(display, use_container_width=True, height=350)

        # Export CSV
        csv = display.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Export client list (CSV)", csv,
            "clients.csv", "text/csv")

    with tab2:
        st.subheader("🏆 Leaderboards")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Most sessions**")
            top_sessions = clients.nlargest(5, 'total_sessions')[['name', 'total_sessions']]
            for i, (_, r) in enumerate(top_sessions.iterrows()):
                medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
                st.markdown(f"{medal} **{r['name']}** — {int(r['total_sessions'])} sessions")

        with col2:
            st.markdown("**Highest volume**")
            top_vol = clients.nlargest(5, 'total_volume')[['name', 'total_volume']]
            for i, (_, r) in enumerate(top_vol.iterrows()):
                medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
                vol = f"{r['total_volume']:,.0f} kg" if pd.notna(r['total_volume']) else "—"
                st.markdown(f"{medal} **{r['name']}** — {vol}")

        with col3:
            st.markdown("**Longest streak**")
            if not streaks.empty:
                streak_named = streaks.merge(clients[['id','name']], left_on='user_id', right_on='id')
                top_streak = streak_named.nlargest(5, 'longest_streak')
                for i, (_, r) in enumerate(top_streak.iterrows()):
                    medal = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
                    st.markdown(f"{medal} **{r['name']}** — {int(r['longest_streak'])} days")

        # Top PRs per exercise
        st.markdown("---")
        st.subheader("🏋️ Strongest clients per exercise")
        if not records.empty:
            rec_named = records.merge(clients[['id','name']], left_on='user_id', right_on='id')
            top_pr = rec_named.sort_values('weight_kg', ascending=False).groupby('exercise').first().reset_index()
            top_pr = top_pr.nlargest(10, 'weight_kg')[['exercise','name','weight_kg']]
            top_pr.columns = ['Exercise','Client','Weight (kg)']
            st.dataframe(top_pr, use_container_width=True, hide_index=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sessions per client")
            fig = px.bar(clients.sort_values('total_sessions', ascending=True),
                x='total_sessions', y='name', orientation='h',
                color='total_sessions', color_continuous_scale='Blues',
                labels={'total_sessions': 'Sessions', 'name': ''})
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            if clients['fitness_goal'].notna().any():
                goal_counts = clients['fitness_goal'].value_counts().reset_index()
                goal_counts.columns = ['Goal', 'Count']
                goal_counts['Goal'] = goal_counts['Goal'].str.replace('_', ' ').str.title()
                fig = px.pie(goal_counts, values='Count', names='Goal',
                    color_discrete_sequence=['#378ADD','#D85A30','#1D9E75','#EF9F27','#7F77DD'],
                    hole=0.4, title="Goal distribution")
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

# =====================================================================
# CLIENT DETAIL
# =====================================================================
elif page == "👤 Client Detail":
    st.title("👤 Client Detail")
    st.markdown("---")

    if client_list.empty:
        st.info("No clients found.")
    else:
        selected = st.selectbox("Select client", client_list['name'].tolist())
        client = clients[clients['name'] == selected].iloc[0]
        client_id = int(client['id'])

        # Client header card
        streak_data = streaks[streaks['user_id'] == client_id]
        streak_val = int(streak_data.iloc[0]['current_streak']) if not streak_data.empty else 0
        best_streak = int(streak_data.iloc[0]['longest_streak']) if not streak_data.empty else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(dark_card("👤", "Client", client['name'],
                f"{client['fitness_level']} | {str(client['fitness_goal']).replace('_',' ')}"), unsafe_allow_html=True)
        with col2:
            st.markdown(dark_card("🏋️", "Total sessions", int(client['total_sessions']),
                f"Last: {str(client['last_session'])[:10] if client['last_session'] else 'Never'}"), unsafe_allow_html=True)
        with col3:
            st.markdown(dark_card("🔥", "Current streak", f"{streak_val} days",
                f"Best: {best_streak} days", "#EF9F27"), unsafe_allow_html=True)
        with col4:
            vol = f"{client['total_volume']:,.0f} kg" if pd.notna(client['total_volume']) else "—"
            st.markdown(dark_card("📦", "Total volume", vol, ""), unsafe_allow_html=True)

        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Goals", "💪 Records", "📊 Analytics", "📋 Info"])

        with tab1:
            client_goals = goals[goals['user_id'] == client_id]
            if not client_goals.empty:
                for _, row in client_goals.iterrows():
                    if row['goal_type'] in ['target_weight', 'target_body_fat']:
                        progress = max(0, min(100,
                            (1 - (row['current_value'] - row['target_value']) /
                             max(row['current_value'], 0.01)) * 100
                        )) if row['current_value'] > row['target_value'] else 100
                    else:
                        progress = min(100,
                            (row['current_value'] / row['target_value']) * 100
                        ) if row['target_value'] > 0 else 0
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{row['goal_type'].replace('_', ' ').title()}** — {row['current_value']} / {row['target_value']} {row['unit']}")
                        st.progress(int(progress))
                    with col2:
                        st.metric("Progress", f"{progress:.0f}%")
                    with col3:
                        days = (pd.to_datetime(row['deadline']) - pd.Timestamp.now()).days
                        st.metric("Days left", max(0, days))
            else:
                st.info("No goals registered.")

        with tab2:
            client_records = records[records['user_id'] == client_id]
            if not client_records.empty:
                fig = px.bar(client_records.sort_values('weight_kg', ascending=True),
                    x='weight_kg', y='exercise', orientation='h',
                    color='weight_kg', color_continuous_scale='Greens',
                    labels={'weight_kg': 'Weight (kg)', 'exercise': ''})
                fig.update_layout(showlegend=False, coloraxis_showscale=False, height=280)
                st.plotly_chart(fig, use_container_width=True)

                # Expandable per exercise
                st.subheader("Exercise deep-dive")
                for ex in client_records['exercise'].unique():
                    ex_data = client_records[client_records['exercise'] == ex]
                    with st.expander(f"🏋️ {ex} — PR: {ex_data['weight_kg'].max():.1f} kg"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Best PR", f"{ex_data['weight_kg'].max():.1f} kg")
                            st.metric("Sessions logged", len(ex_data))
                        with col2:
                            if len(ex_data) > 1:
                                fig = px.line(ex_data.sort_values('date'), x='date', y='weight_kg',
                                    markers=True, title="PR progression",
                                    color_discrete_sequence=['#1D9E75'])
                                fig.update_layout(height=180, margin=dict(t=30, b=0))
                                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No personal records.")

        with tab3:
            client_exs = exercises_log[exercises_log['user_id'] == client_id].copy()
            if not client_exs.empty:
                client_exs['week'] = pd.to_datetime(client_exs['date']).dt.strftime('%Y-W%W')
                client_exs['volume'] = client_exs['sets'] * client_exs['reps'] * client_exs['weight_kg'].fillna(0)
                col1, col2 = st.columns(2)
                with col1:
                    weekly = client_exs.groupby('week')['volume'].sum().reset_index()
                    fig = px.bar(weekly, x='week', y='volume', color_discrete_sequence=['#378ADD'],
                        title="Weekly volume", labels={'week':'','volume':'kg'})
                    fig.update_layout(height=260, xaxis_tickangle=-30)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    muscle = client_exs.groupby('body_part').size().reset_index(name='count')
                    fig = px.pie(muscle, values='count', names='body_part',
                        title="Muscle group distribution")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=260, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No training data.")

        with tab4:
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Email:** {client['email']}")
                st.write(f"**Age:** {client['age']}")
                st.write(f"**Weight:** {client['weight_kg']} kg")
                st.write(f"**Height:** {client['height_cm']} cm")
            with col2:
                st.write(f"**Level:** {client['fitness_level']}")
                st.write(f"**Goal:** {str(client['fitness_goal']).replace('_',' ')}")
                st.write(f"**Experience:** {client['experience_level']}")
                st.write(f"**Member since:** {str(client['created_at'])[:10]}")

            # Body measurements
            if not body_measurements.empty:
                bm = body_measurements[body_measurements['user_id'] == client_id]
                if not bm.empty:
                    st.markdown("**Body measurements**")
                    st.dataframe(bm[['date','weight_kg','body_fat_percentage',
                        'chest_cm','waist_cm','bicep_cm']].head(5),
                        use_container_width=True, hide_index=True)

# =====================================================================
# MUSCLE BALANCE ANALYSIS
# =====================================================================
elif page == "💪 Muscle Balance":
    st.title("💪 Muscle Balance Analysis")
    st.markdown("---")

    with engine.connect() as conn:
        muscle_data = pd.read_sql(text("""
            SELECT u.name AS client, bp.name AS body_part,
                COUNT(we.id) AS exercises_logged,
                SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS volume
            FROM users u
            JOIN workout_sessions ws ON u.id = ws.user_id
            JOIN workout_exercises we ON ws.id = we.session_id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            GROUP BY u.name, bp.name
        """), conn)

    tab1, tab2, tab3 = st.tabs(["📊 All Clients", "🔥 Heatmap", "⚠️ Imbalances"])

    with tab1:
        if not muscle_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                total_muscle = muscle_data.groupby('body_part')['volume'].sum().reset_index()
                total_muscle = total_muscle.sort_values('volume', ascending=True)
                fig = px.bar(total_muscle, x='volume', y='body_part', orientation='h',
                    color='volume', color_continuous_scale='RdYlGn',
                    labels={'volume': 'Total volume (kg)', 'body_part': ''})
                fig.update_layout(showlegend=False, coloraxis_showscale=False, height=350,
                    title="Volume by muscle group")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                total_muscle2 = muscle_data.groupby('body_part')['exercises_logged'].sum().reset_index()
                fig = px.pie(total_muscle2, values='exercises_logged', names='body_part',
                    title="Exercise frequency by muscle")
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if not muscle_data.empty:
            pivot = muscle_data.pivot_table(
                index='client', columns='body_part',
                values='exercises_logged', fill_value=0)
            fig = px.imshow(pivot, color_continuous_scale='Blues',
                labels={'color': 'Exercises', 'x': '', 'y': ''},
                title='Exercises per muscle group per client', aspect='auto')
            fig.update_layout(height=400, xaxis_tickangle=0,
                margin=dict(l=120, r=20, t=60, b=20))
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if not muscle_data.empty:
            st.subheader("Clients with imbalances")
            found = False
            for client_name in muscle_data['client'].unique():
                cd = muscle_data[muscle_data['client'] == client_name]
                max_v = cd['volume'].max()
                min_v = cd['volume'].min()
                if max_v > 0 and min_v / max_v < 0.3:
                    weak = cd.nsmallest(2, 'volume')['body_part'].tolist()
                    strong = cd.nlargest(2, 'volume')['body_part'].tolist()
                    st.warning(f"**{client_name}** — ⚠️ Weak: {', '.join(weak)} | Strong: {', '.join(strong)}")
                    found = True
            if not found:
                st.success("No major imbalances detected across clients! 💪")

# =====================================================================
# RECOVERY & READINESS
# =====================================================================
elif page == "😴 Recovery & Readiness":
    st.title("😴 Recovery & Readiness")
    st.markdown("---")

    if not recovery.empty:
        recovery_named = recovery.merge(clients[['id', 'name']], left_on='user_id', right_on='id')

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            avg_sleep = recovery_named['sleep_hours'].mean()
            st.metric("Avg sleep", f"{avg_sleep:.1f}h",
                "Optimal" if avg_sleep >= 7 else "Low")
        with col2:
            st.metric("Avg energy", f"{recovery_named['energy_level'].mean():.1f}/10")
        with col3:
            st.metric("Avg stress", f"{recovery_named['stress_level'].mean():.1f}/10")
        with col4:
            if 'recovery_score' in recovery_named.columns:
                st.metric("Avg recovery score", f"{recovery_named['recovery_score'].mean():.1f}/100")

        st.markdown("---")

        tab1, tab2 = st.tabs(["🚦 Client Readiness", "📊 Trends"])

        with tab1:
            latest = recovery_named.sort_values('date').groupby('name').last().reset_index()

            # Sort: at-risk first
            latest['_priority'] = latest.apply(lambda r:
                0 if (r['sleep_hours'] < 6 or r['energy_level'] < 5 or r['stress_level'] > 7)
                else 1, axis=1)
            latest = latest.sort_values('_priority')

            for _, row in latest.iterrows():
                sleep = row['sleep_hours']
                energy = row['energy_level']
                stress = row['stress_level']
                score = row.get('recovery_score', 0)

                col1, col2 = st.columns([3, 1])
                with col1:
                    if sleep >= 7 and energy >= 7 and stress <= 4:
                        st.success(f"✅ **{row['name']}** — READY | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
                    elif sleep < 6 or energy < 5:
                        st.error(f"🔴 **{row['name']}** — NEEDS REST | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
                    elif stress > 7:
                        st.warning(f"🟡 **{row['name']}** — HIGH STRESS | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
                    else:
                        st.info(f"🔵 **{row['name']}** — GOOD | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
                with col2:
                    if 'recovery_score' in row:
                        st.metric("Recovery", f"{score:.0f}/100")

        with tab2:
            recovery_named['week'] = pd.to_datetime(recovery_named['date']).dt.strftime('%Y-W%W')
            weekly = recovery_named.groupby('week').agg({
                'sleep_hours': 'mean', 'energy_level': 'mean', 'stress_level': 'mean'}).reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=weekly['week'], y=weekly['sleep_hours'],
                name='Avg Sleep (h)', mode='lines+markers', line=dict(color='#5DCAA5')))
            fig.add_trace(go.Scatter(x=weekly['week'], y=weekly['energy_level'],
                name='Avg Energy', mode='lines+markers', line=dict(color='#378ADD')))
            fig.add_trace(go.Scatter(x=weekly['week'], y=weekly['stress_level'],
                name='Avg Stress', mode='lines+markers', line=dict(color='#D85A30')))
            fig.update_layout(height=350, title="Recovery trends (all clients)",
                xaxis_tickangle=-30, legend=dict(orientation='h'))
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No recovery data logged yet.")

# =====================================================================
# PROGRESS TRACKING
# =====================================================================
elif page == "📈 Progress Tracking":
    st.title("📈 Progress Tracking")
    st.markdown("---")

    if client_list.empty:
        st.info("No clients found.")
    else:
        selected = st.selectbox("Select client", client_list['name'].tolist())
        client_id = int(clients[clients['name'] == selected]['id'].values[0])

        with engine.connect() as conn:
            volume_data = pd.read_sql(text("""
                SELECT DATE_TRUNC('week', ws.date) AS week,
                    SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS volume,
                    AVG(we.rpe) AS avg_rpe,
                    COUNT(DISTINCT ws.id) AS sessions
                FROM workout_sessions ws
                JOIN workout_exercises we ON ws.id = we.session_id
                WHERE ws.user_id = :uid
                GROUP BY week ORDER BY week
            """), conn, params={"uid": client_id})

            pr_data = pd.read_sql(text("""
                SELECT pr.date, e.name AS exercise, pr.weight_kg
                FROM personal_records pr
                JOIN exercises e ON pr.exercise_id = e.id
                WHERE pr.user_id = :uid ORDER BY pr.date
            """), conn, params={"uid": client_id})

        tab1, tab2, tab3 = st.tabs(["📊 Volume & RPE", "🏆 PRs", "📉 ACWR"])

        with tab1:
            if not volume_data.empty:
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(volume_data, x='week', y='volume',
                        color_discrete_sequence=['#378ADD'], title="Weekly volume",
                        labels={'week': '', 'volume': 'kg'})
                    fig.update_layout(height=300, xaxis_tickangle=-30)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    fig = px.line(volume_data, x='week', y='avg_rpe',
                        markers=True, color_discrete_sequence=['#D85A30'], title="RPE trend",
                        labels={'week': '', 'avg_rpe': 'Avg RPE'})
                    fig.add_hline(y=8, line_dash="dash", line_color="orange",
                        annotation_text="RPE 8 target")
                    fig.update_layout(height=300, xaxis_tickangle=-30, yaxis_range=[0, 10])
                    st.plotly_chart(fig, use_container_width=True)

                # Export
                csv = volume_data.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Export progress data (CSV)", csv,
                    f"{selected}_progress.csv", "text/csv")
            else:
                st.info("No training data for this client.")

        with tab2:
            if not pr_data.empty:
                exercises_list = pr_data['exercise'].unique().tolist()
                selected_ex = st.selectbox("Select exercise", exercises_list)
                ex_data = pr_data[pr_data['exercise'] == selected_ex]
                fig = px.line(ex_data, x='date', y='weight_kg',
                    markers=True, color_discrete_sequence=['#1D9E75'],
                    title=f"{selected_ex} — PR progression",
                    labels={'date': 'Date', 'weight_kg': 'Weight (kg)'})
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

                # All PRs table
                st.dataframe(pr_data[['exercise','weight_kg','date']].rename(columns={
                    'exercise': 'Exercise', 'weight_kg': 'Weight (kg)', 'date': 'Date'}),
                    use_container_width=True, hide_index=True)
            else:
                st.info("No personal records.")

        with tab3:
            # ACWR beräkning
            if not volume_data.empty and len(volume_data) >= 2:
                volume_data = volume_data.sort_values('week')
                volume_data['acute'] = volume_data['volume'].rolling(1, min_periods=1).mean()
                volume_data['chronic'] = volume_data['volume'].rolling(4, min_periods=1).mean()
                volume_data['acwr'] = (volume_data['acute'] / volume_data['chronic'].replace(0, 1)).round(2)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=volume_data['week'], y=volume_data['acwr'],
                    mode='lines+markers', name='ACWR', line=dict(color='#7F77DD')))
                fig.add_hline(y=0.8, line_dash="dash", line_color="#5DCAA5",
                    annotation_text="Safe zone min (0.8)")
                fig.add_hline(y=1.3, line_dash="dash", line_color="#D85A30",
                    annotation_text="Danger zone (1.3)")
                fig.update_layout(height=300, title="ACWR — Acute:Chronic Workload Ratio",
                    yaxis=dict(range=[0, 2.5]), xaxis_tickangle=-30)
                st.plotly_chart(fig, use_container_width=True)

                latest_acwr = volume_data['acwr'].iloc[-1]
                if latest_acwr < 0.8:
                    st.warning(f"⚠️ ACWR: {latest_acwr:.2f} — Undertraining. Increase load gradually.")
                elif latest_acwr <= 1.3:
                    st.success(f"✅ ACWR: {latest_acwr:.2f} — Optimal training zone.")
                else:
                    st.error(f"🔴 ACWR: {latest_acwr:.2f} — Overreaching risk! Consider deload.")
            else:
                st.info("Need at least 2 weeks of data for ACWR.")

# =====================================================================
# EQUIPMENT ANALYTICS
# =====================================================================
elif page == "🏋️ Equipment Analytics":
    st.title("🏋️ Equipment Analytics")
    st.markdown("Analyze training across all equipment types.")
    st.markdown("---")

    equipment_icons = {
        "Hantlar": "🏋️", "Kettlebell": "⚫", "Skivstång": "🏋️‍♂️",
        "Kroppsvikt": "🤸", "Kabelmaskin": "🔗", "Resistansband": "🪢"
    }

    if not exercises_log.empty and 'equipment_name' in exercises_log.columns:
        available_equip = sorted(exercises_log['equipment_name'].dropna().unique().tolist())
        selected_equips = st.multiselect(
            "🏋️ Select equipment (one or more)",
            options=available_equip,
            default=available_equip[:2] if len(available_equip) >= 2 else available_equip
        )

        # Client filter
        client_filter = st.multiselect(
            "👤 Filter by client",
            options=sorted(exercises_log['client_name'].unique().tolist()),
            default=[]
        )

        filtered = exercises_log.copy()
        if selected_equips:
            filtered = filtered[filtered['equipment_name'].isin(selected_equips)]
        if client_filter:
            filtered = filtered[filtered['client_name'].isin(client_filter)]

        if not filtered.empty:
            filtered['volume'] = filtered['sets'] * filtered['reps'] * filtered['weight_kg'].fillna(0)

            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Unique exercises", filtered['exercise_name'].nunique())
            with col2:
                st.metric("Total volume", f"{filtered['volume'].sum():,.0f} kg")
            with col3:
                top_ex = filtered['exercise_name'].value_counts().idxmax()
                st.metric("Top exercise", top_ex)
            with col4:
                st.metric("Avg RPE", f"{filtered['rpe'].mean():.1f}")

            st.markdown("---")

            tab1, tab2, tab3 = st.tabs(["📊 Overview", "🏋️ Exercises", "📈 Analytics"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    top_exs = filtered['exercise_name'].value_counts().head(10).reset_index()
                    top_exs.columns = ['Exercise', 'Count']
                    fig = px.bar(top_exs, x='Count', y='Exercise', orientation='h',
                        color='Count', color_continuous_scale='Blues',
                        title="Top exercises")
                    fig.update_layout(height=320, showlegend=False, coloraxis_showscale=False)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    muscles = filtered.groupby('body_part').size().reset_index(name='count')
                    fig = px.pie(muscles, values='count', names='body_part',
                        title="Muscle groups trained")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(height=320, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                # Per client
                if not client_filter:
                    client_vol = filtered.groupby('client_name')['volume'].sum().reset_index()
                    client_vol = client_vol.sort_values('volume', ascending=True)
                    fig = px.bar(client_vol, x='volume', y='client_name', orientation='h',
                        color='volume', color_continuous_scale='Purples',
                        title="Volume per client",
                        labels={'volume': 'kg', 'client_name': ''})
                    fig.update_layout(height=280, showlegend=False, coloraxis_showscale=False)
                    st.plotly_chart(fig, use_container_width=True)

            with tab2:
                ex_summary = filtered.groupby('exercise_name').agg(
                    sessions=('session_id', 'nunique'),
                    avg_weight=('weight_kg', 'mean'),
                    max_weight=('weight_kg', 'max'),
                    avg_rpe=('rpe', 'mean'),
                    volume=('volume', 'sum')
                ).reset_index().sort_values('volume', ascending=False)
                ex_summary.columns = ['Exercise', 'Sessions', 'Avg Weight', 'Max Weight', 'Avg RPE', 'Volume (kg)']
                ex_summary = ex_summary.round(1)
                st.dataframe(ex_summary, use_container_width=True, hide_index=True)

                csv = ex_summary.to_csv(index=False).encode('utf-8')
                st.download_button("⬇️ Export exercise data (CSV)", csv,
                    "equipment_exercises.csv", "text/csv")

            with tab3:
                filtered['week'] = pd.to_datetime(filtered['date']).dt.strftime('%Y-W%W')
                weekly = filtered.groupby('week')['volume'].sum().reset_index()
                fig = px.bar(weekly, x='week', y='volume',
                    color_discrete_sequence=['#7F77DD'],
                    title=f"Weekly volume — {', '.join(selected_equips) if selected_equips else 'All'}",
                    labels={'week': '', 'volume': 'kg'})
                fig.update_layout(height=280, xaxis_tickangle=-30)
                st.plotly_chart(fig, use_container_width=True)

                # RPE trend
                weekly_rpe = filtered.groupby('week')['rpe'].mean().reset_index()
                fig = px.line(weekly_rpe, x='week', y='rpe',
                    markers=True, color_discrete_sequence=['#D85A30'],
                    title="Avg RPE trend", labels={'week': '', 'rpe': 'Avg RPE'})
                fig.update_layout(height=250, xaxis_tickangle=-30, yaxis=dict(range=[0,10]))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for selected filters.")
    else:
        st.info("No equipment data available.")

# =====================================================================
# AI INSIGHTS & ALERTS
# =====================================================================
elif page == "🧠 AI Insights & Alerts":
    st.title("🧠 AI Insights & Alerts")
    st.markdown("Smart alerts and insights generated from client data.")
    st.markdown("---")

    # ── Auto-generated alerts ────────────────────────────────────────
    st.subheader("⚠️ Automatic Alerts")

    alerts_found = False

    # 1. Ingen träning på 14 dagar
    if not exercises_log.empty:
        last_workout = exercises_log.groupby('user_id')['date'].max().reset_index()
        last_workout = last_workout.merge(clients[['id','name']], left_on='user_id', right_on='id')
        last_workout['days_since'] = (pd.Timestamp.now() - pd.to_datetime(last_workout['date'])).dt.days
        inactive = last_workout[last_workout['days_since'] > 14]
        for _, r in inactive.iterrows():
            st.error(f"🔴 **{r['name']}** — No workouts in {int(r['days_since'])} days. Risk of losing progress.")
            alerts_found = True

    # 2. Recovery risk
    if not recovery.empty:
        recovery_named = recovery.merge(clients[['id','name']], left_on='user_id', right_on='id')
        latest_rec = recovery_named.sort_values('date').groupby('name').last().reset_index()
        for _, r in latest_rec.iterrows():
            if r['sleep_hours'] < 6:
                st.warning(f"😴 **{r['name']}** — Sleep {r['sleep_hours']}h (below 6h). Recommend rest day.")
                alerts_found = True
            if r['stress_level'] > 7:
                st.warning(f"😤 **{r['name']}** — Stress {r['stress_level']}/10. Consider light session only.")
                alerts_found = True
            if r['energy_level'] < 4:
                st.error(f"⚡ **{r['name']}** — Very low energy ({r['energy_level']}/10). Rest recommended.")
                alerts_found = True

    # 3. Volume spike (ACWR)
    if not exercises_log.empty:
        exercises_log['volume'] = exercises_log['sets'] * exercises_log['reps'] * exercises_log['weight_kg'].fillna(0)
        exercises_log['week'] = pd.to_datetime(exercises_log['date']).dt.strftime('%Y-W%W')
        for uid in exercises_log['user_id'].unique():
            user_data = exercises_log[exercises_log['user_id'] == uid]
            weekly_vol = user_data.groupby('week')['volume'].sum().reset_index().sort_values('week')
            if len(weekly_vol) >= 4:
                acute = weekly_vol['volume'].iloc[-1]
                chronic = weekly_vol['volume'].iloc[-4:].mean()
                if chronic > 0:
                    acwr = acute / chronic
                    name = user_data['client_name'].iloc[0]
                    if acwr > 1.5:
                        st.error(f"🔴 **{name}** — ACWR {acwr:.2f} (overreaching risk!). Recommend deload.")
                        alerts_found = True
                    elif acwr < 0.6:
                        st.warning(f"📉 **{name}** — ACWR {acwr:.2f} (undertraining). Increase load.")
                        alerts_found = True

    if not alerts_found:
        st.success("✅ All clients look good! No critical alerts.")

    st.markdown("---")

    # ── AI Insights från databasen ───────────────────────────────────
    st.subheader("💡 AI Insights from database")
    if not ai_insights.empty:
        type_filter = st.selectbox("Filter by type",
            ["All"] + ai_insights['insight_type'].unique().tolist())
        filtered_ins = ai_insights if type_filter == "All" else \
            ai_insights[ai_insights['insight_type'] == type_filter]

        for _, ins in filtered_ins.iterrows():
            client_label = f"[{ins['client_name']}] " if 'client_name' in ins else ""
            if ins['insight_type'] in ['recovery_advice', 'progress_summary']:
                st.success(f"**{client_label}{ins['title']}**\n\n{ins['content']}")
            elif ins['insight_type'] in ['training_tip', 'weekly_analysis']:
                st.info(f"**{client_label}{ins['title']}**\n\n{ins['content']}")
            else:
                st.warning(f"**{client_label}{ins['title']}**\n\n{ins['content']}")
    else:
        st.info("No AI insights in database yet.")

# =====================================================================
# RECOMMENDATIONS
# =====================================================================
elif page == "📋 Recommendations":
    st.title("📋 Smart Recommendations")
    st.markdown("---")

    if not recommendations.empty:
        recs_named = recommendations.merge(clients[['id','name']], left_on='user_id', right_on='id')

        # Filter
        selected_clients = st.multiselect("Filter by client",
            options=sorted(recs_named['name'].unique().tolist()), default=[])
        filtered_recs = recs_named if not selected_clients else \
            recs_named[recs_named['name'].isin(selected_clients)]

        for client_name in filtered_recs['name'].unique():
            with st.expander(f"👤 {client_name}", expanded=True):
                client_recs = filtered_recs[filtered_recs['name'] == client_name]
                for _, row in client_recs.iterrows():
                    if row['score'] >= 0.8:
                        st.error(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
                    elif row['score'] >= 0.5:
                        st.warning(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
                    else:
                        st.info(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
    else:
        st.info("No recommendations yet. Run the recommendation pipeline.")

# =====================================================================
# TRAINING PLANS
# =====================================================================
elif page == "📅 Training Plans":
    st.title("📅 Training Plans")
    st.markdown("---")

    tab1, tab2 = st.tabs(["📋 Available Plans", "➕ Assign Plan"])

    with tab1:
        goal_filter = st.selectbox("Filter by goal", ["All"] + plans['goal'].unique().tolist())
        filtered_plans = plans if goal_filter == "All" else plans[plans['goal'] == goal_filter]

        cols = st.columns(3)
        for i, (_, plan) in enumerate(filtered_plans.iterrows()):
            with cols[i % 3]:
                weeks = f"{plan['duration_weeks']}w" if plan['duration_weeks'] > 0 else "Ongoing"
                level = {'nybörjare': 'Beginner', 'medel': 'Intermediate',
                         'avancerad': 'Advanced'}.get(plan['difficulty'], plan['difficulty'])
                goal = plan['goal'].replace('_', ' ').title()
                st.markdown(f"""
                <div style="background:#111827; border:1px solid #1f2937; border-radius:8px;
                    padding:12px; margin-bottom:10px;">
                    <div style="font-weight:700; color:#378ADD;">{plan['name']}</div>
                    <div style="font-size:12px; color:#9ca3af; margin-top:4px;">
                        {goal} | {weeks} | {level} | {plan['days_per_week']}x/week
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            selected_client = st.selectbox("Client", clients['name'].tolist())
        with col2:
            selected_plan = st.selectbox("Plan", plans['name'].tolist())
        start_date = st.date_input("Start date")
        if st.button("✅ Assign plan"):
            client_id = int(clients[clients['name'] == selected_client]['id'].values[0])
            plan_id = int(plans[plans['name'] == selected_plan]['id'].values[0])
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO user_training_plans (user_id, plan_id, start_date, is_active)
                    VALUES (:uid, :pid, :start, TRUE)
                    ON CONFLICT DO NOTHING
                """), {"uid": client_id, "pid": plan_id, "start": str(start_date)})
                conn.commit()
            st.success(f"✅ **{selected_plan}** assigned to **{selected_client}**!")
            st.cache_data.clear()

# =====================================================================
# NOTIFICATIONS
# =====================================================================
elif page == "🔔 Notifications":
    st.title("🔔 Notifications")
    st.markdown("---")

    if not notifications.empty:
        notif_named = notifications.merge(
            clients[['id','name']], left_on='user_id', right_on='id', how='left')
        unread = notif_named[notif_named['is_read'] == False]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total notifications", len(notif_named))
        with col2:
            st.metric("Unread", len(unread))

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            type_filter = st.selectbox("Filter by type", ["All",
                "workout_reminder", "personal_record", "streak_milestone",
                "weekly_report", "goal_achieved", "ai_insight"])
        with col2:
            client_filter = st.selectbox("Filter by client",
                ["All"] + sorted(notif_named['name'].dropna().unique().tolist()))

        filtered = notif_named.copy()
        if type_filter != "All":
            filtered = filtered[filtered['notification_type'] == type_filter]
        if client_filter != "All":
            filtered = filtered[filtered['name'] == client_filter]

        st.markdown(f"**{len(filtered)} notifications**")

        for _, row in filtered.iterrows():
            client_name = row['name'] if pd.notna(row.get('name')) else "Unknown"
            ntype = row['notification_type']
            unread_badge = "🔴 " if not row['is_read'] else ""
            msg = f"{unread_badge}**{client_name}** — {row['title']}: {row['message']}"
            if ntype == 'personal_record':
                st.success(msg)
            elif ntype == 'workout_reminder':
                st.warning(msg)
            elif ntype == 'streak_milestone':
                st.info(msg)
            else:
                st.info(msg)

        # Export
        csv = filtered[['name','notification_type','title','message','is_read','created_at']].to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Export notifications (CSV)", csv,
            "notifications.csv", "text/csv")
    else:
        st.info("No notifications yet.")