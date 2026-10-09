from datetime import datetime, timedelta
from agent.scoring import calculate_subject_priority_score
from agent.planner import allocate_clean_time_blocks
from agent.decisions import AgentDecisionLogger
from agent.utils import format_time

def recalculate_and_replan(
    user_id: int,
    existing_plan: dict,
    study_logs: dict,
    subjects_data: list,
    daily_hours: int,
    max_daily_hours: int,
    exam_date_str: str,
    current_date_str: str
) -> dict:
    """
    Intelligent replanning algorithm for a specific user using clean 15-minute time blocks:
    1. Computes exact per-subject backlog from past dates <= current_date_str.
    2. Recalculates subject priority scores with backlog weight.
    3. Redistributes backlog across remaining future days (> current_date_str).
    4. Enforces max_daily_hours constraint (capacity limit).
    5. Formats allocations into clean 15-minute study blocks.
    """
    all_dates = sorted(list(existing_plan.keys()))
    past_dates = [d for d in all_dates if d <= current_date_str]
    future_dates = [d for d in all_dates if d > current_date_str]

    if not future_dates:
        AgentDecisionLogger.log(
            user_id=user_id,
            trigger_event="Replanning Triggered",
            reason=f"No remaining study days after {current_date_str}.",
            decision="Could not redistribute backlog because exam is today or in the past.",
            constraint_applied="0 remaining days.",
            result="Plan unchanged."
        )
        return existing_plan

    # Step 1: Calculate per-subject backlog
    backlog_by_subject = {}
    subject_scores_map = {s['name']: s for s in subjects_data}
    
    for subj_name in subject_scores_map.keys():
        total_planned = sum(existing_plan[d].get(subj_name, 0) for d in past_dates)
        total_completed = sum(study_logs.get(d, {}).get(subj_name, 0) for d in past_dates)
        backlog_by_subject[subj_name] = max(0, total_planned - total_completed)

    total_backlog_minutes = sum(backlog_by_subject.values())

    if total_backlog_minutes == 0:
        AgentDecisionLogger.log(
            user_id=user_id,
            trigger_event="Replanning Check",
            reason=f"Checked completion history up to {current_date_str}. All work on schedule.",
            decision="Keep current schedule intact.",
            constraint_applied=f"Daily limit = {daily_hours} hrs.",
            result="No backlog detected. Zero schedule changes needed."
        )
        return existing_plan

    # Step 2: Capacity planning
    base_daily_minutes = daily_hours * 60
    max_daily_minutes = max_daily_hours * 60
    num_future_days = len(future_dates)
    
    extra_capacity_per_day = max_daily_minutes - base_daily_minutes
    total_extra_capacity = extra_capacity_per_day * num_future_days

    absorbed_backlog = min(total_backlog_minutes, total_extra_capacity)
    unabsorbed_backlog = total_backlog_minutes - absorbed_backlog

    # Backlog added per future day rounded to 15-minute increments
    extra_minutes_per_day = (absorbed_backlog // num_future_days // 15) * 15
    extra_remainder = absorbed_backlog - (extra_minutes_per_day * num_future_days)

    # Step 3: Compute updated priority scores with backlog term
    updated_scores = {}
    days_left = len(future_dates)
    for subj_name, subj_info in subject_scores_map.items():
        updated_scores[subj_name] = calculate_subject_priority_score(
            score=subj_info['score'],
            user_priority=subj_info.get('priority', 3),
            days_left=days_left,
            backlog_minutes=backlog_by_subject[subj_name]
        )

    # Step 4: Re-build future plan days using clean 15-minute time blocks
    new_plan = existing_plan.copy()

    for idx, f_date in enumerate(future_dates):
        daily_target_minutes = base_daily_minutes + extra_minutes_per_day + (15 if idx * 15 < extra_remainder else 0)
        daily_target_minutes = min(daily_target_minutes, max_daily_minutes)
        
        new_plan[f_date] = allocate_clean_time_blocks(updated_scores, daily_target_minutes, block_size=15)

    # Step 5: Log Explainable Agent Decision
    backlog_desc = ", ".join([f"{s}: {format_time(m)}" for s, m in backlog_by_subject.items() if m > 0])
    
    result_msg = f"Redistributed {format_time(absorbed_backlog)} across {num_future_days} days in clean 15-min blocks."
    if unabsorbed_backlog > 0:
        result_msg += f" WARNING: {format_time(unabsorbed_backlog)} could not be scheduled due to {max_daily_hours}hr daily max limit!"

    AgentDecisionLogger.log(
        user_id=user_id,
        trigger_event="Automatic Replanning Triggered",
        reason=f"Detected backlog up to {current_date_str}: {backlog_desc}.",
        decision=f"Increased daily target from {format_time(base_daily_minutes)} up to {format_time(max_daily_minutes)} cap.",
        constraint_applied=f"Strict max comfortable limit: {max_daily_hours} hrs/day ({max_daily_minutes} mins).",
        result=result_msg
    )

    return new_plan
