from agent.memory import load_memory, mark_day_missed
from agent.performance import identify_weak_subjects
from agent.planner import generate_plan
from agent.utils import format_time
from datetime import datetime


class StudyPlannerAgent:

    def __init__(self, subjects_scores, exam_date, daily_hours):
        self.subjects_scores = subjects_scores
        self.exam_date = datetime.strptime(exam_date, "%Y-%m-%d")
        self.daily_hours = daily_hours
        self.memory = load_memory()

    def run(self):
        print("\n--- Agent Started ---\n")

        # Step 1: Analyze Performance
        weak_subjects = identify_weak_subjects(self.subjects_scores)
        print("Weak Subjects Identified:", weak_subjects)

        today = datetime.today()
        days_left = (self.exam_date - today).days

        if days_left <= 0:
            print("Exam date must be in the future.")
            return

        # Step 2: Generate Plan
        plan = generate_plan(
            list(self.subjects_scores.keys()),
            weak_subjects,
            self.daily_hours,
            days_left
        )

        # Explain reasoning
        print("\nReasoning:")
        for subject, score in self.subjects_scores.items():
            if score < 60:
                print(f"{subject} classified as weak (score {score} < 60 threshold)")

        # Display Plan
        print("\nGenerated Study Plan:\n")
        for date, subjects in plan.items():
            print(f"\nDate: {date}")
            for subject, minutes in subjects.items():
                print(f"  {subject}: {format_time(minutes)}")

        # Step 3: Monitor Execution
        miss = input("\nDid you miss today? (yes/no): ")

        if miss.lower() == "yes":
            today_str = today.strftime("%Y-%m-%d")
            mark_day_missed(today_str)

            print("\nReplanning due to missed day...")

            upcoming_days = list(plan.keys())[1:3]

            for date in upcoming_days:
                total_minutes = sum(plan[date].values())
                remaining_minutes = self.daily_hours * 60

                subjects = list(plan[date].keys())

                for i, subject in enumerate(subjects):
                    if i == len(subjects) - 1:
                        plan[date][subject] = remaining_minutes
                    else:
                        ratio = plan[date][subject] / total_minutes
                        allocated = int(ratio * (self.daily_hours * 60))
                        plan[date][subject] = allocated
                        remaining_minutes -= allocated

            print("\nUpdated Plan After Replanning:\n")
            for date in upcoming_days:
                print(f"\nDate: {date}")
                for subject, minutes in plan[date].items():
                    print(f"  {subject}: {format_time(minutes)}")

        print("\n--- Agent Finished ---\n")
