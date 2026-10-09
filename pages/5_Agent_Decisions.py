import streamlit as st
from agent.memory import load_agent_decisions
from agent.theme import apply_custom_theme, render_hero

st.set_page_config(page_title="Agent Decisions", page_icon="🤖", layout="wide")
apply_custom_theme()

# Check Authentication
if "user" not in st.session_state or not st.session_state["user"]:
    st.warning("🔒 Please log in or register on the Home Page first to view agent decision logs.")
    st.stop()

user = st.session_state["user"]
user_id = user["id"]

st.sidebar.markdown(f"### 👤 Profile")
st.sidebar.info(f"**Logged in as:** `{user['username']}`")
if st.sidebar.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear()
    st.rerun()

render_hero(
    title="Explainable Agent Decision Log",
    subtitle=f"Audit trail explaining WHY allocations were generated or modified for {user['username']}.",
    icon="🤖"
)

decisions = load_agent_decisions(user_id)

if not decisions:
    st.info("ℹ️ No agent decisions recorded yet. Create or replan a study schedule to view decision logs.")
    st.stop()

st.markdown(f"**Total Recorded Decision Events:** `{len(decisions)}`")

for idx, dec in enumerate(decisions):
    with st.expander(f"📌 Event #{len(decisions)-idx}: {dec['trigger_event']} ({dec['timestamp']})", expanded=(idx == 0)):
        st.markdown(f"**Reason / Analysis:** {dec['reason']}")
        st.markdown(f"**Agent Decision:** {dec['decision']}")
        st.markdown(f"**Constraint Enforced:** `{dec['constraint_applied']}`")
        
        if "WARNING" in dec['result']:
            st.warning(f"**Result:** {dec['result']}")
        else:
            st.success(f"**Result:** {dec['result']}")
