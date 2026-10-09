# 🧠 Adaptive AI Study Planner Agent

An adaptive, rule-based autonomous study-planning agent built with Python, Streamlit, and SQLite. The system dynamically balances student workload based on subject weakness, exam urgency, user priority, and accumulated study backlog while strictly enforcing human daily study capacity limits.

---

## 🎯 Problem Statement

Traditional study schedulers suffer from two major flaws:
1. **Static Scheduling**: They do not adapt when a student misses a study session or partially completes a topic.
2. **Unrealistic Overload**: Naive replanning algorithms dump all missed hours onto future days without considering daily human study limits.

---

## 💡 Solution

The **AI Study Planner Agent** models study planning as an autonomous **Observe-Analyze-Decide-Act-Monitor-Reflect-Replan** control loop. It tracks progress at the **subject-minute level**, calculates exact per-subject backlog, and redistributes uncompleted work across remaining days without exceeding a user's maximum comfortable daily cap (`max_daily_hours`).

---

## 🤖 Agent Control Loop (7-Stage Architecture)

```
       [ 1. OBSERVE ] ──> Ingest raw scores, exam date & daily limits
             │
       [ 2. ANALYZE ] ──> Categorize weakness & calculate priority scores
             │
       [ 3. DECIDE  ] ──> Compute target minute allocation ratios
             │
       [ 4. ACT     ] ──> Generate & persist initial daily plan
             │
       [ 5. MONITOR ] ──> Capture actual user study execution logs
             │
       [ 6. REFLECT ] ──> Compare planned vs completed (Compute Backlog)
             │
       [ 7. REPLAN  ] ──> Redistribute backlog subject to daily max cap
```

1. **OBSERVE**: Collects subject scores, user priorities (1–5), target exam date, base daily hours, and max daily cap.
2. **ANALYZE**: Computes transparent priority scores:
   $$\text{Priority Score} = (\text{Weakness} \times 0.4) + (\text{UserPriority} \times 10) + (\text{Urgency} \times 5) + (\text{BacklogFactor} \times 8)$$
3. **DECIDE**: Determines optimal time allocation ratios across subjects.
4. **ACT**: Generates an initial integer-minute schedule and stores it in SQLite.
5. **MONITOR**: Records actual studied minutes per subject for each date.
6. **REFLECT**: Computes subject-level backlog: $\text{Backlog} = \text{Planned Minutes} - \text{Completed Minutes}$.
7. **REPLAN**: Redistributes backlog across remaining days, capping daily workload at `max_daily_hours` and logging transparent decision warnings if capacity is reached.

---

## 🏗️ Tech Stack & System Architecture

- **Language**: Python 3.12+
- **Frontend / UI**: Streamlit (Multi-page app with glassmorphism CSS & dark theme)
- **Database**: SQLite3 (`data/study_planner.db`)
- **Data & Visualization**: Pandas, Matplotlib
- **Machine Learning (Optional Component)**: Scikit-learn (`LogisticRegression` completion probability predictor)

### Directory Structure
```
ai-study-planner/
│
├── agent/
│   ├── __init__.py
│   ├── agent.py         # Main StudyPlannerAgent (7-Stage Loop)
│   ├── memory.py        # SQLite Persistence & Multi-User Authentication
│   ├── scoring.py       # Transparent Subject Priority Scoring Algorithm
│   ├── decisions.py     # Explainable Agent Decision Logger
│   ├── planner.py       # Integer-Minute Initial Plan Generator
│   ├── replanner.py     # Capacity-Constrained Backlog Replanner
│   ├── ml_predictor.py  # Optional Logistic Regression Completion Model
│   ├── theme.py        # Modern UI Styling & Dark Theme CSS Injection
│   └── utils.py         # Time formatting (minutes <-> '1 hr 20 min') & validations
│
├── data/
│   └── study_planner.db # Multi-user SQLite database
│
├── pages/
│   ├── 1_Create_Plan.py      # Input subjects, scores, priorities, exam date & cap
│   ├── 2_Today.py            # Subject-level study execution logging & instant replan
│   ├── 3_Schedule.py         # Expandable daily schedule cards & status indicators
│   ├── 4_Progress.py         # Weighted Productivity Score, streak & dark charts
│   ├── 5_Agent_Decisions.py # Transparent audit trail of agent reasoning
│   └── 6_Settings.py        # Demo Mode Date Simulator & database memory management
│
├── streamlit_app.py     # Main Streamlit App & Authentication Entrypoint
├── test_day1.py         # Automated CLI Verification Test Suite
├── requirements.txt
└── README.md
```

