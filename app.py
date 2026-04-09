import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis import (
    load_data, get_summary,
    score_distribution_chart, subject_avg_bar, grade_distribution_chart,
    attendance_vs_score_chart, dept_comparison_chart,
    gender_performance_chart, study_hours_chart,
    radar_chart_dept, correlation_heatmap, dept_comparison_chart,
    top_students_table, bottom_students_table, get_all_students,
    SUBJECTS, SUBJECT_LABELS
)
import json

st.set_page_config(
    page_title="EduMetrics — Student Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600&family=Syne:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: #e2e8f0 !important;
}
.stApp {
    background: #050810 !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 10% 0%, rgba(0,212,255,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 100%, rgba(124,58,237,0.05) 0%, transparent 60%) !important;
}
footer, header { visibility: hidden; }
#MainMenu { visibility: visible !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1440px !important; }
section[data-testid="stSidebar"] > div { padding-top: 1rem !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070b18 0%, #0a0e1f 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebarContent"] { padding: 0 1rem !important; }
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { display: flex; flex-direction: column; gap: 4px; }
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    padding: 10px 14px !important; border-radius: 10px !important;
    transition: all 0.2s ease !important; cursor: pointer !important; border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    background: rgba(255,255,255,0.06) !important; color: #fff !important;
}
[data-testid="stSidebar"] .stRadio label[aria-checked="true"] {
    background: linear-gradient(135deg, rgba(0,212,255,0.12), rgba(124,58,237,0.08)) !important;
    border-color: rgba(0,212,255,0.2) !important; color: #fff !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.82rem !important; line-height: 1.7 !important;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important; padding: 1.3rem 1.2rem !important;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    position: relative !important; overflow: hidden !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px) !important;
    border-color: rgba(0,212,255,0.35) !important;
    box-shadow: 0 8px 32px rgba(0,212,255,0.1) !important;
}
[data-testid="metric-container"]::after {
    content: '' !important; position: absolute !important;
    bottom: 0 !important; left: 0 !important; right: 0 !important; height: 2px !important;
    background: linear-gradient(90deg, #00d4ff, #7c3aed) !important; opacity: 0.5 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important; font-size: 1.9rem !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #00d4ff, #a78bfa) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important; color: #475569 !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important; font-weight: 500 !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 14px !important; overflow: hidden !important;
}

[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: white !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: rgba(0,212,255,0.5) !important; box-shadow: 0 0 0 2px rgba(0,212,255,0.1) !important;
}
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important; color: white !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.5rem 0 !important; }

