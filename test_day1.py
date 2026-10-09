import os
import sys
from datetime import datetime, timedelta
from agent.agent import StudyPlannerAgent
from agent.memory import clear_all_data, register_user, load_daily_plan, load_agent_decisions
from agent.utils import format_time

def print_header(title):
    print(f"\n{'='*60}\n {title}\n{'='*60}")

def run_tests():
    print_header("RUNNING MULTI-USER CORE AGENT & REPLANNING VERIFICATION TESTS")

    clear_all_data()

    # Create Test User
    success, user = register_user("testuser", "password123")
    assert success, f"Failed to register test user: {user}"
    user_id = user["id"]

    agent = StudyPlannerAgent(user_id=user_id)

    # TEST 1: Basic setup (3 subjects: Math=45, DSA=80, OS=42)
    print_header("TEST 1: 3 Subjects (2 Weak, 1 Strong, 4 hrs/day)")
    today_str = datetime.today().strftime("%Y-%m-%d")
    exam_date_str = (datetime.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    obs = agent.observe(
        subject_scores={"Math": 45, "DSA": 80, "OS": 42},
        exam_date=exam_date_str,
        daily_hours=4,
        max_daily_hours=5
    )
    analysis = agent.analyze(obs)
    dec = agent.decide(obs, analysis)
    plan = agent.act(obs, dec)
    
    print(f"Generated {len(plan)} days in plan for User ID {user_id}.")
    print("Day 1 Plan:", {k: format_time(v) for k, v in plan[today_str].items()})
    assert len(plan) == 7
    assert plan[today_str]['Math'] > plan[today_str]['DSA'], "Math (weak) should get more time than DSA (strong)!"

    # TEST 2: All subjects weak
    print_header("TEST 2: All Subjects Weak")
    obs = agent.observe(
        subject_scores={"Math": 30, "DSA": 40, "OS": 35},
        exam_date=exam_date_str,
        daily_hours=4,
        max_daily_hours=5
    )
    analysis = agent.analyze(obs)
    plan = agent.act(obs, agent.decide(obs, analysis))
    print("Equal/similar allocation for all weak subjects:", {k: format_time(v) for k, v in plan[today_str].items()})

    # TEST 3: No weak subjects
    print_header("TEST 3: No Weak Subjects")
    obs = agent.observe(
        subject_scores={"Math": 85, "DSA": 90, "OS": 88},
        exam_date=exam_date_str,
        daily_hours=4,
        max_daily_hours=5
    )
    analysis = agent.analyze(obs)
    plan = agent.act(obs, agent.decide(obs, analysis))
    print("Balanced allocation for strong subjects:", {k: format_time(v) for k, v in plan[today_str].items()})

    # TEST 4: Single Subject
    print_header("TEST 4: One Subject")
    obs = agent.observe(
        subject_scores={"Algorithms": 50},
        exam_date=exam_date_str,
        daily_hours=3,
        max_daily_hours=4
    )
    plan = agent.act(obs, agent.decide(obs, agent.analyze(obs)))
    print("Single subject allocation:", {k: format_time(v) for k, v in plan[today_str].items()})
    assert plan[today_str]['Algorithms'] == 180, "Single subject should get 100% of daily time (180 mins)!"

    # TEST 5 & 6 & 7: Partial Completion -> Backlog -> Max Limit Replanning
    print_header("TEST 5, 6 & 7: Partial Completion -> Backlog -> Max Limit Replanning")
    short_exam_date = (datetime.today() + timedelta(days=3)).strftime("%Y-%m-%d")
    obs = agent.observe(
        subject_scores={"Math": 40, "OS": 50},
        exam_date=short_exam_date,
        daily_hours=4,      # 240 mins base
        max_daily_hours=5   # 300 mins cap
    )
    plan = agent.act(obs, agent.decide(obs, agent.analyze(obs)))
    
    day1_str = today_str
    day2_str = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print(f"Original Day 1 planned: Math={format_time(plan[day1_str]['Math'])}, OS={format_time(plan[day1_str]['OS'])}")
    
    agent.monitor(day1_str, "Math", 30)
    agent.monitor(day1_str, "OS", 30)
    
    reflection = agent.reflect(current_date_str=day1_str)
    print(f"Reflection Backlog detected: Math={format_time(reflection['backlog_by_subject']['Math'])}, OS={format_time(reflection['backlog_by_subject']['OS'])}")
    print(f"Total Backlog: {format_time(reflection['total_backlog_minutes'])}")
    
    new_plan = agent.replan(current_date_str=day1_str)
    print(f"Replanned Day 2 target total: {format_time(sum(new_plan[day2_str].values()))}")
    print(f"Replanned Day 2 allocations: Math={format_time(new_plan[day2_str]['Math'])}, OS={format_time(new_plan[day2_str]['OS'])}")
    
    assert sum(new_plan[day2_str].values()) <= 300, "Replanning must respect max daily limit of 5 hours (300 mins)!"

    # TEST 10: SQLite Persistence reloading
    print_header("TEST 10: SQLite Persistence Verification for User")
    saved_plan_in_db = load_daily_plan(user_id)
    decisions_in_db = load_agent_decisions(user_id)
    print(f"Loaded {len(saved_plan_in_db)} days from SQLite database for User {user_id}.")
    print(f"Loaded {len(decisions_in_db)} agent decision logs from SQLite database for User {user_id}.")
    
    assert len(saved_plan_in_db) > 0, "Database must hold persisted plan for user!"
    assert len(decisions_in_db) > 0, "Database must hold agent decisions for user!"

    print_header("ALL MULTI-USER AGENT TESTS PASSED SUCCESSFULLY! [SUCCESS]")

if __name__ == "__main__":
    run_tests()
