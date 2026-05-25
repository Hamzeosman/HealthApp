import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(page_title="HealthApp v3", page_icon="🏋️", layout="wide")

st.markdown("""
<style>
.metric-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 18px 20px;
    text-align: center;
    margin-bottom: 12px;
}
.metric-value { font-size: 32px; font-weight: 700; }
.metric-label { font-size: 12px; color: #9ca3af; margin-top: 4px; }
.metric-sub   { font-size: 11px; margin-top: 6px; }
.risk-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-top: 4px;
}
.badge-ok     { background: #e8f8f2; color: #0f6e56; }
.badge-warn   { background: #faeeda; color: #854f0b; }
.badge-danger { background: #fcebeb; color: #a32d2d; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────
def risk_badge(val):
    if val > 60:
        return f'<span class="risk-badge badge-danger">HIGH {val:.0f}</span>'
    elif val > 40:
        return f'<span class="risk-badge badge-warn">MED {val:.0f}</span>'
    return f'<span class="risk-badge badge-ok">OK {val:.0f}</span>'

def readiness_color(r):
    if r >= 75: return "#1D9E75"
    elif r >= 60: return "#EF9F27"
    return "#E24B4A"

def readiness_emoji(r):
    if r >= 75: return "🟢"
    elif r >= 60: return "🟡"
    return "🔴"

def intensity_color(i):
    return {"rest":"#E24B4A","very_light":"#D85A30","light":"#EF9F27",
            "moderate":"#378ADD","hard":"#1D9E75","very_hard":"#7F77DD"}.get(i,"#888")

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("🏋️ HealthApp v3")
    st.markdown("*AI-driven coaching platform*")
    st.markdown("---")

    try:
        health = requests.get(f"{API}/health", timeout=2).json()
        if health['status'] == 'healthy':
            st.success(f"✅ API healthy | DB connected")
        else:
            st.error("API unhealthy")
    except:
        st.error("❌ API offline")

    st.markdown("---")

    users_data = requests.get(f"{API}/users/").json()
    user_options = {u['name']: u['id'] for u in users_data}
    selected_name = st.selectbox("👤 Select user", list(user_options.keys()))
    user_id = user_options[selected_name]

    # Mini readiness widget in sidebar
    try:
        r_data = requests.get(f"{API}/users/{user_id}/readiness").json()
        r = r_data['readiness_score']
        color = readiness_color(r)
        emoji = readiness_emoji(r)
        st.markdown(f"""
        <div style="background:#111827; border:1px solid #1f2937; border-radius:8px;
            padding:10px; text-align:center; margin:8px 0;">
            <div style="font-size:28px; font-weight:700; color:{color};">{r:.0f}</div>
            <div style="font-size:11px; color:#9ca3af;">{emoji} Readiness today</div>
            <div style="font-size:11px; color:{intensity_color(r_data['recommended_intensity'])};
                margin-top:4px;">→ {r_data['recommended_intensity'].upper()}</div>
        </div>""", unsafe_allow_html=True)
    except:
        pass

    st.markdown("---")
    page = st.radio("Navigation", [
        "🧠 AI Coach",
        "📊 Readiness & Trends",
        "📈 Volume & Fatigue",
        "🏆 Progression & PRs",
        "😴 Sleep Analytics",
        "⚠️ Risk Dashboard",
        "🏋️ PT Overview",
        "🔔 Notifications",
        "⚙️ Scheduler",
    ])

# ── AI COACH ─────────────────────────────────────────────────
if page == "🧠 AI Coach":
    st.title("🧠 AI Coach")
    st.markdown("---")

    coach = requests.get(f"{API}/users/{user_id}/coach").json()
    r_data = requests.get(f"{API}/users/{user_id}/readiness").json()
    r = coach['readiness_score']
    risks = coach['risk_scores']
    # Synka intensity med readiness score
    if r >= 75:
        synced_intensity = "hard"
    elif r >= 65:
        synced_intensity = "moderate"
    elif r >= 55:
        synced_intensity = "light"
    elif r >= 40:
        synced_intensity = "very_light"
    else:
        synced_intensity = "rest"
    coach['recommended_intensity'] = synced_intensity

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    rc = readiness_color(r)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{rc};">{r:.0f}</div>
            <div class="metric-label">Readiness</div>
            <div class="metric-sub" style="color:{rc};">{readiness_emoji(r)}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        ic = intensity_color(coach['recommended_intensity'])
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{ic}; font-size:20px;">
                {coach['recommended_intensity'].upper()}</div>
            <div class="metric-label">Recommended intensity</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{'#E24B4A' if risks['injury_risk']>60 else '#EF9F27' if risks['injury_risk']>40 else '#1D9E75'};">
                {risks['injury_risk']:.0f}</div>
            <div class="metric-label">Injury risk /100</div>
            <div class="metric-sub">{risk_badge(risks['injury_risk'])}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{'#E24B4A' if risks['dropout_risk']>60 else '#EF9F27' if risks['dropout_risk']>40 else '#1D9E75'};">
                {risks['dropout_risk']:.0f}</div>
            <div class="metric-label">Dropout risk /100</div>
            <div class="metric-sub">{risk_badge(risks['dropout_risk'])}</div>
        </div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{'#E24B4A' if risks['overtraining_risk']>60 else '#EF9F27' if risks['overtraining_risk']>40 else '#1D9E75'};">
                {risks['overtraining_risk']:.0f}</div>
            <div class="metric-label">Overtraining /100</div>
            <div class="metric-sub">{risk_badge(risks['overtraining_risk'])}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Coach message — färg baserad på korrekt threshold
    st.subheader("💬 Coach säger")
    if r >= 75:
        st.success(f"**{coach['coach_message']}**")
    elif r >= 55:
        st.warning(f"**{coach['coach_message']}**")
    else:
        st.error(f"**{coach['coach_message']}**")

    # Next action med intensitetsfärg
    ic = intensity_color(coach['recommended_intensity'])
    st.markdown(f"""
    <div style="background:#111827; border-left:4px solid {ic};
        border-radius:8px; padding:14px 16px; margin:8px 0;">
        <span style="color:#9ca3af; font-size:12px;">NEXT ACTION</span><br>
        <span style="color:{ic}; font-weight:600;">→ {coach['next_action']}</span>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⚠️ Warnings")
        if coach['warnings']:
            for w in coach['warnings']:
                sev = w['severity']
                icon = {"critical":"🔴","high":"🟠","medium":"🔵","low":"⚪"}.get(sev,"⚪")
                if sev == 'critical':
                    st.error(f"{icon} **{w['type'].replace('_',' ').title()}**\n\n{w['message']}")
                elif sev == 'high':
                    st.warning(f"{icon} **{w['type'].replace('_',' ').title()}**\n\n{w['message']}")
                else:
                    st.info(f"{icon} **{w['type'].replace('_',' ').title()}**\n\n{w['message']}")
        else:
            st.success("✅ Inga varningar — allt ser bra ut!")

    with col2:
        st.subheader("✅ Recommendations")
        if coach['recommendations']:
            for rec in coach['recommendations']:
                with st.expander(f"#{rec['priority']} — {rec['category'].replace('_',' ').title()}", expanded=rec['priority']==1):
                    st.markdown(f"**🎯 Action:** {rec['action']}")
                    st.markdown(f"**💡 Reason:** {rec['reason']}")
        else:
            st.success("Ingen åtgärd behövs idag!")

    # Risk bar chart med korrekt färgkodning
    st.markdown("---")
    st.subheader("📊 Risk overview")
    categories = ['Injury', 'Dropout', 'Plateau', 'Overtraining']
    values = [risks['injury_risk'], risks['dropout_risk'],
              risks['plateau_risk'], risks['overtraining_risk']]
    colors = ['#E24B4A' if v > 60 else '#EF9F27' if v > 40 else '#1D9E75' for v in values]
    labels = ['HIGH' if v > 60 else 'MEDIUM' if v > 40 else 'OK' for v in values]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories, y=values,
        marker_color=colors,
        text=[f"{v:.0f} — {l}" for v, l in zip(values, labels)],
        textposition='outside'
    ))
    fig.add_hline(y=60, line_dash="dash", line_color="#E24B4A",
                  annotation_text="High risk threshold (60)")
    fig.add_hline(y=40, line_dash="dash", line_color="#EF9F27",
                  annotation_text="Medium risk threshold (40)")
    fig.update_layout(height=300, yaxis=dict(range=[0, 110], title="Risk score /100"),
                      showlegend=False, margin=dict(t=20, b=0))
    st.plotly_chart(fig, width="stretch")

