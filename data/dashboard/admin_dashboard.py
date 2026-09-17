"""
admin_dashboard.py
Admin-dashboard för HealthApp.
Visar data quality score, pipeline historik och anomalier.
Kör: streamlit run dashboard/admin_dashboard.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))
engine = create_engine(os.getenv("DATABASE_URL"))

st.set_page_config(
    page_title="HealthApp — Admin Dashboard",
    page_icon="shield",
    layout="wide"
)

# ── Dark theme card ───────────────────────────────────────────
def card(icon, title, value, subtitle="", color="#378ADD"):
    return f"""
    <div style="background:#111827; border:1px solid #1f2937; border-radius:10px;
        padding:14px 16px; margin-bottom:10px;">
        <div style="font-size:22px;">{icon}</div>
        <div style="font-size:12px; color:#9ca3af; margin-top:2px;">{title}</div>
        <div style="font-size:22px; font-weight:700; color:{color};">{value}</div>
        <div style="font-size:11px; color:#6b7280;">{subtitle}</div>
    </div>"""


# ── Load data ─────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_pipeline_logs():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT pipeline_name, status, duration_seconds,
                   started_at, finished_at, errors, error_message
            FROM pipeline_logs
            ORDER BY started_at DESC
            LIMIT 100
        """), conn)

@st.cache_data(ttl=60)
def load_quality_history():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT changed_at, old_value
            FROM audit_log
            WHERE table_name = 'data_quality_pipeline'
            ORDER BY changed_at DESC
            LIMIT 30
        """), conn)

@st.cache_data(ttl=60)
def load_anomalies():
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT n.created_at, u.name AS user_name,
                   n.title, n.message, n.notification_type
            FROM notifications n
            JOIN users u ON n.user_id = u.id
            WHERE n.notification_type IN (
                'recovery_alert', 'workout_reminder', 'ai_insight'
            )
            ORDER BY n.created_at DESC
            LIMIT 50
        """), conn)

@st.cache_data(ttl=60)
def load_db_stats():
    with engine.connect() as conn:
        tables = pd.read_sql(text("""
            SELECT relname AS tabell, n_live_tup AS rader
            FROM pg_stat_user_tables
            WHERE n_live_tup > 0
            ORDER BY n_live_tup DESC
            LIMIT 15
        """), conn)
        triggers = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema = 'public'"
        )).scalar()
        constraints = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_schema = 'public' AND constraint_type = 'CHECK'"
        )).scalar()
        indexes = conn.execute(text(
            "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public'"
        )).scalar()
        users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar()
        return tables, triggers, constraints, indexes, users


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("Admin Dashboard")
    st.divider()
    page = st.radio("Navigation", [
        "Oversikt",
        "Data Quality",
        "Pipeline Historik",
        "Anomalier",
        "Databas Status"
    ])
    st.divider()
    if st.button("Kor pipelines nu"):
        with st.spinner("Kör alla pipelines..."):
            import subprocess
            result = subprocess.run(
                ["python", "pipelines/run_all_pipelines.py"],
                capture_output=True, text=True, cwd=os.path.dirname(__file__) + "/.."
            )
            if result.returncode == 0:
                st.success("Alla pipelines körde OK!")
            else:
                st.error(f"Fel: {result.stderr[:200]}")
        st.cache_data.clear()


# ── Översikt ──────────────────────────────────────────────────
if page == "Oversikt":
    st.title("System Oversikt")

    tables, triggers, constraints, indexes, users = load_db_stats()
    logs = load_pipeline_logs()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(card("-", "Användare", users, "i databasen"), unsafe_allow_html=True)
    with col2:
        st.markdown(card("-", "Triggers", triggers, "updated_at + audit"), unsafe_allow_html=True)
    with col3:
        st.markdown(card("-", "CHECK constraints", constraints, "dataintegritet"), unsafe_allow_html=True)
    with col4:
        st.markdown(card("-", "Index", indexes, "query optimering"), unsafe_allow_html=True)

    st.divider()

    # Senaste pipeline-körning
    if not logs.empty:
        last_run = logs.iloc[0]['started_at']
        ok_count = len(logs[logs['status'] == 'success'])
        fail_count = len(logs[logs['status'] == 'error'])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(card("-", "Senaste körning", str(last_run)[:16], "pipeline orchestrator"), unsafe_allow_html=True)
        with col2:
            st.markdown(card("-", "Lyckade pipelines", ok_count, "senaste 100"), unsafe_allow_html=True)
        with col3:
            color = "#ef4444" if fail_count > 0 else "#22c55e"
            st.markdown(card("-", "Misslyckade", fail_count, "senaste 100", color), unsafe_allow_html=True)


