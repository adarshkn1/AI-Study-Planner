from datetime import datetime, timedelta

def generate_plan(subjects, weak_subjects, daily_hours, days_left):
    plan = {}

    total_minutes = daily_hours * 60

    for day in range(days_left):
        date = (datetime.today() + timedelta(days=day)).strftime("%Y-%m-%d")
        plan[date] = {}

        # Assign weights
        weights = {}
        for subject in subjects:
            if subject in weak_subjects:
                weights[subject] = 2
            else:
                weights[subject] = 1

        total_weight = sum(weights.values())
        remaining_minutes = total_minutes

        for i, subject in enumerate(subjects):
            if i == len(subjects) - 1:
                allocated = remaining_minutes
            else:
                allocated = int((weights[subject] / total_weight) * total_minutes)
                remaining_minutes -= allocated

            plan[date][subject] = allocated  # store in minutes

    return plan
