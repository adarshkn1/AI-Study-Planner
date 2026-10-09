import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from agent.memory import load_daily_plan, load_study_logs, load_settings, load_subjects
from agent.utils import format_time
from agent.theme import apply_custom_theme, render_hero, style_matplotlib_dark

st.set_page_config(page_title="Progress Dashboard", page_icon="📈", layout="wide")
apply_custom_theme()
style_matplotlib_dark()

# Check Authentication
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("🔒 Please log in or register on the Home Page first to view your progress analytics.")
    st.stop()

user = st.session_state["user"]
user_id = user["id"]

st.sidebar.markdown(f"### 👤 Profile")
st.sidebar.info(f"**Logged in as:** `{user['username']}`")
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear()
    st.rerun()

render_hero(
    title="Analytics & Progress Dashboard",
    subtitle="Track your weighted productivity score breakdown, streak metrics, and workload trends.",
    icon="📈"
)

daily_plan = load_daily_plan(user_id)
study_logs = load_study_logs(user_id)
settings = load_settings(user_id)
subjects = load_subjects(user_id)

if not settings or not daily_plan:
    st.warning(f"⚠️ No active study plan found for {user['username']}. Please create a plan first in 1_Create_Plan.")
    st.stop()

today_sim = st.session_state.get("simulated_date", datetime.today().strftime("%Y-%m-%d"))
past_and_today_dates = sorted([d for d in daily_plan.keys() if d <= today_sim])

# Compute Metrics
total_planned_mins = 0
total_completed_mins = 0
successful_days = 0

for d in past_and_today_dates:
    day_tasks = daily_plan[d]
    day_logs = study_logs.get(d, {})
    
    d_plan = sum(day_tasks.values())
    d_comp = sum(day_logs.get(s, 0) for s in day_tasks.keys())
    
    total_planned_mins += d_plan
    total_completed_mins += d_comp
    
    if d_plan > 0 and (d_comp / d_plan) >= 0.8:
        successful_days += 1

total_backlog_mins = max(0, total_planned_mins - total_completed_mins)

# ---------------- PRODUCTIVITY SCORE ----------------
st.subheader("📊 Weighted Productivity Score Engine")

if total_planned_mins == 0 or len(past_and_today_dates) == 0:
    st.info("ℹ️ Not enough historical data yet to calculate productivity score.")
else:
    completion_ratio = min(1.0, total_completed_mins / total_planned_mins)
    consistency_ratio = min(1.0, successful_days / max(1, len(past_and_today_dates)))
    backlog_ratio = max(0.0, 1.0 - (total_backlog_mins / max(1, total_planned_mins)))
    
    prod_score = int((0.60 * completion_ratio + 0.25 * consistency_ratio + 0.15 * backlog_ratio) * 100)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Productivity Score", f"{prod_score}%")
    with c2:
        st.metric("Completion (60% Weight)", f"{int(completion_ratio*100)}%")
    with c3:
        st.metric("Consistency (25% Weight)", f"{int(consistency_ratio*100)}%")
    with c4:
        st.metric("Backlog Control (15%)", f"{int(backlog_ratio*100)}%")

    if prod_score >= 80:
        st.success(f"🔥 Outstanding! Overall Productivity: **{prod_score}%**")
    elif prod_score >= 50:
        st.info(f"⚡ Good effort! Overall Productivity: **{prod_score}%**")
    else:
        st.warning(f"⚠️ Action Required! Overall Productivity: **{prod_score}%**")

st.divider()

# ---------------- STREAK TRACKING ----------------
st.subheader("🔥 Study Streak Tracking")
st.caption("A study day counts toward your streak if you complete **≥ 80%** of your planned minutes.")

streak = 0
for d in past_and_today_dates:
    d_plan = sum(daily_plan[d].values())
    d_comp = sum(study_logs.get(d, {}).get(s, 0) for s in daily_plan[d].keys())
    if d_plan > 0 and (d_comp / d_plan) >= 0.8:
        streak += 1
    else:
        streak = 0  # reset on missed/incomplete day

if streak >= 5:
    st.success(f"🔥 **{streak}-Day Super Streak!** Excellent consistency!")
elif streak > 0:
    st.info(f"⚡ **{streak}-Day Active Streak!** Keep momentum going!")
else:
    st.warning("⚠️ **No Active Streak.** Complete today's plan (≥ 80%) to start a streak!")

st.divider()

# ---------------- CHARTS ----------------
st.subheader("📈 Visual Analytics Dashboard")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("##### 🗓️ Planned vs Completed Study Minutes")
    dates_plot = past_and_today_dates[:10]
    planned_vals = [sum(daily_plan[d].values()) for d in dates_plot]
    completed_vals = [sum(study_logs.get(d, {}).get(s, 0) for s in daily_plan[d].keys()) for d in dates_plot]

    fig, ax = plt.subplots(figsize=(6, 4))
    
    ax.plot(dates_plot, planned_vals, marker='o', label='Planned Mins', color='#60A5FA', linewidth=2.5)
    ax.fill_between(dates_plot, planned_vals, alpha=0.15, color='#60A5FA')

    ax.plot(dates_plot, completed_vals, marker='s', label='Completed Mins', color='#34D399', linewidth=2.5)
    ax.fill_between(dates_plot, completed_vals, alpha=0.15, color='#34D399')

    ax.set_title("Daily Workload Trend", color='#F8FAFC', fontsize=12, fontweight='bold', pad=12)
    ax.set_ylabel("Minutes", color='#94A3B8')
    ax.tick_params(colors='#CBD5E1', rotation=25)
    ax.legend(facecolor='#1E293B', edgecolor='#334155', labelcolor='#F8FAFC')
    ax.grid(True, linestyle='--', alpha=0.3)

    st.pyplot(fig)

with col_right:
    st.markdown("##### 📚 Total Workload Allocated per Subject")
    subj_names = [s['name'] for s in subjects]
    subj_totals = []
    
    for s_n in subj_names:
        tot = sum(daily_plan[d].get(s_n, 0) for d in daily_plan.keys())
        subj_totals.append(tot)

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    colors = ['#818CF8', '#F472B6', '#38BDF8', '#FBBF24', '#A78BFA']
    bar_colors = [colors[i % len(colors)] for i in range(len(subj_names))]

    bars = ax2.bar(subj_names, subj_totals, color=bar_colors, alpha=0.9, width=0.55)

    ax2.set_title("Subject Time Allocation (Total Minutes)", color='#F8FAFC', fontsize=12, fontweight='bold', pad=12)
    ax2.set_ylabel("Total Minutes", color='#94A3B8')
    ax2.tick_params(colors='#CBD5E1', rotation=20)
    ax2.grid(axis='y', linestyle='--', alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'{int(height)} m',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  
                    textcoords="offset points",
                    ha='center', va='bottom', color='#F8FAFC', fontsize=9, fontweight='bold')

    st.pyplot(fig2)