.page-title {
    font-family: 'Syne', sans-serif; font-size: 2.3rem; font-weight: 800;
    background: linear-gradient(135deg, #00d4ff 0%, #a78bfa 50%, #34d399 100%);
    background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 4s linear infinite; line-height: 1.2; margin-bottom: 0.3rem;
}
@keyframes shimmer { 0% { background-position: 0% center; } 50% { background-position: 100% center; } 100% { background-position: 0% center; } }
.page-sub { color: #334155; font-size: 0.9rem; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); }

.section-label {
    font-family: 'Syne', sans-serif; font-size: 0.78rem; color: #a78bfa;
    text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;
    display: flex; align-items: center; gap: 8px; margin: 2rem 0 1rem;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(167,139,250,0.25), transparent); }

.badge { display:inline-block; padding:3px 11px; border-radius:20px; font-size:0.75rem; font-weight:700; }
.badge-A  { background:rgba(16,185,129,0.15); color:#10b981; border:1px solid rgba(16,185,129,0.3); }
.badge-Ap { background:rgba(0,255,204,0.15); color:#00ffcc; border:1px solid rgba(0,255,204,0.3); }
.badge-B  { background:rgba(0,212,255,0.15); color:#00d4ff; border:1px solid rgba(0,212,255,0.3); }
.badge-C  { background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.3); }
.badge-D  { background:rgba(251,146,60,0.15); color:#fb923c; border:1px solid rgba(251,146,60,0.3); }
.badge-F  { background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid rgba(239,68,68,0.3); }
.badge-pass { background:rgba(52,211,153,0.15); color:#34d399; border:1px solid rgba(52,211,153,0.3); }
.badge-fail { background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid rgba(239,68,68,0.3); }

.insight-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 1.3rem; height: 100%;
}
.insight-num {
    font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
    background: linear-gradient(135deg, #00d4ff, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1; margin: 6px 0 4px;
}
.insight-title { font-size: 0.85rem; color: #94a3b8; font-weight: 500; }

.cmp-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px; padding: 1.4rem;
}
.cmp-name { font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 700; color: #fff; margin-bottom: 1rem; }
.cmp-row { display: flex; justify-content: space-between; padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem; }
.cmp-row:last-child { border: none; }
.cmp-key { color: #475569; }
.cmp-val { color: #e2e8f0; font-weight: 500; }

.prog-wrap { background: rgba(255,255,255,0.07); border-radius: 4px; height: 6px; overflow: hidden; margin-top: 4px; }
.prog-fill { height: 100%; border-radius: 4px; background: linear-gradient(90deg, #00d4ff, #a78bfa); }

.risk-banner {
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(251,146,60,0.06));
    border: 1px solid rgba(239,68,68,0.25); border-radius: 12px;
    padding: 1rem 1.4rem; margin-bottom: 1rem; font-size: 0.87rem; color: #fca5a5;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


def render_chart(fig_data):
    if isinstance(fig_data, str):
        fig_dict = json.loads(fig_data)
    else:
        fig_dict = fig_data
    fig = go.Figure(fig_dict)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def page_header(title, subtitle):
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-sub">{subtitle}</div>', unsafe_allow_html=True)

def section(icon, label):
    st.markdown(f'<div class="section-label">{icon} {label}</div>', unsafe_allow_html=True)

def grade_badge(grade):
    cls = {"A+": "Ap", "A": "A", "B": "B", "C": "C", "D": "D", "F": "F"}.get(grade, "B")
    return f'<span class="badge badge-{cls}">{grade}</span>'

def score_color(score):
    if score >= 80: return "#10b981"
    if score >= 65: return "#00d4ff"
    if score >= 50: return "#f59e0b"
    return "#ef4444"


df = load_data()
summary = get_summary(df)

# Initialize sidebar state
if "sidebar_open" not in st.session_state:
    st.session_state.sidebar_open = True
if "drawer_open" not in st.session_state:
    st.session_state.drawer_open = False

# Custom sidebar toggle button
col_toggle, col_title = st.columns([0.08, 0.92])
with col_toggle:
    # Show single button - hamburger when sidebar open, menu icon when closed
    if st.session_state.sidebar_open:
        if st.button("☰", key="sidebar_toggle", help="Toggle sidebar"):
            st.session_state.sidebar_open = not st.session_state.sidebar_open
            st.session_state.drawer_open = False
            st.rerun()
    else:
        if st.button("☰", key="drawer_toggle", help="Open menu"):
            st.session_state.drawer_open = not st.session_state.drawer_open
            st.rerun()

with col_title:
    st.markdown("""
    <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;
        background:linear-gradient(135deg,#00d4ff,#a78bfa);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0.5rem">
        EduMetrics Analytics Platform
    </div>
    <div style="font-size:0.8rem;color:#64748b;margin-bottom:1rem">
        Student Performance Dashboard 2026
    </div>
    """, unsafe_allow_html=True)

# Show sidebar content only when open
if st.session_state.sidebar_open:
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1.2rem 0 1.8rem">
            <div style="font-size:2.8rem;filter:drop-shadow(0 0 20px rgba(0,212,255,0.6))">📊</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                background:linear-gradient(135deg,#00d4ff,#a78bfa);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:6px">
                EduMetrics
            </div>
            <div style="font-size:0.7rem;color:#1e293b;margin-top:3px;letter-spacing:0.08em">
                ANALYTICS PLATFORM 2026
            </div>
        </div>
        """, unsafe_allow_html=True)

        current_page = st.session_state.get("page", "Dashboard")
        page = st.radio("Navigation", [
            "Dashboard",
            "Analysis",
            "Students",
            "Insights",
            "Compare"
        ], index=["Dashboard", "Analysis", "Students", "Insights", "Compare"].index(current_page), label_visibility="collapsed")

        # Update session state page when radio changes
        if page != current_page:
            st.session_state.page = page
            st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="font-size:0.8rem;line-height:2;color:#334155">
            <div><b style="color:#64748b">{summary['total_students']}</b> students enrolled</div>
            <div><b style="color:#64748b">{summary['departments']}</b> departments</div>
            <div><b style="color:#34d399">{summary['pass_rate']}%</b> pass rate</div>
            <div><b style="color:#00d4ff">{summary['avg_score']}</b> avg score</div>
        </div>
        """, unsafe_allow_html=True)
else:
    page = st.session_state.get("page", "Dashboard")

# Show interactive drawer menu when sidebar is closed and drawer is open
if not st.session_state.sidebar_open and st.session_state.drawer_open:
    # Create overlay that closes drawer when clicked
    st.markdown("""
    <div style="
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 900;
        cursor: pointer;
    " onclick="document.querySelector('[data-testid*=drawer-close]').click();"></div>
    """, unsafe_allow_html=True)
    
    # Hidden close button for overlay clicks
    if st.button("", key="drawer-close", help="Close drawer"):
        st.session_state.drawer_open = False
        st.rerun()
    
    # Create fixed-position drawer container with navigation
    st.markdown("""
    <style>
    .drawer-container {
        position: fixed;
        left: 0;
        top: 0;
        width: 320px;
        height: 100vh;
        background: linear-gradient(180deg, #070b18 0%, #0a0e1f 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
        z-index: 1000;
        padding: 2rem 1.5rem;
        box-sizing: border-box;
        overflow-y: auto;
    }
    .drawer-logo {
        text-align: center;
        margin-bottom: 2.5rem;
        padding-bottom: 1.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .drawer-nav-btn {
        width: 100% !important;
        height: 60px !important;
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 12px !important;
        color: #94a3b8 !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 16px !important;
        padding: 14px 16px !important;
        margin-bottom: 10px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        text-decoration: none !important;
    }
    .drawer-nav-btn:hover {
        background: rgba(0,212,255,0.08) !important;
        border-color: rgba(0,212,255,0.2) !important;
        color: #e2e8f0 !important;
        transform: translateX(4px) !important;
    }
    .drawer-nav-btn.active {
        background: rgba(0,212,255,0.12) !important;
        border-color: rgba(0,212,255,0.3) !important;
        color: #00d4ff !important;
    }
    .drawer-icon {
        width: 32px;
        height: 32px;
        flex-shrink: 0;
    }
    </style>
    
    <div class="drawer-container">
        <div class="drawer-logo">
            <svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="margin: 0 auto 12px; display: block;">
                <defs>
                    <linearGradient id="logoDraw" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#00d4ff;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#a78bfa;stop-opacity:1" />
                    </linearGradient>
                </defs>
                <rect x="15" y="65" width="12" height="20" fill="url(#logoDraw)" rx="2"/>
                <rect x="32" y="45" width="12" height="40" fill="url(#logoDraw)" rx="2" opacity="0.8"/>
                <rect x="49" y="25" width="12" height="60" fill="url(#logoDraw)" rx="2" opacity="0.9"/>
                <rect x="66" y="35" width="12" height="50" fill="url(#logoDraw)" rx="2" opacity="0.85"/>
                <path d="M 20 60 Q 40 35 75 38" stroke="url(#logoDraw)" stroke-width="2" fill="none" opacity="0.6"/>
            </svg>
            <div style="
                font-family: 'Syne', sans-serif;
                font-size: 1.3rem;
                font-weight: 800;
                background: linear-gradient(135deg, #00d4ff, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 4px;
            ">EduMetrics</div>
            <div style="
                font-size: 0.65rem;
                color: #64748b;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            ">Analytics Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons positioned over the drawer
    menu_items = [
        ("Dashboard", "▦"),
        ("Analysis", "▤"), 
        ("Students", "▥"),
        ("Insights", "▢"),
        ("Compare", "◆")
    ]
    
    current_page = st.session_state.get("page", "Dashboard")
    
    # Create buttons with custom styling
    for label, icon in menu_items:
        # Custom CSS for each button
        st.markdown(f"""
        <style>
        div[data-testid="stButton"][data-key="drawer_nav_{label}"] {{
            position: fixed !important;
            left: 24px !important;
            top: {220 + menu_items.index((label, icon)) * 70}px !important;
            z-index: 1001 !important;
            width: 272px !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Create the button
        if st.button(f"{icon} {label}", key=f"drawer_nav_{label}"):
            st.session_state.page = label
            st.session_state.drawer_open = False
            st.rerun()
    
    # Set page from session state
    page = st.session_state.get("page", "Dashboard")
else:
    # Set page from session state when drawer is not showing
    if not st.session_state.sidebar_open:
        page = st.session_state.get("page", "Dashboard")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    page_header("Overview Dashboard",
                f"Academic snapshot · {summary['total_students']} students · {summary['departments']} departments")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("👥 Students",       summary["total_students"])
    c2.metric("📊 Avg Score",      summary["avg_score"])
    c3.metric("✅ Pass Rate",      f"{summary['pass_rate']}%")
    c4.metric("🏆 Top Score",      summary["top_score"])
    c5.metric("📅 Avg Attendance", f"{summary['avg_attendance']}%")
    c6.metric("🎓 A-Grade Count",  summary["grade_a_count"])

    section("📊", "Score Overview")
    col1, col2 = st.columns([3, 2])
    with col1:
        render_chart(score_distribution_chart(df))
    with col2:
        render_chart(grade_distribution_chart(df))

    section("📚", "Subject & Department")
    col3, col4 = st.columns(2)
    with col3:
        render_chart(subject_avg_bar(df))
    with col4:
        render_chart(dept_comparison_chart(df))

    section("🏆", "Top 10 Performers")
    top = pd.DataFrame(top_students_table(df))
    st.dataframe(top, use_container_width=True, hide_index=True, height=350)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Analysis":
    page_header("Deep Analysis",
                "Multi-dimensional breakdowns of attendance, study habits & subject performance")

    section("📍", "Attendance & Study Patterns")
    col1, col2 = st.columns([3, 2])
    with col1:
        render_chart(attendance_vs_score_chart(df))
    with col2:
        render_chart(study_hours_chart(df))

    section("🧩", "Subject Breakdown")
    col3, col4 = st.columns(2)
    with col3:
        render_chart(radar_chart_dept(df))
    with col4:
        render_chart(dept_comparison_chart(df))

    section("🔗", "Gender & Correlations")
    col5, col6 = st.columns([2, 3])
    with col5:
        render_chart(gender_performance_chart(df))
    with col6:
        render_chart(correlation_heatmap(df))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — STUDENTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Students":
    page_header("Student Records",
                "Search, filter and explore every student's academic profile")

    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
    with col1:
        search = st.text_input("🔍 Search by name", placeholder="e.g. Aarav...")
    with col2:
        dept_f = st.selectbox("Department", ["All"] + sorted(df["department"].unique().tolist()))
    with col3:
        grade_f = st.selectbox("Grade", ["All", "A+", "A", "B", "C", "D", "F"])
    with col4:
        status_f = st.selectbox("Status", ["All", "Pass", "Fail"])

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["name"].str.lower().str.contains(search.lower())]
    if dept_f != "All":
        filtered = filtered[filtered["department"] == dept_f]
    if grade_f != "All":
        filtered = filtered[filtered["grade"] == grade_f]
    if status_f != "All":
        filtered = filtered[filtered["status"] == status_f]

    st.markdown(f"<div style='font-size:0.82rem;color:#334155;margin-bottom:0.8rem'>"
                f"Showing <b style='color:#00d4ff'>{len(filtered)}</b> of {len(df)} students</div>",
                unsafe_allow_html=True)

    display_cols = ["name", "gender", "age", "department", "avg_score",
                    "grade", "attendance", "study_hours_per_day", "extracurricular", "status"]
    available = [c for c in display_cols if c in filtered.columns]
    st.dataframe(filtered[available].reset_index(drop=True),
                 use_container_width=True, height=420, hide_index=True)

    st.markdown("---")
    col_top, col_risk = st.columns(2)

    with col_top:
        section("🏆", "Top 10 Students")
        for s in top_students_table(df):
            ca, cb, cc = st.columns([3, 1, 1])
            ca.markdown(f"**{s['name']}** <span style='color:#475569;font-size:0.78rem'> · {s['department']}</span>",
                        unsafe_allow_html=True)
            cb.markdown(f"<span style='color:{score_color(s['avg_score'])};font-weight:700'>{s['avg_score']}</span>",
                        unsafe_allow_html=True)
            cc.markdown(grade_badge(s["grade"]), unsafe_allow_html=True)

    with col_risk:
        section("⚠️", "At-Risk Students (Score < 60)")
        risk_data = bottom_students_table(df)
        if risk_data:
            st.markdown(f'<div class="risk-banner">⚠️ {len(risk_data)} students may need academic support</div>',
                        unsafe_allow_html=True)
            for s in risk_data[:10]:
                ca, cb, cc = st.columns([3, 1, 1])
                ca.markdown(f"**{s['name']}** <span style='color:#475569;font-size:0.78rem'> · {s['department']}</span>",
                            unsafe_allow_html=True)
                cb.markdown(f"<span style='color:#ef4444;font-weight:700'>{s['avg_score']}</span>",
                            unsafe_allow_html=True)
                cc.markdown(grade_badge(s["grade"]), unsafe_allow_html=True)
        else:
            st.success("No at-risk students! 🎉")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Insights":
    page_header("Key Insights",
                "Statistical highlights and patterns across the cohort")

    section("📌", "Quick Statistics")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    stats = [
        (c1, "🎯 Top Score",    summary["top_score"],                        "#00ffcc"),
        (c2, "📉 Lowest Score", summary["lowest_score"],                     "#ef4444"),
        (c3, "📊 Median",       round(float(df["avg_score"].median()), 1),   "#a78bfa"),
        (c4, "📐 Std Dev",      summary["std_dev"],                          "#f59e0b"),
        (c5, "👩 Female",       summary["female_count"],                     "#f472b6"),
        (c6, "👨 Male",         summary["male_count"],                       "#00d4ff"),
    ]
    for col, label, val, color in stats:
        col.markdown(f"""
        <div class="insight-card">
            <div class="insight-title">{label}</div>
            <div class="insight-num" style="background:linear-gradient(135deg,{color},{color}99);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent">{val}</div>
        </div>""", unsafe_allow_html=True)

    section("🌐", "Factor Analysis")
    col1, col2 = st.columns(2)

    base_layout = dict(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0"), margin=dict(t=50, b=30, l=30, r=30),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", range=[0, 110])
    )

    with col1:
        net_avg = df.groupby("internet_access")["avg_score"].mean().round(1)
        fig = go.Figure(go.Bar(
            x=["No Internet" if x == "No" else "Has Internet" for x in net_avg.index],
            y=net_avg.values, marker_color=["#ef4444", "#10b981"],
            text=net_avg.values, textposition="outside", textfont=dict(color="white", size=13)
        ))
        fig.update_layout(title="Internet Access vs Avg Score", **base_layout)
        render_chart(fig.to_dict())

    with col2:
        ext_avg = df.groupby("extracurricular")["avg_score"].mean().round(1)
        fig2 = go.Figure(go.Bar(
            x=["No Extracurricular" if x == "No" else "Has Extracurricular" for x in ext_avg.index],
            y=ext_avg.values, marker_color=["#7c3aed", "#00d4ff"],
            text=ext_avg.values, textposition="outside", textfont=dict(color="white", size=13)
        ))
        fig2.update_layout(title="Extracurricular vs Avg Score", **base_layout)
        render_chart(fig2.to_dict())

    section("🎓", "Parent Education Impact")
    pe_avg = df.groupby("parent_education")["avg_score"].mean().round(1).reset_index()
    pe_avg.columns = ["Education Level", "Avg Score"]
    fig3 = px.bar(pe_avg, x="Education Level", y="Avg Score",
                  color="Avg Score",
                  color_continuous_scale=[[0,"#1e1b4b"],[0.5,"#7c3aed"],[1,"#00d4ff"]],
                  text="Avg Score")
    fig3.update_traces(textposition="outside", textfont_color="white")
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(color="#e2e8f0"), margin=dict(t=50,b=30,l=30,r=30),
                       xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                       yaxis=dict(gridcolor="rgba(255,255,255,0.06)", range=[0,110]),
                       coloraxis_showscale=False)
    render_chart(fig3.to_dict())

    section("💼", "Part-time Job Impact")
    col3, col4 = st.columns([1, 2])
    with col3:
        pt_avg = df.groupby("part_time_job")["avg_score"].mean().round(1)
        pt_count = df.groupby("part_time_job").size()
        for job, avg in pt_avg.items():
            label = "Has Part-time Job" if job == "Yes" else "No Part-time Job"
            color = "#ef4444" if job == "Yes" else "#10b981"
            st.markdown(f"""
            <div style="margin-bottom:1.2rem">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:4px">
                    <span style="color:#94a3b8">{label}</span>
                    <span style="color:{color};font-weight:700">{avg}</span>
                </div>
                <div class="prog-wrap">
                    <div class="prog-fill" style="width:{int(avg)}%;background:{color}"></div>
                </div>
                <div style="font-size:0.75rem;color:#334155;margin-top:3px">{pt_count[job]} students</div>
            </div>""", unsafe_allow_html=True)

    with col4:
        pt_grade = df.groupby(["part_time_job","grade"]).size().reset_index(name="count")
        pt_grade["Job"] = pt_grade["part_time_job"].map({"Yes":"Part-time Job","No":"No Job"})
        fig4 = px.bar(pt_grade, x="Job", y="count", color="grade", barmode="stack",
                      color_discrete_map={"A":"#10b981","B":"#00d4ff","C":"#f59e0b","D":"#fb923c","F":"#ef4444"},
                      title="Grade Distribution by Employment", labels={"count":"Students"})
        fig4.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font=dict(color="#e2e8f0"), margin=dict(t=50,b=30,l=30,r=30),
                           xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                           yaxis=dict(gridcolor="rgba(255,255,255,0.06)"))
        render_chart(fig4.to_dict())

    section("🗂️", "Full Dataset")
    st.dataframe(df, use_container_width=True, height=350, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — COMPARE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Compare":
    page_header("Student Comparison",
                "Select any two students for a detailed side-by-side analysis")

    all_names = sorted(df["name"].tolist())
    col1, _, col2 = st.columns([5, 1, 5])
    with col1:
        name_a = st.selectbox("🔵 Student A", all_names, index=0)
    with col2:
        name_b = st.selectbox("🟣 Student B", all_names, index=min(1, len(all_names)-1))

    a = df[df["name"] == name_a].iloc[0]
    b = df[df["name"] == name_b].iloc[0]

    st.markdown("---")

    col_a, col_mid, col_b_col = st.columns([5, 1, 5])

    def render_cmp_card(student, color):
        score_c = score_color(student["avg_score"])
        rows = [
            ("Department",     student["department"]),
            ("Average Score",  f"<span style='color:{score_c};font-weight:700'>{student['avg_score']}</span>"),
            ("Grade",          grade_badge(student["grade"])),
            ("Status",         f'<span class="badge badge-{student["status"].lower()}">{student["status"]}</span>'),
            ("Attendance",     f"{student['attendance']}%"),
            ("Study Hrs/Day",  f"{student['study_hours_per_day']}h"),
            ("Extracurricular",student["extracurricular"]),
            ("Part-time Job",  student["part_time_job"]),
            ("Parent Edu",     student["parent_education"]),
            ("Internet",       student["internet_access"]),
        ]
        rows_html = "".join([
            f'<div class="cmp-row"><span class="cmp-key">{k}</span><span class="cmp-val">{v}</span></div>'
            for k, v in rows
        ])
        st.markdown(f"""
        <div class="cmp-card" style="border-top:3px solid {color}">
            <div class="cmp-name" style="color:{color}">{student['name']}</div>
            <div style="font-size:0.78rem;color:#334155;margin-bottom:1rem">
                {student['gender']} · Age {student['age']}
            </div>
            {rows_html}
        </div>""", unsafe_allow_html=True)

    with col_a:
        render_cmp_card(a, "#00d4ff")
    with col_mid:
        st.markdown("""
        <div style="text-align:center;padding-top:3rem;font-family:'Syne',sans-serif;
             font-size:1.3rem;font-weight:800;
             background:linear-gradient(135deg,#00d4ff,#a78bfa);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent">VS</div>
        """, unsafe_allow_html=True)
    with col_b_col:
        render_cmp_card(b, "#a78bfa")

    section("📡", "Subject Score Radar")
    subjects_vals_a = [float(a[s]) for s in SUBJECTS]
    subjects_vals_b = [float(b[s]) for s in SUBJECTS]

    fig = go.Figure()
    for vals, sname, color in [
        (subjects_vals_a, name_a, "#00d4ff"),
        (subjects_vals_b, name_b, "#a78bfa")
    ]:
        closed = vals + [vals[0]]
        theta  = SUBJECT_LABELS + [SUBJECT_LABELS[0]]
        fig.add_trace(go.Scatterpolar(
            r=closed, theta=theta, fill="toself", name=sname,
            line=dict(color=color, width=2),
            fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.15)"
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100],
                            gridcolor="rgba(255,255,255,0.08)", color="#64748b"),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.08)", color="#64748b"),
            bgcolor="rgba(0,0,0,0)"
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="DM Sans, sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
        margin=dict(t=40, b=40, l=60, r=60), height=420
    )
    render_chart(fig.to_dict())

    section("📊", "Subject-by-Subject Bar Comparison")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        name=name_a, x=SUBJECT_LABELS, y=subjects_vals_a,
        marker_color="#00d4ff", opacity=0.85,
        text=subjects_vals_a, textposition="outside", textfont=dict(color="white")
    ))
    fig2.add_trace(go.Bar(
        name=name_b, x=SUBJECT_LABELS, y=subjects_vals_b,
        marker_color="#a78bfa", opacity=0.85,
        text=subjects_vals_b, textposition="outside", textfont=dict(color="white")
    ))
    fig2.update_layout(
        barmode="group",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e2e8f0", family="DM Sans, sans-serif"),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.06)", range=[0, 115]),
        margin=dict(t=30, b=30, l=30, r=30), height=380
    )
    render_chart(fig2.to_dict())

    section("⚡", "Score Differences  (B − A)")
    diff_cols = st.columns(5)
    for i, (subj, label) in enumerate(zip(SUBJECTS, SUBJECT_LABELS)):
        diff  = round(float(b[subj]) - float(a[subj]), 1)
        color = "#10b981" if diff > 0 else "#ef4444" if diff < 0 else "#64748b"
        arrow = "▲" if diff > 0 else "▼" if diff < 0 else "—"
        diff_cols[i].markdown(f"""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
             border-radius:12px;padding:1rem;text-align:center">
            <div style="font-size:0.75rem;color:#475569;text-transform:uppercase;
                 letter-spacing:0.06em;margin-bottom:4px">{label}</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:{color}">
                {arrow} {abs(diff)}
            </div>
        </div>""", unsafe_allow_html=True)