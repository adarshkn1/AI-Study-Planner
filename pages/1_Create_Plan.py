import streamlit as st
from datetime import datetime, timedelta
from agent.agent import StudyPlannerAgent
from agent.utils import format_time
from agent.theme import apply_custom_theme, render_hero

st.set_page_config(page_title="Create Study Plan", page_icon="📝", layout="wide")
apply_custom_theme()

# Check Authentication
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("🔒 Please log in or register on the Home Page first to create your personal study plan.")
    st.stop()

user = st.session_state["user"]
user_id = user["id"]

# Sidebar User Info
st.sidebar.markdown(f"### 👤 Profile")
st.sidebar.info(f"**Logged in as:** `{user['username']}`")
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear()
    st.rerun()

render_hero(
    title="Configure Study Plan",
    subtitle=f"Set up subjects, scores, exam dates, time slots, and daily study caps for {user['username']}.",
    icon="📝"
)

agent = StudyPlannerAgent(user_id=user_id)

st.subheader("1. Select Number of Subjects")
num_subjects = st.number_input(
    "How many subjects do you want to plan for?",
    min_value=1,
    max_value=15,
    value=3,
    step=1,
    help="Changing this number immediately updates the subject input rows below."
)

st.divider()

with st.form("create_plan_form"):
    st.subheader("2. Target Exam & Daily Time Limits")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        exam_date = st.date_input("Exam Date", datetime.today() + timedelta(days=7))
    with col2:
        daily_hours = st.number_input("Target Daily Study Hours", min_value=1, max_value=16, value=4, step=1)
    with col3:
        max_daily_hours = st.number_input("Maximum Comfortable Daily Cap (Hours)", min_value=1, max_value=18, value=5, step=1)
    with col4:
        pref_slot = st.selectbox("Preferred Study Time Window", ["Morning (8 AM - 12 PM)", "Afternoon (12 PM - 5 PM)", "Evening (5 PM - 9 PM)", "Night (9 PM - 12 AM)"])

    st.divider()
    st.subheader("3. Enter Subject Details, Scores & Priorities")
    
    subjects_input = []
    
    for i in range(num_subjects):
        st.markdown(f"##### 📚 Subject #{i+1}")
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            s_name = st.text_input(
                f"Subject {i+1} Name",
                value="",
                placeholder=f"Enter subject {i+1} name (e.g. Mathematics)...",
                key=f"s_name_{i}"
            )
        with c2:
            s_score = st.number_input(
                f"Current Score (0-100)",
                min_value=0,
                max_value=100,
                value=50,
                key=f"s_score_{i}"
            )
            if s_score < 60:
                st.markdown("<span class='badge-warning'>⚠️ Category: Weak (<60)</span>", unsafe_allow_html=True)
            elif s_score < 80:
                st.markdown("<span class='badge-info'>⚡ Category: Medium (60-79)</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='badge-success'>🔥 Category: Strong (80+)</span>", unsafe_allow_html=True)

        with c3:
            s_priority = st.slider(
                f"User Priority (1=Low, 5=High)",
                min_value=1,
                max_value=5,
                value=3,
                key=f"s_priority_{i}"
            )
            
        if s_name.strip():
            subjects_input.append({
                'name': s_name.strip(),
                'score': s_score,
                'priority': s_priority
            })
            
        st.caption("---")

    submit_button = st.form_submit_button("🚀 Generate Adaptive Plan", use_container_width=True)

if submit_button:
    if max_daily_hours < daily_hours:
        st.error("❌ Maximum comfortable daily limit cannot be smaller than your base daily target hours.")
    elif exam_date <= datetime.today().date():
        st.error("❌ Exam date must be at least 1 day in the future.")
    elif len(subjects_input) < num_subjects:
        st.error(f"❌ Please fill in all {num_subjects} subject names before submitting.")
    else:
        subj_names = [s['name'] for s in subjects_input]
        if len(subj_names) != len(set(subj_names)):
            st.error("❌ Duplicate subject names detected. Each subject name must be unique.")
        else:
            try:
                scores_dict = {s['name']: s['score'] for s in subjects_input}
                exam_date_str = exam_date.strftime("%Y-%m-%d")
                
                # Run 7-Stage Agent Loop for logged-in user
                obs = agent.observe(
                    subject_scores=scores_dict,
                    exam_date=exam_date_str,
                    daily_hours=daily_hours,
                    max_daily_hours=max_daily_hours
                )
                analysis = agent.analyze(obs)
                dec = agent.decide(obs, analysis)
                plan = agent.act(obs, dec)
                
                st.success(f"✅ Personal Study Plan generated for **{user['username']}**! (Preferred Time Window: {pref_slot})")
                
                st.markdown("### 📋 Generated Initial Day Allocation (Clean 15-Min Blocks)")
                first_day = list(plan.keys())[0]
                st.info(f"**Day 1 Allocation ({first_day}):**")
                
                cols = st.columns(len(plan[first_day]))
                for idx, (subj, mins) in enumerate(plan[first_day].items()):
                    with cols[idx]:
                        st.metric(subj, format_time(mins))
                        
            except Exception as e:
                st.error(f"Error generating plan: {str(e)}")
