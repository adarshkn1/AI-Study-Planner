from datetime import datetime, timedelta
from agent.scoring import calculate_subject_priority_score
from agent.decisions import AgentDecisionLogger

def allocate_clean_time_blocks(scores: dict, total_target_minutes: int, block_size: int = 15) -> dict:
    """
    Quantizes minute allocations into clean human-friendly time blocks (15-min increments).
    Prevents messy odd numbers like 1 hr 23 min or 1 hr 07 min.
    """
    if not scores or total_target_minutes <= 0:
        return {k: 0 for k in scores.keys()}
        
    total_score = sum(scores.values())
    if total_score <= 0:
        total_score = 1.0
        
    remaining_blocks = total_target_minutes // block_size
    allocations = {subj: 0 for subj in scores.keys()}
    
    # Minimum 1 block (15 min) per subject if capacity permits
    if remaining_blocks >= len(scores):
        for subj in scores.keys():
            allocations[subj] = 1
            
    used_blocks = sum(allocations.values())
    blocks_to_distribute = max(0, remaining_blocks - used_blocks)
    
    if blocks_to_distribute > 0:
        fractional_parts = {}
        for subj, score in scores.items():
            exact_blocks = (score / total_score) * blocks_to_distribute
            whole_blocks = int(exact_blocks)
            allocations[subj] += whole_blocks
            fractional_parts[subj] = exact_blocks - whole_blocks
            
        remaining_unassigned = remaining_blocks - sum(allocations.values())
        sorted_subjs = sorted(fractional_parts.keys(), key=lambda s: (fractional_parts[s], scores[s]), reverse=True)
        for i in range(remaining_unassigned):
            subj_to_bump = sorted_subjs[i % len(sorted_subjs)]
            allocations[subj_to_bump] += 1

    final_minutes = {subj: blocks * block_size for subj, blocks in allocations.items()}
    
    # Adjust residual minutes if total_target_minutes wasn't multiple of block_size
    diff = total_target_minutes - sum(final_minutes.values())
    if diff > 0:
        highest_subj = max(scores.keys(), key=lambda s: scores[s])
        final_minutes[highest_subj] += diff
        
    return final_minutes

def generate_initial_plan(
    user_id: int,
    subjects_data: list,
    daily_hours: int,
    days_left: int,
    start_date_str: str = None
) -> dict:
    """
    Generates an initial study plan using clean 15-minute time blocks for a specific user.
    subjects_data: list of dicts [{'name': 'Math', 'score': 45, 'priority': 3}, ...]
    """
    if start_date_str:
        base_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    else:
        base_date = datetime.today().date()

    daily_minutes = daily_hours * 60
    scores = {}
    
    for subj in subjects_data:
        p_score = calculate_subject_priority_score(
            score=subj['score'],
            user_priority=subj.get('priority', 3),
            days_left=days_left,
            backlog_minutes=0
        )
        scores[subj['name']] = p_score

    plan = {}

    for day_offset in range(days_left):
        current_date_str = (base_date + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        plan[current_date_str] = allocate_clean_time_blocks(scores, daily_minutes, block_size=15)

    # Log initial decision
    reason_desc = ", ".join([f"{subj['name']}: score {subj['score']} (Priority Weight: {scores[subj['name']]})" for subj in subjects_data])
    AgentDecisionLogger.log(
        user_id=user_id,
        trigger_event="Initial Plan Creation",
        reason=f"Generated plan for {days_left} days. Subject scores & weights: {reason_desc}",
        decision=f"Allocated {daily_hours} hrs ({daily_minutes} mins) per day using clean 15-minute study blocks.",
        constraint_applied=f"Daily limit = {daily_hours} hrs.",
        result=f"Clean plan generated across {days_left} days successfully."
    )

    return plan
