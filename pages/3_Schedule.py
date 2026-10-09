import streamlit as st
import pandas as pd
from datetime import datetime
from agent.memory import load_daily_plan, load_study_logs, load_settings
from agent.utils import format_time
from agent.theme import apply_custom_theme, render_hero

st.set_page_config(page_title="Study Schedule", page_icon="📊", layout="wide")
apply_custom_theme()

# Check Authentication
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("🔒 Please log in or register on the Home Page first to view your schedule.")
    st.stop()

user = st.session_state["user"]
user_id = user["id"]

st.sidebar.markdown(f"### 👤 Profile")
st.sidebar.info(f"**Logged in as:** `{user['username']}`")
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear()
    st.rerun()

render_hero(
    title="Complete Study Schedule",
    subtitle="Inspect upcoming daily allocations, status indicators, and subject-level backlog.",
    icon="📊"
)

daily_plan = load_daily_plan(user_id)
study_logs = load_study_logs(user_id)
settings = load_settings(user_id)

if not settings or not daily_plan:
    st.warning(f"⚠️ No active study plan found for {user['username']}. Please create a plan first in 1_Create_Plan.")
    st.stop()

all_dates = sorted(list(daily_plan.keys()))
st.markdown(f"**Total Plan Horizon:** `{all_dates[0]}` to `{all_dates[-1]}` ({len(all_dates)} Days)")

today_sim = st.session_state.get("simulated_date", datetime.today().strftime("%Y-%m-%d"))

col1, col2 = st.columns(2)
with col1:
    view_option = st.radio("Display Horizon", ["Next 7 Days", "Full Plan Horizon"], horizontal=True)

if view_option == "Next 7 Days":
    display_dates = [d for d in all_dates if d >= today_sim][:7]
    if not display_dates:
        display_dates = all_dates[:7]
else:
    display_dates = all_dates

for p_date in display_dates:
    tasks = daily_plan[p_date]
    logs = study_logs.get(p_date, {})
    
    day_planned_tot = sum(tasks.values())
    day_completed_tot = sum(logs.get(s, 0) for s in tasks.keys())
    day_backlog = max(0, day_planned_tot - day_completed_tot)
    
    is_today = (p_date == today_sim)
    is_past = (p_date < today_sim)
    
    if is_today:
        badge = "📍 [TODAY]"
    elif is_past:
        badge = "⏳ [PAST]"
    else:
        badge = "🔮 [FUTURE]"

    title_str = f"{badge} Date: {p_date} — Total Planned: {format_time(day_planned_tot)}"
    if is_past:
        if day_completed_tot >= day_planned_tot and day_planned_tot > 0:
            title_str += " | Status: ✅ Completed"
        elif day_completed_tot > 0:
            title_str += f" | Status: ⚠️ Partial (Backlog: {format_time(day_backlog)})"
        else:
            title_str += f" | Status: ❌ Missed (Backlog: {format_time(day_backlog)})"

    with st.expander(title_str, expanded=(is_today or is_past)):
        table_data = []
        for subj, planned_m in tasks.items():
            comp_m = logs.get(subj, 0)
            rem_m = max(0, planned_m - comp_m)
            table_data.append({
                "Subject": subj,
                "Planned Time": format_time(planned_m),
                "Completed Time": format_time(comp_m),
                "Backlog / Remaining": format_time(rem_m),
                "Status": "✅ Done" if comp_m >= planned_m and planned_m > 0 else ("⏳ In Progress" if comp_m > 0 else "❌ Pending")
            })
            
        df = pd.DataFrame(table_data)
        st.table(df)
