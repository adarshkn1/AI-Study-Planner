import streamlit as st
import time
from datetime import datetime
from agent.performance import identify_weak_subjects
from agent.planner import generate_plan

st.title("📅 Generate Study Plan")

subjects_scores = {}

num_subjects = st.number_input("Number of Subjects", min_value=1, step=1)

for i in range(num_subjects):
    subject = st.text_input(f"Subject {i+1} Name", key=f"sub{i}")
    score = st.number_input(f"{subject} Score", 0, 100, key=f"score{i}")
    if subject:
        subjects_scores[subject] = score

exam_date = st.date_input("Exam Date")
daily_hours = st.number_input("Daily Study Hours", min_value=1)

if st.button("Generate Plan"):

    st.info("🤖 Agent is analyzing performance...")
    time.sleep(2)

    weak_subjects = identify_weak_subjects(subjects_scores)

    days_left = (exam_date - datetime.today().date()).days

    if days_left > 0:
        plan = generate_plan(
            list(subjects_scores.keys()),
            weak_subjects,
            daily_hours,
            days_left
        )

        st.session_state.plan = plan
        st.session_state.daily_hours = daily_hours
        st.session_state.weak_subjects = weak_subjects

        st.success("Plan Generated Successfully ✅")
    else:
        st.error("Exam date must be in the future.")
