from datetime import datetime, date

def format_time(minutes: int) -> str:
    """Formats integer minutes into human-readable hours and minutes string.
    Example:
    80 -> '1 hr 20 min'
    45 -> '45 min'
    120 -> '2 hr'
    0 -> '0 min'
    """
    if minutes <= 0:
        return "0 min"
    
    hours = minutes // 60
    mins = minutes % 60

    if hours > 0 and mins > 0:
        return f"{hours} hr {mins} min"
    elif hours > 0:
        return f"{hours} hr"
    else:
        return f"{mins} min"

def parse_date(date_input) -> date:
    """Parses date string (YYYY-MM-DD) or returns date object."""
    if isinstance(date_input, date):
        return date_input
    if isinstance(date_input, str):
        return datetime.strptime(date_input, "%Y-%m-%d").date()
    raise ValueError(f"Invalid date format: {date_input}")

def validate_inputs(subject_scores: dict, exam_date_str: str, daily_hours: int, max_daily_hours: int):
    """Validates user inputs to prevent edge case crashes."""
    if not subject_scores:
        raise ValueError("At least one subject must be provided.")
    
    for subj, score in subject_scores.items():
        if not (0 <= score <= 100):
            raise ValueError(f"Score for {subj} must be between 0 and 100.")
            
    exam_dt = parse_date(exam_date_str)
    today = date.today()
    days_left = (exam_dt - today).days
    
    if days_left <= 0:
        raise ValueError("Exam date must be at least 1 day in the future.")
        
    if daily_hours <= 0:
        raise ValueError("Daily study hours must be greater than 0.")
        
    if max_daily_hours < daily_hours:
        raise ValueError("Maximum daily study hours cannot be less than daily study hours.")
        
    return days_left