# ── READINESS & TRENDS ────────────────────────────────────────
elif page == "📊 Readiness & Trends":
    st.title("📊 Readiness & Recovery")
    st.markdown("---")

    r = requests.get(f"{API}/users/{user_id}/readiness").json()
    f = requests.get(f"{API}/users/{user_id}/fatigue").json()
    feat = requests.get(f"{API}/users/{user_id}/features").json()

    # Top cards
    col1, col2, col3, col4 = st.columns(4)
    rc = readiness_color(r['readiness_score'])
    zone_color = {'optimal':'#1D9E75','caution':'#EF9F27',
                  'danger':'#E24B4A','undertraining':'#378ADD'}.get(f['training_zone'],'#888')

    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{rc};">{r['readiness_score']:.0f}</div>
            <div class="metric-label">Readiness Score</div>
            <div class="metric-sub" style="color:{rc};">{r['status_message']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:#378ADD;">{r['recovery_score']:.0f}</div>
            <div class="metric-label">Recovery Score</div>
            <div class="metric-sub" style="color:#9ca3af;">Sleep 35% + Energy 30% + Stress 20%</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{zone_color};">{f['acwr']:.2f}</div>
            <div class="metric-label">ACWR</div>
            <div class="metric-sub" style="color:{zone_color};">{f['training_zone'].upper()}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        deload_color = "#E24B4A" if f['deload_recommended'] else "#1D9E75"
        deload_text = "⚠️ DELOAD!" if f['deload_recommended'] else "✅ Normal"
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="color:{deload_color}; font-size:22px;">{deload_text}</div>
            <div class="metric-label">Training recommendation</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("😴 Recovery metrics")
        sleep = r.get('sleep_hours')
        energy = r.get('energy_level')
        stress = r.get('stress_level')

        if sleep:
            sleep_color = "🟢" if sleep >= 7 else "🟡" if sleep >= 6 else "🔴"
            st.metric(f"{sleep_color} Sleep hours", f"{sleep:.1f}h",
                delta="Good" if sleep >= 7 else "Low")
        if energy:
            energy_color = "🟢" if energy >= 7 else "🟡" if energy >= 5 else "🔴"
            st.metric(f"{energy_color} Energy level", f"{energy:.1f}/10")
        if stress:
            stress_color = "🟢" if stress <= 4 else "🟡" if stress <= 7 else "🔴"
            st.metric(f"{stress_color} Stress level", f"{stress:.1f}/10",
                delta="High" if stress > 7 else "OK",
                delta_color="inverse")

        if feat:
            st.markdown("---")
            st.markdown("**7-day averages**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Sleep consistency", f"{feat.get('sleep_consistency_score',0):.0f}%")
                st.metric("HRV avg", f"{feat.get('hrv_7d_avg') or 0:.1f} ms")
            with col_b:
                st.metric("Resting HR", f"{feat.get('resting_hr_7d_avg') or 0:.0f} bpm")
                st.metric("Consistency 30d", f"{feat.get('workout_consistency_30d',0):.0f}%")

    with col2:
        st.subheader("⚡ Training load")
        st.metric("Acute load (7d)", f"{f['acute_load']:,.0f} kg")
        st.metric("Chronic load (28d)", f"{f['chronic_load']:,.0f} kg")

        # Load comparison bar
        max_load = max(f['acute_load'], f['chronic_load'], 1)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Acute (7d)', x=['Load'],
            y=[f['acute_load']], marker_color='#378ADD'))
        fig.add_trace(go.Bar(name='Chronic (28d)', x=['Load'],
            y=[f['chronic_load']], marker_color='#9ca3af'))
        fig.update_layout(barmode='group', height=180,
            margin=dict(t=10,b=10), showlegend=True,
            legend=dict(orientation='h', y=-0.3))
        st.plotly_chart(fig, width="stretch")

        st.metric("Fatigue score", f"{f['fatigue_score']:.1f}/100")
        if f['deload_recommended']:
            st.error("🔔 Deload rekommenderas! Minska volym med 40-50%.")

    # ACWR zones med bättre visualisering
    st.markdown("---")
    st.subheader("📈 ACWR Zones — var befinner du dig?")

    acwr_val = f['acwr']
    fig = go.Figure()
    # Zones
    fig.add_hrect(y0=0, y1=0.8, fillcolor="#378ADD", opacity=0.12, line_width=0)
    fig.add_hrect(y0=0.8, y1=1.3, fillcolor="#1D9E75", opacity=0.12, line_width=0)
    fig.add_hrect(y0=1.3, y1=1.5, fillcolor="#EF9F27", opacity=0.12, line_width=0)
    fig.add_hrect(y0=1.5, y1=2.5, fillcolor="#E24B4A", opacity=0.12, line_width=0)

    # Zone labels
    for y, label in [(0.4,"Undertraining"), (1.05,"✅ Optimal"), (1.4,"⚠️ Caution"), (2.0,"🔴 Danger")]:
        fig.add_annotation(x=0.02, y=y, text=label, showarrow=False,
            xref="paper", yref="y", font=dict(size=11, color="#9ca3af"), xanchor="left")

    # Current ACWR marker
    fig.add_trace(go.Scatter(
        x=["Current ACWR"], y=[acwr_val],
        mode='markers+text',
        marker=dict(size=24, color=zone_color, symbol='diamond'),
        text=[f"ACWR: {acwr_val:.2f}"],
        textposition='middle right',
        name=f"ACWR: {acwr_val:.2f}"
    ))

    # Threshold lines
    for y, color, label in [(0.8,"#378ADD","Min optimal (0.8)"),
                             (1.3,"#EF9F27","Caution (1.3)"),
                             (1.5,"#E24B4A","Danger (1.5)")]:
        fig.add_hline(y=y, line_dash="dash", line_color=color,
                      line_width=1, annotation_text=label,
                      annotation_position="right")

    fig.update_layout(height=300, yaxis=dict(range=[0, 2.5], title="ACWR"),
                      xaxis=dict(showticklabels=False),
                      showlegend=False, margin=dict(t=20, r=120))
    st.plotly_chart(fig, width="stretch")

    # Readiness historik via fatigue_scores
    st.markdown("---")
    st.subheader("📅 Readiness trend — historik")
    try:
        hist = requests.get(f"{API}/users/{user_id}/readiness-history").json()
        if hist and len(hist) > 0:
            df_hist = pd.DataFrame(hist)
            df_hist['date'] = pd.to_datetime(df_hist['date']).dt.date
            fig = go.Figure()
            # Readiness linje
            fig.add_trace(go.Scatter(
                x=df_hist['date'], y=df_hist['readiness_score'],
                mode='lines+markers', name='Readiness',
                line=dict(color='#1D9E75', width=2),
                marker=dict(size=8), fill='tozeroy',
                fillcolor='rgba(29,158,117,0.1)'
            ))
            # Recovery linje
            fig.add_trace(go.Scatter(
                x=df_hist['date'], y=df_hist['recovery_score'],
                mode='lines+markers', name='Recovery',
                line=dict(color='#378ADD', width=2, dash='dot'),
                marker=dict(size=6)
            ))
            # ACWR på sekundär axel
            fig.add_trace(go.Scatter(
                x=df_hist['date'], y=df_hist['acwr'],
                mode='lines+markers', name='ACWR',
                line=dict(color='#EF9F27', width=1),
                marker=dict(size=5), yaxis='y2'
            ))
            fig.add_hline(y=70, line_dash="dot", line_color="#1D9E75",
                          annotation_text="Good readiness (70)")
            fig.add_hline(y=55, line_dash="dot", line_color="#EF9F27",
                          annotation_text="Low readiness (55)")
            fig.update_layout(
                height=300, title="Readiness & Recovery over time",
                yaxis=dict(title="Score /100", range=[0,100]),
                yaxis2=dict(title="ACWR", overlaying='y', side='right',
                           range=[0,2]),
                legend=dict(orientation='h', y=-0.2),
                margin=dict(t=40)
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Kör fatigue_pipeline för att bygga readiness-historik.")
    except Exception as e:
        st.info(f"Readiness-historik: {e}")

# ── VOLUME & FATIGUE ──────────────────────────────────────────
elif page == "📈 Volume & Fatigue":
    st.title("📈 Volume & Fatigue Trends")
    st.markdown("---")

    volume = requests.get(f"{API}/users/{user_id}/volume").json()
    features = requests.get(f"{API}/users/{user_id}/features").json()

    if volume:
        df = pd.DataFrame(volume).sort_values('week_label')

        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total = df['total_volume_kg'].sum()
            st.metric("Total volume", f"{total:,.0f} kg")
        with col2:
            avg_sess = df['sessions'].mean()
            st.metric("Avg sessions/week", f"{avg_sess:.1f}")
        with col3:
            avg_rpe = df['avg_rpe'].mean()
            st.metric("Avg RPE", f"{avg_rpe:.1f}/10" if avg_rpe else "N/A")
        with col4:
            last_vol = df['total_volume_kg'].iloc[-1] if len(df) > 0 else 0
            prev_vol = df['total_volume_kg'].iloc[-2] if len(df) > 1 else last_vol
            delta = last_vol - prev_vol
            st.metric("Last week volume", f"{last_vol:,.0f} kg",
                delta=f"{delta:+,.0f} kg vs prev week")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df, x='week_label', y='total_volume_kg',
                color='total_volume_kg', color_continuous_scale='Blues',
                title="Weekly volume (kg)",
                labels={'week_label':'','total_volume_kg':'kg'})
            fig.update_layout(height=300, xaxis_tickangle=-30,
                showlegend=False, coloraxis_showscale=False)
            st.plotly_chart(fig, width="stretch")
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['week_label'], y=df['avg_rpe'],
                mode='lines+markers', name='Avg RPE',
                line=dict(color='#D85A30', width=2),
                marker=dict(size=8)))
            fig.add_hrect(y0=7, y1=8, fillcolor="#1D9E75", opacity=0.1, line_width=0)
            fig.add_hline(y=8, line_dash="dash", line_color="#EF9F27",
                          annotation_text="RPE 8 — hard")
            fig.add_hline(y=7, line_dash="dash", line_color="#1D9E75",
                          annotation_text="RPE 7 — moderate")
            fig.update_layout(height=300, xaxis_tickangle=-30,
                yaxis=dict(range=[0,10], title="RPE"),
                title="Avg RPE per week", showlegend=False)
            st.plotly_chart(fig, width="stretch")

        # Volume + sessions combo
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df['week_label'], y=df['total_volume_kg'],
            name='Volume (kg)', marker_color='#378ADD', opacity=0.7))
        fig.add_trace(go.Scatter(x=df['week_label'], y=df['sessions'],
            name='Sessions', mode='lines+markers',
            line=dict(color='#EF9F27', width=2), yaxis='y2'))
        fig.update_layout(
            height=280, title="Volume vs Sessions per week",
            xaxis_tickangle=-30,
            yaxis=dict(title="Volume (kg)"),
            yaxis2=dict(title="Sessions", overlaying='y', side='right'),
            legend=dict(orientation='h'))
        st.plotly_chart(fig, width="stretch")

    if features:
        st.markdown("---")
        st.subheader("🔬 ML Features — today's snapshot")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("**Training**")
            sess = features.get('sessions_7d') or 0
            vol = features.get('volume_7d') or 0
            rpe = features.get('avg_rpe_7d') or 0
            st.metric("Sessions 7d", int(sess))
            st.metric("Volume 7d", f"{vol:,.0f} kg")
            st.metric("Avg RPE 7d", f"{rpe:.1f}" if rpe else "N/A")
        with col2:
            st.markdown("**Sleep**")
            st.metric("Sleep avg 7d", f"{features.get('sleep_hours_7d_avg', 0):.1f}h")
            st.metric("Sleep quality", f"{features.get('sleep_quality_7d_avg', 0):.1f}/10")
            st.metric("Consistency", f"{features.get('sleep_consistency_score', 0):.0f}%")
        with col3:
            st.markdown("**Biometrics**")
            st.metric("HRV avg", f"{features.get('hrv_7d_avg') or 0:.1f} ms")
            st.metric("Resting HR", f"{features.get('resting_hr_7d_avg') or 0:.0f} bpm")
            st.metric("Energy avg", f"{features.get('energy_7d_avg', 0):.1f}/10")
        with col4:
            st.markdown("**Behavior**")
            st.metric("Days since workout", features.get('days_since_last_workout', 0))
            st.metric("Streak", features.get('streak_current', 0))
            st.metric("Consistency 30d", f"{features.get('workout_consistency_30d', 0):.0f}%")

