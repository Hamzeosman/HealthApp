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
    page_title="HealthApp — PT Dashboard",
    page_icon="🧑‍🏫",
    layout="wide"
)

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
            WHERE u.role = 'user'
            LEFT JOIN workout_exercises we ON ws.id = we.session_id
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
            SELECT user_id, date, sleep_hours, energy_level, stress_level
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

    return clients, streaks, goals, records, recovery, recommendations, plans, notifications

clients, streaks, goals, records, recovery, recommendations, plans, notifications = load_all_clients()

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.title("PT Dashboard")
    st.markdown("*Personal Trainer View*")
    st.markdown("---")

    page = st.radio("Navigation", [
        "Client Overview",
        "Client Detail",
        "Muscle Balance Analysis",
        "Recovery & Readiness",
        "Progress Tracking",
        "Recommendations",
        "Training Plans",
        "Notifications"
    ])

    st.markdown("---")
    st.metric("Total clients", len(clients))
    active = clients[clients['last_session'].notna()]
    st.metric("Active this month", len(active))
    st.markdown("---")
    st.caption("HealthApp PT Dashboard")
    st.caption("Data Engineer: Abdulrahman Fahmi")

# ================================
# CLIENT OVERVIEW
# ================================
if page == "Client Overview":
    st.title("Client Overview")
    st.markdown("All your clients at a glance.")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total clients", len(clients))
    with col2:
        avg_sessions = clients['total_sessions'].mean()
        st.metric("Avg sessions/client", f"{avg_sessions:.1f}")
    with col3:
        active_clients = len(clients[clients['total_sessions'] > 0])
        st.metric("Active clients", active_clients)
    with col4:
        avg_rpe = clients['avg_rpe'].mean()
        st.metric("Avg RPE", f"{avg_rpe:.1f}/10" if not pd.isna(avg_rpe) else "N/A")

    st.markdown("---")

    # Client table with color coding
    st.subheader("Client list")
    display = clients[['name', 'email', 'fitness_level', 'fitness_goal',
                       'total_sessions', 'last_session', 'avg_rpe']].copy()
    display.columns = ['Name', 'Email', 'Level', 'Goal',
                       'Sessions', 'Last Session', 'Avg RPE']
    display['Goal'] = display['Goal'].str.replace('_', ' ').str.title()
    display['Level'] = display['Level'].str.title()
    st.dataframe(display, use_container_width=True, height=400)

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sessions per client")
        if not clients.empty:
            fig = px.bar(
                clients.sort_values('total_sessions', ascending=True),
                x='total_sessions', y='name', orientation='h',
                color='total_sessions', color_continuous_scale='Blues',
                labels={'total_sessions': 'Sessions', 'name': 'Client'}
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=300)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Client goals distribution")
        if not clients.empty and clients['fitness_goal'].notna().any():
            goal_counts = clients['fitness_goal'].value_counts().reset_index()
            goal_counts.columns = ['Goal', 'Count']
            goal_counts['Goal'] = goal_counts['Goal'].str.replace('_', ' ').str.title()
            fig = px.pie(
                goal_counts, values='Count', names='Goal',
                color_discrete_sequence=['#378ADD', '#D85A30', '#1D9E75',
                                         '#EF9F27', '#7F77DD'],
                hole=0.4
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

# ================================
# CLIENT DETAIL
# ================================
elif page == "Client Detail":
    st.title("Client Detail")
    st.markdown("---")

    if clients.empty:
        st.info("No clients found.")
    else:
        selected = st.selectbox("Select client", clients['name'].tolist())
        client = clients[clients['name'] == selected].iloc[0]
        client_id = int(client['id'])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(client['name'])
            st.write(f"Email: {client['email']}")
            st.write(f"Level: {client['fitness_level']}")
            st.write(f"Goal: {str(client['fitness_goal']).replace('_', ' ')}")
        with col2:
            st.metric("Total sessions", client['total_sessions'])
            st.metric("Last session", str(client['last_session'])[:10] if client['last_session'] else "Never")
        with col3:
            streak_data = streaks[streaks['user_id'] == client_id]
            if not streak_data.empty:
                s = streak_data.iloc[0]
                st.metric("Current streak", f"{s['current_streak']} days")
                st.metric("Best streak", f"{s['longest_streak']} days")

        st.markdown("---")

        # Goals
        st.subheader("Goals")
        client_goals = goals[goals['user_id'] == client_id]
        if not client_goals.empty:
            for _, row in client_goals.iterrows():
                if row['goal_type'] in ['target_weight', 'target_body_fat']:
                    progress = max(0, min(100, (1 - (row['current_value'] - row['target_value']) / max(row['current_value'], 0.01)) * 100)) if row['current_value'] > row['target_value'] else 100
                else:
                    progress = min(100, (row['current_value'] / row['target_value']) * 100) if row['target_value'] > 0 else 0
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{row['goal_type'].replace('_', ' ').title()}** — {row['current_value']} / {row['target_value']} {row['unit']}")
                    st.progress(int(progress))
                with col2:
                    st.metric("Progress", f"{progress:.0f}%")

        st.markdown("---")

        # Personal records
        st.subheader("Personal records")
        client_records = records[records['user_id'] == client_id]
        if not client_records.empty:
            fig = px.bar(
                client_records.sort_values('weight_kg', ascending=True),
                x='weight_kg', y='exercise', orientation='h',
                color='weight_kg', color_continuous_scale='Greens',
                labels={'weight_kg': 'Weight (kg)', 'exercise': 'Exercise'}
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=250)
            st.plotly_chart(fig, use_container_width=True)

        # Recommendations for client
        st.subheader("Current recommendations")
        client_recs = recommendations[recommendations['user_id'] == client_id]
        if not client_recs.empty:
            for _, row in client_recs.iterrows():
                if row['score'] >= 0.8:
                    st.error(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
                elif row['score'] >= 0.5:
                    st.warning(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
                else:
                    st.info(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")

# ================================
# MUSCLE BALANCE ANALYSIS
# ================================
elif page == "Muscle Balance Analysis":
    st.title("Muscle Balance Analysis")
    st.markdown("Identify muscle imbalances across all clients.")
    st.markdown("---")

    with engine.connect() as conn:
        muscle_data = pd.read_sql(text("""
            SELECT
                u.name AS client,
                bp.name AS body_part,
                COUNT(we.id) AS exercises_logged,
                SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS volume
            FROM users u
            JOIN workout_sessions ws ON u.id = ws.user_id
            JOIN workout_exercises we ON ws.id = we.session_id
            JOIN exercises e ON we.exercise_id = e.id
            JOIN body_parts bp ON e.body_part_id = bp.id
            GROUP BY u.name, bp.name
            ORDER BY u.name, exercises_logged DESC
        """), conn)

    if not muscle_data.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Volume by muscle group (all clients)")
            total_muscle = muscle_data.groupby('body_part')['volume'].sum().reset_index()
            total_muscle = total_muscle.sort_values('volume', ascending=True)
            fig = px.bar(
                total_muscle, x='volume', y='body_part', orientation='h',
                color='volume', color_continuous_scale='RdYlGn',
                labels={'volume': 'Total volume (kg)', 'body_part': 'Muscle group'}
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Muscle balance heatmap")
            pivot = muscle_data.pivot_table(
                index='client', columns='body_part',
                values='exercises_logged', fill_value=0
            )
            fig = px.imshow(
                pivot, color_continuous_scale='Blues',
                labels={'color': 'Exercises', 'x': '', 'y': ''},
                title='Exercises per muscle group per client',
                aspect='auto'
            )
            fig.update_layout(height=380,
                xaxis_tickangle=0,
                margin=dict(l=120, r=20, t=60, b=20))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Clients with muscle imbalances")
        for client_name in muscle_data['client'].unique():
            client_data = muscle_data[muscle_data['client'] == client_name]
            if len(client_data) > 0:
                max_vol = client_data['volume'].max()
                min_vol = client_data['volume'].min()
                if max_vol > 0 and min_vol / max_vol < 0.3:
                    weak = client_data.nsmallest(2, 'volume')['body_part'].tolist()
                    st.warning(f"**{client_name}** — Weak areas: {', '.join(weak)}")
    else:
        st.info("No training data available yet.")

# ================================
# RECOVERY & READINESS
# ================================
elif page == "Recovery & Readiness":
    st.title("Recovery & Readiness")
    st.markdown("Monitor client recovery and training readiness.")
    st.markdown("---")

    if not recovery.empty:
        # Merge with client names
        recovery_named = recovery.merge(
            clients[['id', 'name']], left_on='user_id', right_on='id'
        )

        col1, col2, col3 = st.columns(3)
        with col1:
            avg_sleep = recovery_named['sleep_hours'].mean()
            status = "Optimal" if avg_sleep >= 7 else "Low"
            st.metric("Avg sleep (all clients)", f"{avg_sleep:.1f}h", status)
        with col2:
            avg_energy = recovery_named['energy_level'].mean()
            st.metric("Avg energy", f"{avg_energy:.1f}/10")
        with col3:
            avg_stress = recovery_named['stress_level'].mean()
            st.metric("Avg stress", f"{avg_stress:.1f}/10")

        st.markdown("---")
        st.subheader("Client readiness today")

        latest = recovery_named.sort_values('date').groupby('name').last().reset_index()
        for _, row in latest.iterrows():
            sleep = row['sleep_hours']
            energy = row['energy_level']
            stress = row['stress_level']

            if sleep >= 7 and energy >= 7 and stress <= 4:
                status = "READY TO TRAIN HARD"
                st.success(f"**{row['name']}** — {status} | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
            elif sleep < 6 or energy < 5:
                status = "NEEDS REST"
                st.error(f"**{row['name']}** — {status} | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
            elif stress > 7:
                status = "HIGH STRESS — LIGHT SESSION"
                st.warning(f"**{row['name']}** — {status} | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
            else:
                status = "GOOD"
                st.info(f"**{row['name']}** — {status} | Sleep: {sleep}h | Energy: {energy}/10 | Stress: {stress}/10")
    else:
        st.info("No recovery data logged yet.")

# ================================
# PROGRESS TRACKING
# ================================
elif page == "Progress Tracking":
    st.title("Progress Tracking")
    st.markdown("Track strength and volume progress for each client.")
    st.markdown("---")

    if clients.empty:
        st.info("No clients found.")
    else:
        selected = st.selectbox("Select client", clients['name'].tolist())
        client_id = int(clients[clients['name'] == selected]['id'].values[0])

        with engine.connect() as conn:
            volume_data = pd.read_sql(text("""
                SELECT
                    DATE_TRUNC('week', ws.date) AS week,
                    SUM(we.sets * we.reps * COALESCE(we.weight_kg, 0)) AS volume,
                    AVG(we.rpe) AS avg_rpe,
                    COUNT(DISTINCT ws.id) AS sessions
                FROM workout_sessions ws
                JOIN workout_exercises we ON ws.id = we.session_id
                WHERE ws.user_id = :uid
                GROUP BY week
                ORDER BY week
            """), conn, params={"uid": client_id})

            pr_data = pd.read_sql(text("""
                SELECT pr.date, e.name AS exercise, pr.weight_kg
                FROM personal_records pr
                JOIN exercises e ON pr.exercise_id = e.id
                WHERE pr.user_id = :uid
                ORDER BY pr.date
            """), conn, params={"uid": client_id})

        if not volume_data.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Weekly volume")
                fig = px.bar(volume_data, x='week', y='volume',
                    color_discrete_sequence=['#378ADD'],
                    labels={'week': '', 'volume': 'Volume (kg)'},
                    hover_data={'volume': ':.0f'})
                fig.update_layout(height=300, xaxis_tickangle=-30,
                    yaxis_title='Volume (kg)', xaxis_title='',
                    bargap=0.2)
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.subheader("RPE trend")
                fig = px.line(volume_data, x='week', y='avg_rpe',
                    markers=True, color_discrete_sequence=['#D85A30'],
                    labels={'week': 'Week', 'avg_rpe': 'Avg RPE'})
                fig.add_hline(y=8, line_dash="dash", line_color="orange",
                    annotation_text="RPE 8 target")
                fig.update_layout(height=300, xaxis_tickangle=-30,
                    yaxis_range=[5, 10], xaxis_title='')
                st.plotly_chart(fig, use_container_width=True)

        if not pr_data.empty:
            st.subheader("Personal record progression")
            exercises = pr_data['exercise'].unique().tolist()
            selected_ex = st.selectbox("Select exercise", exercises)
            ex_data = pr_data[pr_data['exercise'] == selected_ex]
            fig = px.line(ex_data, x='date', y='weight_kg',
                markers=True, color_discrete_sequence=['#1D9E75'],
                labels={'date': 'Date', 'weight_kg': 'Weight (kg)'},
                title=f"{selected_ex} — PR progression")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No personal records logged yet for this client.")

# ================================
# RECOMMENDATIONS
# ================================
elif page == "Recommendations":
    st.title("Smart Recommendations")
    st.markdown("AI-generated exercise recommendations for all clients.")
    st.markdown("---")

    if not recommendations.empty:
        recs_named = recommendations.merge(
            clients[['id', 'name']], left_on='user_id', right_on='id'
        )
        for client_name in recs_named['name'].unique():
            st.subheader(f"{client_name}")
            client_recs = recs_named[recs_named['name'] == client_name]
            for _, row in client_recs.iterrows():
                if row['score'] >= 0.8:
                    st.error(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
                elif row['score'] >= 0.5:
                    st.warning(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
                else:
                    st.info(f"**{row['exercise']}** ({row['body_part']}) — {row['reason']}")
            st.markdown("---")
    else:
        st.info("No recommendations generated yet. Run the recommendation pipeline.")

# ================================
# TRAINING PLANS
# ================================
elif page == "Training Plans":
    st.title("Training Plans")
    st.markdown("Assign and manage training plans for clients.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Available plans")
        for _, plan in plans.iterrows():
            weeks = f"{plan['duration_weeks']}w" if plan['duration_weeks'] > 0 else "Ongoing"
            level = {'nybörjare': 'Beginner', 'medel': 'Intermediate', 'avancerad': 'Advanced'}.get(plan['difficulty'], plan['difficulty'])
            goal = plan['goal'].replace('_', ' ').title()
            st.markdown(f"""
            <div style="border-left: 3px solid #378ADD; padding: 10px;
                margin-bottom: 10px; background: #f8f9fa; border-radius: 6px;">
                <strong>{plan['name']}</strong><br>
                <span style="color: #555; font-size: 13px;">
                {goal} | {weeks} | {level} | {plan['days_per_week']}x/week
                </span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader("Assign plan to client")
        selected_client = st.selectbox("Client", clients['name'].tolist())
        selected_plan = st.selectbox("Plan", plans['name'].tolist())
        start_date = st.date_input("Start date")
        if st.button("Assign plan"):
            client_id = int(clients[clients['name'] == selected_client]['id'].values[0])
            plan_id = int(plans[plans['name'] == selected_plan]['id'].values[0])
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO user_training_plans
                        (user_id, plan_id, start_date, is_active)
                    VALUES (:uid, :pid, :start, TRUE)
                    ON CONFLICT DO NOTHING
                """), {"uid": client_id, "pid": plan_id, "start": str(start_date)})
                conn.commit()
            st.success(f"Plan assigned to {selected_client}!")
            st.cache_data.clear()

# ================================
# NOTIFICATIONS
# ================================
elif page == "Notifications":
    st.title("Notifications")
    st.markdown("All client notifications and alerts.")
    st.markdown("---")

    if not notifications.empty:
        notif_named = notifications.merge(
            clients[['id', 'name']], left_on='user_id', right_on='id', how='left'
        )
        unread = notif_named[notif_named['is_read'] == False]
        st.metric("Unread notifications", len(unread))
        st.markdown("---")

        type_filter = st.selectbox("Filter by type", [
            "All", "workout_reminder", "personal_record",
            "streak_milestone", "weekly_report", "goal_achieved"
        ])

        filtered = notif_named if type_filter == "All" else \
            notif_named[notif_named['notification_type'] == type_filter]

        for _, row in filtered.iterrows():
            client_name = row['name'] if 'name' in row and pd.notna(row['name']) else "Unknown"
            notif_type = row['notification_type']
            if notif_type == 'personal_record':
                st.success(f"**{client_name}** — {row['title']}: {row['message']}")
            elif notif_type == 'workout_reminder':
                st.warning(f"**{client_name}** — {row['title']}: {row['message']}")
            elif notif_type == 'streak_milestone':
                st.info(f"**{client_name}** — {row['title']}: {row['message']}")
            else:
                st.info(f"**{client_name}** — {row['title']}: {row['message']}")
    else:
        st.info("No notifications yet.")