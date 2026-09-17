import streamlit as st
import pandas as pd
from datetime import datetime
from agent.utils import format_time
import matplotlib.pyplot as plt

st.title("📊 Study Schedule")

if "plan" not in st.session_state:
    st.warning("Please generate a study plan first.")
else:
    plan = st.session_state.plan
    daily_minutes = st.session_state.daily_hours * 60
    today_str = datetime.today().strftime("%Y-%m-%d")

    missed_day = None

    # ------------------ DISPLAY SCHEDULE ------------------
    for date, subjects in list(plan.items())[:7]:
        st.markdown(f"### {date}")

        completed = st.checkbox(
            f"Mark {date} as Completed",
            key=f"completed_{date}"
        )

        formatted_data = []
        for subject, minutes in subjects.items():
            formatted_data.append({
                "Subject": subject,
                "Study Time": format_time(minutes)
            })

        df = pd.DataFrame(formatted_data)
        st.table(df)

        # Detect missed only for past dates
        if date < today_str and not completed and missed_day is None:
            missed_day = date

    # ------------------ STORE MISSED DAY ------------------
    if missed_day:
        st.session_state.missed_day = missed_day
    else:
        st.session_state.pop("missed_day", None)

    # ------------------ PRODUCTIVITY SCORE (MINUTE BASED) ------------------
    scheduled_minutes = 0
    completed_minutes = 0

    for date, subjects in plan.items():
        if date <= today_str:
            day_total = sum(subjects.values())
            scheduled_minutes += day_total

            if st.session_state.get(f"completed_{date}", False):
                completed_minutes += day_total

    st.markdown("## 📈 Productivity Score")

    if scheduled_minutes > 0:
        productivity_score = int((completed_minutes / scheduled_minutes) * 100)

        if productivity_score >= 80:
            st.success(f"🔥 Excellent! Productivity: {productivity_score}%")
        elif productivity_score >= 50:
            st.info(f"⚡ Moderate Productivity: {productivity_score}%")
        else:
            st.error(f"⚠ Low Productivity: {productivity_score}%")
    else:
        st.info("Not enough historical data yet.")

    # ------------------ STREAK TRACKING ------------------

    st.markdown("## 🔥 Study Streak")

    streak = 0

    sorted_dates = sorted(plan.keys())

    for date in sorted_dates:
        if date > today_str:
            break

        if st.session_state.get(f"completed_{date}", False):
            streak += 1
        else:
            streak = 0  # Reset streak on miss

    if streak >= 5:
        st.success(f"🔥 Amazing! {streak}-Day Streak!")
    elif streak >= 3:
        st.info(f"⚡ Great! {streak}-Day Streak")
    elif streak > 0:
        st.write(f"📘 Current Streak: {streak} days")
    else:
        st.warning("No active streak yet.")

    # ------------------ ANIMATED PROGRESS BAR ------------------

    if scheduled_minutes > 0:
        st.markdown("### 🚀 Overall Progress")

        progress_value = productivity_score / 100

        progress_bar = st.progress(0)

        for i in range(int(progress_value * 100) + 1):
            progress_bar.progress(i / 100)

        st.write(f"{productivity_score}% Complete")


    # ------------------ PROGRESS LINE CHART ------------------

    st.markdown("## 📊 Progress Dashboard")

    dates = list(plan.keys())[:7]
    completion_data = []

    for d in dates:
        completed = st.session_state.get(f"completed_{d}", False)
        completion_data.append(1 if completed else 0)

    fig, ax = plt.subplots()

    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    ax.plot(
        range(len(completion_data)),
        completion_data,
        marker='o',
        linewidth=3,
        color='#00BFFF'
    )

    ax.fill_between(
        range(len(completion_data)),
        completion_data,
        alpha=0.3,
        color='#00BFFF'
    )

    ax.set_title("Daily Completion Trend", color='white')   
    ax.set_ylabel("Completed (1 = Yes, 0 = No)", color='white')
    ax.set_xlabel("Day Index", color='white')

    ax.tick_params(colors='white')
    ax.set_ylim(0, 1.2)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    st.pyplot(fig)

    # ------------------ AUTO REPLAN ------------------
    if "missed_day" in st.session_state:

        missed_day = st.session_state.missed_day

        st.warning(f"⚠ Missed Day Detected: {missed_day}")
        st.info("🤖 Agent is recalculating optimal schedule...")

        upcoming_days = [
            d for d in plan.keys()
            if d > missed_day
        ][:2]

        for date in upcoming_days:
            total_minutes = sum(plan[date].values())
            remaining_minutes = daily_minutes
            subjects = list(plan[date].keys())

            for i, subject in enumerate(subjects):
                if i == len(subjects) - 1:
                    plan[date][subject] = remaining_minutes
                else:
                    ratio = plan[date][subject] / total_minutes
                    allocated = int(ratio * daily_minutes)
                    plan[date][subject] = allocated
                    remaining_minutes -= allocated

        st.success("Reschedule Complete ✅")

        for date in upcoming_days:
            st.markdown(f"### 🔄 Updated {date}")
            for subject, minutes in plan[date].items():
                st.write(f"{subject}: {format_time(minutes)}")