# ── RISK DASHBOARD ────────────────────────────────────────────
elif page == "⚠️ Risk Dashboard":
    st.title("⚠️ Risk Dashboard")
    st.markdown("---")

    preds = requests.get(f"{API}/users/{user_id}/predictions").json()
    coach = requests.get(f"{API}/users/{user_id}/coach").json()

    risks = {
        "Injury": preds['injury_risk'],
        "Dropout": preds['dropout_risk'],
        "Plateau": preds['plateau_risk'],
        "Overtraining": preds['overtraining_risk'],
    }

    # Risk cards med korrekt färg
    cols = st.columns(4)
    for (label, val), col in zip(risks.items(), cols):
        color = "#E24B4A" if val > 60 else "#EF9F27" if val > 40 else "#1D9E75"
        badge = "HIGH ⚠️" if val > 60 else "MEDIUM" if val > 40 else "OK ✅"
        with col:
            st.markdown(f"""<div class="metric-card" style="border-color:{color}40;">
                <div class="metric-value" style="color:{color};">{val:.0f}</div>
                <div class="metric-label">{label} risk /100</div>
                <div class="metric-sub">
                    <span class="risk-badge {'badge-danger' if val>60 else 'badge-warn' if val>40 else 'badge-ok'}">{badge}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("🤖 AI Recommendation")
        ic = intensity_color(preds['recommended_intensity'])
        st.markdown(f"""
        <div style="background:#111827; border-left:4px solid {ic};
            border-radius:8px; padding:14px 16px;">
            <span style="color:{ic}; font-weight:600; font-size:15px;">
                {preds['recommendation']}</span>
        </div>""", unsafe_allow_html=True)
        st.markdown("")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Intensity", preds['recommended_intensity'].upper())
        with col_b:
            st.metric("Volume multiplier", f"{preds['volume_multiplier']:.1f}x")
        with col_c:
            conf = preds['confidence']
            st.metric("Confidence", f"{conf:.0f}%",
                delta="High" if conf > 70 else "Medium" if conf > 50 else "Low")
    with col2:
        # Risk radar
        categories_r = list(risks.keys())
        values_r = list(risks.values()) + [list(risks.values())[0]]
        categories_r_closed = categories_r + [categories_r[0]]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_r, theta=categories_r_closed,
            fill='toself', fillcolor='rgba(226,75,74,0.15)',
            line=dict(color='#E24B4A', width=2), name='Risk'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            height=280, showlegend=False, margin=dict(t=20)
        )
        st.plotly_chart(fig, width="stretch")

    # Gauge charts med threshold labels
    st.markdown("---")
    st.subheader("📊 Risk gauges")
    fig = go.Figure()
    for i, (label, val) in enumerate(risks.items()):
        color = '#E24B4A' if val > 60 else '#EF9F27' if val > 40 else '#1D9E75'
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=val,
            title={'text': f"{label}<br><span style='font-size:10px;color:gray'>{'HIGH' if val>60 else 'MEDIUM' if val>40 else 'OK'}</span>"},
            gauge={
                'axis': {'range': [0, 100], 'tickvals': [0,40,60,100],
                          'ticktext': ['0','40<br>MED','60<br>HIGH','100']},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 40], 'color': '#e8f8f2'},
                    {'range': [40, 60], 'color': '#fef3cd'},
                    {'range': [60, 100], 'color': '#fde8e8'}
                ],
                'threshold': {
                    'line': {'color': '#E24B4A', 'width': 3},
                    'thickness': 0.75, 'value': 60
                }
            },
            domain={'row': 0, 'column': i}
        ))
    fig.update_layout(grid={'rows': 1, 'columns': 4},
                      height=260, margin=dict(t=40, b=0))
    st.plotly_chart(fig, width="stretch")

# ── PT OVERVIEW ───────────────────────────────────────────────
elif page == "🏋️ PT Overview":
    st.title("🏋️ PT Overview — All Clients")
    st.markdown("---")

    dashboard = requests.get(f"{API}/analytics/readiness-dashboard").json()
    at_risk = requests.get(f"{API}/analytics/at-risk").json()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total clients", len(dashboard))
    with col2:
        avg_r = sum(c['readiness_score'] for c in dashboard if c['readiness_score']) / max(len(dashboard),1)
        st.metric("Avg readiness", f"{avg_r:.0f}/100",
            delta="Good" if avg_r >= 65 else "Low")
    with col3:
        optimal = sum(1 for c in dashboard if c.get('training_zone') == 'optimal')
        st.metric("In optimal zone", f"{optimal}/{len(dashboard)}")
    with col4:
        st.metric("⚠️ At risk", len(at_risk),
            delta="Needs attention" if at_risk else "All OK",
            delta_color="inverse" if at_risk else "normal")

    if at_risk:
        st.markdown("---")
        st.subheader("🔴 At-risk clients — action needed")
        for c in at_risk:
            col1, col2, col3 = st.columns([2,2,4])
            with col1:
                st.error(f"**{c['name']}**")
            with col2:
                st.markdown(f"Dropout: **{c['dropout_risk']:.0f}** | Injury: **{c['injury_risk']:.0f}**")
            with col3:
                st.markdown(f"→ {c['recommendation']}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Client readiness ranking")
        df = pd.DataFrame(dashboard)
        if not df.empty:
            df = df.sort_values('readiness_score')
            df['color'] = df['readiness_score'].apply(readiness_color)
            fig = px.bar(df, x='readiness_score', y='user_name',
                orientation='h', color='readiness_score',
                color_continuous_scale=[[0,'#E24B4A'],[0.4,'#EF9F27'],[0.55,'#1D9E75'],[1,'#1D9E75']],
                range_color=[40, 100],
                labels={'readiness_score':'Readiness /100', 'user_name':''},
                text='readiness_score')
            fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')
            fig.update_layout(height=320, showlegend=False,
                coloraxis_showscale=False, margin=dict(r=40))
            st.plotly_chart(fig, width="stretch")
    with col2:
        st.subheader("📈 ACWR distribution")
        if not df.empty:
            fig = go.Figure()
            for _, row in df.iterrows():
                zone_c = {'optimal':'#1D9E75','caution':'#EF9F27',
                          'danger':'#E24B4A','undertraining':'#378ADD'}.get(row['training_zone'],'#888')
                fig.add_trace(go.Bar(
                    x=[row['user_name']], y=[row['acwr']],
                    marker_color=zone_c, name=row['training_zone'],
                    showlegend=False
                ))
            fig.add_hline(y=0.8, line_dash="dash", line_color="#378ADD",
                line_width=1.5, annotation_text="Min (0.8)", annotation_position="right")
            fig.add_hline(y=1.3, line_dash="dash", line_color="#EF9F27",
                line_width=1.5, annotation_text="Caution (1.3)", annotation_position="right")
            fig.add_hline(y=1.5, line_dash="dash", line_color="#E24B4A",
                line_width=1.5, annotation_text="Danger (1.5)", annotation_position="right")
            fig.update_layout(height=320, yaxis=dict(range=[0,2],title="ACWR"),
                xaxis_tickangle=-20, margin=dict(r=20))
            st.plotly_chart(fig, width="stretch")

    # Full table
    st.markdown("---")
    if not df.empty:
        display = df[['user_name','training_zone','readiness_score',
                      'recovery_score','acwr','last_workout_date','active_goals']].copy()
        display.columns = ['Client','Zone','Readiness','Recovery','ACWR','Last workout','Goals']
        display['Readiness'] = display['Readiness'].round(1)
        display['Recovery'] = display['Recovery'].round(1)
        display['ACWR'] = display['ACWR'].round(3)
        st.dataframe(display.sort_values('Readiness', ascending=False),
                     width="stretch", hide_index=True)

        # Export
        csv = display.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Export client data (CSV)", csv,
            "pt_overview.csv", "text/csv")

# ── SCHEDULER ─────────────────────────────────────────────────
elif page == "⚙️ Scheduler":
    st.title("⚙️ Pipeline Scheduler")
    st.markdown("---")

    status = requests.get(f"{API}/scheduler/status").json()

    col1, col2 = st.columns(2)
    with col1:
        if status['running']:
            st.success("🟢 Scheduler is running")
        else:
            st.error("🔴 Scheduler stopped")
    with col2:
        st.metric("Scheduled jobs", len(status['jobs']))

    st.markdown("---")
    st.subheader("📅 Scheduled jobs")

    job_descriptions = {
        "refresh_views": ("🔄 Refresh materialized views", "Every hour", "low"),
        "feature_store": ("🔬 Feature store pipeline", "Nightly 02:00", "high"),
        "fatigue": ("😴 Fatigue & ACWR pipeline", "Nightly 02:15", "high"),
        "recommendations": ("💡 Recommendations pipeline", "Nightly 02:30", "medium"),
        "streaks": ("🔥 Streaks pipeline", "Nightly 02:45", "medium"),
        "weekly_reports": ("📊 Weekly reports", "Monday 06:00", "low"),
    }

    for job in status['jobs']:
        desc, schedule, priority = job_descriptions.get(job['id'],
            (job['id'], "Scheduled", "low"))
        priority_color = {"high":"#E24B4A","medium":"#EF9F27","low":"#1D9E75"}.get(priority,"#888")

        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            st.markdown(f"**{desc}**")
        with col2:
            st.markdown(f"🕐 {schedule}")
        with col3:
            next_run = job['next_run'][:19] if job['next_run'] else "N/A"
            st.markdown(f"Next: `{next_run}`")
        with col4:
            if st.button("▶️", key=job['id'], help=f"Run {job['id']} now"):
                resp = requests.post(f"{API}/scheduler/run/{job['id']}")
                if resp.status_code == 200:
                    st.success("✅ Triggered!")
                else:
                    st.error("❌ Failed")
        st.markdown("---")

# ── PROGRESSION & PRs ─────────────────────────────────────────
elif page == "🏆 Progression & PRs":
    st.title("🏆 Progression & Personal Records")
    st.markdown("---")

    # PR endpoint finns redan
    from sqlalchemy import text
    import requests as req

    # Hämta PRs via API
    recs = req.get(f"{API}/users/{user_id}/recommendations").json()

    # Hämta volume historik
    volume = req.get(f"{API}/users/{user_id}/volume").json()
    hist = req.get(f"{API}/users/{user_id}/readiness-history").json()

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        if volume:
            df_vol = pd.DataFrame(volume)
            best_week = df_vol.loc[df_vol['total_volume_kg'].idxmax()]
            st.metric("Best week volume", f"{best_week['total_volume_kg']:,.0f} kg",
                delta=f"Week {best_week['week_label']}")
    with col2:
        if volume:
            trend = df_vol['total_volume_kg'].iloc[-1] - df_vol['total_volume_kg'].iloc[0] if len(df_vol) > 1 else 0
            st.metric("Volume trend", f"{trend:+,.0f} kg",
                delta="Increasing" if trend > 0 else "Decreasing",
                delta_color="normal" if trend > 0 else "inverse")
    with col3:
        if hist:
            avg_readiness = sum(h['readiness_score'] for h in hist) / len(hist)
            st.metric("Avg readiness", f"{avg_readiness:.0f}/100")

    st.markdown("---")

    # Volume progression
    if volume:
        st.subheader("📈 Volume progression")
        df_vol = pd.DataFrame(volume).sort_values('week_label')

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_vol['week_label'], y=df_vol['total_volume_kg'],
            mode='lines+markers+text',
            text=[f"{v/1000:.1f}k" for v in df_vol['total_volume_kg']],
            textposition='top center',
            name='Volume (kg)',
            line=dict(color='#378ADD', width=3),
            marker=dict(size=10),
            fill='tozeroy', fillcolor='rgba(55,138,221,0.1)'
        ))
        # Trend linje
        if len(df_vol) > 1:
            import numpy as np
            x_num = list(range(len(df_vol)))
            z = np.polyfit(x_num, df_vol['total_volume_kg'], 1)
            p = np.poly1d(z)
            trend_vals = [p(x) for x in x_num]
            fig.add_trace(go.Scatter(
                x=df_vol['week_label'], y=trend_vals,
                mode='lines', name='Trend',
                line=dict(color='#EF9F27', width=2, dash='dash')
            ))
        fig.update_layout(height=320, xaxis_tickangle=-30,
            yaxis=dict(title="Volume (kg)"),
            legend=dict(orientation='h'), margin=dict(t=20))
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # RPE + Sets progression
    if volume:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("💪 RPE progression")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_vol['week_label'], y=df_vol['avg_rpe'],
                mode='lines+markers', name='Avg RPE',
                line=dict(color='#D85A30', width=2),
                marker=dict(size=8)
            ))
            fig.add_hrect(y0=7, y1=8, fillcolor="#1D9E75", opacity=0.1,
                          annotation_text="Optimal zone (7-8)")
            fig.update_layout(height=260, xaxis_tickangle=-30,
                yaxis=dict(range=[0,10], title="RPE"),
                showlegend=False, margin=dict(t=20))
            st.plotly_chart(fig, width="stretch")
        with col2:
            st.subheader("📊 Sets per week")
            fig = px.bar(df_vol, x='week_label', y='total_sets',
                color='total_sets', color_continuous_scale='Greens',
                labels={'week_label':'','total_sets':'Sets'})
            fig.update_layout(height=260, xaxis_tickangle=-30,
                showlegend=False, coloraxis_showscale=False, margin=dict(t=20))
            st.plotly_chart(fig, width="stretch")

    # Readiness vs Volume correlation
    if volume and hist:
        st.markdown("---")
        st.subheader("🔗 Readiness vs Volume correlation")
        df_r = pd.DataFrame(hist)
        df_r['date_str'] = df_r['date'].astype(str)
        fig = px.scatter(df_r, x='recovery_score', y='readiness_score',
            color='acwr', size=[10]*len(df_r),
            color_continuous_scale='RdYlGn',
            labels={'recovery_score':'Recovery','readiness_score':'Readiness','acwr':'ACWR'},
            title="Recovery vs Readiness (colored by ACWR)")
        fig.update_layout(height=280)
        st.plotly_chart(fig, width="stretch")

# ── SLEEP ANALYTICS ───────────────────────────────────────────
elif page == "😴 Sleep Analytics":
    st.title("😴 Sleep Analytics")
    st.markdown("---")

    features = requests.get(f"{API}/users/{user_id}/features").json()
    readiness = requests.get(f"{API}/users/{user_id}/readiness").json()
    hist = requests.get(f"{API}/users/{user_id}/readiness-history").json()

    if features:
        # KPIs
        col1, col2, col3, col4 = st.columns(4)
        sleep_avg = features.get('sleep_hours_7d_avg') or 0
        sleep_q = features.get('sleep_quality_7d_avg') or 0
        consistency = features.get('sleep_consistency_score') or 0
        hrv = features.get('hrv_7d_avg') or 0

        sleep_color = "#1D9E75" if sleep_avg >= 7 else "#EF9F27" if sleep_avg >= 6 else "#E24B4A"
        with col1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{sleep_color};">{sleep_avg:.1f}h</div>
                <div class="metric-label">Avg sleep 7d</div>
                <div class="metric-sub" style="color:{sleep_color};">
                    {'✅ Good' if sleep_avg >= 7 else '⚠️ Low' if sleep_avg >= 6 else '🔴 Critical'}
                </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            q_color = "#1D9E75" if sleep_q >= 7 else "#EF9F27" if sleep_q >= 5 else "#E24B4A"
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{q_color};">{sleep_q:.1f}</div>
                <div class="metric-label">Sleep quality /10</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            c_color = "#1D9E75" if consistency >= 80 else "#EF9F27" if consistency >= 65 else "#E24B4A"
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{c_color};">{consistency:.0f}%</div>
                <div class="metric-label">Sleep consistency</div>
            </div>""", unsafe_allow_html=True)
        with col4:
            hrv_color = "#1D9E75" if hrv >= 50 else "#EF9F27" if hrv >= 35 else "#E24B4A"
            st.markdown(f"""<div class="metric-card">
                <div class="metric-value" style="color:{hrv_color};">{hrv:.0f}</div>
                <div class="metric-label">HRV avg (ms)</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Sleep vs Recovery scatter
        if hist:
            st.subheader("📊 Sleep impact on readiness")
            df_h = pd.DataFrame(hist)
            col1, col2 = st.columns(2)
            with col1:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_h['date'].astype(str),
                    y=df_h['recovery_score'],
                    mode='lines+markers', name='Recovery',
                    line=dict(color='#378ADD', width=2),
                    marker=dict(size=8)
                ))
                fig.add_trace(go.Scatter(
                    x=df_h['date'].astype(str),
                    y=df_h['readiness_score'],
                    mode='lines+markers', name='Readiness',
                    line=dict(color='#1D9E75', width=2),
                    marker=dict(size=8)
                ))
                fig.update_layout(height=260, title="Recovery & Readiness trend",
                    legend=dict(orientation='h', y=-0.3), margin=dict(t=40))
                st.plotly_chart(fig, width="stretch")
            with col2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df_h['date'].astype(str),
                    y=df_h['acwr'],
                    mode='lines+markers', name='ACWR',
                    line=dict(color='#EF9F27', width=2),
                    fill='tozeroy', fillcolor='rgba(239,159,39,0.1)'
                ))
                fig.add_hline(y=0.8, line_dash="dash", line_color="#378ADD")
                fig.add_hline(y=1.3, line_dash="dash", line_color="#E24B4A")
                fig.update_layout(height=260, title="ACWR trend",
                    yaxis=dict(range=[0,2]), margin=dict(t=40))
                st.plotly_chart(fig, width="stretch")

        st.markdown("---")

        # Sleep recommendations
        st.subheader("💡 Sleep recommendations")
        if sleep_avg < 7:
            st.error(f"🔴 **Sleep deficit detected** — averaging {sleep_avg:.1f}h vs recommended 7-9h")
            st.markdown("""
            **Actions to improve:**
            - Set a consistent bedtime (same time ±30 min)
            - Avoid screens 1h before bed
            - Keep room temperature 16-19°C
            - Avoid caffeine after 14:00
            """)
        elif consistency < 75:
            st.warning(f"⚠️ **Inconsistent sleep pattern** — {consistency:.0f}% consistency")
            st.markdown("""
            **Actions to improve:**
            - Set a fixed wake time even on weekends
            - Avoid naps longer than 20 minutes
            - Create a wind-down routine
            """)
        else:
            st.success(f"✅ **Good sleep habits!** — {sleep_avg:.1f}h avg, {consistency:.0f}% consistent")

        # Resting HR trend
        rhr = features.get('resting_hr_7d_avg') or 0
        if rhr > 0:
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                rhr_color = "#1D9E75" if rhr < 65 else "#EF9F27" if rhr < 75 else "#E24B4A"
                st.metric("Resting HR", f"{rhr:.0f} bpm",
                    delta="Athletic" if rhr < 60 else "Good" if rhr < 70 else "Elevated")
            with col2:
                stress = features.get('stress_7d_avg') or 0
                s_color = "#1D9E75" if stress <= 4 else "#EF9F27" if stress <= 7 else "#E24B4A"
                st.metric("Avg stress 7d", f"{stress:.1f}/10",
                    delta="Low" if stress <= 4 else "High" if stress > 7 else "Moderate",
                    delta_color="normal" if stress <= 4 else "inverse")
    else:
        st.info("No feature data available. Run the feature store pipeline first.")

# ── NOTIFICATIONS ─────────────────────────────────────────────
elif page == "🔔 Notifications":
    st.title("🔔 Notifications & Alerts")
    st.markdown("---")

    # Auto-generated alerts från AI coach för alla users
    dashboard = requests.get(f"{API}/analytics/readiness-dashboard").json()
    at_risk = requests.get(f"{API}/analytics/at-risk").json()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total clients", len(dashboard))
    with col2:
        st.metric("⚠️ At risk", len(at_risk))
    with col3:
        avg_r = sum(c['readiness_score'] for c in dashboard if c['readiness_score']) / max(len(dashboard),1)
        st.metric("Avg readiness", f"{avg_r:.0f}/100")

    st.markdown("---")
    st.subheader("🚨 System alerts")

    alerts = []
    for c in dashboard:
        days_since = (pd.Timestamp.now() - pd.to_datetime(c['last_workout_date'])).days if c['last_workout_date'] else 999
        if days_since > 14:
            alerts.append(("critical", "inactivity", c['user_name'],
                f"No workouts in {days_since} days — high dropout risk"))
        elif days_since > 7:
            alerts.append(("warning", "inactivity", c['user_name'],
                f"No workouts in {days_since} days"))
        if c['readiness_score'] and c['readiness_score'] < 50:
            alerts.append(("critical", "readiness", c['user_name'],
                f"Very low readiness ({c['readiness_score']:.0f}/100)"))
        if c['acwr'] and c['acwr'] > 1.5:
            alerts.append(("critical", "overtraining", c['user_name'],
                f"ACWR {c['acwr']:.2f} — overtraining risk!"))
        if c['deload_recommended']:
            alerts.append(("warning", "deload", c['user_name'],
                "Deload week recommended"))

    if alerts:
        critical = [a for a in alerts if a[0] == "critical"]
        warnings = [a for a in alerts if a[0] == "warning"]

        if critical:
            st.markdown(f"**🔴 Critical ({len(critical)})**")
            for _, atype, name, msg in critical:
                st.error(f"**{name}** [{atype}] — {msg}")

        if warnings:
            st.markdown(f"**🟡 Warnings ({len(warnings)})**")
            for _, atype, name, msg in warnings:
                st.warning(f"**{name}** [{atype}] — {msg}")
    else:
        st.success("✅ No alerts — all clients looking good!")

    st.markdown("---")
    st.subheader("📋 Client status feed")
    for c in sorted(dashboard, key=lambda x: x['readiness_score'] or 0):
        days = (pd.Timestamp.now() - pd.to_datetime(c['last_workout_date'])).days if c['last_workout_date'] else 999
        rc = readiness_color(c['readiness_score'] or 0)
        zone_c = {'optimal':'#1D9E75','caution':'#EF9F27',
                  'danger':'#E24B4A','undertraining':'#378ADD'}.get(c['training_zone'],'#888')
        st.markdown(f"""
        <div style="background:#111827; border-left:3px solid {rc};
            border-radius:8px; padding:12px 16px; margin-bottom:8px;
            display:flex; justify-content:space-between;">
            <div>
                <span style="font-weight:600; color:{rc};">{c['user_name']}</span>
                <span style="color:#9ca3af; font-size:12px; margin-left:8px;">
                    Last workout: {c['last_workout_date'] or 'Never'} ({days}d ago)
                </span>
            </div>
            <div style="text-align:right;">
                <span style="color:{rc}; font-weight:600;">{c['readiness_score']:.0f}/100</span>
                <span style="color:{zone_c}; font-size:12px; margin-left:8px;">
                    {c['training_zone'].upper() if c['training_zone'] else 'N/A'}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Export alerts as CSV
    if alerts:
        df_alerts = pd.DataFrame(alerts, columns=['severity','type','client','message'])
        csv = df_alerts.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Export alerts (CSV)", csv, "alerts.csv", "text/csv")