---

## 🔒 Multi-User Authentication & Database Schema

All database records are isolated by `user_id`:

- `users`: `id`, `username` (UNIQUE), `password_hash` (SHA-256), `created_at`
- `settings`: `user_id` (PK), `exam_date`, `daily_hours`, `max_daily_hours`, `updated_at`
- `subjects`: `(user_id, name)` (PK), `score`, `priority`
- `daily_plan`: `(user_id, plan_date, subject_name)` (UNIQUE), `planned_minutes`
- `study_logs`: `(user_id, log_date, subject_name)` (UNIQUE), `completed_minutes`, `logged_at`
- `agent_decisions`: `user_id`, `timestamp`, `trigger_event`, `reason`, `decision`, `constraint_applied`, `result`

---

## ⚡ Installation & Usage

1. **Clone Repository & Install Dependencies**:
   ```powershell
   git clone https://github.com/your-username/ai-study-planner.git
   cd ai-study-planner
   pip install -r requirements.txt
   ```

2. **Run Automated Backend Verification Test Suite**:
   ```powershell
   python test_day1.py
   ```

3. **Launch Streamlit Web Application**:
   ```powershell
   python -m streamlit run streamlit_app.py
   ```

---

## 📈 Productivity Score Formula

$$\text{Productivity Score} = (0.60 \times \text{Completion Ratio}) + (0.25 \times \text{Consistency Ratio}) + (0.15 \times \text{Backlog Control Ratio})$$

- **Completion Ratio**: Total Completed Minutes / Total Planned Minutes
- **Consistency Ratio**: Days with $\ge 80\%$ completion / Total Expected Days
- **Backlog Control Ratio**: $\max(0, 1 - (\text{Backlog Minutes} / \text{Planned Minutes}))$

---

## 📄 Resume Bullet Points

- **Built a Rule-Based Autonomous Study Planner Agent** in Python & Streamlit using an `Observe-Analyze-Decide-Act-Monitor-Reflect-Replan` control loop to optimize study time across subjects based on weakness, exam urgency, and backlog.
- **Engineered a Capacity-Constrained Replanning Algorithm** that tracks per-subject progress at integer-minute precision, redistributing unfinished backlog while strictly enforcing human daily study limits (`max_daily_hours`).
- **Implemented Multi-User Authentication & SQLite Persistence** using SHA-256 password hashing and isolated relational database schemas for users, plans, execution logs, and explainable decision logs.

---

## 💡 Interview Questions & Answers

### 1. "Why describe this as a rule-based agent rather than an LLM agent?"
> **Answer**: Deterministic numerical scheduling requires exact minute calculations and hard capacity constraints. LLMs suffer from arithmetic hallucinations and latency. A rule-based autonomous agent with an explicit control loop delivers 100% mathematical precision, zero API cost, instant latency, and complete explainability.

### 2. "How does your system prevent human burnout when backlog accumulates?"
> **Answer**: The agent enforces a strict maximum comfortable study cap (`max_daily_hours`). When backlog accumulates, the agent distributes extra workload up to this daily cap. If backlog exceeds available capacity, it allocates up to the cap limit and logs a transparent warning in the decision audit trail.

---

## ⚠️ Limitations & Future Improvements

- **Current Limitation**: Does not auto-sync with Google Calendar or Outlook Calendar APIs.
- **Future Improvement**: Add calendar integration (iCal / Google Calendar API) to block out study slots automatically.
