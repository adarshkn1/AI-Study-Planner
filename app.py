from agent.agent import StudyPlannerAgent

def main():
    print("=== AI Study Planner Agent ===")

    subjects_scores = {}

    n = int(input("How many subjects? "))

    for _ in range(n):
        subject = input("Enter subject name: ")
        score = int(input(f"Enter score for {subject}: "))
        subjects_scores[subject] = score

    exam_date = input("Enter exam date (YYYY-MM-DD): ")
    daily_hours = int(input("Enter daily study hours: "))

    agent = StudyPlannerAgent(subjects_scores, exam_date, daily_hours)
    agent.run()

if __name__ == "__main__":
    main()
