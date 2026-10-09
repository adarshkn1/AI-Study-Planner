import streamlit as st
from datetime import datetime
from agent.memory import (
    init_db,
    register_user,
    authenticate_user,
    load_settings,
    load_daily_plan,
    load_subjects,
    load_study_logs
)
from agent.utils import format_time
from agent.theme import apply_custom_theme, render_hero

st.set_page_config(
    page_title="AI Study Planner Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
apply_custom_theme()

# Sidebar User Profile & Logout
if "user" in st.session_state and st.session_state["user"]:
    user = st.session_state["user"]
    st.sidebar.markdown(f"### 👤 Profile")
    st.sidebar.info(f"**Logged in as:** `{user['username']}`")
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.clear()
        st.rerun()

render_hero(
    title="Adaptive AI Study Planner Agent",
    subtitle="A Rule-Based Autonomous Agent with Multi-User Authentication & Constraint-Based Adaptive Replanning.",
    icon="🧠"
)

# --- CHECK AUTHENTICATION STATE ---
if "user" not in st.session_state or not st.session_state["user"]:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h3 style="color: #94A3B8;">Welcome! Please log in or register a new account to continue.</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_main, _ = st.columns([2, 1])
    with col_main:
        tab_login, tab_signup = st.tabs(["🔑 Log In", "📝 Sign Up / Register"])
        
        with tab_login:
            with st.form("login_form"):
                st.subheader("Log In to Your Account")
                login_username = st.text_input("Username", key="login_user")
                login_password = st.text_input("Password", type="password", key="login_pwd")
                login_btn = st.form_submit_button("🔑 Log In", use_container_width=True)
                
                if login_btn:
                    if not login_username or not login_password:
                        st.error("Please enter both username and password.")
                    else:
                        user_data = authenticate_user(login_username, login_password)
                        if user_data:
                            st.session_state["user"] = user_data
                            st.success(f"Welcome back, {user_data['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password. Please try again.")

        with tab_signup:
            with st.form("signup_form"):
                st.subheader("Create a New Account")
                signup_username = st.text_input("Choose Username", key="signup_user")
                signup_password = st.text_input("Choose Password", type="password", key="signup_pwd")
                confirm_password = st.text_input("Confirm Password", type="password", key="confirm_pwd")
                signup_btn = st.form_submit_button("✨ Register & Create Account", use_container_width=True)
                
                if signup_btn:
                    if signup_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        success, res = register_user(signup_username, signup_password)
                        if success:
                            st.session_state["user"] = res
                            st.success(f"Account created successfully! Welcome, {res['username']}!")
                            st.rerun()
                        else:
                            st.error(f"Registration failed: {res}")
    st.stop()

# --- LOGGED IN USER DASHBOARD ---
user = st.session_state["user"]
user_id = user["id"]

st.markdown("""
<div class="agent-loop-card">
    <h4 style="color: #6366F1; margin-bottom: 6px;">🤖 Autonomous Agent Decision Loop</h4>
    <p style="color: #CBD5E1; margin: 0; font-size: 0.95rem;">
        <b>OBSERVE</b> (Scores & Limits) ➔ <b>ANALYZE</b> (Weakness & Urgency) ➔ <b>DECIDE</b> (Allocation Ratios) ➔ <b>ACT</b> (Generate Schedule) ➔ <b>MONITOR</b> (Study Logs) ➔ <b>REFLECT</b> (Backlog Detection) ➔ <b>REPLAN</b> (Capacity-Constrained Redistribution)
    </p>
</div>
""", unsafe_allow_html=True)

settings = load_settings(user_id)
daily_plan = load_daily_plan(user_id)
subjects = load_subjects(user_id)
study_logs = load_study_logs(user_id)

if not settings or not daily_plan:
    st.warning(f"⚠️ Welcome **{user['username']}**! You have not created a study plan yet.")
    st.info("👉 Navigate to **1_Create_Plan** in the sidebar to configure your subjects and generate your personalized adaptive schedule.")
else:
    today_str = st.session_state.get("simulated_date", datetime.today().strftime("%Y-%m-%d"))
    exam_dt = datetime.strptime(settings['exam_date'], "%Y-%m-%d").date()
    today_dt = datetime.strptime(today_str, "%Y-%m-%d").date()
    days_left = max(0, (exam_dt - today_dt).days)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="🎯 Exam Date", value=settings['exam_date'], delta=f"{days_left} days left")
    with col2:
        st.metric(label="⏱️ Base Daily Target", value=f"{settings['daily_hours']} hrs/day")
    with col3:
        st.metric(label="🛡️ Max Daily Cap", value=f"{settings['max_daily_hours']} hrs/day")
    with col4:
        st.metric(label="📚 Total Subjects", value=len(subjects))

    st.divider()

    st.subheader(f"📅 Today's Overview ({today_str})")
    
    if today_str in daily_plan:
        today_planned = daily_plan[today_str]
        today_logs = study_logs.get(today_str, {})
        
        total_planned_mins = sum(today_planned.values())
        total_completed_mins = sum(today_logs.values())
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Planned", format_time(total_planned_mins))
        with c2:
            st.metric("Total Completed", format_time(total_completed_mins))
        with c3:
            remaining = max(0, total_planned_mins - total_completed_mins)
            st.metric("Remaining", format_time(remaining))

        progress_pct = min(100, int((total_completed_mins / total_planned_mins * 100))) if total_planned_mins > 0 else 0
        st.progress(progress_pct / 100)
        st.caption(f"Today's Completion: **{progress_pct}%**")
    else:
        st.info(f"No specific plan entry scheduled for {today_str}.")

    st.divider()
    st.markdown("""
    ### 📌 Navigation Quick-Links:
    - **1_Create_Plan**: Configure your personal subjects, exam date, and daily study hours.
    - **2_Today**: Log actual subject study time for today.
    - **3_Schedule**: Inspect upcoming daily allocations and total workload.
    - **4_Progress**: View productivity score breakdown, completion metrics & charts.
    - **5_Agent_Decisions**: View transparent logs explaining *why* the agent scheduled or replanned your workload.
    - **6_Settings**: Demo mode date simulator and personal memory controls.
    """)
