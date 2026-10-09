import streamlit as st
from datetime import datetime
from agent.memory import load_settings, load_daily_plan, clear_all_data
from agent.theme import apply_custom_theme, render_hero

st.set_page_config(page_title="Settings & Demo Mode", page_icon="⚙️", layout="wide")
apply_custom_theme()

# Check Authentication
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("🔒 Please log in or register on the Home Page first to manage settings.")
    st.stop()

user = st.session_state["user"]
user_id = user["id"]

st.sidebar.markdown(f"### 👤 Profile")
st.sidebar.info(f"**Logged in as:** `{user['username']}`")
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear()
    st.rerun()

render_hero(
    title="System Settings & Demo Mode",
    subtitle=f"Manage simulation parameters and database memory for {user['username']}.",
    icon="⚙️"
)

settings = load_settings(user_id)
daily_plan = load_daily_plan(user_id)

st.subheader("🧪 Demo Mode: Date Simulator")
st.markdown("""
Use Demo Mode to simulate different current dates (e.g. fast-forward 1 or 2 days).
This lets you test **missed-day detection**, **backlog calculation**, and **automatic replanning** without changing your computer's system date!
""")

actual_today_str = datetime.today().strftime("%Y-%m-%d")
simulated_current = st.session_state.get("simulated_date", actual_today_str)

st.info(f"**Actual System Date:** `{actual_today_str}` | **Currently Active Date:** `{simulated_current}`")

if daily_plan:
    all_dates = sorted(list(daily_plan.keys()))
    
    selected_sim_date = st.selectbox(
        "Select Simulated Current Date for Testing:",
        options=all_dates,
        index=all_dates.index(simulated_current) if simulated_current in all_dates else 0
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Apply Simulated Date", use_container_width=True):
            st.session_state["simulated_date"] = selected_sim_date
            st.session_state["demo_mode_active"] = True
            st.success(f"✅ Active date set to {selected_sim_date}!")
            st.rerun()
            
    with col2:
        if st.button("Reset to Real Today's Date", use_container_width=True):
            st.session_state["simulated_date"] = actual_today_str
            st.session_state["demo_mode_active"] = False
            st.success("✅ Reset active date to system today!")
            st.rerun()
else:
    st.info("Create a study plan first to enable Demo Mode date simulation.")

st.divider()

st.subheader("🗑️ Database Memory Management")
st.warning(f"Clearing your data will delete all stored subjects, schedules, logs, and decision entries for user **{user['username']}** from SQLite.")

if st.button(f"⚠️ Clear All Data for {user['username']}", type="primary"):
    clear_all_data(user_id=user_id)
    st.session_state.pop("simulated_date", None)
    st.session_state.pop("demo_mode_active", None)
    st.success(f"✅ All database memory cleared for {user['username']}.")
    st.rerun()
