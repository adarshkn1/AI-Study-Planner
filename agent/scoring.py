def calculate_subject_priority_score(
    score: int,
    user_priority: int = 3,
    days_left: int = 10,
    backlog_minutes: int = 0
) -> float:
    """
    Calculates balanced, transparent priority score for a subject.
    Weakness is given primary weight so weak subjects receive maximum support.
    
    Formula:
    Weakness (0 to 100): (100 - score) * 1.2
    User Priority (1 to 5): user_priority * 6.0 (6 to 30)
    Urgency (Days Left): max(2.0, 30.0 / max(1, days_left)) (3 to 30)
    Backlog Weight: (backlog_minutes / 30.0) * 10.0
    """
    weakness = (100 - score) * 1.2
    priority_weight = user_priority * 6.0
    urgency = max(2.0, 30.0 / max(1, days_left))
    backlog_weight = (backlog_minutes / 30.0) * 10.0

    total_score = weakness + priority_weight + urgency + backlog_weight
    return round(total_score, 2)

def categorize_subject_performance(score: int) -> str:
    """Categorizes subject score into Weak, Medium, Strong."""
    if score < 60:
        return "Weak"
    elif score < 80:
        return "Medium"
    else:
        return "Strong"