# ── Data Quality ──────────────────────────────────────────────
elif page == "Data Quality":
    st.title("Data Quality Dashboard")

    quality_history = load_quality_history()

    if quality_history.empty:
        st.info("Ingen quality-data ännu. Kör data_quality_pipeline.py.")
    else:
        # Parsa senaste rapporten
        latest = quality_history.iloc[0]
        try:
            report = latest["old_value"] if isinstance(latest["old_value"], dict) else json.loads(latest["old_value"])
            issues = report.get('issues', [])
            summary = report.get('summary', '')

            high   = [i for i in issues if i.get('severity') == 'HIGH']
            medium = [i for i in issues if i.get('severity') == 'MEDIUM']
            low    = [i for i in issues if i.get('severity') in ('LOW', 'INFO')]

            # Quality score
            total_checks = 6
            penalty = len(high) * 2 + len(medium)
            score = max(0, round(100 - (penalty / (total_checks * 2)) * 100, 1))

            color = "#22c55e" if score >= 95 else "#f59e0b" if score >= 80 else "#ef4444"

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(card("-", "Data Quality Score", f"{score}%", summary[:50], color), unsafe_allow_html=True)
            with col2:
                st.markdown(card("-", "HIGH issues", len(high), "kritiska problem"), unsafe_allow_html=True)
            with col3:
                st.markdown(card("-", "MEDIUM issues", len(medium), "varningar"), unsafe_allow_html=True)
            with col4:
                st.markdown(card("-", "LOW issues", len(low), "info"), unsafe_allow_html=True)

            st.divider()

            # Checkmatris
            st.subheader("Kontroller")
            checks = {
                "null_values":      ("NULL checks",     "Inga NULL-värden på kritiska kolumner"),
                "duplicates":       ("Dubbletter",       "Inga dubbletter i UNIQUE-kolumner"),
                "out_of_range":     ("Värdeintervall",   "Alla värden inom rimliga gränser"),
                "orphaned_records": ("Foreign Keys",     "Inga orphaned records"),
                "master_data":      ("Master Data",      "Alla övningar har primary_muscle etc"),
                "stale_data":       ("User Aktivitet",   "Users tränar regelbundet"),
            }

            for check_key, (check_name, check_desc) in checks.items():
                check_issues = [i for i in issues if i.get('check') == check_key]
                if check_issues:
                    st.error(f"**{check_name}** — {len(check_issues)} problem: {check_issues[0].get('message', '')}")
                else:
                    st.success(f"**{check_name}** — {check_desc}")

        except Exception as e:
            st.error(f"Kunde inte parsa rapport: {e}")

        # Historik
        st.divider()
        st.subheader("Quality Score Historik")
        if len(quality_history) > 1:
            scores = []
            for _, row in quality_history.iterrows():
                try:
                    r = json.loads(row['old_value'])
                    issues = r.get('issues', [])
                    high = len([i for i in issues if i.get('severity') == 'HIGH'])
                    medium = len([i for i in issues if i.get('severity') == 'MEDIUM'])
                    s = max(0, round(100 - ((high * 2 + medium) / 12) * 100, 1))
                    scores.append({"datum": row['changed_at'], "score": s})
                except:
                    pass
            if scores:
                df_scores = pd.DataFrame(scores)
                fig = px.line(df_scores, x='datum', y='score',
                             title='Data Quality Score över tid',
                             labels={'score': 'Score (%)', 'datum': 'Datum'})
                fig.update_yaxes(range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)


# ── Pipeline Historik ─────────────────────────────────────────
elif page == "Pipeline Historik":
    st.title("Pipeline Historik")

    logs = load_pipeline_logs()

    if logs.empty:
        st.info("Ingen pipeline-historik ännu.")
    else:
        # Summering
        col1, col2, col3 = st.columns(3)
        ok = len(logs[logs['status'] == 'success'])
        fail = len(logs[logs['status'] == 'error'])
        with col1:
            st.metric("Totalt körda", len(logs))
        with col2:
            st.metric("Lyckade", ok)
        with col3:
            st.metric("Misslyckade", fail)

        st.divider()

        # Pipeline status per namn
        st.subheader("Status per pipeline")
        pipeline_stats = logs.groupby('pipeline_name').agg(
            körningar=('status', 'count'),
            lyckade=('status', lambda x: (x == 'success').sum()),
            avg_duration=('duration_seconds', 'mean')
        ).reset_index()

        pipeline_stats['success_rate'] = (pipeline_stats['lyckade'] / pipeline_stats['körningar'] * 100).round(1)
        st.dataframe(pipeline_stats, use_container_width=True)

        st.divider()

        # Senaste körningar
        st.subheader("Senaste körningar")
        display_logs = logs[['pipeline_name', 'status', 'duration_seconds', 'started_at', 'errors']].copy()
        display_logs['status'] = display_logs['status'].map(
            {'success': '✅ success', 'error': '❌ error'}
        )
        st.dataframe(display_logs, use_container_width=True)


# ── Anomalier ─────────────────────────────────────────────────
elif page == "Anomalier":
    st.title("Anomali Historik")

    anomalies = load_anomalies()

    if anomalies.empty:
        st.success("Inga anomalier detekterade.")
    else:
        st.metric("Totalt detekterade anomalier", len(anomalies))

        type_counts = anomalies['notification_type'].value_counts()
        fig = px.bar(type_counts, title='Anomalier per typ',
                    labels={'value': 'Antal', 'index': 'Typ'})
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Senaste anomalier")
        st.dataframe(
            anomalies[['created_at', 'user_name', 'title', 'message']],
            use_container_width=True
        )


# ── Databas Status ────────────────────────────────────────────
elif page == "Databas Status":
    st.title("Databas Status")

    tables, triggers, constraints, indexes, users = load_db_stats()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tabeller med mest data")
        fig = px.bar(tables, x='rader', y='tabell', orientation='h',
                    title='Rader per tabell (top 15)')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Databas statistik")
        stats = pd.DataFrame({
            'Kategori': ['Triggers', 'CHECK constraints', 'Index', 'Användare'],
            'Antal': [triggers, constraints, indexes, users]
        })
        st.dataframe(stats, use_container_width=True)

        st.subheader("PostgreSQL-roller")
        with engine.connect() as conn:
            roles = pd.read_sql(text("""
                SELECT rolname AS roll
                FROM pg_roles
                WHERE rolname LIKE 'healthapp_%'
                ORDER BY rolname
            """), conn)
        st.dataframe(roles, use_container_width=True)