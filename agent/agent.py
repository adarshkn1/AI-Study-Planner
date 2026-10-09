from datetime import datetime, date
from agent.utils import validate_inputs
from agent.scoring import categorize_subject_performance, calculate_subject_priority_score
from agent.planner import generate_initial_plan
from agent.replanner import recalculate_and_replan
from agent.memory import (
    init_db,
    save_settings,
    load_settings,
    save_subjects,
    load_subjects,
    save_daily_plan,
    load_daily_plan,
    log_subject_completion,
    load_study_logs
)

class StudyPlannerAgent:
    """
    Rule-Based Adaptive Autonomous Agent implementing the 7-Stage Loop per User:
    OBSERVE -> ANALYZE -> DECIDE -> ACT -> MONITOR -> REFLECT -> REPLAN
    """

    def __init__(self, user_id: int):
        init_db()
        self.user_id = user_id

    def observe(self, subject_scores: dict, exam_date: str, daily_hours: int, max_daily_hours: int):
        """1. OBSERVE: Ingest raw environment state and user constraints."""
        days_left = validate_inputs(subject_scores, exam_date, daily_hours, max_daily_hours)
        
        subjects_data = []
        for name, score in subject_scores.items():
            subjects_data.append({
                'name': name,
                'score': score,
                'priority': 3  # default priority
            })
            
        save_settings(self.user_id, exam_date, daily_hours, max_daily_hours)
        save_subjects(self.user_id, subjects_data)
        
        return {
            'subjects_data': subjects_data,
            'exam_date': exam_date,
            'daily_hours': daily_hours,
            'max_daily_hours': max_daily_hours,
            'days_left': days_left
        }

    def analyze(self, observation: dict) -> dict:
        """2. ANALYZE: Evaluate performance categories and priority scores."""
        analysis = {}
        for s in observation['subjects_data']:
            cat = categorize_subject_performance(s['score'])
            p_score = calculate_subject_priority_score(
                score=s['score'],
                user_priority=s.get('priority', 3),
                days_left=observation['days_left'],
                backlog_minutes=0
            )
            analysis[s['name']] = {
                'category': cat,
                'priority_score': p_score
            }
        return analysis

    def decide(self, observation: dict, analysis: dict) -> dict:
        """3. DECIDE: Determine target allocation parameters."""
        total_days = observation['days_left']
        daily_mins = observation['daily_hours'] * 60
        max_mins = observation['max_daily_hours'] * 60
        
        return {
            'total_days': total_days,
            'daily_minutes': daily_mins,
            'max_daily_minutes': max_mins,
            'analysis': analysis
        }

    def act(self, observation: dict, decision: dict) -> dict:
        """4. ACT: Generate initial schedule artifact and store in DB memory."""
        plan = generate_initial_plan(
            user_id=self.user_id,
            subjects_data=observation['subjects_data'],
            daily_hours=observation['daily_hours'],
            days_left=observation['days_left']
        )
        save_daily_plan(self.user_id, plan)
        return plan

    def monitor(self, date_str: str, subject_name: str, completed_minutes: int):
        """5. MONITOR: Capture actual user study execution logs."""
        log_subject_completion(self.user_id, date_str, subject_name, completed_minutes)

    def reflect(self, current_date_str: str) -> dict:
        """
        6. REFLECT: Compare planned vs completed work up to current_date_str.
        Returns backlog metrics per subject and overall productivity.
        """
        plan = load_daily_plan(self.user_id)
        logs = load_study_logs(self.user_id)
        subjects = load_subjects(self.user_id)
        
        past_dates = [d for d in plan.keys() if d <= current_date_str]
        
        backlog = {}
        total_planned = 0
        total_completed = 0
        
        for s in subjects:
            s_name = s['name']
            p_min = sum(plan[d].get(s_name, 0) for d in past_dates)
            c_min = sum(logs.get(d, {}).get(s_name, 0) for d in past_dates)
            
            total_planned += p_min
            total_completed += c_min
            backlog[s_name] = max(0, p_min - c_min)
            
        completion_ratio = (total_completed / total_planned) if total_planned > 0 else 0.0
        
        return {
            'past_dates': past_dates,
            'total_planned_minutes': total_planned,
            'total_completed_minutes': total_completed,
            'backlog_by_subject': backlog,
            'total_backlog_minutes': sum(backlog.values()),
            'completion_ratio': round(completion_ratio, 2)
        }

    def replan(self, current_date_str: str) -> dict:
        """7. REPLAN: Automatically adjust future schedule based on reflection."""
        settings = load_settings(self.user_id)
        if not settings:
            raise ValueError("No settings found for this user in memory. Create a plan first.")
            
        plan = load_daily_plan(self.user_id)
        logs = load_study_logs(self.user_id)
        subjects = load_subjects(self.user_id)
        
        updated_plan = recalculate_and_replan(
            user_id=self.user_id,
            existing_plan=plan,
            study_logs=logs,
            subjects_data=subjects,
            daily_hours=settings['daily_hours'],
            max_daily_hours=settings['max_daily_hours'],
            exam_date_str=settings['exam_date'],
            current_date_str=current_date_str
        )
        
        save_daily_plan(self.user_id, updated_plan)
        return updated_plan
