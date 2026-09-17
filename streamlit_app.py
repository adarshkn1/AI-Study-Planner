import streamlit as st

st.set_page_config(
    page_title="AI Study Planner",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🧠 AI Study Planner Agent")

st.markdown("""
Welcome to your intelligent study planning system.

Use the pages on the left:
- Generate Plan
- View Schedule
- Replan
""")
