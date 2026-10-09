import streamlit as st
from datetime import datetime
from agent.agent import StudyPlannerAgent
from agent.memory import load_daily_plan, load_study_logs, load_settings, load_subjects
from agent.utils import format_time
from agent.theme import apply_custom_theme, render_hero

st.set_page_config(page_title="Today's Execution", page_icon="📅", layout="wide")
apply_custom_theme()

# Check Authentication
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("🔒 Please log in or register on the Home Page first to access your study execution page.")
    st.stop()

user = st.session_state["user"]
user_id = user["id"]

st.sidebar.markdown(f"### 👤 Profile")
st.sidebar.info(f"**Logged in as:** `{user['username']}`")
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear()
    st.rerun()

render_hero(
    title="Today's Execution & Tracking",
    subtitle="Log actual studied minutes per subject and trigger instant autonomous replanning.",
    icon="📅"
)

daily_plan = load_daily_plan(user_id)
study_logs = load_study_logs(user_id)
settings = load_settings(user_id)
subjects = load_subjects(user_id)

if not settings or not daily_plan:
    st.warning(f"⚠️ No active study plan found for {user['username']}. Please create a plan first in 1_Create_Plan.")
    st.stop()

agent = StudyPlannerAgent(user_id=user_id)
current_date_str = st.session_state.get("simulated_date", datetime.today().strftime("%Y-%m-%d"))

st.subheader(f"Target Execution Date: {current_date_str}")

today_actual = datetime.today().strftime("%Y-%m-%d")
if current_date_str > today_actual and not st.session_state.get("demo_mode_active", False):
    st.warning("⚠️ Note: Logging completion for future dates is restricted unless Demo Mode is enabled in Settings.")

if current_date_str not in daily_plan:
    st.info(f"No study tasks scheduled for {current_date_str}.")
    st.stop()

today_tasks = daily_plan[current_date_str]
today_logs = study_logs.get(current_date_str, {})

total_planned = sum(today_tasks.values())
total_completed = sum(today_logs.get(s, 0) for s in today_tasks.keys())
total_remaining = max(0, total_planned - total_completed)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Planned Time", format_time(total_planned))
with col2:
    st.metric("Total Completed Time", format_time(total_completed))
with col3:
    st.metric("Remaining Time", format_time(total_remaining))

pct = int((total_completed / total_planned) * 100) if total_planned > 0 else 0
st.progress(min(1.0, pct / 100))
st.caption(f"Overall Day Completion: **{pct}%**")

st.divider()
st.subheader("📚 Subject Study Logging")
st.write("Enter your actual studied minutes for each subject today:")

with st.form("log_today_form"):
    logged_inputs = {}
    
    for subj_name, planned_mins in today_tasks.items():
        prev_completed = today_logs.get(subj_name, 0)
        
        st.markdown(f"#### 📖 {subj_name}")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.write(f"**Planned:** {format_time(planned_mins)}")
        with c2:
            st.write(f"**Current Logged:** {format_time(prev_completed)}")
        with c3:
            rem = max(0, planned_mins - prev_completed)
            st.write(f"**Remaining:** {format_time(rem)}")

        new_val = st.number_input(
            f"Set Completed Minutes for {subj_name}",
            min_value=0,
            max_value=1440,
            value=prev_completed,
            step=15,
            key=f"input_{subj_name}"
        )
        logged_inputs[subj_name] = new_val
        st.caption("---")

    save_and_replan = st.form_submit_button("💾 Save Study Logs & Trigger Agent Replanning", use_container_width=True)

if save_and_replan:
    for subj_name, completed_mins in logged_inputs.items():
        agent.monitor(current_date_str, subj_name, completed_mins)

    with st.spinner("🤖 Agent is reflecting on progress and recalculating future schedule..."):
        agent.reflect(current_date_str)
        updated_plan = agent.replan(current_date_str)

    st.success("✅ Progress logged and autonomous replanning cycle completed!")
    st.rerun()
