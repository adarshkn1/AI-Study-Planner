import pandas as pd

def identify_weak_subjects(subject_scores):
    """
    subject_scores = {"Math": 45, "DSA": 80}
    """

    df = pd.DataFrame(list(subject_scores.items()), columns=["Subject", "Score"])

    # Simple classification logic
    df["Weak"] = df["Score"] < 60

    weak_subjects = df[df["Weak"] == True]["Subject"].tolist()

    return weak_subjects
