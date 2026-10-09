import numpy as np
from sklearn.linear_model import LogisticRegression
from agent.memory import load_study_logs, load_daily_plan, load_subjects

class CompletionPredictorML:
    """
    Optional Simple ML Component:
    Predicts completion probability (0.0 to 1.0) for a subject session
    using Logistic Regression trained on user historical study logs.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.model = LogisticRegression()
        self.is_trained = False

    def train(self):
        daily_plan = load_daily_plan(self.user_id)
        study_logs = load_study_logs(self.user_id)
        subjects = load_subjects(self.user_id)

        if not daily_plan or not study_logs:
            return False

        subj_score_map = {s['name']: s['score'] for s in subjects}

        X = []
        y = []

        for p_date, tasks in daily_plan.items():
            for subj, planned_m in tasks.items():
                comp_m = study_logs.get(p_date, {}).get(subj, 0)
                score = subj_score_map.get(subj, 50)
                
                # Features: [planned_minutes, subject_score]
                X.append([planned_m, score])
                # Target: 1 if >= 80% completed, 0 otherwise
                completed_target = 1 if (planned_m > 0 and (comp_m / planned_m) >= 0.8) else 0
                y.append(completed_target)

        if len(X) < 4 or len(set(y)) < 2:
            # Need minimum samples and both classes to train
            return False

        self.model.fit(np.array(X), np.array(y))
        self.is_trained = True
        return True

    def predict_completion_prob(self, planned_minutes: int, subject_score: int) -> float:
        """Predicts probability (0-100%) of user completing planned session."""
        if not self.is_trained:
            # Fallback heuristic if not enough ML training data
            base = (subject_score / 100.0) * 0.7 + (1.0 - min(1.0, planned_minutes / 240.0)) * 0.3
            return round(min(95.0, max(30.0, base * 100)), 1)

        prob = self.model.predict_proba([[planned_minutes, subject_score]])[0][1]
        return round(float(prob * 100), 1)
